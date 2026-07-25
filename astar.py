import math
import heapq



# =====================================
# Node Class
# =====================================

class Node:


    def __init__(
        self,
        name,
        latitude,
        longitude
    ):

        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.neighbors = {}



    def add_neighbor(
        self,
        node,
        distance
    ):

        self.neighbors[node] = distance



    def __lt__(
        self,
        other
    ):

        return self.name < other.name





# =====================================
# A* Search Algorithm
# =====================================

class AStar:


    def __init__(self):

        self.nodes = {}



    # =================================
    # Haversine Distance (KM)
    # =================================

    def haversine(
        self,
        lat1,
        lon1,
        lat2,
        lon2
    ):


        R = 6371


        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)

        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)



        dlat = lat2 - lat1
        dlon = lon2 - lon1



        a = (
            math.sin(dlat / 2) ** 2
            +
            math.cos(lat1)
            *
            math.cos(lat2)
            *
            math.sin(dlon / 2) ** 2
        )


        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )


        return R * c





    # =================================
    # Heuristic Function
    # =================================

    def heuristic(
        self,
        node1,
        node2
    ):


        return self.haversine(

            node1.latitude,
            node1.longitude,

            node2.latitude,
            node2.longitude

        )





    # =================================
    # Build Graph
    # =================================

    def build_graph(
        self,
        dataframe,
        neighbours=4
    ):


        self.nodes = {}



        # Create nodes

        for _, row in dataframe.iterrows():


            node = Node(

                row["name"],
                row["latitude"],
                row["longitude"]

            )


            self.nodes[row["name"]] = node




        node_list = list(
            self.nodes.values()
        )



        # Connect nearest attractions

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


                distances.append(
                    (
                        distance,
                        other
                    )
                )



            distances.sort(
                key=lambda x: x[0]
            )



            for distance, neighbour in distances[:neighbours]:


                node.add_neighbor(

                    neighbour,
                    distance

                )





    # =================================
    # A* Search
    # =================================

    def search(
        self,
        start_name,
        goal_name
    ):


        if start_name not in self.nodes:
            return []


        if goal_name not in self.nodes:
            return []



        start = self.nodes[start_name]

        goal = self.nodes[goal_name]



        open_list = []



        heapq.heappush(

            open_list,

            (
                0,
                start
            )

        )



        came_from = {}



        g_score = {

            node: float("inf")

            for node in self.nodes.values()

        }



        g_score[start] = 0



        visited = set()



        while open_list:


            current = heapq.heappop(
                open_list
            )[1]



            if current in visited:
                continue



            visited.add(current)



            # Destination reached

            if current == goal:


                return self.reconstruct_path(

                    came_from,
                    current

                )



            for neighbour, distance in current.neighbors.items():



                tentative_g = (

                    g_score[current]
                    +
                    distance

                )



                if tentative_g < g_score[neighbour]:


                    came_from[neighbour] = current



                    g_score[neighbour] = tentative_g



                    f_score = (

                        tentative_g
                        +
                        self.heuristic(
                            neighbour,
                            goal
                        )

                    )



                    heapq.heappush(

                        open_list,

                        (
                            f_score,
                            neighbour
                        )

                    )



        return []





    # =================================
    # Reconstruct Path
    # =================================

    def reconstruct_path(
        self,
        came_from,
        current
    ):


        path = [

            current.name

        ]



        while current in came_from:


            current = came_from[current]


            path.append(

                current.name

            )



        path.reverse()



        return path





    # =================================
    # Calculate Route Distance
    # =================================

    def route_distance(
        self,
        route
    ):


        total_distance = 0



        for i in range(
            len(route)-1
        ):


            current = self.nodes[route[i]]

            next_node = self.nodes[route[i+1]]



            total_distance += self.haversine(

                current.latitude,
                current.longitude,

                next_node.latitude,
                next_node.longitude

            )



        return round(
            total_distance,
            2
        )