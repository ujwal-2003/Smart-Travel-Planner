import streamlit as st
from planner import SmartTravelPlanner


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="✈️",
    layout="wide"
)


# Initialize Planner
@st.cache_resource
def load_planner():
    return SmartTravelPlanner()


planner = load_planner()


# -----------------------------
# Header
# -----------------------------

st.title("🌍 Smart Travel Planner")

st.write(
    """
    Plan your perfect trip using AI-powered:
    - 🤖 Recommendation System
    - 🧠 Fuzzy Logic Evaluation
    - 🗺 A* Route Planning
    """
)


# -----------------------------
# Sidebar Inputs
# -----------------------------

st.sidebar.header("✈️ Trip Preferences")


interests = st.sidebar.multiselect(
    "Choose your interests",
    [
        "Nature",
        "Hiking",
        "Adventure",
        "Religious",
        "Culture",
        "Food"
    ]
)


hotel_budget = st.sidebar.slider(
    "🏨 Hotel Budget per Night (NPR)",
    min_value=1000,
    max_value=10000,
    value=3500,
    step=500
)


food_budget = st.sidebar.slider(
    "🍽 Food Budget per Day (NPR)",
    min_value=200,
    max_value=3000,
    value=1000,
    step=100
)


total_budget = st.sidebar.slider(
    "💰 Total Trip Budget (NPR)",
    min_value=5000,
    max_value=50000,
    value=20000,
    step=1000
)


days = st.sidebar.slider(
    "📅 Trip Duration",
    min_value=1,
    max_value=7,
    value=3
)


generate = st.sidebar.button(
    "🚀 Generate Travel Plan"
)



# -----------------------------
# Generate Plan
# -----------------------------

if generate:

    if not interests:
        st.warning(
            "Please select at least one interest."
        )

    else:

        with st.spinner("Creating your AI travel plan..."):

            result = planner.generate_plan(
                interests=interests,
                hotel_budget=hotel_budget,
                food_budget=food_budget,
                total_budget=total_budget,
                days=days
            )


        st.success(
            "Your travel plan has been generated!"
        )


        # -----------------------------
        # Score Card
        # -----------------------------

        st.subheader("🤖 AI Trip Suitability Score")


        col1, col2, col3 = st.columns(3)


        with col1:
            st.metric(
                "Suitability Score",
                f"{result['score']:.2f}/100"
            )


        with col2:
            st.metric(
                "Trip Duration",
                f"{result['days']} Days"
            )


        with col3:
            st.metric(
                "Budget",
                f"NPR {result['budget']}"
            )



        # -----------------------------
        # Route
        # -----------------------------

        st.subheader("🗺 Suggested Travel Route")


        if result["route"]:

            route_text = " ➡️ ".join(
                result["route"]
            )

            st.info(route_text)

        else:

            st.warning(
                "Route could not be generated."
            )



        # -----------------------------
        # Attractions
        # -----------------------------

        st.subheader("🏞 Recommended Attractions")


        st.dataframe(
            result["attractions"],
            use_container_width=True
        )



        # -----------------------------
        # Hotels
        # -----------------------------

        st.subheader("🏨 Recommended Hotels")


        st.dataframe(
            result["hotels"],
            use_container_width=True
        )



        # -----------------------------
        # Restaurants
        # -----------------------------

        st.subheader("🍴 Recommended Restaurants")


        st.dataframe(
            result["restaurants"],
            use_container_width=True
        )


        # -----------------------------
        # Download Option
        # -----------------------------

        st.subheader("📥 Export Plan")


        csv = result["attractions"].to_csv(
            index=False
        )


        st.download_button(
            label="Download Attractions CSV",
            data=csv,
            file_name="travel_plan.csv",
            mime="text/csv"
        )

