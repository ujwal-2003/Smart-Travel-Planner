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
        city,
        interests,
        max_results=5
    ):


        if not interests:
            return pd.DataFrame()



        # Filter city first

        attractions = self.attractions[
            self.attractions["city"]
            .str.contains(
                city,
                case=False,
                na=False
            )
        ].copy()



        if attractions.empty:
            return attractions



        # Match user interests

        pattern = "|".join(interests)



        recommendations = attractions[
            attractions["category"]
            .str.contains(
                pattern,
                case=False,
                na=False
            )
        ].copy()



        if recommendations.empty:

            # fallback: return highest rated places
            recommendations = attractions



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
        city,
        budget_per_night,
        max_results=5
    ):



        # Filter city

        hotels = self.hotels[
            self.hotels["city"]
            .str.contains(
                city,
                case=False,
                na=False
            )
        ].copy()



        if hotels.empty:
            return hotels



        # Filter budget

        affordable_hotels = hotels[
            hotels["price_per_night"]
            <= budget_per_night
        ]



        if affordable_hotels.empty:

            # If no hotel fits budget,
            # show cheapest available hotels

            hotels = hotels.sort_values(
                by="price_per_night"
            )


            return hotels.head(
                max_results
            )



        affordable_hotels = affordable_hotels.sort_values(
            by="rating",
            ascending=False
        )



        return affordable_hotels.head(
            max_results
        )



    # ---------------------------------
    # Restaurant Recommendation
    # ---------------------------------

    def recommend_restaurants(
        self,
        city,
        budget_per_meal,
        max_results=5
    ):



        # Filter city

        restaurants = self.restaurants[
            self.restaurants["city"]
            .str.contains(
                city,
                case=False,
                na=False
            )
        ].copy()



        if restaurants.empty:
            return restaurants



        # Filter budget

        affordable_restaurants = restaurants[
            restaurants["average_cost"]
            <= budget_per_meal
        ]



        if affordable_restaurants.empty:

            # fallback: cheapest restaurants

            restaurants = restaurants.sort_values(
                by="average_cost"
            )


            return restaurants.head(
                max_results
            )



        affordable_restaurants = (
            affordable_restaurants
            .sort_values(
                by="rating",
                ascending=False
            )
        )



        return affordable_restaurants.head(
            max_results
        )