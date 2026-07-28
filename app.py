import pandas as pd
import streamlit as st

from planner import SmartTravelPlanner

# =====================================
# Page Configuration
# =====================================

st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# =====================================
# Load Planner
# =====================================

@st.cache_resource
def load_planner():
    return SmartTravelPlanner()

try:
    planner = load_planner()
except FileNotFoundError as e:
    st.error(
        "Could not load the travel data files. Make sure attractions.csv, "
        f"hotels.csv, and restaurants.csv are in the `data/` folder.\n\n{e}"
    )
    st.stop()

# =====================================
# Header
# =====================================

st.title("🌍 Smart Travel Planner")

st.markdown("""
Plan your perfect Nepal trip using AI.

### Features
- 🤖 AI-powered recommendations (interest-matched with TF-IDF similarity)
- 🧠 Fuzzy-logic trip evaluation (budget, duration, destination cost, interest fit)
- 🗺 Optimized multi-stop route (A* graph + 2-opt refinement)
- 📅 Day-by-day itinerary, not just a flat list
- 💰 Budget breakdown with over-budget warnings
""")

# =====================================
# Sidebar
# =====================================

st.sidebar.header("✈️ Trip Preferences")

cities = sorted(planner.attractions["city"].dropna().unique())

city = st.sidebar.selectbox("📍 Destination", cities)

interests = st.sidebar.multiselect(
    "🏞 Interests",
    ["Nature", "Adventure", "Culture", "Religious", "Food", "Hiking", "Museum"],
)

hotel_budget = st.sidebar.slider("🏨 Hotel Budget / Night (NPR)", 1000, 15000, 5000, 500)
food_budget = st.sidebar.slider("🍴 Food Budget / Day (NPR)", 200, 5000, 1000, 100)
total_budget = st.sidebar.slider("💰 Total Budget (NPR)", 5000, 100000, 30000, 1000)
days = st.sidebar.slider("📅 Duration (Days)", 1, 14, 5)

generate = st.sidebar.button("🚀 Generate Plan", use_container_width=True)

# =====================================
# Generate Plan
# =====================================

if generate:

    if len(interests) == 0:
        st.warning("Please select at least one interest.")
        st.stop()

    with st.spinner("Generating your travel plan..."):
        result = planner.generate_plan(
            city=city,
            interests=interests,
            hotel_budget=hotel_budget,
            food_budget=food_budget,
            total_budget=total_budget,
            days=days,
        )

    st.success("Travel plan generated successfully!")

    # =====================================
    # Trip Score
    # =====================================

    st.subheader("🤖 AI Trip Evaluation")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trip Score", f"{result['score']:.1f}/100", result["score_label"])
    c2.metric("Destination", result["city"])
    c3.metric("Duration", f"{result['days']} Days")
    c4.metric("Interest Fit", f"{result['interest_fit']:.1f}/10")

    # =====================================
    # Budget Breakdown
    # =====================================

    st.subheader("💰 Budget Breakdown")

    breakdown = result["cost_breakdown"]

    b1, b2 = st.columns([2, 1])

    with b1:
        chart_df = pd.DataFrame(
            {
                "Category": ["Attractions", "Hotel", "Food"],
                "Estimated Cost (NPR)": [
                    breakdown["attractions"],
                    breakdown["hotel"],
                    breakdown["food"],
                ],
            }
        ).set_index("Category")
        st.bar_chart(chart_df)

    with b2:
        st.metric("Estimated Total", f"NPR {breakdown['total_estimated']:,.0f}")
        st.metric("Your Budget", f"NPR {breakdown['total_budget']:,.0f}")
        if breakdown["within_budget"]:
            st.success(f"Within budget by NPR {breakdown['difference']:,.0f}")
        else:
            st.error(f"Over budget by NPR {-breakdown['difference']:,.0f}")

    # =====================================
    # Route + Day-wise Itinerary
    # =====================================

    st.subheader("🗺 Optimized Travel Route")

    if len(result["route"]) > 0:

        st.success(f"Estimated Route Distance: {result['distance']} km")

        st.markdown("**Day-by-day itinerary:**")

        day_tabs = st.tabs([f"Day {i + 1}" for i in range(len(result["daily_itinerary"]))])

        for tab, day_stops in zip(day_tabs, result["daily_itinerary"]):
            with tab:
                if day_stops:
                    for i, place in enumerate(day_stops, start=1):
                        st.write(f"**{i}. {place}**")
                else:
                    st.caption("Free day / buffer day — no stops scheduled.")

        # Map of the attractions in the route
        route_coords = result["attractions"][
            result["attractions"]["name"].isin(result["route"])
        ][["latitude", "longitude"]]

        if not route_coords.empty:
            st.map(route_coords, latitude="latitude", longitude="longitude", size=40)

    else:
        st.error("Unable to generate an optimized route.")

    # =====================================
    # Attractions
    # =====================================

    st.subheader("🏞 Recommended Attractions")

    if not result["attractions"].empty:
        display_cols = [c for c in ["name", "category", "rating", "cost", "duration_hours"] if c in result["attractions"].columns]
        st.dataframe(result["attractions"][display_cols], use_container_width=True)
    else:
        st.warning("No attractions found.")

    # =====================================
    # Hotels
    # =====================================

    st.subheader("🏨 Recommended Hotels")

    if not result["hotels"].empty:
        display_cols = [c for c in ["name", "star", "rating", "price_per_night", "address"] if c in result["hotels"].columns]
        st.dataframe(result["hotels"][display_cols], use_container_width=True)
    else:
        st.warning("No hotels found within your budget.")

    # =====================================
    # Restaurants
    # =====================================

    st.subheader("🍴 Recommended Restaurants")

    if not result["restaurants"].empty:
        display_cols = [c for c in ["name", "cuisine", "rating", "average_cost"] if c in result["restaurants"].columns]
        st.dataframe(result["restaurants"][display_cols], use_container_width=True)
    else:
        st.warning("No restaurants found within your budget.")

    # =====================================
    # Export
    # =====================================

    st.subheader("📥 Export Travel Plan")

    e1, e2 = st.columns(2)

    with e1:
        csv = result["attractions"].to_csv(index=False)
        st.download_button(
            label="Download Attractions CSV",
            data=csv,
            file_name=f"{city}_attractions.csv",
            mime="text/csv",
        )

    with e2:
        lines = [f"Smart Travel Plan — {city} ({days} days)", ""]
        lines.append(f"Trip score: {result['score']}/100 ({result['score_label']})")
        lines.append(f"Estimated cost: NPR {breakdown['total_estimated']:,.0f} "
                      f"(budget: NPR {breakdown['total_budget']:,.0f})")
        lines.append("")
        for i, day_stops in enumerate(result["daily_itinerary"], start=1):
            lines.append(f"Day {i}:")
            if day_stops:
                for stop in day_stops:
                    lines.append(f"  - {stop}")
            else:
                lines.append("  - (free day)")
        itinerary_text = "\n".join(lines)

        st.download_button(
            label="Download Itinerary (.txt)",
            data=itinerary_text,
            file_name=f"{city}_itinerary.txt",
            mime="text/plain",
        )

    # =====================================
    # Debug Information
    # =====================================

    with st.expander("🔍 Debug Information"):
        st.write("Number of Attractions:", len(result["attractions"]))
        st.write("Generated Route:", result["route"])
        st.write("Route Distance:", result["distance"])
        st.write("Fuzzy rule breakdown available via planner.fuzzy.evaluate(...)")

else:
    st.info("Set your preferences in the sidebar and click **Generate Plan** to get started.")