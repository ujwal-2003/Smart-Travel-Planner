import math
import heapq


class Node:

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = {}

    def add_neighbor(self, neighbor, distance):
        self.neighbors[neighbor] = distance


class AStar:

    def heuristic(self, node1, node2):
        """
        Straight-line distance (Euclidean).
        """
        return math.sqrt(
            (node1.latitude - node2.latitude) ** 2 +
            (node1.longitude - node2.longitude) ** 2
        )

    def search(self, start, goal):

        open_set = []

        heapq.heappush(open_set, (0, start))

        came_from = {}

        g_score = {start: 0}

        f_score = {start: self.heuristic(start, goal)}

        while open_set:

            _, current = heapq.heappop(open_set)

            if current == goal:

                path = [current.name]

                while current in came_from:
                    current = came_from[current]
                    path.append(current.name)

                return path[::-1]

            for neighbor, distance in current.neighbors.items():

                tentative_g = g_score[current] + distance

                if neighbor not in g_score or tentative_g < g_score[neighbor]:

                    came_from[neighbor] = current

                    g_score[neighbor] = tentative_g

                    f_score[neighbor] = tentative_g + self.heuristic(
                        neighbor,
                        goal
                    )

                    heapq.heappush(
                        open_set,
                        (
                            f_score[neighbor],
                            neighbor
                        )
                    )

        return None