# pip install scikit-fuzzy
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyTravelPlanner:

    def __init__(self):

        # -------------------------
        # INPUT VARIABLES
        # -------------------------

        self.budget = ctrl.Antecedent(np.arange(0, 50001, 1000), 'budget')

        self.days = ctrl.Antecedent(np.arange(1, 11, 1), 'days')

        # -------------------------
        # OUTPUT VARIABLE
        # -------------------------

        self.trip_quality = ctrl.Consequent(
            np.arange(0, 101, 1),
            'trip_quality'
        )

        # -------------------------
        # MEMBERSHIP FUNCTIONS
        # -------------------------

        self.budget['low'] = fuzz.trimf(
            self.budget.universe,
            [0, 0, 15000]
        )

        self.budget['medium'] = fuzz.trimf(
            self.budget.universe,
            [10000, 25000, 40000]
        )

        self.budget['high'] = fuzz.trimf(
            self.budget.universe,
            [30000, 50000, 50000]
        )

        self.days['short'] = fuzz.trimf(
            self.days.universe,
            [1, 1, 3]
        )

        self.days['medium'] = fuzz.trimf(
            self.days.universe,
            [2, 5, 7]
        )

        self.days['long'] = fuzz.trimf(
            self.days.universe,
            [6, 10, 10]
        )

        self.trip_quality['poor'] = fuzz.trimf(
            self.trip_quality.universe,
            [0, 0, 40]
        )

        self.trip_quality['average'] = fuzz.trimf(
            self.trip_quality.universe,
            [30, 50, 70]
        )

        self.trip_quality['excellent'] = fuzz.trimf(
            self.trip_quality.universe,
            [60, 100, 100]
        )

        # -------------------------
        # RULES
        # -------------------------

        rules = [

            ctrl.Rule(
                self.budget['low'] &
                self.days['long'],
                self.trip_quality['poor']
            ),

            ctrl.Rule(
                self.budget['low'] &
                self.days['short'],
                self.trip_quality['average']
            ),

            ctrl.Rule(
                self.budget['medium'] &
                self.days['medium'],
                self.trip_quality['average']
            ),

            ctrl.Rule(
                self.budget['high'] &
                self.days['short'],
                self.trip_quality['excellent']
            ),

            ctrl.Rule(
                self.budget['high'] &
                self.days['long'],
                self.trip_quality['excellent']
            ),

            ctrl.Rule(
                self.budget['medium'] &
                self.days['long'],
                self.trip_quality['average']
            ),

        ]

        system = ctrl.ControlSystem(rules)

        self.simulation = ctrl.ControlSystemSimulation(system)

    # -----------------------------------

    def evaluate(self, budget, days):

        self.simulation.input['budget'] = budget
        self.simulation.input['days'] = days

        self.simulation.compute()

        score = self.simulation.output['trip_quality']

        return round(score, 2)