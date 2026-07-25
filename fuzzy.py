import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl



class FuzzyTravelPlanner:


    def __init__(self):


        # ---------------------------------
        # INPUT VARIABLES
        # ---------------------------------

        self.budget = ctrl.Antecedent(
            np.arange(0, 100001, 1000),
            "budget"
        )


        self.days = ctrl.Antecedent(
            np.arange(1, 15, 1),
            "days"
        )


        self.destination_cost = ctrl.Antecedent(
            np.arange(0, 11, 1),
            "destination_cost"
        )



        # ---------------------------------
        # OUTPUT VARIABLE
        # ---------------------------------

        self.trip_quality = ctrl.Consequent(
            np.arange(0, 101, 1),
            "trip_quality"
        )



        # ---------------------------------
        # Budget Membership
        # ---------------------------------

        self.budget["low"] = fuzz.trimf(
            self.budget.universe,
            [0, 0, 30000]
        )


        self.budget["medium"] = fuzz.trimf(
            self.budget.universe,
            [20000, 50000, 70000]
        )


        self.budget["high"] = fuzz.trimf(
            self.budget.universe,
            [60000, 100000, 100000]
        )



        # ---------------------------------
        # Days Membership
        # ---------------------------------

        self.days["short"] = fuzz.trimf(
            self.days.universe,
            [1, 1, 4]
        )


        self.days["medium"] = fuzz.trimf(
            self.days.universe,
            [3, 7, 10]
        )


        self.days["long"] = fuzz.trimf(
            self.days.universe,
            [8, 14, 14]
        )



        # ---------------------------------
        # Destination Cost
        # ---------------------------------

        self.destination_cost["cheap"] = fuzz.trimf(
            self.destination_cost.universe,
            [0, 0, 4]
        )


        self.destination_cost["average"] = fuzz.trimf(
            self.destination_cost.universe,
            [3, 5, 7]
        )


        self.destination_cost["expensive"] = fuzz.trimf(
            self.destination_cost.universe,
            [6, 10, 10]
        )



        # ---------------------------------
        # Output Membership
        # ---------------------------------

        self.trip_quality["poor"] = fuzz.trimf(
            self.trip_quality.universe,
            [0, 0, 40]
        )


        self.trip_quality["average"] = fuzz.trimf(
            self.trip_quality.universe,
            [30, 50, 70]
        )


        self.trip_quality["good"] = fuzz.trimf(
            self.trip_quality.universe,
            [60, 75, 90]
        )


        self.trip_quality["excellent"] = fuzz.trimf(
            self.trip_quality.universe,
            [80, 100, 100]
        )



        # ---------------------------------
        # FUZZY RULES
        # ---------------------------------

        rules = [

            # Low budget

            ctrl.Rule(
                self.budget["low"]
                &
                self.destination_cost["expensive"],
                self.trip_quality["poor"]
            ),


            ctrl.Rule(
                self.budget["low"]
                &
                self.destination_cost["cheap"],
                self.trip_quality["average"]
            ),


            ctrl.Rule(
                self.budget["low"]
                &
                self.days["short"],
                self.trip_quality["average"]
            ),



            # Medium budget

            ctrl.Rule(
                self.budget["medium"]
                &
                self.destination_cost["average"],
                self.trip_quality["good"]
            ),


            ctrl.Rule(
                self.budget["medium"]
                &
                self.days["medium"],
                self.trip_quality["good"]
            ),



            # High budget

            ctrl.Rule(
                self.budget["high"]
                &
                self.destination_cost["expensive"],
                self.trip_quality["excellent"]
            ),


            ctrl.Rule(
                self.budget["high"]
                &
                self.days["long"],
                self.trip_quality["excellent"]
            ),



            # Balanced trip

            ctrl.Rule(
                self.budget["medium"]
                &
                self.days["short"],
                self.trip_quality["average"]
            ),


            ctrl.Rule(
                self.budget["high"]
                &
                self.destination_cost["average"],
                self.trip_quality["excellent"]
            )

        ]



        system = ctrl.ControlSystem(
            rules
        )


        self.simulation = ctrl.ControlSystemSimulation(
            system
        )



    # ---------------------------------
    # Destination Cost Mapping
    # ---------------------------------

    def get_destination_cost(
        self,
        city
    ):


        expensive_places = [

            "Mustang",
            "Rara",
            "Everest",
            "Manang",
            "Solukhumbu"

        ]


        cheap_places = [

            "Lumbini",
            "Janakpur",
            "Ilam"

        ]



        if city in expensive_places:

            return 9


        elif city in cheap_places:

            return 3


        else:

            return 5



    # ---------------------------------
    # Evaluate Trip
    # ---------------------------------

    def evaluate(
        self,
        budget,
        days,
        city
    ):


        cost = self.get_destination_cost(
            city
        )


        self.simulation.input["budget"] = budget

        self.simulation.input["days"] = days

        self.simulation.input["destination_cost"] = cost



        self.simulation.compute()



        score = self.simulation.output[
            "trip_quality"
        ]


        return round(
            score,
            2
        )