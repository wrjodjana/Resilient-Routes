import {
  EarthquakeType,
  GraphResponse,
  GraphSize,
  TrafficCity,
  TrafficDemandResponse,
  TrafficNetworkResponse,
  TrafficSeverity,
  TrainingJobResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchGraph(size: GraphSize): Promise<GraphResponse> {
  const resp = await fetch(`${API_URL}/api/graph/${size}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${size} graph: ${resp.status}`);
  }
  return resp.json();
}

export async function startTraining(size: GraphSize, targetNodeId: number, earthquakeType: EarthquakeType): Promise<TrainingJobResponse> {
  const resp = await fetch(`${API_URL}/api/seismic/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ size, target_node_id: targetNodeId, earthquake_type: earthquakeType }),
  });
  if (!resp.ok) {
    const body: { detail?: string } | null = await resp.json().catch(() => null);
    throw new Error(body?.detail ?? `Failed to start training: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTrainingJob(jobId: string): Promise<TrainingJobResponse> {
  const resp = await fetch(`${API_URL}/api/seismic/train/${jobId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch training job: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTrafficNetwork(city: TrafficCity, severity: TrafficSeverity): Promise<TrafficNetworkResponse> {
  const resp = await fetch(`${API_URL}/api/traffic/${city}/scenario/${severity}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${city} network: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTrafficDemand(city: TrafficCity, nodeId: number): Promise<TrafficDemandResponse> {
  const resp = await fetch(`${API_URL}/api/traffic/${city}/demand/${nodeId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch demand for node ${nodeId}: ${resp.status}`);
  }
  return resp.json();
}
