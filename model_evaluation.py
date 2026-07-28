"""
Model Evaluation — Smart Travel Planner
==========================================

None of the three "models" in this project (the TF-IDF recommendation
engine, the fuzzy trip-quality evaluator, and the A* route optimizer)
are trained on labeled data in the usual supervised-learning sense, so
there's no pre-existing ground truth to score them against. This script
builds a reasonable ground truth for each piece so it can still be
evaluated with standard classification/regression metrics:

1. RECOMMENDATION ENGINE (attraction interest-matching) — evaluated as
   a BINARY CLASSIFIER:
       predicted = 1  if the attraction is returned in the top-K
                       recommendations for a given (city, interest) query
       actual    = 1  if the attraction's true category matches the
                       queried interest
   -> confusion matrix, accuracy, precision, recall, F1 (via sklearn).

2. FUZZY TRIP-QUALITY EVALUATOR — evaluated as a REGRESSOR against an
   independent reference formula (not the same logic as the fuzzy
   engine, so it's a genuine external benchmark, not circular):
       reference_score = weighted combination of budget/day/destination
                          -cost/interest-fit "goodness", scaled 0-100
   -> MAE, MSE, RMSE, R^2 (via sklearn) over many sampled trips.

3. HOTEL & RESTAURANT RECOMMENDERS — evaluated as REGRESSORS: their
   composite_score (which blends budget fit + rating) is compared
   against normalized rating alone, used as a simple "true quality"
   proxy, across a range of budget levels.
   -> MAE, MSE, RMSE, R^2 for each.

Outputs:
    - Printed metrics report to the console
    - evaluation_report.txt with the same report
    - confusion_matrix.png (recommendation engine)
    - regression_scatter_fuzzy.png / _hotels.png / _restaurants.png
    All written to ./outputs/
"""

import os
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from recommendation import RecommendationEngine, _normalize
from fuzzy import FuzzyTravelPlanner

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def load_data():
    attractions = pd.read_csv(f"{DATA_DIR}/attractions.csv")
    hotels = pd.read_csv(f"{DATA_DIR}/hotels.csv")
    restaurants = pd.read_csv(f"{DATA_DIR}/restaurants.csv")
    return attractions, hotels, restaurants


# ==========================================================================
# 1. Recommendation Engine — classification metrics
# ==========================================================================

def evaluate_recommendation_classifier(engine: RecommendationEngine, attractions: pd.DataFrame, top_k=5):
    """
    For every city and every category present in that city, query the
    recommender with that single category as the "interest" and check
    whether it retrieves the attractions that actually belong to that
    category in its top-K results.

    predicted label per (city, category, attraction):
        1 if attraction appears in the top-K recommendations
    actual label:
        1 if attraction["category"] == queried category
    """

    y_true, y_pred = [], []

    cities = attractions["city"].unique()

    for city in cities:
        city_attractions = attractions[attractions["city"] == city]
        categories = city_attractions["category"].unique()

        for category in categories:
            recs = engine.recommend_attractions(city, [category], max_results=top_k)
            recommended_names = set(recs["name"]) if not recs.empty else set()

            for _, row in city_attractions.iterrows():
                y_true.append(1 if row["category"] == category else 0)
                y_pred.append(1 if row["name"] in recommended_names else 0)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    cm = confusion_matrix(y_true, y_pred)
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "n_samples": len(y_true),
        "n_positive": int(y_true.sum()),
    }
    return cm, metrics


def plot_confusion_matrix(cm, path, title="Recommendation Engine — Confusion Matrix"):
    plt.figure(figsize=(5.5, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", cbar=False,
        xticklabels=["Not Recommended", "Recommended"],
        yticklabels=["Not Relevant", "Relevant"],
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ==========================================================================
# 2. Fuzzy Trip-Quality Evaluator — regression metrics
# ==========================================================================

def reference_trip_score(budget, days, destination_cost, interest_fit):
    """
    Independent reference formula for "how good should this trip score
    be", used purely as an external benchmark for the fuzzy engine — it
    does NOT reuse the fuzzy engine's own rules/logic.
    """
    budget_score = np.clip(budget / 80000, 0, 1)          # richer budget -> better, saturates
    days_score = 1 - abs(days - 7) / 13                    # ~7 days considered ideal, tapers off
    days_score = np.clip(days_score, 0, 1)
    cost_score = 1 - (destination_cost / 10)                # cheaper destination -> better
    fit_score = interest_fit / 10                           # stronger interest match -> better

    composite = (
        0.35 * budget_score
        + 0.20 * days_score
        + 0.20 * cost_score
        + 0.25 * fit_score
    )
    return float(np.clip(composite * 100, 0, 100))


def evaluate_fuzzy_regressor(fuzzy_engine: FuzzyTravelPlanner, n_samples=300):
    cities = list(fuzzy_engine.DESTINATION_COST_MAP.keys())

    y_true, y_pred = [], []

    for _ in range(n_samples):
        budget = random.uniform(3000, 100000)
        days = random.uniform(1, 14)
        city = random.choice(cities)
        interest_fit = random.uniform(0, 10)

        destination_cost = fuzzy_engine.get_destination_cost(city)

        predicted = fuzzy_engine.evaluate(
            budget=budget, days=days, city=city, interest_fit=interest_fit
        )["score"]
        reference = reference_trip_score(budget, days, destination_cost, interest_fit)

        y_pred.append(predicted)
        y_true.append(reference)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    return {"mae": mae, "mse": mse, "rmse": rmse, "r2": r2, "n_samples": n_samples}, y_true, y_pred


# ==========================================================================
# 3. Hotel / Restaurant recommenders — regression metrics
# ==========================================================================

def evaluate_scored_recommender(df, score_col_builder, budget_col_name, budget_range, n_trials=200):
    """
    Generic helper: repeatedly score the full dataframe at a random
    budget level, compare the resulting composite_score against
    normalized rating (the "true quality" proxy), and pool the results.
    """
    y_true, y_pred = [], []

    for _ in range(n_trials):
        budget = random.uniform(*budget_range)
        scored = score_col_builder(df.copy(), budget)
        y_pred.extend(scored["composite_score"].tolist())
        y_true.extend(_normalize(scored["rating"]).tolist())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    return {"mae": mae, "mse": mse, "rmse": rmse, "r2": r2, "n_samples": len(y_true)}, y_true, y_pred


def _score_hotels(df, budget):
    from recommendation import _budget_fit
    df["budget_fit"] = _budget_fit(df["price_per_night"], budget)
    df["composite_score"] = 0.55 * df["budget_fit"] + 0.45 * _normalize(df["rating"])
    return df


def _score_restaurants(df, budget):
    from recommendation import _budget_fit
    df["budget_fit"] = _budget_fit(df["average_cost"], budget)
    df["composite_score"] = 0.55 * df["budget_fit"] + 0.45 * _normalize(df["rating"])
    return df


# ==========================================================================
# Plotting helpers
# ==========================================================================

def plot_regression_scatter(y_true, y_pred, path, title, xlabel="Reference / true value", ylabel="Predicted value"):
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, alpha=0.4, s=20, color="#2563eb", edgecolor="white")
    lo = min(np.min(y_true), np.min(y_pred))
    hi = max(np.max(y_true), np.max(y_pred))
    plt.plot([lo, hi], [lo, hi], color="black", linestyle="--", linewidth=1, label="Perfect prediction")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ==========================================================================
# Main
# ==========================================================================

def main():
    attractions, hotels, restaurants = load_data()
    engine = RecommendationEngine(attractions, hotels, restaurants)
    fuzzy_engine = FuzzyTravelPlanner()

    report_lines = []

    def log(line=""):
        print(line)
        report_lines.append(line)

    log("=" * 70)
    log("MODEL EVALUATION REPORT — Smart Travel Planner")
    log("=" * 70)

    # ---------------- 1. Recommendation engine (classification) ----------------
    log("\n[1] Recommendation Engine — classification metrics")
    log("    (predicted = attraction recommended in top-5 for a category query,")
    log("     actual = attraction's true category matches the query)")

    cm, cls_metrics = evaluate_recommendation_classifier(engine, attractions, top_k=5)
    log(f"    Confusion matrix [[TN FP] [FN TP]]:\n{cm}")
    log(f"    Accuracy : {cls_metrics['accuracy']:.4f}")
    log(f"    Precision: {cls_metrics['precision']:.4f}")
    log(f"    Recall   : {cls_metrics['recall']:.4f}")
    log(f"    F1 score : {cls_metrics['f1']:.4f}")
    log(f"    Samples  : {cls_metrics['n_samples']} (positives: {cls_metrics['n_positive']})")

    plot_confusion_matrix(cm, f"{OUT_DIR}/confusion_matrix_recommender.png")

    # ---------------- 2. Fuzzy trip-quality evaluator (regression) ----------------
    log("\n[2] Fuzzy Trip-Quality Evaluator — regression metrics")
    log("    (predicted = fuzzy engine score, reference = independent weighted-formula benchmark)")

    fuzzy_metrics, y_true_fuzzy, y_pred_fuzzy = evaluate_fuzzy_regressor(fuzzy_engine, n_samples=300)
    log(f"    MAE : {fuzzy_metrics['mae']:.3f}")
    log(f"    MSE : {fuzzy_metrics['mse']:.3f}")
    log(f"    RMSE: {fuzzy_metrics['rmse']:.3f}")
    log(f"    R^2 : {fuzzy_metrics['r2']:.4f}")
    log(f"    Samples: {fuzzy_metrics['n_samples']}")

    plot_regression_scatter(
        y_true_fuzzy, y_pred_fuzzy,
        f"{OUT_DIR}/regression_scatter_fuzzy.png",
        "Fuzzy Engine vs. Reference Trip-Quality Score",
        xlabel="Reference score (0-100)", ylabel="Fuzzy engine score (0-100)",
    )

    # ---------------- 3. Hotel recommender (regression) ----------------
    log("\n[3] Hotel Recommender — regression metrics")
    log("    (predicted = composite_score, true = normalized rating)")

    hotel_metrics, y_true_h, y_pred_h = evaluate_scored_recommender(
        hotels, _score_hotels, "price_per_night", (2500, 16000), n_trials=200
    )
    log(f"    MAE : {hotel_metrics['mae']:.4f}")
    log(f"    MSE : {hotel_metrics['mse']:.4f}")
    log(f"    RMSE: {hotel_metrics['rmse']:.4f}")
    log(f"    R^2 : {hotel_metrics['r2']:.4f}")
    log(f"    Samples: {hotel_metrics['n_samples']}")

    plot_regression_scatter(
        y_true_h, y_pred_h,
        f"{OUT_DIR}/regression_scatter_hotels.png",
        "Hotel Composite Score vs. Normalized Rating",
        xlabel="Normalized rating (0-1)", ylabel="Composite score (0-1)",
    )

    # ---------------- 4. Restaurant recommender (regression) ----------------
    log("\n[4] Restaurant Recommender — regression metrics")
    log("    (predicted = composite_score, true = normalized rating)")

    rest_metrics, y_true_r, y_pred_r = evaluate_scored_recommender(
        restaurants, _score_restaurants, "average_cost", (400, 4000), n_trials=200
    )
    log(f"    MAE : {rest_metrics['mae']:.4f}")
    log(f"    MSE : {rest_metrics['mse']:.4f}")
    log(f"    RMSE: {rest_metrics['rmse']:.4f}")
    log(f"    R^2 : {rest_metrics['r2']:.4f}")
    log(f"    Samples: {rest_metrics['n_samples']}")

    plot_regression_scatter(
        y_true_r, y_pred_r,
        f"{OUT_DIR}/regression_scatter_restaurants.png",
        "Restaurant Composite Score vs. Normalized Rating",
        xlabel="Normalized rating (0-1)", ylabel="Composite score (0-1)",
    )

    log("\n" + "=" * 70)
    log(f"Charts written to {OUT_DIR}/")
    log("=" * 70)

    with open(f"{OUT_DIR}/evaluation_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


if __name__ == "__main__":
    main()