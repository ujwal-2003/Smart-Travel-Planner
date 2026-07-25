import math
import heapq
import pandas as pd


class Node:

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = {}

    def add_neighbor(self, neighbor, distance):
        self.neighbors[neighbor] = distance

    def __lt__(self, other):
        return self.name < other.name


class AStar:

    def __init__(self):
        self.nodes = {}

    # ----------------------------------------
    # Haversine Distance (Kilometres)
    # ----------------------------------------

    def haversine(self, lat1, lon1, lat2, lon2):

        R = 6371

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)

        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    # ----------------------------------------
    # Straight-line heuristic
    # ----------------------------------------

    def heuristic(self, node1, node2):

        return self.haversine(
            node1.latitude,
            node1.longitude,
            node2.latitude,
            node2.longitude
        )

    # ----------------------------------------
    # Build graph automatically from CSV
    # ----------------------------------------

    def build_graph(self, csv_path, neighbors=3):

        df = pd.read_csv(csv_path)

        # Create nodes

        for _, row in df.iterrows():

            self.nodes[row["name"]] = Node(
                row["name"],
                row["latitude"],
                row["longitude"]
            )

        # Connect nearest neighbours

        node_list = list(self.nodes.values())

        for node in node_list:

            distances = []

            for other in node_list:

                if node == other:
                    continue

                distance = self.haversine(
                    node.latitude,
                    node.longitude,
                    other.latitude,
                    other.longitude
                )

                distances.append((distance, other))

            distances.sort(key=lambda x: x[0])

            for distance, other in distances[:neighbors]:
                node.add_neighbor(other, distance)

    # ----------------------------------------
    # A* Search
    # ----------------------------------------

    def search(self, start_name, goal_name):

        start = self.nodes[start_name]
        goal = self.nodes[goal_name]

        open_set = []

        heapq.heappush(open_set, (0, start))

        came_from = {}

        g_score = {
            node: float("inf")
            for node in self.nodes.values()
        }

        g_score[start] = 0

        f_score = {
            node: float("inf")
            for node in self.nodes.values()
        }

        f_score[start] = self.heuristic(start, goal)

        while open_set:

            _, current = heapq.heappop(open_set)

            if current == goal:

                path = []

                while current in came_from:

                    path.append(current.name)

                    current = came_from[current]

                path.append(start.name)

                return path[::-1]

            for neighbor, distance in current.neighbors.items():

                tentative = g_score[current] + distance

                if tentative < g_score[neighbor]:

                    came_from[neighbor] = current

                    g_score[neighbor] = tentative

                    f_score[neighbor] = (
                        tentative
                        + self.heuristic(neighbor, goal)
                    )

                    heapq.heappush(
                        open_set,
                        (
                            f_score[neighbor],
                            neighbor
                        )
                    )

        return None