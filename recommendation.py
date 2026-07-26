import pandas as pd


class RecommendationEngine:

    def __init__(
        self,
        attractions_df,
        hotels_df,
        restaurants_df
    ):

        self.attractions = attractions_df.copy()
        self.hotels = hotels_df.copy()
        self.restaurants = restaurants_df.copy()

        # ----------------------------
        # Clean Attraction Dataset
        # ----------------------------

        self.attractions["city"] = (
            self.attractions["city"]
            .astype(str)
            .str.strip()
        )

        self.attractions["category"] = (
            self.attractions["category"]
            .astype(str)
            .str.strip()
        )

        self.attractions["name"] = (
            self.attractions["name"]
            .astype(str)
            .str.strip()
        )

        # ----------------------------
        # Clean Hotel Dataset
        # ----------------------------

        self.hotels["city"] = (
            self.hotels["city"]
            .astype(str)
            .str.strip()
        )

        self.hotels["name"] = (
            self.hotels["name"]
            .astype(str)
            .str.strip()
        )

        # ----------------------------
        # Clean Restaurant Dataset
        # ----------------------------

        self.restaurants["city"] = (
            self.restaurants["city"]
            .astype(str)
            .str.strip()
        )

        self.restaurants["name"] = (
            self.restaurants["name"]
            .astype(str)
            .str.strip()
        )

    # =====================================================
    # Attraction Recommendation
    # =====================================================

    def recommend_attractions(
        self,
        city,
        interests,
        max_results=5
    ):

        city = city.strip().lower()

        attractions = self.attractions[
            self.attractions["city"]
            .str.lower()
            == city
        ].copy()

        if attractions.empty:
            return pd.DataFrame()

        # -----------------------------------------
        # If no interests selected
        # -----------------------------------------

        if not interests:

            return (
                attractions
                .sort_values(
                    by="rating",
                    ascending=False
                )
                .head(max_results)
                .reset_index(drop=True)
            )

        # -----------------------------------------
        # Match interests
        # -----------------------------------------

        interests = [
            i.lower().strip()
            for i in interests
        ]

        attractions["match_score"] = attractions[
            "category"
        ].apply(
            lambda x:
            sum(
                interest in str(x).lower()
                for interest in interests
            )
        )

        recommendations = attractions[
            attractions["match_score"] > 0
        ].copy()

        # -----------------------------------------
        # Fallback if no interest match
        # -----------------------------------------

        if recommendations.empty:

            recommendations = attractions.copy()

        recommendations = recommendations.sort_values(
            by=[
                "match_score",
                "rating"
            ],
            ascending=[
                False,
                False
            ]
        )

        recommendations = recommendations.drop_duplicates(
            subset=["name"]
        )

        return recommendations.head(
            max_results
        ).reset_index(drop=True)

    # =====================================================
    # Hotel Recommendation
    # =====================================================

    def recommend_hotels(
        self,
        city,
        budget_per_night,
        max_results=5
    ):

        city = city.strip().lower()

        hotels = self.hotels[
            self.hotels["city"]
            .str.lower()
            == city
        ].copy()

        if hotels.empty:
            return pd.DataFrame()

        hotels = hotels.sort_values(
            by="price_per_night"
        )

        affordable = hotels[
            hotels["price_per_night"]
            <= budget_per_night
        ].copy()

        if affordable.empty:

            affordable = hotels.head(max_results)

        affordable = affordable.sort_values(
            by=[
                "rating",
                "price_per_night"
            ],
            ascending=[
                False,
                True
            ]
        )

        affordable = affordable.drop_duplicates(
            subset=["name"]
        )

        return affordable.head(
            max_results
        ).reset_index(drop=True)

    # =====================================================
    # Restaurant Recommendation
    # =====================================================

    def recommend_restaurants(
        self,
        city,
        budget_per_meal,
        max_results=5
    ):

        city = city.strip().lower()

        restaurants = self.restaurants[
            self.restaurants["city"]
            .str.lower()
            == city
        ].copy()

        if restaurants.empty:
            return pd.DataFrame()

        restaurants = restaurants.sort_values(
            by="average_cost"
        )

        affordable = restaurants[
            restaurants["average_cost"]
            <= budget_per_meal
        ].copy()

        if affordable.empty:

            affordable = restaurants.head(max_results)

        affordable = affordable.sort_values(
            by=[
                "rating",
                "average_cost"
            ],
            ascending=[
                False,
                True
            ]
        )

        affordable = affordable.drop_duplicates(
            subset=["name"]
        )

        return affordable.head(
            max_results
        ).reset_index(drop=True)


