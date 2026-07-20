from astar import Node, AStar

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