# 🌍 Smart Travel Planner

An AI-powered travel planning system that generates personalized travel itineraries for destinations across Nepal. Instead of simply listing tourist attractions, the planner recommends places based on user interests, budget, travel duration, and destination while optimizing the travel route and evaluating the quality of the trip using multiple Artificial Intelligence techniques.

This project was developed as part of the **BSc (Hons) Computer Science with Artificial Intelligence** coursework.

---

# ✨ Features

- 🤖 AI-powered attraction recommendations using **TF-IDF + Cosine Similarity**
- 🧠 Trip evaluation using a **custom Mamdani Fuzzy Logic** engine
- 🗺 Route optimization using **A\* Search** with **2-opt route refinement**
- 📅 Automatic **day-wise itinerary generation**
- 💰 Detailed budget estimation and breakdown
- 🏨 Hotel recommendations based on budget and ratings
- 🍴 Restaurant recommendations based on food budget
- 📍 Interactive map displaying recommended attractions
- 📥 Export itinerary as TXT
- 📄 Export attraction list as CSV
- 📊 Debug information for generated routes

---

# 🧠 AI Techniques Used

The Smart Travel Planner combines multiple AI techniques to provide intelligent travel recommendations.

## Recommendation System

The recommendation engine suggests attractions, hotels, and restaurants based on the user's preferences.

### Attractions
- TF-IDF Vectorization
- Cosine Similarity
- Rating-based ranking
- Interest matching

### Hotels & Restaurants
Recommendations are generated using a weighted composite score based on:

- Budget fitness
- User budget
- Ratings

---

## Fuzzy Logic

A custom **Mamdani-style fuzzy inference system** evaluates the overall quality of the planned trip.

Unlike traditional rule-based systems, fuzzy logic handles uncertain concepts such as:

- Low / Medium / High Budget
- Short / Medium / Long Trip
- Cheap / Average / Expensive Destination
- Weak / Moderate / Strong Interest Match

The fuzzy engine produces:

- Trip Score (0–100)
- Quality Label
    - Excellent
    - Good
    - Average
    - Poor

Unlike previous versions, this implementation does **not require Scikit-Fuzzy**, as all membership functions and centroid defuzzification are implemented manually using NumPy.

---

## A* Search Route Planning

The travel route is optimized using an A* graph.

Features include:

- Haversine distance calculation
- Nearest-neighbour graph construction
- 2-opt local search optimization
- Estimated route distance
- Estimated travel time
- Multi-stop itinerary generation

---

# 📁 Project Structure

```text
Smart-Travel-Planner/
│
├── data/
│   ├── attractions.csv
│   ├── hotels.csv
│   ├── restaurants.csv
│
├── app.py
├── planner.py
├── recommendation.py
├── fuzzy.py
├── astar.py
├── clean_data.py
├── evaluation.py
├── visualization.py
├── requirements.txt
└── README.md
```

---

# 📊 Dataset

The project uses custom datasets containing tourist information for cities across Nepal.

## Attractions Dataset

Each attraction includes:

- Name
- City
- Category
- Rating
- Entry Cost
- Visit Duration
- Latitude
- Longitude

## Hotels Dataset

Includes:

- Name
- City
- Star Rating
- Hotel Rating
- Price per Night
- Address
- Coordinates

## Restaurants Dataset

Includes:

- Name
- City
- Cuisine
- Rating
- Average Cost

---

# ⚙️ How the System Works

1. The user selects:
   - Destination
   - Interests
   - Hotel budget
   - Food budget
   - Total budget
   - Trip duration

2. The Recommendation Engine finds attractions using TF-IDF similarity.

3. Hotels and restaurants are ranked using budget and rating.

4. The fuzzy engine evaluates the trip quality.

5. The A* planner builds an optimized travel route.

6. Attractions are automatically distributed into a day-wise itinerary.

7. A complete travel plan is displayed including:

   - Trip Score
   - Budget Breakdown
   - Optimized Route
   - Interactive Map
   - Recommended Attractions
   - Hotels
   - Restaurants

8. Users can export:

   - Attractions (CSV)
   - Travel itinerary (TXT)

---

# 💻 Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Matplotlib

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Smart-Travel-Planner.git
```

Move into the project folder

```bash
cd Smart-Travel-Planner
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 🖥 Example Usage

### Input

Destination

```
Pokhara
```

Interests

```
Nature
Adventure
Hiking
```

Hotel Budget

```
NPR 5,000
```

Food Budget

```
NPR 1,000
```

Total Budget

```
NPR 30,000
```

Duration

```
5 Days
```

---

# 📤 Example Output

The planner generates:

- AI Trip Score
- Trip Quality Label
- Interest Match Score
- Budget Breakdown
- Optimized Route
- Estimated Travel Distance
- Day-wise Itinerary
- Interactive Attraction Map
- Recommended Attractions
- Recommended Hotels
- Recommended Restaurants
- Downloadable CSV
- Downloadable TXT itinerary

---

# 📈 Evaluation

The project includes a dedicated evaluation module.

It evaluates:

### Recommendation Engine

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

### Fuzzy Evaluation Engine

- MAE
- MSE
- RMSE
- R² Score

### Hotel & Restaurant Recommendation

- MAE
- MSE
- RMSE
- R² Score

Generated outputs include:

- Evaluation Report
- Confusion Matrix
- Regression Scatter Plots

---

# 📊 Data Visualization

The visualization module generates:

- Attractions per City
- Attraction Category Distribution
- Rating Distribution
- Cost vs Rating
- Hotel Price Distribution
- Cuisine Distribution
- Geographic Scatter Maps
- Correlation Heatmaps

---

# 🧹 Data Cleaning

A preprocessing module is included to improve dataset quality.

It performs:

- Duplicate removal
- Missing value handling
- Numeric conversion
- Coordinate validation
- Rating validation
- Price validation
- Standardization of text fields

---

# 🔮 Future Improvements

Potential future enhancements include:

- Google Maps API integration
- Live weather information
- Real-time traffic updates
- Hotel booking integration
- User accounts and trip history
- Collaborative filtering recommendations
- Voice-assisted trip planning
- Mobile application deployment

---

# 👨‍💻 Author

**Ujwal Acharya**

BSc (Hons) Computer Science with Artificial Intelligence

---

# 📄 License

This project was developed for educational purposes as part of university coursework.