export type GraphSize = "small" | "middle" | "large";

export interface GraphNode {
  id: number;
  lat: number;
  lon: number;
  value: number;
  is_target: boolean;
}

export interface GraphEdge {
  source: number;
  target: number;
}

export interface GraphResponse {
  size: GraphSize;
  n_node: number;
  n_bridge: number;
  n_road: number;
  n_edge: number;
  threshold: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}
