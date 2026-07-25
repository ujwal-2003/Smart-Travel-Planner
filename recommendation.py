import pandas as pd


class RecommendationEngine:


    def __init__(
        self,
        attractions_df,
        hotels_df,
        restaurants_df
    ):

        self.attractions = attractions_df
        self.hotels = hotels_df
        self.restaurants = restaurants_df



    # ---------------------------------
    # Attraction Recommendation
    # ---------------------------------

    def recommend_attractions(
        self,
        interests,
        max_results=5
    ):


        if not interests:
            return pd.DataFrame()



        pattern = "|".join(interests)



        recommendations = self.attractions[
            self.attractions["category"]
            .str.contains(
                pattern,
                case=False,
                na=False
            )
        ].copy()



        if recommendations.empty:
            return recommendations



        recommendations = recommendations.sort_values(
            by="rating",
            ascending=False
        )


        return recommendations.head(
            max_results
        )



    # ---------------------------------
    # Hotel Recommendation
    # ---------------------------------

    def recommend_hotels(
        self,
        budget_per_night,
        max_results=5
    ):


        hotels = self.hotels[
            self.hotels["price_per_night"]
            <= budget_per_night
        ].copy()



        if hotels.empty:
            return hotels



        hotels = hotels.sort_values(
            by="rating",
            ascending=False
        )



        return hotels.head(
            max_results
        )



    # ---------------------------------
    # Restaurant Recommendation
    # ---------------------------------

    def recommend_restaurants(
        self,
        budget_per_meal,
        max_results=5
    ):


        restaurants = self.restaurants[
            self.restaurants["average_cost"]
            <= budget_per_meal
        ].copy()



        if restaurants.empty:
            return restaurants



        restaurants = restaurants.sort_values(
            by="rating",
            ascending=False
        )



        return restaurants.head(
            max_results
        )