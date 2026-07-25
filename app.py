import streamlit as st

from planner import SmartTravelPlanner



# --------------------------
# Page Setup
# --------------------------

st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="✈️",
    layout="wide"
)



@st.cache_resource
def load_planner():

    return SmartTravelPlanner()



planner = load_planner()



# --------------------------
# Header
# --------------------------

st.title(
    "🌍 Smart Travel Planner"
)


st.write(
"""
AI-powered travel planning system using:

🤖 Recommendation System  
🧠 Fuzzy Logic Evaluation  
🗺 A* Route Optimization
"""
)



# --------------------------
# Sidebar
# --------------------------

st.sidebar.header(
    "✈️ Trip Preferences"
)



interests = st.sidebar.multiselect(
    "Select Interests",
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
    "🏨 Hotel Budget / Night",
    1000,
    10000,
    3500,
    500
)



food_budget = st.sidebar.slider(
    "🍴 Food Budget / Day",
    200,
    3000,
    1000,
    100
)



total_budget = st.sidebar.slider(
    "💰 Total Budget",
    5000,
    50000,
    20000,
    1000
)



days = st.sidebar.slider(
    "📅 Trip Duration",
    1,
    14,
    3
)



generate = st.sidebar.button(
    "🚀 Generate Plan"
)



# --------------------------
# Generate
# --------------------------

if generate:


    if not interests:

        st.warning(
            "Please select interests"
        )


    else:


        with st.spinner(
            "Creating AI travel plan..."
        ):


            result = planner.generate_plan(

                interests,

                hotel_budget,

                food_budget,

                total_budget,

                days
            )



        st.success(
            "Travel plan generated!"
        )



        # Score Cards

        c1,c2,c3 = st.columns(3)



        c1.metric(
            "AI Score",
            f"{result['score']}/100"
        )


        c2.metric(
            "Days",
            result["days"]
        )


        c3.metric(
            "Budget",
            f"NPR {result['budget']}"
        )



        # Tabs

        tab1,tab2,tab3,tab4 = st.tabs(
            [
                "🗺 Route",
                "🏞 Attractions",
                "🏨 Hotels",
                "🍴 Restaurants"
            ]
        )



        with tab1:

            if result["route"]:

                st.success(
                    " ➡️ ".join(
                        result["route"]
                    )
                )

            else:

                st.warning(
                    "No route found"
                )



        with tab2:

            st.dataframe(
                result["attractions"],
                use_container_width=True
            )



        with tab3:

            st.dataframe(
                result["hotels"],
                use_container_width=True
            )



        with tab4:

            st.dataframe(
                result["restaurants"],
                use_container_width=True
            )



        # Export

        csv = (
            result["attractions"]
            .to_csv(
                index=False
            )
        )


        st.download_button(

            "📥 Download Plan",

            csv,

            "travel_plan.csv",

            "text/csv"

        )