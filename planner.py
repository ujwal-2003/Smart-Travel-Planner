
import pandas as pd

from recommendation import RecommendationEngine
from fuzzy import FuzzyTravelPlanner
from astar import AStar


class SmartTravelPlanner:

    def __init__(self):

        # =====================================
        # Load Datasets
        # =====================================

        self.attractions = pd.read_csv("data/attractions.csv")
        self.hotels = pd.read_csv("data/hotels.csv")
        self.restaurants = pd.read_csv("data/restaurants.csv")

        # Remove missing values
        self.attractions = self.attractions.dropna(
            subset=["name", "city", "latitude", "longitude"]
        )

        self.hotels = self.hotels.dropna(subset=["name", "city"])
        self.restaurants = self.restaurants.dropna(subset=["name", "city"])

        # Remove duplicate attraction names
        self.attractions = self.attractions.drop_duplicates(
            subset=["name"]
        )

        # =====================================
        # AI Components
        # =====================================

        self.recommendation = RecommendationEngine(
            self.attractions,
            self.hotels,
            self.restaurants
        )

        self.fuzzy = FuzzyTravelPlanner()

        self.astar = AStar()

    # =====================================
    # Generate Travel Plan
    # =====================================

    def generate_plan(
        self,
        city,
        interests,
        hotel_budget,
        food_budget,
        total_budget,
        days
    ):

        # =====================================
        # Attractions for Selected City
        # =====================================

        city_attractions = self.attractions[
            self.attractions["city"].str.lower().str.strip()
            ==
            city.lower().strip()
        ].copy()

        # Build graph
        self.astar.build_graph(
            city_attractions,
            neighbours=5
        )

        # =====================================
        # Recommendation System
        # =====================================

        attractions = self.recommendation.recommend_attractions(
            city,
            interests
        )

        hotels = self.recommendation.recommend_hotels(
            city,
            hotel_budget
        )

        restaurants = self.recommendation.recommend_restaurants(
            city,
            food_budget
        )

        # =====================================
        # Fuzzy Evaluation
        # =====================================

        score = self.fuzzy.evaluate(
            total_budget,
            days,
            city
        )

        # =====================================
        # Route Optimization
        # =====================================

        route = []
        distance = 0

        if not attractions.empty:

            attraction_names = attractions["name"].tolist()

            # keep only attractions that exist in graph
            attraction_names = [
                name
                for name in attraction_names
                if name in self.astar.nodes
            ]

            if len(attraction_names) == 1:

                route = attraction_names
                distance = 0

            elif len(attraction_names) > 1:

                route = self.astar.optimize_route(
                    attraction_names
                )

                distance = self.astar.route_distance(
                    route
                )

        # =====================================
        # Return Results
        # =====================================

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

