import pandas as pd

from recommendation import RecommendationEngine
from fuzzy import FuzzyTravelPlanner
from astar import Node, AStar


class SmartTravelPlanner:

    def __init__(self):

        # Load datasets
        self.attractions = pd.read_csv("data/attractions.csv")
        self.hotels = pd.read_csv("data/hotels.csv")
        self.restaurants = pd.read_csv("data/restaurants.csv")

        # AI Components
        self.recommendation = RecommendationEngine(
            self.attractions,
            self.hotels,
            self.restaurants
        )

        self.fuzzy = FuzzyTravelPlanner()

        self.astar = AStar()

    # --------------------------------------------------

    def generate_plan(
        self,
        interests,
        hotel_budget,
        food_budget,
        total_budget,
        days
    ):

        print("=" * 60)
        print("SMART TRAVEL PLANNER")
        print("=" * 60)

        # -----------------------------
        # Fuzzy Evaluation
        # -----------------------------

        score = self.fuzzy.evaluate(
            total_budget,
            days
        )

        print(f"\nTrip Suitability Score : {score:.2f}/100")

        # -----------------------------
        # Attractions
        # -----------------------------

        attractions = self.recommendation.recommend_attractions(
            interests
        )

        print("\nRecommended Attractions")

        for _, row in attractions.iterrows():

            print(
                f"• {row['name']} "
                f"({row['category']}) "
                f"⭐ {row['rating']}"
            )

        # -----------------------------
        # Hotels
        # -----------------------------

        hotels = self.recommendation.recommend_hotels(
            hotel_budget
        )

        print("\nRecommended Hotels")

        for _, row in hotels.iterrows():

            print(
                f"• {row['name']} "
                f"NPR {row['price_per_night']} "
                f"⭐ {row['rating']}"
            )

        # -----------------------------
        # Restaurants
        # -----------------------------

        restaurants = self.recommendation.recommend_restaurants(
            food_budget
        )

        print("\nRecommended Restaurants")

        for _, row in restaurants.iterrows():

            print(
                f"• {row['name']} "
                f"NPR {row['average_cost']} "
                f"⭐ {row['rating']}"
            )

        # -----------------------------
        # Simple Route Demonstration
        # -----------------------------

        print("\nSuggested Route")

        nodes = []

        for _, row in attractions.iterrows():

            nodes.append(
                Node(
                    row["name"],
                    row["latitude"],
                    row["longitude"]
                )
            )

        if len(nodes) > 1:

            route = []

            for i in range(len(nodes) - 1):
                route.append(nodes[i].name)

            route.append(nodes[-1].name)

            print(" -> ".join(route))

        print("\nTrip Planning Complete!")

        return {
            "score": score,
            "attractions": attractions,
            "hotels": hotels,
            "restaurants": restaurants
        }