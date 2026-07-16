import csv
import importlib.util
import pickle
import threading
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

import dgl
import torch
import torch.nn.functional as F
from torch.optim.lr_scheduler import MultiStepLR
from torch.utils.data import DataLoader, random_split

SEISMIC_DIR = Path(__file__).parent / "seismic"

EarthquakeType = Literal["minor", "moderate", "major"]
GraphSize = Literal["small", "middle", "large"]

SIZE_CONFIG: dict[str, dict] = {
  "small": {
    "dir": SEISMIC_DIR / "connectivity_gnn_small",
    "modelzoo": "modelzoo_rev.py",
    "suffix": "v2",
    "seed": 234,
  },
  "middle": {
    "dir": SEISMIC_DIR / "connectivity_gnn_middle",
    "modelzoo": "modelzoo_v3_rev.py",
    "suffix": "v3",
    "seed": 42,
  },
  "large": {
    "dir": SEISMIC_DIR / "connectivity_gnn_large",
    "modelzoo": "modelzoo_v4_rev.py",
    "suffix": "v4",
    "seed": 42,
  },
}

N_NODES = {"small": 39, "middle": 84, "large": 103}

NUM_SAMPLES = 100
NUM_EPOCHS = 200
BATCH_SIZE = 512
LEARNING_RATE = 0.001
HIDDEN_SIZE = 512
REG_NUM = 1
CLA_NUM = 2

device = "cuda:0" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=3)
def load_model_class(size: str):
  config = SIZE_CONFIG[size]
  path = config["dir"] / config["modelzoo"]
  spec = importlib.util.spec_from_file_location(f"modelzoo_{size}", path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module.GraphSageConv_xn_only


@dataclass
class TrainingJob:
  job_id: str
  size: str
  target_node_id: int
  earthquake_type: str
  status: str = "running"
  epoch: int = 0
  total_epochs: int = NUM_EPOCHS
  train_loss: list[float] = field(default_factory=list)
  test_loss: list[float] = field(default_factory=list)
  result: dict | None = None
  error: str | None = None

  def to_dict(self) -> dict:
    return {
      "job_id": self.job_id,
      "status": self.status,
      "size": self.size,
      "target_node_id": self.target_node_id,
      "earthquake_type": self.earthquake_type,
      "epoch": self.epoch,
      "total_epochs": self.total_epochs,
      "train_loss": self.train_loss,
      "test_loss": self.test_loss,
      "result": self.result,
      "error": self.error,
    }


JOBS: dict[str, TrainingJob] = {}
JOBS_LOCK = threading.Lock()


def build_graph(graph_data: dict, n_node: int) -> dgl.DGLGraph:
  node_1 = torch.tensor(graph_data["edge_order"][:, 0].squeeze(), dtype=torch.int32)
  node_2 = torch.tensor(graph_data["edge_order"][:, 1].squeeze(), dtype=torch.int32)
  edge_feat_half = torch.tensor(graph_data["edge_feat"], dtype=torch.float32)
  edge_feat = torch.cat((edge_feat_half, edge_feat_half), axis=0)
  src = torch.cat((node_1, node_2))
  dst = torch.cat((node_2, node_1))

  g = dgl.graph((src, dst), num_nodes=n_node)
  g.ndata["feat"] = torch.tensor(graph_data["node_feat"], dtype=torch.float32)
  g.ndata["label"] = torch.tensor(graph_data["node_res"], dtype=torch.float32)
  g.edata["feat"] = edge_feat
  return g.to(device)


def collate(samples: list) -> tuple:
  reg_list = [g.ndata["label"] for g in samples]
  batched_graph = dgl.batch(samples)
  return batched_graph, torch.vstack((*reg_list,))


@lru_cache(maxsize=3)
def load_coords(size: str) -> dict[int, tuple[float, float]]:
  coords = {}
  with open(SIZE_CONFIG[size]["dir"] / "map.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
      coords[int(row["id"])] = (float(row["lat"]), float(row["lon"]))
  return coords


def run_training(job: TrainingJob) -> None:
  config = SIZE_CONFIG[job.size]
  torch.manual_seed(config["seed"])
  data_dir = config["dir"] / "data" / f"data_{job.target_node_id}_{config['suffix']}"

  with open(data_dir / "graph_info.pickle", "rb") as f:
    graph_info = pickle.load(f)
  n_node = graph_info["n_node"]

  with open(data_dir / "all_result.pickle", "rb") as f:
    all_result = pickle.load(f)

  graphs = [build_graph(all_result[i], n_node) for i in range(NUM_SAMPLES)]

  train_batch, test_batch = random_split(
    graphs, [int(NUM_SAMPLES * 0.75), int(NUM_SAMPLES * 0.25)]
  )
  train_loader = DataLoader(train_batch, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate)
  test_loader = DataLoader(test_batch, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate)

  n_feat = graphs[0].ndata["feat"].shape[1]
  model_class = load_model_class(job.size)
  model = model_class(n_feat, HIDDEN_SIZE, REG_NUM, CLA_NUM).to(device)

  optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
  scheduler = MultiStepLR(optimizer, milestones=[200], gamma=0.2)

  for e in range(NUM_EPOCHS):
    err_train = []
    err_test = []

    model.train()
    for g, reg_label in train_loader:
      reg_logits = model(g, g.ndata["feat"], g.edata["feat"])
      loss = F.l1_loss(reg_logits, reg_label)
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      err_train.append(loss.cpu().detach().numpy().item())
    scheduler.step()

    model.eval()
    with torch.no_grad():
      for g, reg_label in test_loader:
        reg_logits = model(g, g.ndata["feat"], g.edata["feat"])
        loss = F.l1_loss(reg_logits, reg_label)
        err_test.append(loss.cpu().detach().numpy().item())

    job.train_loss.append(round(sum(err_train) / len(err_train), 4))
    job.test_loss.append(round(sum(err_test) / len(err_test), 4))
    job.epoch = e + 1

  with open(data_dir / "all_result_lite.pickle", "rb") as f:
    lite = pickle.load(f)
  scenario = lite[job.earthquake_type]
  eval_graph = build_graph(scenario, n_node)

  model.eval()
  with torch.no_grad():
    reg_logits = model(eval_graph, eval_graph.ndata["feat"], eval_graph.edata["feat"])

  predictions = reg_logits.cpu().numpy().ravel()
  actuals = scenario["node_res"].ravel()
  mae = float(abs(predictions - actuals).mean())
  threshold = float(scenario["node_thre"][0])
  coords = load_coords(job.size)

  nodes = []
  for node_id in range(n_node):
    lat, lon = coords[node_id]
    nodes.append({
      "id": node_id,
      "lat": lat,
      "lon": lon,
      "predicted": round(float(predictions[node_id]), 4),
      "actual": round(float(actuals[node_id]), 4),
      "is_target": node_id == job.target_node_id,
    })

  edge_order = scenario["edge_order"]
  edge_feat = scenario["edge_feat"].ravel()
  edges = [
    {
      "source": int(edge_order[i, 0]),
      "target": int(edge_order[i, 1]),
      "failure": round(float(edge_feat[i]), 4),
    }
    for i in range(edge_order.shape[0])
  ]

  job.result = {"mae": round(mae, 4), "threshold": threshold, "nodes": nodes, "edges": edges}


def _run(job: TrainingJob) -> None:
  try:
    run_training(job)
    job.status = "completed"
  except Exception as exc:
    job.status = "failed"
    job.error = str(exc)


def start_job(size: str, target_node_id: int, earthquake_type: str) -> TrainingJob | None:
  with JOBS_LOCK:
    if any(job.status == "running" for job in JOBS.values()):
      return None
    job = TrainingJob(uuid.uuid4().hex[:12], size, target_node_id, earthquake_type)
    JOBS[job.job_id] = job
  threading.Thread(target=_run, args=(job,), daemon=True).start()
  return job


def get_job(job_id: str) -> TrainingJob | None:
  return JOBS.get(job_id)
