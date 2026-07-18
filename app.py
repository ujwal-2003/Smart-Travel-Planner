import pandas as pd

attractions = pd.read_csv("data/attractions.csv")
hotels = pd.read_csv("data/hotels.csv")
restaurants = pd.read_csv("data/restaurants.csv")

print("Attractions")
print(attractions.head())

print("\nHotels")
print(hotels.head())

print("\nRestaurants")
print(restaurants.head())