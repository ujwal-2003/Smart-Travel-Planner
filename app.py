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
# Load AI Planner
# =====================================

@st.cache_resource
def load_planner():

    return SmartTravelPlanner()



planner = load_planner()



# =====================================
# Header
# =====================================

st.title(
    "🌍 Smart Travel Planner"
)


st.write(
    """
    Plan your perfect Nepal trip using AI:

    🤖 Recommendation System  
    🧠 Fuzzy Logic Trip Evaluation  
    🗺 A* Route Optimization
    """
)



# =====================================
# Sidebar
# =====================================

st.sidebar.header(
    "✈️ Trip Preferences"
)



# -------------------------------------
# City Selection
# -------------------------------------

cities = sorted(
    planner.attractions["city"]
    .unique()
)


city = st.sidebar.selectbox(

    "📍 Select Destination",

    cities

)



# -------------------------------------
# Interests
# -------------------------------------

interests = st.sidebar.multiselect(

    "🏞 Select Interests",

    [

        "Nature",
        "Hiking",
        "Adventure",
        "Religious",
        "Culture",
        "Food"

    ]

)



# -------------------------------------
# Budget Inputs
# -------------------------------------

hotel_budget = st.sidebar.slider(

    "🏨 Hotel Budget Per Night (NPR)",

    min_value=1000,

    max_value=15000,

    value=5000,

    step=500

)



food_budget = st.sidebar.slider(

    "🍽 Food Budget Per Day (NPR)",

    min_value=200,

    max_value=5000,

    value=1000,

    step=100

)



total_budget = st.sidebar.slider(

    "💰 Total Trip Budget (NPR)",

    min_value=5000,

    max_value=100000,

    value=30000,

    step=1000

)



days = st.sidebar.slider(

    "📅 Trip Duration (Days)",

    min_value=1,

    max_value=14,

    value=5

)



generate = st.sidebar.button(

    "🚀 Generate Travel Plan"

)



# =====================================
# Generate Plan
# =====================================

if generate:


    if not interests:


        st.warning(
            "Please select at least one interest."
        )


    else:


        with st.spinner(
            "Creating AI travel plan..."
        ):


            result = planner.generate_plan(

                city=city,

                interests=interests,

                hotel_budget=hotel_budget,

                food_budget=food_budget,

                total_budget=total_budget,

                days=days

            )



        st.success(
            "Travel plan generated successfully!"
        )



        # =================================
        # AI Score
        # =================================

        st.subheader(
            "🤖 AI Trip Suitability Score"
        )



        col1, col2, col3 = st.columns(3)



        with col1:

            st.metric(

                "Trip Score",

                f"{result['score']}/100"

            )



        with col2:

            st.metric(

                "Destination",

                result["city"]

            )



        with col3:

            st.metric(

                "Duration",

                f"{result['days']} Days"

            )



        # =================================
        # Route
        # =================================

        st.subheader(
            "🗺 Optimized Travel Route"
        )



        if result["route"]:


            route_text = " ➡️ ".join(

                result["route"]

            )


            st.info(
                route_text
            )


            st.write(

                f"📏 Estimated Distance: {result['distance']} km"

            )


        else:


            st.warning(

                "Route could not be generated."

            )



        # =================================
        # Attractions
        # =================================

        st.subheader(

            "🏞 Recommended Attractions"

        )


        if not result["attractions"].empty:


            st.dataframe(

                result["attractions"],

                use_container_width=True

            )


        else:


            st.warning(

                "No attractions found."

            )



        # =================================
        # Hotels
        # =================================

        st.subheader(

            "🏨 Recommended Hotels"

        )


        if not result["hotels"].empty:


            st.dataframe(

                result["hotels"],

                use_container_width=True

            )


        else:


            st.warning(

                "No hotels found for this budget."

            )



        # =================================
        # Restaurants
        # =================================

        st.subheader(

            "🍴 Recommended Restaurants"

        )


        if not result["restaurants"].empty:


            st.dataframe(

                result["restaurants"],

                use_container_width=True

            )


        else:


            st.warning(

                "No restaurants found."

            )



        # =================================
        # Download
        # =================================

        st.subheader(

            "📥 Export Travel Plan"

        )


        export_data = result["attractions"].to_csv(

            index=False

        )



        st.download_button(

            label="Download Attractions CSV",

            data=export_data,

            file_name=f"{city}_travel_plan.csv",

            mime="text/csv"

        )