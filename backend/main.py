import csv
import os
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    FRONTEND_URL,
    *ALLOWED_ORIGINS
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

DATASETS_DIR = Path(__file__).parent / "datasets"

GraphSize = Literal["small", "middle", "large"]

TARGET_NODE_ID = 17

@lru_cache(maxsize=3)
def load_graph(size: str) -> dict:
  graph_dir = DATASETS_DIR / f"connectivity_graph_{size}"

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

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
