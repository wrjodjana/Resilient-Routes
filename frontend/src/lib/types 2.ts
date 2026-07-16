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

export type EarthquakeType = "minor" | "moderate" | "major";

export type TrainingStatus = "running" | "completed" | "failed";

export interface TrainingNode {
  id: number;
  lat: number;
  lon: number;
  predicted: number;
  actual: number;
  is_target: boolean;
}

export interface TrainingResult {
  mae: number;
  threshold: number;
  nodes: TrainingNode[];
}

export interface TrainingJobResponse {
  job_id: string;
  status: TrainingStatus;
  target_node_id: number;
  earthquake_type: EarthquakeType;
  epoch: number;
  total_epochs: number;
  train_loss: number[];
  test_loss: number[];
  result: TrainingResult | null;
  error: string | null;
}

export type TrafficCity = "anaheim" | "siouxfalls";

export type TrafficMode = "network" | "od";

export type TrafficMetric = "ratio" | "flow" | "capacity";

export interface TrafficNode {
  id: number;
  lat: number;
  lon: number;
}

export interface TrafficLinkDirection {
  from: number;
  to: number;
  flow: number;
  capacity: number;
  ratio: number;
  t0: number;
}

export interface TrafficLink {
  source: number;
  target: number;
  ratio: number;
  directions: TrafficLinkDirection[];
}

export interface TrafficNetworkResponse {
  city: TrafficCity;
  n_node: number;
  n_link: number;
  n_directed_link: number;
  total_demand: number;
  total_time: number;
  congested: number;
  max_ratio: number;
  nodes: TrafficNode[];
  links: TrafficLink[];
}

export interface TrafficDemandEntry {
  node: number;
  demand: number;
}

export interface TrafficDemandResponse {
  city: TrafficCity;
  origin: number;
  total: number;
  max: number;
  destinations: TrafficDemandEntry[];
}
