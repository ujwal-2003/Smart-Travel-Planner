import pandas as pd

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