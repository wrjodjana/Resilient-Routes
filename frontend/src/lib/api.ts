import { GraphResponse, GraphSize, TrafficCity, TrafficDemandResponse, TrafficNetworkResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchGraph(size: GraphSize): Promise<GraphResponse> {
  const resp = await fetch(`${API_URL}/api/graph/${size}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${size} graph: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTrafficNetwork(city: TrafficCity): Promise<TrafficNetworkResponse> {
  const resp = await fetch(`${API_URL}/api/traffic/${city}`);
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
