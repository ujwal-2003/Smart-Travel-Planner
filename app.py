from fuzzy import FuzzyTravelPlanner

planner = FuzzyTravelPlanner()

budget = 12000
days = 5

score = planner.evaluate(budget, days)

print("=" * 40)
print("FUZZY TRAVEL SCORE")
print("=" * 40)
print(f"Budget : NPR {budget}")
print(f"Days   : {days}")
print(f"Score  : {score:.2f}/100")