"""
Data Cleaning — Smart Travel Planner Dataset
==============================================

"""

import os
import pandas as pd
import numpy as np

# Resolve data/ relative to THIS SCRIPT's location, not the current working
# directory — so it works the same whether you run it from the project root
# or from inside evaluation/.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# The project-level data/ folder (one level up from this script's folder,
# e.g. evaluaton/) that docs/ and graphs/ read from. Every clean run copies
# the cleaned CSVs here too, so it never goes stale.
PROJECT_DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

# Rough bounding box for Nepal — used only to flag suspicious coordinates,
# not to hard-fail on them.
NEPAL_LAT_RANGE = (26.3, 30.5)
NEPAL_LON_RANGE = (80.0, 88.3)


def _strip_strings(df):
    str_cols = df.columns[df.dtypes == "object"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def _title_case(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = df[col].str.title()
    return df


def _report(label, before, after):
    dropped = before - after
    flag = f" (-{dropped})" if dropped else ""
    print(f"  {label}: {before} -> {after}{flag}")


def clean_generic(df, name, id_col="id", numeric_cols=None,
                   rating_col="rating", lat_col=None, lon_col=None,
                   price_cols=None):
    print(f"\nCleaning {name} ({len(df)} rows)")
    start = len(df)

    df = _strip_strings(df.copy())
    if "city" in df.columns:
        df = _title_case(df, ["city"])
    if "category" in df.columns:
        df = _title_case(df, ["category"])
    if "cuisine" in df.columns:
        df = _title_case(df, ["cuisine"])

    # Drop exact duplicate rows
    n_before = len(df)
    df = df.drop_duplicates()
    _report("exact duplicate rows removed", n_before, len(df))

    # Drop duplicate IDs (keep first)
    if id_col in df.columns:
        n_before = len(df)
        df = df.drop_duplicates(subset=[id_col], keep="first")
        _report("duplicate IDs removed", n_before, len(df))

    # Coerce numeric columns
    if numeric_cols:
        for col in numeric_cols:
            if col in df.columns:
                coerced = pd.to_numeric(df[col], errors="coerce")
                bad = coerced.isna() & df[col].notna()
                if bad.any():
                    print(f"  WARNING: {bad.sum()} non-numeric value(s) in '{col}' set to NaN")
                df[col] = coerced

    # Drop rows with nulls in essential columns
    essential = [c for c in [id_col, "name", "city", rating_col] if c and c in df.columns]
    n_before = len(df)
    df = df.dropna(subset=essential)
    _report(f"rows dropped for missing {essential}", n_before, len(df))

    # Flag (don't drop) out-of-range ratings
    if rating_col in df.columns:
        bad_rating = ~df[rating_col].between(0, 5)
        if bad_rating.any():
            print(f"  WARNING: {bad_rating.sum()} row(s) with rating outside 0-5")

    # Flag negative prices/costs
    if price_cols:
        for col in price_cols:
            if col in df.columns:
                bad_price = df[col] < 0
                if bad_price.any():
                    print(f"  WARNING: {bad_price.sum()} row(s) with negative '{col}'")

    # Flag coordinates outside Nepal's rough bounding box
    if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
        bad_geo = (
            ~df[lat_col].between(*NEPAL_LAT_RANGE)
            | ~df[lon_col].between(*NEPAL_LON_RANGE)
        )
        if bad_geo.any():
            print(f"  WARNING: {bad_geo.sum()} row(s) with lat/lon outside Nepal's bounding box")

    print(f"  Final: {start} -> {len(df)} rows")
    return df.reset_index(drop=True)


def _save_both(df, filename):
    """Write the cleaned CSV to evaluaton/data/ and the project-level data/
    folder, so anything reading from the top-level data/ (docs, graphs)
    always has the latest cleaned version."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROJECT_DATA_DIR, exist_ok=True)
    local_path = os.path.join(DATA_DIR, filename)
    project_path = os.path.join(PROJECT_DATA_DIR, filename)
    df.to_csv(local_path, index=False)
    df.to_csv(project_path, index=False)
    print(f"  -> saved {local_path}")
    print(f"  -> saved {project_path}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Hotels ---
    hotels_path = f"{DATA_DIR}/hotels_raw.csv"
    if os.path.exists(hotels_path):
        hotels = pd.read_csv(hotels_path)
        hotels = clean_generic(
            hotels, "hotels",
            numeric_cols=["star", "rating", "price_per_night", "latitude", "longitude"],
            lat_col="latitude", lon_col="longitude",
            price_cols=["price_per_night"],
        )
        _save_both(hotels, "hotels.csv")
    else:
        print(f"\nSkipping hotels: {hotels_path} not found")

    # --- Attractions (only runs if the raw file is supplied) ---
    attractions_path = f"{DATA_DIR}/attractions_raw.csv"
    if os.path.exists(attractions_path):
        attractions = pd.read_csv(attractions_path)
        attractions = clean_generic(
            attractions, "attractions",
            numeric_cols=["rating", "cost", "duration_hours", "latitude", "longitude"],
            lat_col="latitude", lon_col="longitude",
            price_cols=["cost"],
        )
        _save_both(attractions, "attractions.csv")
    else:
        print(f"\nSkipping attractions: {attractions_path} not found (not provided)")

    # --- Restaurants (only runs if the raw file is supplied) ---
    restaurants_path = f"{DATA_DIR}/restaurants_raw.csv"
    if os.path.exists(restaurants_path):
        restaurants = pd.read_csv(restaurants_path)
        restaurants = clean_generic(
            restaurants, "restaurants",
            numeric_cols=["rating", "average_cost"],
            price_cols=["average_cost"],
        )
        _save_both(restaurants, "restaurants.csv")
    else:
        print(f"\nSkipping restaurants: {restaurants_path} not found (not provided)")


if __name__ == "__main__":
    main()