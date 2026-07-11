import { GraphResponse, GraphSize } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchGraph(size: GraphSize): Promise<GraphResponse> {
  const resp = await fetch(`${API_URL}/api/graph/${size}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${size} graph: ${resp.status}`);
  }
  return resp.json();
}
