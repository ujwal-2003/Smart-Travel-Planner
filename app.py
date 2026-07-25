from planner import SmartTravelPlanner


def main():

    planner = SmartTravelPlanner()

    planner.generate_plan(
        interests=["Nature", "Hiking"],
        hotel_budget=3500,
        food_budget=1000,
        total_budget=20000,
        days=3
    )


if __name__ == "__main__":
    main()
from astar import AStar

astar = AStar()

astar.build_graph(
    "data/attractions.csv",
    neighbors=3
)

route = astar.search(
    "Phewa Lake",
    "Davis Falls"
)

print("Optimized Route")
print(route)
