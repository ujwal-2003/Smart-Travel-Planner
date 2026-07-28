"""
Data Visualization — Smart Travel Planner Dataset
====================================================


Outputs (written to ./outputs/):
    dv_attractions_per_city.png            [needs attractions.csv]
    dv_category_distribution.png           [needs attractions.csv]
    dv_rating_distributions.png            [needs any of the 3]
    dv_cost_vs_rating.png                  [needs attractions.csv]
    dv_hotel_price_by_star.png             [needs hotels.csv]
    dv_restaurant_cuisine_distribution.png [needs restaurants.csv]
    dv_geographic_scatter.png              [needs attractions.csv]
    dv_correlation_heatmaps.png            [needs any of the 3]
    dv_hotel_geographic_scatter.png        [needs hotels.csv]
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Resolve data/ and outputs/ relative to THIS SCRIPT's location, not the
# current working directory — so it works the same whether you run it from
# the project root or from inside evaluation/.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")


def load_optional(name):
    path = f"{DATA_DIR}/{name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    print(f"  [skip] {name}.csv not found in {DATA_DIR}/ — related plots skipped")
    return None


# ------------------------------------------------------------
# 1. Attractions per city
# ------------------------------------------------------------

def plot_attractions_per_city(attractions, path):
    counts = attractions["city"].value_counts().sort_values(ascending=True)
    plt.figure(figsize=(8, 8))
    counts.plot(kind="barh", color="#2563eb")
    plt.xlabel("Number of attractions")
    plt.title("Attractions per City")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 2. Category distribution (overall)
# ------------------------------------------------------------

def plot_category_distribution(attractions, path):
    counts = attractions["category"].value_counts()
    plt.figure(figsize=(7, 6))
    colors = sns.color_palette("Set2", len(counts))
    plt.pie(
        counts.values, labels=counts.index, autopct="%1.0f%%",
        colors=colors, startangle=90, pctdistance=0.8,
    )
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    plt.gca().add_artist(centre_circle)
    plt.title("Attraction Category Mix (all cities)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 3. Rating distributions across available datasets
# ------------------------------------------------------------

def plot_rating_distributions(datasets, path):
    """datasets: list of (label, series, color) tuples for whichever
    dataframes were successfully loaded."""
    n = len(datasets)
    fig, axes = plt.subplots(1, n, figsize=(4.5 * n, 4.5), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, (label, values, color) in zip(axes, datasets):
        ax.hist(values, bins=12, color=color, edgecolor="white")
        ax.set_title(label)
        ax.set_xlabel("Rating")
        ax.axvline(values.mean(), color="black", linestyle="--", linewidth=1,
                   label=f"mean={values.mean():.2f}")
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Count")
    plt.suptitle("Rating Distributions")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 4. Cost vs rating (attractions), by category
# ------------------------------------------------------------

def plot_cost_vs_rating(attractions, path):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=attractions, x="cost", y="rating", hue="category",
        size="duration_hours", sizes=(30, 200), alpha=0.75, palette="tab10",
    )
    plt.xlabel("Entry Cost (NPR)")
    plt.ylabel("Rating")
    plt.title("Attraction Cost vs. Rating\n(bubble size = visit duration)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 5. Hotel price by star rating
# ------------------------------------------------------------

def plot_hotel_price_by_star(hotels, path):
    plt.figure(figsize=(7, 5))
    order = sorted(hotels["star"].unique())
    sns.boxplot(data=hotels, x="star", y="price_per_night", order=order,
                hue="star", palette="Blues", legend=False)
    sns.stripplot(data=hotels, x="star", y="price_per_night", order=order,
                  color="black", size=3, alpha=0.4)
    plt.xlabel("Star Rating")
    plt.ylabel("Price per Night (NPR)")
    plt.title("Hotel Price Distribution by Star Rating")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 6. Restaurant cuisine distribution (top cuisines)
# ------------------------------------------------------------

def plot_restaurant_cuisine_distribution(restaurants, path, top_n=10):
    counts = restaurants["cuisine"].value_counts().head(top_n).sort_values()
    plt.figure(figsize=(8, 6))
    counts.plot(kind="barh", color="#dc2626")
    plt.xlabel("Number of restaurants")
    plt.title(f"Top {top_n} Cuisines")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 7. Geographic scatter of attractions (lat/lon, colored by category)
# ------------------------------------------------------------

def plot_geographic_scatter(attractions, path):
    plt.figure(figsize=(7, 8))
    categories = attractions["category"].unique()
    palette = sns.color_palette("tab10", len(categories))
    color_map = dict(zip(categories, palette))

    for cat in categories:
        subset = attractions[attractions["category"] == cat]
        plt.scatter(
            subset["longitude"], subset["latitude"],
            label=cat, color=color_map[cat], s=40, alpha=0.8, edgecolor="white",
        )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographic Spread of Attractions\n(colored by category)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 7b. Geographic scatter of hotels (lat/lon, colored by city)
# ------------------------------------------------------------

def plot_hotel_geographic_scatter(hotels, path):
    plt.figure(figsize=(7, 8))
    cities = hotels["city"].unique()
    palette = sns.color_palette("tab20", len(cities))
    color_map = dict(zip(cities, palette))

    for city in cities:
        subset = hotels[hotels["city"] == city]
        plt.scatter(
            subset["longitude"], subset["latitude"],
            label=city, color=color_map[city], s=45, alpha=0.85, edgecolor="white",
        )
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographic Spread of Hotels\n(colored by city)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7, ncol=1)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
# 8. Correlation heatmaps (numeric columns per available dataset)
# ------------------------------------------------------------

def plot_correlation_heatmaps(panels, path):
    """panels: list of (label, df, cols) for whichever datasets loaded."""
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]

    for ax, (label, df, cols) in zip(axes, panels):
        corr = df[cols].corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax, cbar=False)
        ax.set_title(label)

    plt.suptitle("Correlation Between Numeric Fields")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main():
    print("Loading data...")
    attractions = load_optional("attractions")
    hotels = load_optional("hotels")
    restaurants = load_optional("restaurants")

    made = []

    if attractions is not None:
        plot_attractions_per_city(attractions, f"{OUT_DIR}/dv_attractions_per_city.png")
        made.append("dv_attractions_per_city.png")
        plot_category_distribution(attractions, f"{OUT_DIR}/dv_category_distribution.png")
        made.append("dv_category_distribution.png")
        plot_cost_vs_rating(attractions, f"{OUT_DIR}/dv_cost_vs_rating.png")
        made.append("dv_cost_vs_rating.png")
        plot_geographic_scatter(attractions, f"{OUT_DIR}/dv_geographic_scatter.png")
        made.append("dv_geographic_scatter.png")

    if hotels is not None:
        plot_hotel_price_by_star(hotels, f"{OUT_DIR}/dv_hotel_price_by_star.png")
        made.append("dv_hotel_price_by_star.png")
        plot_hotel_geographic_scatter(hotels, f"{OUT_DIR}/dv_hotel_geographic_scatter.png")
        made.append("dv_hotel_geographic_scatter.png")

    if restaurants is not None:
        plot_restaurant_cuisine_distribution(restaurants, f"{OUT_DIR}/dv_restaurant_cuisine_distribution.png")
        made.append("dv_restaurant_cuisine_distribution.png")

    # Rating distributions — combine whichever datasets are available
    rating_datasets = []
    if attractions is not None:
        rating_datasets.append(("Attractions", attractions["rating"], "#2563eb"))
    if hotels is not None:
        rating_datasets.append(("Hotels", hotels["rating"], "#16a34a"))
    if restaurants is not None:
        rating_datasets.append(("Restaurants", restaurants["rating"], "#f97316"))
    if rating_datasets:
        plot_rating_distributions(rating_datasets, f"{OUT_DIR}/dv_rating_distributions.png")
        made.append("dv_rating_distributions.png")

    # Correlation heatmaps — combine whichever datasets are available
    panels = []
    if attractions is not None:
        panels.append(("Attractions", attractions, ["rating", "cost", "duration_hours"]))
    if hotels is not None:
        panels.append(("Hotels", hotels, ["star", "rating", "price_per_night"]))
    if restaurants is not None:
        panels.append(("Restaurants", restaurants, ["rating", "average_cost"]))
    if panels:
        plot_correlation_heatmaps(panels, f"{OUT_DIR}/dv_correlation_heatmaps.png")
        made.append("dv_correlation_heatmaps.png")

    print(f"\nGenerated {len(made)} visualization(s) in ./{OUT_DIR}/:")
    for f in made:
        print(f"  - {f}")


if __name__ == "__main__":
    main()