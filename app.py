import pandas as pd

from fuzzy import FuzzyTravelPlanner

from astar import Node, AStar

from recommendation import RecommendationEngine

# Load datasets
attractions = pd.read_csv("data/attractions.csv")
hotels = pd.read_csv("data/hotels.csv")
restaurants = pd.read_csv("data/restaurants.csv")

# Create Recommendation Engine
engine = RecommendationEngine(
    attractions,
    hotels,
    restaurants
)

# Example User Preferences
interests = ["Nature", "Hiking"]
hotel_budget = 3500
food_budget = 1000

print("=" * 50)
print("Recommended Attractions")
print("=" * 50)

print(
    engine.recommend_attractions(interests)
)

print("\n")

print("=" * 50)
print("Recommended Hotels")
print("=" * 50)

print(
    engine.recommend_hotels(hotel_budget)
)

print("\n")

print("=" * 50)
print("Recommended Restaurants")
print("=" * 50)

print(
    engine.recommend_restaurants(food_budget)
)
hotel = Node("Hotel", 28.2095, 83.9602)

phewa = Node("Phewa Lake", 28.2096, 83.9596)

peace = Node("World Peace Pagoda", 28.2004, 83.9448)

davis = Node("Davis Falls", 28.1937, 83.9591)

hotel.add_neighbor(phewa, 2)

phewa.add_neighbor(peace, 4)

peace.add_neighbor(davis, 3)

astar = AStar()

route = astar.search(
    hotel,
    davis
)

print(route)
planner = FuzzyTravelPlanner()

budget = 12000
days = 5

score = planner.evaluate(budget, days)

print("=" * 40)
print("FUZZY TRAVEL SCORE")
print("=" * 40)
print(f"Budget : NPR {budget}")
print(f"Days   : {days}")
print(f"Score  : {score:.2f}/100")
