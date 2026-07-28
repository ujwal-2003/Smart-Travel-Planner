"""
Recommendation Engine
=======================

Upgrades over the original version:
    * Interest matching now uses TF-IDF + cosine similarity over each
      attraction's category text instead of a plain substring count.
      This still works with the single-category dataset used here, but
      generalises cleanly if a future dataset has richer, multi-word
      category/tag text (e.g. "Nature, Hiking, Photography").
    * Attraction/hotel/restaurant scores are now a single weighted
      composite (interest fit, rating, budget fit) instead of pure
      sort-by-rating, so a slightly cheaper 4.6-star option can
      outrank a 4.7-star option that blows the budget.
    * Budget matching is now a *soft* fit score (closer to the budget
      is better, going over budget is penalised but not an outright
      cutoff) rather than a hard `<=` filter — this avoids the old
      "silently returns the 5 cheapest hotels" fallback returning
      options that have nothing to do with the traveller's budget.
    * `interest_fit_score()` exposes a single 0-10 number summarising
      how well the recommended attractions match stated interests, fed
      into the fuzzy trip-quality evaluation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize(series: pd.Series) -> pd.Series:
    """Min-max normalise a numeric series to 0-1, safe against constant columns."""
    if series.empty:
        return series
    lo, hi = series.min(), series.max()
    if hi - lo < 1e-9:
        return pd.Series(np.ones(len(series)) * 0.5, index=series.index)
    return (series - lo) / (hi - lo)


def _budget_fit(cost: pd.Series, budget: float) -> pd.Series:
    """
    Soft budget-fit score in [0, 1]. 1.0 = right at or comfortably under
    budget, decaying smoothly for items above budget rather than being
    hard-excluded.
    """
    if budget <= 0:
        budget = 1  # avoid division by zero on a degenerate input

    ratio = cost / budget
    # At or under budget -> full score, tapering slightly as it approaches
    # the limit; over budget -> exponential falloff.
    fit = np.where(
        ratio <= 1.0,
        1.0 - 0.15 * ratio,
        np.exp(-(ratio - 1.0) * 2.5),
    )
    return pd.Series(fit, index=cost.index)


class RecommendationEngine:

    def __init__(self, attractions_df, hotels_df, restaurants_df):

        self.attractions = attractions_df.copy()
        self.hotels = hotels_df.copy()
        self.restaurants = restaurants_df.copy()

        for df, cols in (
            (self.attractions, ["city", "category", "name"]),
            (self.hotels, ["city", "name"]),
            (self.restaurants, ["city", "name"]),
        ):
            for col in cols:
                df[col] = df[col].astype(str).str.strip()

        # Pre-fit a TF-IDF vectorizer over attraction categories once, at
        # construction time, rather than rebuilding it on every request.
        self._vectorizer = TfidfVectorizer()
        categories = self.attractions["category"].fillna("").tolist()
        if categories:
            self._category_matrix = self._vectorizer.fit_transform(categories)
        else:
            self._category_matrix = None

    # =====================================================
    # Attraction Recommendation
    # =====================================================

    def _interest_similarity(self, city_attractions: pd.DataFrame, interests: list[str]) -> pd.Series:
        """
        Cosine similarity between each attraction's category text and the
        traveller's interest list (interests joined into one "query
        document"). Falls back gracefully to zeros if vectorizer/corpus
        is empty.
        """

        if not interests or self._category_matrix is None:
            return pd.Series(np.zeros(len(city_attractions)), index=city_attractions.index)

        query = " ".join(interests)
        query_vec = self._vectorizer.transform([query])

        # Re-vectorize just this city's rows using the *same* fitted
        # vocabulary so the similarity is directly comparable.
        city_vecs = self._vectorizer.transform(city_attractions["category"].fillna(""))

        sims = cosine_similarity(query_vec, city_vecs).flatten()
        return pd.Series(sims, index=city_attractions.index)

    def recommend_attractions(self, city, interests, max_results=5):

        city = city.strip().lower()

        attractions = self.attractions[
            self.attractions["city"].str.lower() == city
        ].copy()

        if attractions.empty:
            return pd.DataFrame()

        interests = [i.lower().strip() for i in interests] if interests else []

        similarity = self._interest_similarity(attractions, interests)
        attractions["interest_match"] = similarity

        # If nothing matched at all (e.g. interests picked a category not
        # present in this city), fall back to rating-only ranking instead
        # of an empty result.
        rating_norm = _normalize(attractions["rating"])

        if interests and similarity.max() > 0:
            attractions["composite_score"] = (
                0.65 * _normalize(similarity) + 0.35 * rating_norm
            )
        else:
            attractions["composite_score"] = rating_norm

        recommendations = (
            attractions
            .drop_duplicates(subset=["name"])
            .sort_values(by="composite_score", ascending=False)
            .head(max_results)
            .reset_index(drop=True)
        )

        return recommendations

    def interest_fit_score(self, city, interests) -> float:
        """
        0-10 summary of how well the *full* pool of city attractions
        matches the traveller's interests — used as a fuzzy-logic input
        so the trip-quality score reflects interest alignment, not just
        money and time.
        """

        city = city.strip().lower()
        attractions = self.attractions[self.attractions["city"].str.lower() == city]

        if attractions.empty or not interests:
            return 5.0  # neutral when we have nothing to judge against

        similarity = self._interest_similarity(attractions, [i.lower().strip() for i in interests])
        if similarity.empty:
            return 5.0

        # Average of top matches scaled to 0-10; using the mean of the
        # best few keeps one lucky high match from dominating the score.
        top = similarity.sort_values(ascending=False).head(5)
        return float(round(top.mean() * 10, 2))

    # =====================================================
    # Hotel Recommendation
    # =====================================================

    def recommend_hotels(self, city, budget_per_night, max_results=5):

        city = city.strip().lower()

        hotels = self.hotels[self.hotels["city"].str.lower() == city].copy()

        if hotels.empty:
            return pd.DataFrame()

        hotels["budget_fit"] = _budget_fit(hotels["price_per_night"], budget_per_night)
        hotels["composite_score"] = (
            0.55 * hotels["budget_fit"] + 0.45 * _normalize(hotels["rating"])
        )

        recommendations = (
            hotels
            .drop_duplicates(subset=["name"])
            .sort_values(by="composite_score", ascending=False)
            .head(max_results)
            .reset_index(drop=True)
        )

        return recommendations

    # =====================================================
    # Restaurant Recommendation
    # =====================================================

    def recommend_restaurants(self, city, budget_per_meal, max_results=5):

        city = city.strip().lower()

        restaurants = self.restaurants[self.restaurants["city"].str.lower() == city].copy()

        if restaurants.empty:
            return pd.DataFrame()

        restaurants["budget_fit"] = _budget_fit(restaurants["average_cost"], budget_per_meal)
        restaurants["composite_score"] = (
            0.55 * restaurants["budget_fit"] + 0.45 * _normalize(restaurants["rating"])
        )

        recommendations = (
            restaurants
            .drop_duplicates(subset=["name"])
            .sort_values(by="composite_score", ascending=False)
            .head(max_results)
            .reset_index(drop=True)
        )

        return recommendations