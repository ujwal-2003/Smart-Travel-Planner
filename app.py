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

planner = load_planner()

# =====================================
# Header
# =====================================

st.title("🌍 Smart Travel Planner")

st.markdown("""
Plan your perfect Nepal trip using AI.

### Features
- 🤖 AI Recommendation System
- 🧠 Fuzzy Logic Trip Evaluation
- 🗺 Optimized Travel Route
""")

# =====================================
# Sidebar
# =====================================

st.sidebar.header("✈️ Trip Preferences")

cities = sorted(planner.attractions["city"].dropna().unique())

city = st.sidebar.selectbox(
    "📍 Destination",
    cities
)

interests = st.sidebar.multiselect(
    "🏞 Interests",
    [
        "Nature",
        "Adventure",
        "Culture",
        "Religious",
        "Food",
        "Hiking"
    ]
)

hotel_budget = st.sidebar.slider(
    "🏨 Hotel Budget / Night (NPR)",
    1000,
    15000,
    5000,
    500
)

food_budget = st.sidebar.slider(
    "🍴 Food Budget / Day (NPR)",
    200,
    5000,
    1000,
    100
)

total_budget = st.sidebar.slider(
    "💰 Total Budget (NPR)",
    5000,
    100000,
    30000,
    1000
)

days = st.sidebar.slider(
    "📅 Duration (Days)",
    1,
    14,
    5
)

generate = st.sidebar.button("🚀 Generate Plan")

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
            days=days
        )

    st.success("Travel plan generated successfully!")

    # =====================================
    # Trip Score
    # =====================================

    st.subheader("🤖 AI Trip Evaluation")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Trip Score",
        f"{result['score']:.1f}/100"
    )

    c2.metric(
        "Destination",
        result["city"]
    )

    c3.metric(
        "Duration",
        f"{result['days']} Days"
    )

    # =====================================
    # Route
    # =====================================

    st.subheader("🗺 Optimized Travel Route")

    if len(result["route"]) > 0:

        for i, place in enumerate(result["route"], start=1):
            st.write(f"**{i}. {place}**")

        st.success(
            f"Estimated Route Distance: {result['distance']} km"
        )

    else:

        st.error("Unable to generate an optimized route.")

    # =====================================
    # Attractions
    # =====================================

    st.subheader("🏞 Recommended Attractions")

    if not result["attractions"].empty:

        st.dataframe(
            result["attractions"],
            use_container_width=True
        )

    else:

        st.warning("No attractions found.")

    # =====================================
    # Hotels
    # =====================================

    st.subheader("🏨 Recommended Hotels")

    if not result["hotels"].empty:

        st.dataframe(
            result["hotels"],
            use_container_width=True
        )

    else:

        st.warning("No hotels found within your budget.")

    # =====================================
    # Restaurants
    # =====================================

    st.subheader("🍴 Recommended Restaurants")

    if not result["restaurants"].empty:

        st.dataframe(
            result["restaurants"],
            use_container_width=True
        )

    else:

        st.warning("No restaurants found within your budget.")

    # =====================================
    # Download CSV
    # =====================================

    st.subheader("📥 Export Travel Plan")

    csv = result["attractions"].to_csv(index=False)

    st.download_button(
        label="Download Attractions CSV",
        data=csv,
        file_name=f"{city}_travel_plan.csv",
        mime="text/csv"
    )

    # =====================================
    # Debug Information
    # =====================================

    with st.expander("🔍 Debug Information"):

        st.write("Number of Attractions:", len(result["attractions"]))
        st.write("Generated Route:", result["route"])
        st.write("Route Distance:", result["distance"])

