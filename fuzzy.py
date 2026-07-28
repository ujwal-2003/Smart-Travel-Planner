"""
Fuzzy Trip Evaluation Engine
=============================

A self-contained Mamdani-style fuzzy inference engine used to score how
well a proposed trip (budget, duration, destination cost level, and how
well the chosen attractions match the traveller's interests) is likely
to work out.

This version has no external fuzzy-logic dependency (no `scikit-fuzzy`
requirement) — membership functions, rule aggregation and centroid
defuzzification are implemented directly with NumPy. This makes the
module easier to install/deploy and easier to unit test, while
producing the same style of trapezoidal/triangular Mamdani output as
before.

New in this version:
    * A fourth input, `interest_fit`, which captures how well the
      recommended attractions actually match the traveller's stated
      interests (0-10). Previously the score only looked at money and
      time, so two trips with identical budgets could get identical
      scores even if one was full of attractions the traveller didn't
      care about.
    * `evaluate()` now returns a small breakdown dict (not just a
      number) so the UI can explain *why* a trip scored the way it did.
    * Defensive clamping of every input so the simulation never raises
      on out-of-range values coming from the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np


# ==========================================================================
# Membership function helpers
# ==========================================================================

def trapmf(x: np.ndarray, points: tuple[float, float, float, float]) -> np.ndarray:
    a, b, c, d = points
    y = np.zeros_like(x, dtype=float)

    if b > a:
        rising = (x >= a) & (x < b)
        y[rising] = (x[rising] - a) / (b - a)
    if c >= b:
        flat = (x >= b) & (x <= c)
        y[flat] = 1.0
    if d > c:
        falling = (x > c) & (x <= d)
        y[falling] = (d - x[falling]) / (d - c)

    return np.clip(y, 0, 1)


def trimf(x: np.ndarray, points: tuple[float, float, float]) -> np.ndarray:
    a, b, c = points
    return trapmf(x, (a, b, b, c))


@dataclass
class FuzzyVariable:
    """A named universe of discourse with one or more membership sets."""

    name: str
    universe: np.ndarray
    sets: Dict[str, np.ndarray] = field(default_factory=dict)

    def add_trap(self, label: str, points: tuple[float, float, float, float]) -> None:
        self.sets[label] = trapmf(self.universe, points)

    def add_tri(self, label: str, points: tuple[float, float, float]) -> None:
        self.sets[label] = trimf(self.universe, points)

    def membership(self, label: str, value: float) -> float:
        value = float(np.clip(value, self.universe.min(), self.universe.max()))
        return float(np.interp(value, self.universe, self.sets[label]))


# ==========================================================================
# Fuzzy Travel Planner
# ==========================================================================

class FuzzyTravelPlanner:
    """Evaluates overall trip quality (0-100) from budget/time/fit signals."""

    def __init__(self) -> None:

        # ---------------------------------------------------------
        # INPUT VARIABLES
        # ---------------------------------------------------------

        self.budget = FuzzyVariable("budget", np.arange(0, 100001, 500))
        self.budget.add_trap("low", (0, 0, 20000, 35000))
        self.budget.add_tri("medium", (25000, 50000, 75000))
        self.budget.add_trap("high", (65000, 80000, 100000, 100000))

        self.days = FuzzyVariable("days", np.arange(1, 14.01, 0.1))
        self.days.add_trap("short", (1, 1, 2, 4))
        self.days.add_tri("medium", (3, 6, 9))
        self.days.add_trap("long", (8, 10, 14, 14))

        self.destination_cost = FuzzyVariable("destination_cost", np.arange(0, 10.01, 0.1))
        self.destination_cost.add_trap("cheap", (0, 0, 2, 4))
        self.destination_cost.add_tri("average", (3, 5, 7))
        self.destination_cost.add_trap("expensive", (6, 8, 10, 10))

        # How well the recommended attractions match stated interests.
        self.interest_fit = FuzzyVariable("interest_fit", np.arange(0, 10.01, 0.1))
        self.interest_fit.add_trap("weak", (0, 0, 2, 4))
        self.interest_fit.add_tri("moderate", (3, 5, 7))
        self.interest_fit.add_trap("strong", (6, 8, 10, 10))

        # ---------------------------------------------------------
        # OUTPUT VARIABLE
        # ---------------------------------------------------------

        self.trip_quality = FuzzyVariable("trip_quality", np.arange(0, 100.01, 0.5))
        self.trip_quality.add_trap("poor", (0, 0, 20, 40))
        self.trip_quality.add_tri("average", (30, 50, 70))
        self.trip_quality.add_tri("good", (60, 75, 90))
        self.trip_quality.add_trap("excellent", (85, 92, 100, 100))

        # ---------------------------------------------------------
        # RULE BASE  (antecedent memberships, consequent label, weight)
        # ---------------------------------------------------------
        # Each rule is (list of (variable, label) pairs ANDed together,
        # output label). AND == min() of memberships, matching the
        # semantics of the original scikit-fuzzy rule set.

        self.rules: list[tuple[list[tuple[str, str]], str]] = [
            # --- Budget vs destination cost -------------------------------
            ([("budget", "low"), ("destination_cost", "expensive")], "poor"),
            ([("budget", "low"), ("destination_cost", "average")], "average"),
            ([("budget", "low"), ("destination_cost", "cheap")], "good"),

            ([("budget", "medium"), ("destination_cost", "cheap")], "excellent"),
            ([("budget", "medium"), ("destination_cost", "average")], "good"),
            ([("budget", "medium"), ("destination_cost", "expensive")], "average"),

            ([("budget", "high"), ("destination_cost", "cheap")], "excellent"),
            ([("budget", "high"), ("destination_cost", "average")], "excellent"),
            ([("budget", "high"), ("destination_cost", "expensive")], "good"),

            # --- Days vs budget ---------------------------------------------
            ([("days", "short"), ("budget", "low")], "average"),
            ([("days", "short"), ("budget", "high")], "good"),
            ([("days", "medium"), ("budget", "medium")], "excellent"),
            ([("days", "long"), ("budget", "high")], "excellent"),
            ([("days", "long"), ("budget", "low")], "poor"),

            # --- Interest fit (new) ------------------------------------------
            ([("interest_fit", "strong"), ("budget", "medium")], "excellent"),
            ([("interest_fit", "strong"), ("budget", "high")], "excellent"),
            ([("interest_fit", "strong"), ("budget", "low")], "good"),
            ([("interest_fit", "moderate")], "good"),
            ([("interest_fit", "weak")], "average"),
            ([("interest_fit", "weak"), ("budget", "low")], "poor"),
        ]

        self._vars = {
            "budget": self.budget,
            "days": self.days,
            "destination_cost": self.destination_cost,
            "interest_fit": self.interest_fit,
        }

    # ---------------------------------------------------------------
    # Destination cost mapping
    # ---------------------------------------------------------------

    DESTINATION_COST_MAP = {
        "Kathmandu": 6, "Pokhara": 5, "Bhaktapur": 5, "Lalitpur": 5,
        "Nagarkot": 6, "Bandipur": 5, "Lumbini": 4, "Janakpur": 3,
        "Ilam": 3, "Bharatpur": 5, "Mustang": 9, "Manang": 9, "Mugu": 9,
        "Khaptad": 8, "Lukla": 10, "Rasuwa": 8, "Gorkha": 6, "Tansen": 4,
        "Dhulikhel": 4, "Bardiya": 6, "Solukhumbu": 9, "Taplejung": 7,
    }

    def get_destination_cost(self, city: str) -> int:
        return self.DESTINATION_COST_MAP.get(str(city).strip(), 5)

    # ---------------------------------------------------------------
    # Inference
    # ---------------------------------------------------------------

    def _fuzzify_inputs(self, values: Dict[str, float]) -> Dict[tuple[str, str], float]:
        memberships: Dict[tuple[str, str], float] = {}
        for var_name, variable in self._vars.items():
            value = values[var_name]
            for label in variable.sets:
                memberships[(var_name, label)] = variable.membership(label, value)
        return memberships

    def evaluate(
        self,
        budget: float,
        days: float,
        city: str,
        interest_fit: float = 5.0,
    ) -> dict:
        """
        Run the fuzzy inference and return a breakdown, not just a score.

        interest_fit: 0-10 score for how well recommended attractions match
        the traveller's interests (see RecommendationEngine.interest_fit_score).
        """

        destination_cost = self.get_destination_cost(city)

        values = {
            "budget": budget,
            "days": days,
            "destination_cost": destination_cost,
            "interest_fit": interest_fit,
        }

        memberships = self._fuzzify_inputs(values)

        universe = self.trip_quality.universe
        aggregated = np.zeros_like(universe, dtype=float)

        fired_rules = []

        for antecedents, consequent_label in self.rules:
            strength = min(
                memberships[(var, label)] for var, label in antecedents
            )
            if strength <= 0:
                continue

            fired_rules.append((antecedents, consequent_label, round(strength, 3)))

            clipped = np.minimum(self.trip_quality.sets[consequent_label], strength)
            aggregated = np.maximum(aggregated, clipped)

        if aggregated.sum() > 0:
            score = float(np.sum(universe * aggregated) / np.sum(aggregated))
        else:
            # No rule fired (shouldn't normally happen) — fall back to a
            # neutral midpoint rather than raising.
            score = 50.0

        score = round(max(0.0, min(100.0, score)), 2)

        return {
            "score": score,
            "label": self._score_label(score),
            "destination_cost": destination_cost,
            "interest_fit": round(interest_fit, 2),
            "fired_rules": fired_rules,
        }

    @staticmethod
    def _score_label(score: float) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 60:
            return "Good"
        if score >= 30:
            return "Average"
        return "Poor"