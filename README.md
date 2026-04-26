# 🚨 DisasterRoute — Real-Time Emergency Evacuation Optimizer

A multi-algorithm evacuation optimization engine that computes, distributes, and dynamically re-routes civilian evacuation flow during natural disasters — replacing static pre-planned routes with live algorithmic decision-making.

> Built with Odisha in mind — a state that faces cyclones annually (Fani 2019, Amphan 2020, Yaas 2021).

---

## 🧠 Problem Statement

During disasters, evacuation fails not because of lack of resources but because of **bad routing decisions made under pressure**:

- Roads get blocked mid-evacuation but systems don't adapt
- Shelters overflow while nearby ones stay empty
- Critical zones like hospitals get evacuated last
- No system reasons over multiple constraints simultaneously

**DisasterRoute solves this with 5 algorithms working together in real time.**

---

## ⚙️ How It Works

### Algorithms

| Algorithm | Purpose |
|---|---|
| **A\*** | Fastest path routing with Haversine heuristic |
| **Dijkstra's** | Guaranteed shortest path, user-selectable |
| **Ford-Fulkerson Max Flow** | Prevents road/shelter bottlenecks |
| **DP (Knapsack variant)** | Optimal shelter capacity allocation |
| **Greedy Priority Scheduling** | Critical zones evacuated first |

### Pipeline

Real OSM Road Network → Danger Zones + Shelters → Greedy Priority Sorting → A* / Dijkstra's Routing → Ford-Fulkerson Max Flow → DP Shelter Allocation → Dynamic Re-routing → Live Map Dashboard (Leaflet.js)

---

## 🗺️ Features

- **Real road networks** — downloads actual city maps from OpenStreetMap via OSMnx
- **Dynamic re-routing** — block a road mid-evacuation, routes recompute instantly
- **Priority-based evacuation** — hospitals and critical zones evacuated first
- **Shelter load balancing** — DP ensures no shelter overflows while others stay empty
- **Live map visualization** — color-coded routes by priority, shelter fill levels
- **REST API** — fully documented via FastAPI's auto-generated Swagger UI

---

## 📊 Results (Bhubaneswar Test)

- Road network: 500+ nodes, 1000+ edges
- 3,500 simulated civilians across 2 danger zones
- Total evacuation time: **605 seconds**
- Shelter load: Kalinga Stadium 30%, KIIT Campus 66%
- Dynamic rerouting recomputes blocked roads in **< 50ms**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python |
| Algorithms | Pure Python (no black boxes) |
| Road Network | OSMnx, OpenStreetMap |
| Graph Operations | NetworkX |
| Database | SQLite |
| Frontend | HTML/CSS/JS, Leaflet.js |
| Deployment | Oracle Cloud Infrastructure (OCI) |

---

## 🚀 Running Locally

```bash
git clone https://github.com/Khushee2023/DisasterRoute.git
cd DisasterRoute

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open browser at: `http://127.0.0.1:8000`

---

## 📁 Project Structure

```
DisasterRoute/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── algorithms/
│   │   ├── dijkstra.py
│   │   ├── astar.py
│   │   ├── maxflow.py
│   │   └── shelter.py
│   ├── data/
│   │   └── graph_loader.py
│   └── routers/
│       └── routes.py
├── static/
│   ├── index.html
│   ├── js/map.js
│   └── css/style.css
└── requirements.txt
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/scenario/create` | Create evacuation scenario |
| POST | `/api/evacuate` | Run evacuation algorithms |
| POST | `/api/block-road` | Block a road dynamically |
| GET | `/api/scenario/{id}/shelters` | Get shelter status |
| GET | `/api/scenario/{id}/blocked-roads` | Get blocked roads |

---

## 👩‍💻 Author

**Khushee Ranjan**
B.Tech CSE (Data Science), ITER SOA University, Bhubaneswar
[LinkedIn](https://linkedin.com/in/khushee-ranjan) | [GitHub](https://github.com/Khushee2023)
