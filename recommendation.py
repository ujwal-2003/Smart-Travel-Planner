import pandas as pd


class RecommendationEngine:
    def __init__(self, attractions_df, hotels_df, restaurants_df):
        self.attractions = attractions_df
        self.hotels = hotels_df
        self.restaurants = restaurants_df

    # -----------------------------
    # Attraction Recommendation
    # -----------------------------
    def recommend_attractions(self, interests, max_results=5):
        """
        Recommend attractions based on user interests.

        Parameters:
            interests (list): Example ["Nature", "Hiking"]
            max_results (int): Number of recommendations

        Returns:
            DataFrame
        """

        recommendations = self.attractions[
            self.attractions["category"].isin(interests)
        ].copy()

        recommendations = recommendations.sort_values(
            by="rating",
            ascending=False
        )

        return recommendations.head(max_results)

    # -----------------------------
    # Hotel Recommendation
    # -----------------------------
    def recommend_hotels(self, budget_per_night, max_results=5):

        hotels = self.hotels[
            self.hotels["price_per_night"] <= budget_per_night
        ].copy()

        hotels = hotels.sort_values(
            by="rating",
            ascending=False
        )

        return hotels.head(max_results)

    # -----------------------------
    # Restaurant Recommendation
    # -----------------------------
    def recommend_restaurants(self, budget_per_meal, max_results=5):

        restaurants = self.restaurants[
            self.restaurants["average_cost"] <= budget_per_meal
        ].copy()

        restaurants = restaurants.sort_values(
            by="rating",
            ascending=False
        )

        return restaurants.head(max_results)