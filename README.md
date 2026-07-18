# Smart-Travel-Planner
A Smart Travel Planner is an AI system that creates a personalized travel itinerary instead of simply listing destinations. It combines several AI techniques to make decisions based on the user's preferences and constraints.

## About the Project

Planning a trip can be exciting, but it can also be stressful. People often spend a lot of time searching for places to visit, comparing hotels, estimating costs, and deciding the best route. This project aims to simplify that process by creating a **Smart Travel Planner** that generates a personalized travel plan based on the user's preferences.
The application uses Artificial Intelligence techniques to recommend attractions, suggest hotels and restaurants, estimate the trip budget, and create an optimized itinerary. Instead of simply showing popular places, the system considers factors such as the user's interests, budget, and travel duration to make more meaningful recommendations.
This project was developed as part of the Artificial Intelligence coursework for the **BSc (Hons) Computer Science with Artificial Intelligence** program.

---

## Features

* Personalized attraction recommendations
* Hotel and restaurant suggestions
* Budget estimation
* Day-wise travel itinerary
* Route optimization between attractions
* Interactive and easy-to-use interface
* Explainable recommendations

---

## AI Techniques Used
This project combines multiple AI concepts instead of relying on a single algorithm.

### Recommendation System
Suggests attractions, hotels, and restaurants based on the user's interests, destination, and budget.

### Fuzzy Logic
People don't usually think in exact numbers like "Budget = NPR 20,000". Instead, they think in terms such as **low**, **medium**, or **high** budget. Fuzzy logic helps the system make decisions in a way that is closer to human reasoning.

### A* Search Algorithm
Once the attractions have been selected, the A* Search algorithm is used to find an efficient route between destinations, helping reduce travel time.

---
## Project Structure

```text
Smart-Travel-Planner/
│
├── data/
│   ├── attractions.csv
│   ├── hotels.csv
│   ├── restaurants.csv
│   └── weather.csv
│
├── recommendation.py
├── fuzzy.py
├── astar.py
├── planner.py
├── app.py
├── requirements.txt
└── README.md
```

---
## Dataset

The project uses a custom dataset containing information about tourist attractions, hotels, and restaurants.
Each attraction includes information such as:

* Name
* Category
* Rating
* Entry Cost
* Estimated Visit Duration
* Latitude and Longitude

The hotel dataset contains prices and ratings, while the restaurant dataset includes cuisine type, average price, and ratings.
---

## How It Works
1. The user enters travel preferences such as destination, budget, number of days, and interests.
2. The recommendation engine filters attractions that best match those preferences.
3. Fuzzy logic evaluates factors like budget and suitability instead of relying on strict rules.
4. The A* Search algorithm calculates an efficient travel route.
5. The system generates a personalized itinerary, including recommended places, estimated expenses, and travel order.

---

## Technologies Used
* Python
* Streamlit
* Pandas
* NumPy
* NetworkX
* Scikit-Fuzzy
* Matplotlib

---

## Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/Smart-Travel-Planner.git
```

Move into the project folder:
```bash
cd Smart-Travel-Planner
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
streamlit run app.py
```

---
## Example Input

* **Destination:** Pokhara
* **Budget:** NPR 20,000
* **Duration:** 3 Days
* **Interests:** Nature, Hiking
* **Hotel Preference:** Budget

---
## Expected Output
The application will generate:

* Recommended attractions
* Suggested hotel
* Restaurant recommendations
* Optimized travel route
* Estimated trip cost
* A day-by-day travel itinerary

---
## Future Improvements

Some features that could be added in future versions include:

* Live weather information
* Google Maps integration
* Real-time traffic updates
* Online hotel booking
* More personalized recommendations using user history
* Voice-based trip planning

---

## Author
**Ujwal Acharya**
BSc (Hons) Computer Science with Artificial Intelligence

---
## License
This project is created for educational purposes as part of university coursework.
