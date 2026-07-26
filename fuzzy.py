import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyTravelPlanner:

    def __init__(self):

        # =====================================
        # INPUT VARIABLES
        # =====================================

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

        # =====================================
        # OUTPUT
        # =====================================

        self.trip_quality = ctrl.Consequent(
            np.arange(0, 101, 1),
            "trip_quality"
        )

        # =====================================
        # Budget Membership
        # =====================================

        self.budget["low"] = fuzz.trapmf(
            self.budget.universe,
            [0, 0, 20000, 35000]
        )

        self.budget["medium"] = fuzz.trimf(
            self.budget.universe,
            [25000, 50000, 75000]
        )

        self.budget["high"] = fuzz.trapmf(
            self.budget.universe,
            [65000, 80000, 100000, 100000]
        )

        # =====================================
        # Days Membership
        # =====================================

        self.days["short"] = fuzz.trapmf(
            self.days.universe,
            [1, 1, 2, 4]
        )

        self.days["medium"] = fuzz.trimf(
            self.days.universe,
            [3, 6, 9]
        )

        self.days["long"] = fuzz.trapmf(
            self.days.universe,
            [8, 10, 14, 14]
        )

        # =====================================
        # Destination Cost
        # =====================================

        self.destination_cost["cheap"] = fuzz.trapmf(
            self.destination_cost.universe,
            [0, 0, 2, 4]
        )

        self.destination_cost["average"] = fuzz.trimf(
            self.destination_cost.universe,
            [3, 5, 7]
        )

        self.destination_cost["expensive"] = fuzz.trapmf(
            self.destination_cost.universe,
            [6, 8, 10, 10]
        )

        # =====================================
        # OUTPUT MEMBERSHIP
        # =====================================

        self.trip_quality["poor"] = fuzz.trapmf(
            self.trip_quality.universe,
            [0, 0, 20, 40]
        )

        self.trip_quality["average"] = fuzz.trimf(
            self.trip_quality.universe,
            [30, 50, 70]
        )

        self.trip_quality["good"] = fuzz.trimf(
            self.trip_quality.universe,
            [60, 75, 90]
        )

        self.trip_quality["excellent"] = fuzz.trapmf(
            self.trip_quality.universe,
            [85, 92, 100, 100]
        )

        # =====================================
        # RULES
        # =====================================

        rules = [

            # Low budget
            ctrl.Rule(
                self.budget["low"] &
                self.destination_cost["expensive"],
                self.trip_quality["poor"]
            ),

            ctrl.Rule(
                self.budget["low"] &
                self.destination_cost["average"],
                self.trip_quality["average"]
            ),

            ctrl.Rule(
                self.budget["low"] &
                self.destination_cost["cheap"],
                self.trip_quality["good"]
            ),

            # Medium budget
            ctrl.Rule(
                self.budget["medium"] &
                self.destination_cost["cheap"],
                self.trip_quality["excellent"]
            ),

            ctrl.Rule(
                self.budget["medium"] &
                self.destination_cost["average"],
                self.trip_quality["good"]
            ),

            ctrl.Rule(
                self.budget["medium"] &
                self.destination_cost["expensive"],
                self.trip_quality["average"]
            ),

            # High budget
            ctrl.Rule(
                self.budget["high"] &
                self.destination_cost["cheap"],
                self.trip_quality["excellent"]
            ),

            ctrl.Rule(
                self.budget["high"] &
                self.destination_cost["average"],
                self.trip_quality["excellent"]
            ),

            ctrl.Rule(
                self.budget["high"] &
                self.destination_cost["expensive"],
                self.trip_quality["good"]
            ),

            # Days
            ctrl.Rule(
                self.days["short"] &
                self.budget["low"],
                self.trip_quality["average"]
            ),

            ctrl.Rule(
                self.days["short"] &
                self.budget["high"],
                self.trip_quality["good"]
            ),

            ctrl.Rule(
                self.days["medium"] &
                self.budget["medium"],
                self.trip_quality["excellent"]
            ),

            ctrl.Rule(
                self.days["long"] &
                self.budget["high"],
                self.trip_quality["excellent"]
            ),

            ctrl.Rule(
                self.days["long"] &
                self.budget["low"],
                self.trip_quality["poor"]
            ),

        ]

        system = ctrl.ControlSystem(rules)

        self.simulation = ctrl.ControlSystemSimulation(system)

    # =====================================
    # Destination Cost Mapping
    # =====================================

    def get_destination_cost(self, city):

        cost_map = {

            "Kathmandu": 6,
            "Pokhara": 5,
            "Bhaktapur": 5,
            "Lalitpur": 5,
            "Nagarkot": 6,
            "Bandipur": 5,
            "Lumbini": 4,
            "Janakpur": 3,
            "Ilam": 3,
            "Bharatpur": 5,
            "Mustang": 9,
            "Manang": 9,
            "Mugu": 9,
            "Khaptad": 8,
            "Lukla": 10,
            "Rasuwa": 8,
            "Gorkha": 6,
            "Tansen": 4,
            "Dhulikhel": 4,
            "Bardiya": 6

        }

        return cost_map.get(city, 5)

    # =====================================
    # Evaluate
    # =====================================

    def evaluate(self, budget, days, city):

        self.simulation.reset()

        self.simulation.input["budget"] = budget
        self.simulation.input["days"] = days
        self.simulation.input["destination_cost"] = self.get_destination_cost(city)

        self.simulation.compute()

        return round(
            self.simulation.output["trip_quality"],
            2
        )
