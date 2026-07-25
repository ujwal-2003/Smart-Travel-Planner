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