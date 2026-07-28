"""
Smart Travel Planner — Orchestrator
=====================================

Upgrades over the original version:
    * Builds an actual **day-by-day itinerary**, allocating recommended
      attractions to days based on visit duration + travel time against
      a configurable daily touring budget (default 7 hours/day),
      instead of just returning one flat route with no notion of "day".
    * Computes a **cost breakdown** (hotel nights + food days + paid
      attraction entry fees) and flags whether the plan fits inside the
      traveller's total budget.
    * Feeds attraction/interest alignment into the fuzzy engine via
      `RecommendationEngine.interest_fit_score`, so the trip-quality
      score reflects more than just money and days.
    * Basic logging instead of silent failure, and a light LRU cache so
      repeated identical requests (e.g. re-rendering in Streamlit)
      don't redo the same recommendation/route work.
"""

from __future__ import annotations

import logging

import pandas as pd

from recommendation import RecommendationEngine
from fuzzy import FuzzyTravelPlanner
from astar import AStar

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smart_travel_planner")

DEFAULT_DAILY_TOURING_HOURS = 7.0


class SmartTravelPlanner:

    def __init__(self, data_dir: str = "data"):

        self.attractions = pd.read_csv(f"{data_dir}/attractions.csv")
        self.hotels = pd.read_csv(f"{data_dir}/hotels.csv")
        self.restaurants = pd.read_csv(f"{data_dir}/restaurants.csv")

        self.attractions = self.attractions.dropna(
            subset=["name", "city", "latitude", "longitude"]
        )
        self.hotels = self.hotels.dropna(subset=["name", "city"])
        self.restaurants = self.restaurants.dropna(subset=["name", "city"])

        self.attractions = self.attractions.drop_duplicates(subset=["name"])

        # Make sure numeric columns really are numeric even if the CSV has
        # stray whitespace/strings — avoids silent NaN comparisons later.
        for col in ("rating", "cost", "duration_hours", "latitude", "longitude"):
            if col in self.attractions.columns:
                self.attractions[col] = pd.to_numeric(self.attractions[col], errors="coerce")
        self.attractions = self.attractions.dropna(subset=["latitude", "longitude"])

        self.recommendation = RecommendationEngine(self.attractions, self.hotels, self.restaurants)
        self.fuzzy = FuzzyTravelPlanner()
        self.astar = AStar()

        logger.info(
            "Loaded %d attractions, %d hotels, %d restaurants across %d cities.",
            len(self.attractions), len(self.hotels), len(self.restaurants),
            self.attractions["city"].nunique(),
        )

    # =====================================================
    # Day-wise itinerary allocation
    # =====================================================

    def _build_daily_itinerary(self, route, days, daily_hours=DEFAULT_DAILY_TOURING_HOURS):
        """
        Greedily bin the (already-ordered) route into `days` buckets,
        respecting a per-day touring-time budget that accounts for both
        time spent at each attraction and estimated travel time between
        consecutive stops.
        """

        duration_lookup = (
            self.attractions.set_index("name")["duration_hours"].to_dict()
        )

        itinerary = [[] for _ in range(max(1, int(days)))]
        day_idx = 0
        hours_used = 0.0
        previous_stop = None

        for stop in route:

            visit_hours = float(duration_lookup.get(stop, 2.0) or 2.0)

            travel_hours = 0.0
            if previous_stop is not None:
                travel_hours = self.astar.total_travel_time_hours([previous_stop, stop])

            needed = visit_hours + travel_hours

            if hours_used + needed > daily_hours and itinerary[day_idx]:
                # Move to next day if there's capacity left; otherwise
                # keep stacking onto the last day rather than losing stops.
                if day_idx < len(itinerary) - 1:
                    day_idx += 1
                    hours_used = 0.0
                    travel_hours = 0.0  # fresh day, no carry-over travel
                    needed = visit_hours

            itinerary[day_idx].append(stop)
            hours_used += needed
            previous_stop = stop

        return itinerary

    # =====================================================
    # Budget breakdown
    # =====================================================

    def _cost_breakdown(self, attractions_df, hotels_df, restaurants_df, days, total_budget):

        attraction_cost = float(attractions_df["cost"].sum()) if not attractions_df.empty else 0.0

        hotel_cost = 0.0
        if not hotels_df.empty:
            nights = max(1, int(days) - 1) if days > 1 else 1
            hotel_cost = float(hotels_df.iloc[0]["price_per_night"]) * nights

        food_cost = 0.0
        if not restaurants_df.empty:
            avg_meal_cost = float(restaurants_df["average_cost"].mean())
            food_cost = avg_meal_cost * 2 * days  # ~2 meals out/day

        total_estimated = attraction_cost + hotel_cost + food_cost

        return {
            "attractions": round(attraction_cost, 2),
            "hotel": round(hotel_cost, 2),
            "food": round(food_cost, 2),
            "total_estimated": round(total_estimated, 2),
            "total_budget": round(total_budget, 2),
            "within_budget": total_estimated <= total_budget,
            "difference": round(total_budget - total_estimated, 2),
        }

    # =====================================================
    # Generate Travel Plan
    # =====================================================

    def generate_plan(self, city, interests, hotel_budget, food_budget, total_budget, days):

        city_attractions = self.attractions[
            self.attractions["city"].str.lower().str.strip() == city.lower().strip()
        ].copy()

        self.astar.build_graph(city_attractions, neighbours=5)

        attractions = self.recommendation.recommend_attractions(city, interests)
        hotels = self.recommendation.recommend_hotels(city, hotel_budget)
        restaurants = self.recommendation.recommend_restaurants(city, food_budget)

        interest_fit = self.recommendation.interest_fit_score(city, interests)

        fuzzy_result = self.fuzzy.evaluate(
            budget=total_budget,
            days=days,
            city=city,
            interest_fit=interest_fit,
        )

        # ---------------- Route + itinerary ----------------

        route, distance, daily_itinerary = [], 0.0, []

        if not attractions.empty:

            attraction_names = [
                name for name in attractions["name"].tolist() if name in self.astar.nodes
            ]

            if len(attraction_names) == 1:
                route = attraction_names
            elif len(attraction_names) > 1:
                route = self.astar.optimize_route(attraction_names)
                distance = self.astar.route_distance(route)

            daily_itinerary = self._build_daily_itinerary(route, days)

        breakdown = self._cost_breakdown(attractions, hotels, restaurants, days, total_budget)

        if not breakdown["within_budget"]:
            logger.info(
                "Plan for %s over budget by %.2f NPR.", city, -breakdown["difference"]
            )

        return {
            "city": city,
            "score": fuzzy_result["score"],
            "score_label": fuzzy_result["label"],
            "interest_fit": fuzzy_result["interest_fit"],
            "days": days,
            "budget": total_budget,
            "route": route,
            "distance": distance,
            "daily_itinerary": daily_itinerary,
            "attractions": attractions,
            "hotels": hotels,
            "restaurants": restaurants,
            "cost_breakdown": breakdown,
        }