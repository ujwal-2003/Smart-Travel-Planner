import math
import heapq
import pandas as pd


class Node:

    def __init__(self, name, latitude, longitude):

        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = {}

    def add_neighbor(self, node, distance):

        self.neighbors[node] = distance

    def __lt__(self, other):

        return self.name < other.name



class AStar:


    def __init__(self):

        self.nodes = {}



    # -------------------------
    # Calculate distance
    # -------------------------

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
            math.sin(dlat/2)**2
            +
            math.cos(lat1)
            *
            math.cos(lat2)
            *
            math.sin(dlon/2)**2
        )


        return R * 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1-a)
        )



    # -------------------------
    # Heuristic
    # -------------------------

    def heuristic(self,node1,node2):

        return self.haversine(
            node1.latitude,
            node1.longitude,
            node2.latitude,
            node2.longitude
        )



    # -------------------------
    # Create graph
    # -------------------------

    def build_graph(
        self,
        dataframe,
        neighbours=3
    ):


        for _,row in dataframe.iterrows():

            self.nodes[row["name"]] = Node(
                row["name"],
                row["latitude"],
                row["longitude"]
            )



        node_list=list(
            self.nodes.values()
        )



        for node in node_list:


            distances=[]


            for other in node_list:


                if node != other:


                    distance=self.haversine(
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
                key=lambda x:x[0]
            )



            for distance,other in distances[:neighbours]:

                node.add_neighbor(
                    other,
                    distance
                )



    # -------------------------
    # A* Search
    # -------------------------

    def search(
        self,
        start,
        goal
    ):


        if start not in self.nodes:
            return []

        if goal not in self.nodes:
            return []



        start_node=self.nodes[start]
        goal_node=self.nodes[goal]



        queue=[]

        heapq.heappush(
            queue,
            (
                0,
                start_node
            )
        )


        came_from={}


        g_score={
            node:float("inf")
            for node in self.nodes.values()
        }


        g_score[start_node]=0



        while queue:


            _,current=heapq.heappop(queue)



            if current==goal_node:


                path=[]


                while current in came_from:

                    path.append(
                        current.name
                    )

                    current=came_from[current]


                path.append(
                    start_node.name
                )


                return path[::-1]



            for neighbour,distance in current.neighbors.items():


                new_cost=(
                    g_score[current]
                    +
                    distance
                )



                if new_cost < g_score[neighbour]:


                    came_from[neighbour]=current

                    g_score[neighbour]=new_cost



                    priority=(
                        new_cost
                        +
                        self.heuristic(
                            neighbour,
                            goal_node
                        )
                    )



                    heapq.heappush(
                        queue,
                        (
                            priority,
                            neighbour
                        )
                    )


        return []