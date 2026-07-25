import pandas as pd

from recommendation import RecommendationEngine
from fuzzy import FuzzyTravelPlanner
from astar import AStar



class SmartTravelPlanner:


    def __init__(self):


        # Load datasets

        self.attractions = pd.read_csv(
            "data/attractions.csv"
        )


        self.hotels = pd.read_csv(
            "data/hotels.csv"
        )


        self.restaurants = pd.read_csv(
            "data/restaurants.csv"
        )



        # AI modules

        self.recommendation = RecommendationEngine(
            self.attractions,
            self.hotels,
            self.restaurants
        )


        self.fuzzy = FuzzyTravelPlanner()


        self.astar = AStar()



        # Build route graph

        self.astar.build_graph(
            self.attractions
        )



    # ----------------------------------
    # Generate Complete Travel Plan
    # ----------------------------------

    def generate_plan(
        self,
        interests,
        hotel_budget,
        food_budget,
        total_budget,
        days
    ):



        # -------------------------
        # Fuzzy Evaluation
        # -------------------------

        score = self.fuzzy.evaluate(
            total_budget,
            days
        )



        # -------------------------
        # Recommendations
        # -------------------------

        attractions = (
            self.recommendation
            .recommend_attractions(
                interests
            )
        )


        hotels = (
            self.recommendation
            .recommend_hotels(
                hotel_budget
            )
        )


        restaurants = (
            self.recommendation
            .recommend_restaurants(
                food_budget
            )
        )



        # -------------------------
        # A* Route Generation
        # -------------------------

        route = []



        if len(attractions) >= 2:


            start = attractions.iloc[0]["name"]

            goal = attractions.iloc[-1]["name"]



            route = self.astar.search(
                start,
                goal
            )



        return {


            "score": score,


            "days": days,


            "budget": total_budget,


            "route": route,


            "attractions": attractions,


            "hotels": hotels,


            "restaurants": restaurants

        }