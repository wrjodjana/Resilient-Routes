import csv
import os
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
  import training
except Exception:
  training = None

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
ALLOWED_ORIGIN_REGEX = os.getenv(
  "ALLOWED_ORIGIN_REGEX",
  r"https://([a-z0-9-]+\.)*resilient-routes\.xyz|https://[a-z0-9-]+\.vercel\.app",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    FRONTEND_URL,
    *ALLOWED_ORIGINS
  ],
  allow_origin_regex=ALLOWED_ORIGIN_REGEX,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

SEISMIC_DIR = Path(__file__).parent / "seismic"

GraphSize = Literal["small", "middle", "large"]

TARGET_NODE_ID = 17

@lru_cache(maxsize=3)
def load_graph(size: str) -> dict:
  graph_dir = SEISMIC_DIR / f"connectivity_graph_{size}"

  with open(graph_dir / "graph_info.pickle", "rb") as f:
    graph_info = pickle.load(f)

  with open(graph_dir / "all_result.pickle", "rb") as f:
    all_result = pickle.load(f)

  scenario = all_result[0]
  node_res = scenario["node_res"].ravel()
  threshold = scenario["node_thre"][0]

  nodes = []
  with open(graph_dir / "map.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
      node_id = int(row["id"])
      value = float(node_res[node_id])
      nodes.append({
        "id": node_id,
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "value": value,
        "is_target": node_id == TARGET_NODE_ID,
      })

  edges = [{"source": int(n1), "target": int(n2)} for n1, n2 in graph_info["edge_list"]]

  return {
    "size": size,
    "n_node": graph_info["n_node"],
    "n_bridge": graph_info["n_bridge"],
    "n_road": graph_info["n_road"],
    "n_edge": graph_info["n_edge"],
    "threshold": float(threshold),
    "nodes": nodes,
    "edges": edges,
  }

@app.get("/api/graph/{size}")
async def fetch_graph(size: GraphSize):
  return load_graph(size)

EarthquakeType = Literal["minor", "moderate", "major"]

class TrainRequest(BaseModel):
  size: GraphSize = "small"
  target_node_id: int = Field(ge=0)
  earthquake_type: EarthquakeType

@app.post("/api/seismic/train")
async def start_training(request: TrainRequest):
  if training is None:
    raise HTTPException(status_code=503, detail="Training is not available in this environment")
  if request.target_node_id >= training.N_NODES[request.size]:
    raise HTTPException(status_code=422, detail="Unknown target node for this network size")
  job = training.start_job(request.size, request.target_node_id, request.earthquake_type)
  if job is None:
    raise HTTPException(status_code=409, detail="A training job is already running")
  return job.to_dict()

@app.get("/api/seismic/train/{job_id}")
async def fetch_training_job(job_id: str):
  if training is None:
    raise HTTPException(status_code=503, detail="Training is not available in this environment")
  job = training.get_job(job_id)
  if job is None:
    raise HTTPException(status_code=404, detail="Unknown job")
  return job.to_dict()

TRAFFIC_DIR = Path(__file__).parent / "traffic"

TrafficCity = Literal["anaheim", "siouxfalls"]

TrafficSeverity = Literal["baseline", "minor", "moderate", "major"]

TRAFFIC_DIRS = {"anaheim": "sta_anaheim", "siouxfalls": "sta_siouxfalls"}

TRAFFIC_SCENARIO_CITIES = {"anaheim": "ANAHEIM", "siouxfalls": "Sioux"}

TRAFFIC_SCENARIO_SAMPLES = {"anaheim": 0, "siouxfalls": 1}

TRAFFIC_MISSING_SCENARIOS = {("anaheim", "major")}

CONGESTION_THRESHOLD = 0.9

@lru_cache(maxsize=3)
def load_traffic_data(city: str) -> dict:
  city_dir = TRAFFIC_DIR / TRAFFIC_DIRS[city]

  with open(city_dir / "data_0.pickle", "rb") as f:
    data = pickle.load(f)

  coords = {}
  with open(city_dir / "modified_coord.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
      coords[int(row["id"])] = (float(row["lat"]), float(row["lon"]))

  return {"data": data, "coords": coords}

@lru_cache(maxsize=8)
def load_traffic_scenario_data(city: str, severity: str) -> dict:
  if severity == "baseline":
    return load_traffic_data(city)["data"]

  scenario_dir = TRAFFIC_DIR / "sta_dataset" / f"data_{TRAFFIC_SCENARIO_CITIES[city]}_{severity}_00"
  with open(scenario_dir / f"data_{TRAFFIC_SCENARIO_SAMPLES[city]}.pickle", "rb") as f:
    return pickle.load(f)

@lru_cache(maxsize=8)
def load_traffic_network(city: str, severity: str) -> dict:
  data = load_traffic_scenario_data(city, severity)
  coords = load_traffic_data(city)["coords"]

  pairs = {}
  for (u, v), ratio in data["ratio"].items():
    key = tuple(sorted((u, v)))
    direction = {
      "from": u + 1,
      "to": v + 1,
      "flow": round(float(data["flow"][(u, v)]), 4),
      "capacity": round(float(data["capacity"][(u, v)]), 4),
      "ratio": round(float(ratio), 4),
      "t0": round(float(data["t0"][(u, v)]), 4),
    }
    if key not in pairs:
      pairs[key] = {"source": key[0] + 1, "target": key[1] + 1, "ratio": 0.0, "directions": []}
    pairs[key]["directions"].append(direction)
    pairs[key]["ratio"] = max(pairs[key]["ratio"], direction["ratio"])

  links = list(pairs.values())
  nodes = [{"id": node_id, "lat": lat, "lon": lon} for node_id, (lat, lon) in sorted(coords.items())]

  return {
    "city": city,
    "severity": severity,
    "n_node": len(nodes),
    "n_link": len(links),
    "n_directed_link": len(data["ratio"]),
    "total_demand": round(float(data["demand_matrix"].sum()), 2),
    "total_time": round(float(data["T"]), 2),
    "congested": sum(1 for link in links if link["ratio"] > CONGESTION_THRESHOLD),
    "max_ratio": round(max(link["ratio"] for link in links), 4),
    "nodes": nodes,
    "links": links,
  }

@app.get("/api/traffic/{city}")
async def fetch_traffic(city: TrafficCity):
  return load_traffic_network(city, "baseline")

@app.get("/api/traffic/{city}/scenario/{severity}")
async def fetch_traffic_scenario(city: TrafficCity, severity: TrafficSeverity):
  if (city, severity) in TRAFFIC_MISSING_SCENARIOS:
    raise HTTPException(status_code=404, detail="No scenario data for this city and severity")
  return load_traffic_network(city, severity)

@app.get("/api/traffic/{city}/demand/{node_id}")
async def fetch_traffic_demand(city: TrafficCity, node_id: int):
  data = load_traffic_data(city)["data"]
  matrix = data["demand_matrix"]
  n = matrix.shape[0]
  if node_id < 1 or node_id > n:
    raise HTTPException(status_code=404, detail="Unknown node")

  row = matrix[node_id - 1]
  destinations = [
    {"node": j + 1, "demand": round(float(d), 2)}
    for j, d in enumerate(row)
    if d > 0 and j != node_id - 1
  ]

  return {
    "city": city,
    "origin": node_id,
    "total": round(float(sum(entry["demand"] for entry in destinations)), 2),
    "max": round(float(max((entry["demand"] for entry in destinations), default=0)), 2),
    "destinations": destinations,
  }

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
