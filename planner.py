import pandas as pd

from recommendation import RecommendationEngine
from fuzzy import FuzzyTravelPlanner
from astar import AStar



class SmartTravelPlanner:


    def __init__(self):


        # -----------------------------
        # Load datasets
        # -----------------------------

        self.attractions = pd.read_csv(
            "data/attractions.csv"
        )


        self.hotels = pd.read_csv(
            "data/hotels.csv"
        )


        self.restaurants = pd.read_csv(
            "data/restaurants.csv"
        )



        # -----------------------------
        # AI Components
        # -----------------------------

        self.recommendation = RecommendationEngine(

            self.attractions,
            self.hotels,
            self.restaurants

        )


        self.fuzzy = FuzzyTravelPlanner()


        self.astar = AStar()



    # =================================
    # Generate Travel Plan
    # =================================

    def generate_plan(
        self,
        city,
        interests,
        hotel_budget,
        food_budget,
        total_budget,
        days
    ):



        # -----------------------------
        # Filter city attractions
        # -----------------------------

        city_attractions = self.attractions[

            self.attractions["city"]
            .str.contains(
                city,
                case=False,
                na=False
            )

        ].copy()



        # -----------------------------
        # Build A* Graph
        # -----------------------------

        if not city_attractions.empty:

            self.astar.build_graph(
                city_attractions
            )



        # -----------------------------
        # Fuzzy Evaluation
        # -----------------------------

        score = self.fuzzy.evaluate(

            total_budget,
            days,
            city

        )



        # -----------------------------
        # Recommendation System
        # -----------------------------

        attractions = (
            self.recommendation
            .recommend_attractions(

                city,
                interests

            )
        )



        hotels = (
            self.recommendation
            .recommend_hotels(

                city,
                hotel_budget

            )
        )



        restaurants = (
            self.recommendation
            .recommend_restaurants(

                city,
                food_budget

            )
        )



        # -----------------------------
        # A* Route Generation
        # -----------------------------

        route = []

        distance = 0



        if len(attractions) >= 2:


            start = attractions.iloc[0]["name"]

            goal = attractions.iloc[-1]["name"]



            route = self.astar.search(

                start,
                goal

            )



            if route:

                distance = self.astar.route_distance(
                    route
                )



        # -----------------------------
        # Return Complete Plan
        # -----------------------------

        return {


            "city": city,


            "score": score,


            "days": days,


            "budget": total_budget,


            "route": route,


            "distance": distance,


            "attractions": attractions,


            "hotels": hotels,


            "restaurants": restaurants

        }