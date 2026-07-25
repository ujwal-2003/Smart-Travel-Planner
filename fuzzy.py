import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyTravelPlanner:


    def __init__(self):

        # --------------------------------
        # INPUT VARIABLES
        # --------------------------------

        self.budget = ctrl.Antecedent(
            np.arange(0, 60001, 1000),
            "budget"
        )


        self.days = ctrl.Antecedent(
            np.arange(1, 15, 1),
            "days"
        )


        # --------------------------------
        # OUTPUT VARIABLE
        # --------------------------------

        self.trip_quality = ctrl.Consequent(
            np.arange(0, 101, 1),
            "trip_quality"
        )


        # --------------------------------
        # Budget Membership Functions
        # --------------------------------

        self.budget["low"] = fuzz.trimf(
            self.budget.universe,
            [0, 0, 20000]
        )


        self.budget["medium"] = fuzz.trimf(
            self.budget.universe,
            [15000, 30000, 45000]
        )


        self.budget["high"] = fuzz.trimf(
            self.budget.universe,
            [40000, 60000, 60000]
        )



        # --------------------------------
        # Duration Membership Functions
        # --------------------------------

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



        # --------------------------------
        # Output Membership Functions
        # --------------------------------

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



        # --------------------------------
        # FUZZY RULES
        # --------------------------------

        rules = [


            # Low budget cases

            ctrl.Rule(
                self.budget["low"]
                &
                self.days["short"],
                self.trip_quality["average"]
            ),


            ctrl.Rule(
                self.budget["low"]
                &
                self.days["medium"],
                self.trip_quality["poor"]
            ),


            ctrl.Rule(
                self.budget["low"]
                &
                self.days["long"],
                self.trip_quality["poor"]
            ),



            # Medium budget cases

            ctrl.Rule(
                self.budget["medium"]
                &
                self.days["short"],
                self.trip_quality["good"]
            ),


            ctrl.Rule(
                self.budget["medium"]
                &
                self.days["medium"],
                self.trip_quality["good"]
            ),


            ctrl.Rule(
                self.budget["medium"]
                &
                self.days["long"],
                self.trip_quality["average"]
            ),



            # High budget cases

            ctrl.Rule(
                self.budget["high"]
                &
                self.days["short"],
                self.trip_quality["excellent"]
            ),


            ctrl.Rule(
                self.budget["high"]
                &
                self.days["medium"],
                self.trip_quality["excellent"]
            ),


            ctrl.Rule(
                self.budget["high"]
                &
                self.days["long"],
                self.trip_quality["good"]
            ),

        ]



        # Create fuzzy system

        system = ctrl.ControlSystem(
            rules
        )


        self.simulation = ctrl.ControlSystemSimulation(
            system
        )



    # --------------------------------
    # Evaluate Trip Quality
    # --------------------------------

    def evaluate(
        self,
        budget,
        days
    ):

        self.simulation.input["budget"] = budget

        self.simulation.input["days"] = days


        self.simulation.compute()


        score = self.simulation.output[
            "trip_quality"
        ]


        return round(
            score,
            2
        )