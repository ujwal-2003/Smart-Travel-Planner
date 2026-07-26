import math         
import heapq


# =====================================
# Node Class
# =====================================

class Node:
    def __init__(self, name, latitude, longitude):
        self.name = str(name).strip()
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.neighbors = {}

    def add_neighbor(self, node, distance):
        self.neighbors[node] = distance

    def __lt__(self, other):
        return self.name < other.name


# =====================================
# A* Route Planner
# =====================================

class AStar:

    def __init__(self):
        self.nodes = {}

    # =================================
    # Haversine Distance (KM)
    # =================================

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):

        R = 6371

        lat1 = math.radians(float(lat1))
        lon1 = math.radians(float(lon1))
        lat2 = math.radians(float(lat2))
        lon2 = math.radians(float(lon2))

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

    # =================================
    # Heuristic
    # =================================

    def heuristic(self, node1, node2):
        return self.haversine(
            node1.latitude,
            node1.longitude,
            node2.latitude,
            node2.longitude
        )

    # =================================
    # Build Graph
    # =================================

    def build_graph(self, dataframe, neighbours=4):

        self.nodes = {}

        if dataframe.empty:
            return

        # -----------------------------
        # Create Nodes
        # -----------------------------
        for _, row in dataframe.iterrows():

            if (
                "latitude" not in row
                or "longitude" not in row
            ):
                continue

            try:
                node = Node(
                    row["name"],
                    row["latitude"],
                    row["longitude"]
                )

                self.nodes[node.name] = node

            except Exception:
                continue

        node_list = list(self.nodes.values())

        if len(node_list) < 2:
            return

        neighbours = min(neighbours, len(node_list) - 1)

        # -----------------------------
        # Connect nearest neighbours
        # -----------------------------
        for node in node_list:

            distances = []

            for other in node_list:

                if node == other:
                    continue

                d = self.haversine(
                    node.latitude,
                    node.longitude,
                    other.latitude,
                    other.longitude
                )

                distances.append((d, other))

            distances.sort(key=lambda x: x[0])

            for distance, neighbour in distances[:neighbours]:

                # IMPORTANT:
                # Make graph bidirectional
                node.add_neighbor(neighbour, distance)
                neighbour.add_neighbor(node, distance)

    # =================================
    # A* Search
    # =================================

    def search(self, start_name, goal_name):

        start_name = start_name.strip()
        goal_name = goal_name.strip()

        if start_name not in self.nodes:
            return []

        if goal_name not in self.nodes:
            return []

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

            current = heapq.heappop(open_set)[1]

            if current == goal:
                return self.reconstruct_path(
                    came_from,
                    current
                )

            for neighbour, distance in current.neighbors.items():

                tentative = g_score[current] + distance

                if tentative < g_score[neighbour]:

                    came_from[neighbour] = current

                    g_score[neighbour] = tentative

                    f = tentative + self.heuristic(
                        neighbour,
                        goal
                    )

                    f_score[neighbour] = f

                    heapq.heappush(
                        open_set,
                        (f, neighbour)
                    )

        return []

    # =================================
    # Reconstruct Path
    # =================================

    def reconstruct_path(self, came_from, current):

        path = [current.name]

        while current in came_from:

            current = came_from[current]

            path.append(current.name)

        path.reverse()

        return path

    # =================================
    # Route Distance
    # =================================

    def route_distance(self, route):

        if len(route) < 2:
            return 0

        total = 0

        for i in range(len(route) - 1):

            n1 = self.nodes[route[i]]
            n2 = self.nodes[route[i + 1]]

            total += self.haversine(
                n1.latitude,
                n1.longitude,
                n2.latitude,
                n2.longitude
            )

        return round(total, 2)

    # =================================
    # Visit All Attractions
    # (Nearest Neighbour Algorithm)
    # =================================

    def optimize_route(self, attraction_names):

        attraction_names = [
            name for name in attraction_names
            if name in self.nodes
        ]

        if len(attraction_names) <= 1:
            return attraction_names

        unvisited = attraction_names.copy()

        route = [unvisited.pop(0)]

        while unvisited:

            current = self.nodes[route[-1]]

            nearest = min(
                unvisited,
                key=lambda x: self.haversine(
                    current.latitude,
                    current.longitude,
                    self.nodes[x].latitude,
                    self.nodes[x].longitude,
                ),
            )

            route.append(nearest)
            unvisited.remove(nearest)

        return route



