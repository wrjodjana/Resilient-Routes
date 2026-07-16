import type { Map as LeafletMap, LayerGroup, default as Leaflet } from "leaflet";
import {
  GraphResponse,
  TrafficDemandResponse,
  TrafficMetric,
  TrafficNetworkResponse,
  TrainingDisplay,
  TrainingResult,
} from "./types";

type LeafletModule = typeof Leaflet;

const EDGE_COLOR = "rgba(71, 85, 105, 0.35)";
const DEST_COLOR = "#4f46e5";
const SELECT_COLOR = "#0d9488";

const RISK_LOW = [220, 38, 38];
const RISK_MID = [245, 158, 11];
const RISK_HIGH = [13, 148, 136];

export const getLeaflet = async () => {
  if (typeof window === "undefined") {
    return null;
  }
  return (await import("leaflet")).default;
};

function mix(a: number[], b: number[], t: number): string {
  const r = Math.round(a[0] + (b[0] - a[0]) * t);
  const g = Math.round(a[1] + (b[1] - a[1]) * t);
  const bl = Math.round(a[2] + (b[2] - a[2]) * t);
  return `rgb(${r}, ${g}, ${bl})`;
}

export function valueToColor(value: number, threshold = 0.75): string {
  const v = Math.min(1, Math.max(0, value));
  const t = Math.min(1, Math.max(0.01, threshold));
  if (v < t) return mix(RISK_LOW, RISK_MID, v / t);
  return mix(RISK_MID, RISK_HIGH, (v - t) / (1 - t));
}

export function initMap(L: LeafletModule, container: HTMLElement): LeafletMap | null {
  if ((container as unknown as { _leaflet_id?: number })._leaflet_id != null) return null;

  const map = L.map(container, { center: [37.4, -122.03], zoom: 12, zoomControl: false });
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    subdomains: "abcd",
    maxZoom: 20,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  }).addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);

  return map;
}

export async function renderGraph(map: LeafletMap, layerGroup: LayerGroup, graph: GraphResponse) {
  const L = await getLeaflet();
  if (!L) return;

  layerGroup.clearLayers();

  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));

  for (const edge of graph.edges) {
    const source = nodeById.get(edge.source);
    const target = nodeById.get(edge.target);
    if (!source || !target) continue;

    L.polyline(
      [
        [source.lat, source.lon],
        [target.lat, target.lon],
      ],
      { color: EDGE_COLOR, weight: 1.5, opacity: 0.9 }
    ).addTo(layerGroup);
  }

  for (const node of graph.nodes) {
    if (node.is_target) {
      L.circleMarker([node.lat, node.lon], {
        radius: 13,
        color: DEST_COLOR,
        weight: 1.5,
        opacity: 0.45,
        fill: false,
      }).addTo(layerGroup);
    }

    const atRisk = !node.is_target && node.value < graph.threshold;
    const marker = L.circleMarker([node.lat, node.lon], {
      radius: node.is_target ? 8 : 6,
      color: "#ffffff",
      weight: node.is_target ? 2.5 : 1.5,
      fillColor: node.is_target ? DEST_COLOR : valueToColor(node.value, graph.threshold),
      fillOpacity: 0.95,
    }).addTo(layerGroup);

    marker.bindPopup(
      `<b>${node.is_target ? "Critical destination" : `Node ${node.id}`}</b><br/>` +
        (node.is_target
          ? ""
          : `Reliability: <b>${node.value.toFixed(3)}</b> ${atRisk ? "· likely cut off" : "· stays connected"}<br/>`) +
        `Lat ${node.lat.toFixed(5)}, Lon ${node.lon.toFixed(5)}`
    );
  }

  const bounds = L.latLngBounds(graph.nodes.map((node) => [node.lat, node.lon]));
  map.fitBounds(bounds, { padding: [30, 30] });
}

export function failureToColor(p: number): string {
  const v = Math.min(1, Math.max(0, p));
  if (v < 0.5) return mix(RISK_HIGH, RISK_MID, v / 0.5);
  return mix(RISK_MID, RISK_LOW, (v - 0.5) / 0.5);
}

export async function renderTrainingSelection(
  map: LeafletMap,
  layerGroup: LayerGroup,
  graph: GraphResponse,
  onNodeClick: (id: number) => void,
  selectedId: number | null
) {
  const L = await getLeaflet();
  if (!L) return;

  layerGroup.clearLayers();

  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));

  for (const edge of graph.edges) {
    const source = nodeById.get(edge.source);
    const target = nodeById.get(edge.target);
    if (!source || !target) continue;

    L.polyline(
      [
        [source.lat, source.lon],
        [target.lat, target.lon],
      ],
      { color: EDGE_COLOR, weight: 1.5, opacity: 0.9 }
    ).addTo(layerGroup);
  }

  for (const node of graph.nodes) {
    if (node.id === selectedId) {
      L.circleMarker([node.lat, node.lon], {
        radius: 12,
        color: SELECT_COLOR,
        weight: 2.5,
        opacity: 0.85,
        fill: false,
        dashArray: "4 3",
      }).addTo(layerGroup);
    }

    const marker = L.circleMarker([node.lat, node.lon], {
      radius: node.id === selectedId ? 6.5 : 5.5,
      color: "#ffffff",
      weight: 1.5,
      fillColor: node.id === selectedId ? SELECT_COLOR : "#64748b",
      fillOpacity: 0.9,
    }).addTo(layerGroup);

    marker.bindTooltip(
      node.id === selectedId ? `Node ${node.id} · destination` : `Node ${node.id} · click to set destination`
    );
    marker.on("click", () => onNodeClick(node.id));
  }

  const bounds = L.latLngBounds(graph.nodes.map((node) => [node.lat, node.lon]));
  map.fitBounds(bounds, { padding: [30, 30] });
}

export async function renderTrainingResult(
  map: LeafletMap,
  layerGroup: LayerGroup,
  result: TrainingResult,
  display: TrainingDisplay
) {
  const L = await getLeaflet();
  if (!L) return;

  layerGroup.clearLayers();

  const showNodes = display !== "links";
  const showLinks = display !== "nodes";

  const nodeById = new Map(result.nodes.map((node) => [node.id, node]));

  for (const edge of result.edges) {
    const source = nodeById.get(edge.source);
    const target = nodeById.get(edge.target);
    if (!source || !target) continue;

    const line = L.polyline(
      [
        [source.lat, source.lon],
        [target.lat, target.lon],
      ],
      showLinks
        ? { color: failureToColor(edge.failure), weight: 2 + 2.5 * edge.failure, opacity: 0.9 }
        : { color: EDGE_COLOR, weight: 1.5, opacity: 0.9 }
    ).addTo(layerGroup);

    line.bindPopup(
      `<b>Link ${edge.source} – ${edge.target}</b><br/>Failure probability: <b>${edge.failure.toFixed(3)}</b>`
    );
  }

  for (const node of result.nodes) {
    if (node.is_target) {
      L.circleMarker([node.lat, node.lon], {
        radius: 13,
        color: SELECT_COLOR,
        weight: 1.5,
        opacity: 0.55,
        fill: false,
      }).addTo(layerGroup);
    }

    const marker = L.circleMarker([node.lat, node.lon], {
      radius: node.is_target ? 8 : showNodes ? 6 : 3.5,
      color: "#ffffff",
      weight: node.is_target ? 2.5 : 1.5,
      fillColor: node.is_target
        ? SELECT_COLOR
        : showNodes
          ? valueToColor(node.predicted, result.threshold)
          : "#94a3b8",
      fillOpacity: 0.95,
    }).addTo(layerGroup);

    marker.bindPopup(
      `<b>${node.is_target ? "Trained destination" : `Node ${node.id}`}</b><br/>` +
        (node.is_target
          ? ""
          : `Predicted connectivity: <b>${node.predicted.toFixed(3)}</b><br/>` +
            `Simulated connectivity: <b>${node.actual.toFixed(3)}</b><br/>` +
            `Error: <b>${Math.abs(node.predicted - node.actual).toFixed(3)}</b><br/>`) +
        `Lat ${node.lat.toFixed(5)}, Lon ${node.lon.toFixed(5)}`
    );
  }

  const bounds = L.latLngBounds(result.nodes.map((node) => [node.lat, node.lon]));
  map.fitBounds(bounds, { padding: [30, 30] });
}

export function ratioToColor(ratio: number): string {
  const r = Math.min(1.2, Math.max(0, ratio));
  if (r < 0.9) return mix(RISK_HIGH, RISK_MID, r / 0.9);
  return mix(RISK_MID, RISK_LOW, (r - 0.9) / 0.3);
}

const SCALE_LOW = [153, 246, 228];
const SCALE_HIGH = [17, 94, 89];

export function magnitudeToColor(t: number): string {
  return mix(SCALE_LOW, SCALE_HIGH, Math.min(1, Math.max(0, t)));
}

function linkMetricValue(directions: { flow: number; capacity: number }[], metric: TrafficMetric): number {
  return Math.max(...directions.map((d) => (metric === "flow" ? d.flow : d.capacity)));
}

export async function renderTrafficNetwork(
  map: LeafletMap,
  layerGroup: LayerGroup,
  network: TrafficNetworkResponse,
  metric: TrafficMetric,
  onNodeClick: (id: number) => void,
  fit: boolean
) {
  const L = await getLeaflet();
  if (!L) return;

  layerGroup.clearLayers();

  const nodeById = new Map(network.nodes.map((node) => [node.id, node]));

  const metricMax =
    metric === "ratio" ? 0 : Math.max(...network.links.map((link) => linkMetricValue(link.directions, metric)));

  for (const link of network.links) {
    const source = nodeById.get(link.source);
    const target = nodeById.get(link.target);
    if (!source || !target) continue;

    const t = metric === "ratio" ? 0 : metricMax > 0 ? linkMetricValue(link.directions, metric) / metricMax : 0;

    const line = L.polyline(
      [
        [source.lat, source.lon],
        [target.lat, target.lon],
      ],
      metric === "ratio"
        ? { color: ratioToColor(link.ratio), weight: 3, opacity: 0.85 }
        : { color: magnitudeToColor(t), weight: 1.5 + 3.5 * t, opacity: 0.85 }
    ).addTo(layerGroup);

    line.bindPopup(
      link.directions
        .map((d) => {
          if (metric === "ratio") return `<b>Node ${d.from} → ${d.to}</b><br/>V/C ratio <b>${d.ratio.toFixed(2)}</b>`;
          if (metric === "flow") return `<b>Node ${d.from} → ${d.to}</b><br/>Flow <b>${Math.round(d.flow).toLocaleString()}</b>`;
          return `<b>Node ${d.from} → ${d.to}</b><br/>Capacity <b>${Math.round(d.capacity).toLocaleString()}</b>`;
        })
        .join("<br/><br/>")
    );
  }

  for (const node of network.nodes) {
    const marker = L.circleMarker([node.lat, node.lon], {
      radius: 3.5,
      color: "#ffffff",
      weight: 1,
      fillColor: "#64748b",
      fillOpacity: 0.9,
    }).addTo(layerGroup);
    marker.bindTooltip(`Node ${node.id}`);
    marker.on("click", () => onNodeClick(node.id));
  }

  if (fit) {
    const bounds = L.latLngBounds(network.nodes.map((node) => [node.lat, node.lon]));
    map.fitBounds(bounds, { padding: [30, 30] });
  }
}

export async function renderTrafficDemand(
  map: LeafletMap,
  layerGroup: LayerGroup,
  network: TrafficNetworkResponse,
  demand: TrafficDemandResponse | null,
  onNodeClick: (id: number) => void,
  fit: boolean
) {
  const L = await getLeaflet();
  if (!L) return;

  layerGroup.clearLayers();

  if (fit) {
    const bounds = L.latLngBounds(network.nodes.map((node) => [node.lat, node.lon]));
    map.fitBounds(bounds, { padding: [30, 30] });
  }

  const nodeById = new Map(network.nodes.map((node) => [node.id, node]));

  for (const link of network.links) {
    const source = nodeById.get(link.source);
    const target = nodeById.get(link.target);
    if (!source || !target) continue;

    L.polyline(
      [
        [source.lat, source.lon],
        [target.lat, target.lon],
      ],
      { color: EDGE_COLOR, weight: 1.5, opacity: 0.9 }
    ).addTo(layerGroup);
  }

  const demandByNode = new Map(demand?.destinations.map((d) => [d.node, d.demand]) ?? []);

  for (const node of network.nodes) {
    if (demand && node.id === demand.origin) continue;

    const trips = demandByNode.get(node.id) ?? 0;
    const hasDemand = demand !== null && trips > 0 && demand.max > 0;

    const marker = L.circleMarker([node.lat, node.lon], {
      radius: demand === null ? 5 : hasDemand ? 3 + 13 * Math.sqrt(trips / demand.max) : 2.5,
      color: hasDemand || demand === null ? "#ffffff" : "#94a3b8",
      weight: hasDemand || demand === null ? 1.5 : 1,
      fillColor: demand === null ? "#64748b" : "#0d9488",
      fillOpacity: demand === null ? 0.9 : hasDemand ? 0.55 : 0,
    }).addTo(layerGroup);

    marker.bindTooltip(
      demand === null
        ? `Node ${node.id} · click to set origin`
        : hasDemand
          ? `Node ${node.id} · ${Math.round(trips).toLocaleString()} trips from Node ${demand.origin}`
          : `Node ${node.id} · no demand`
    );
    marker.on("click", () => onNodeClick(node.id));
  }

  if (demand) {
    const origin = nodeById.get(demand.origin);
    if (origin) {
      L.circleMarker([origin.lat, origin.lon], {
        radius: 13,
        color: DEST_COLOR,
        weight: 1.5,
        opacity: 0.45,
        fill: false,
      }).addTo(layerGroup);

      const originMarker = L.circleMarker([origin.lat, origin.lon], {
        radius: 8,
        color: "#ffffff",
        weight: 2.5,
        fillColor: DEST_COLOR,
        fillOpacity: 0.95,
      }).addTo(layerGroup);
      originMarker.bindTooltip(`Origin · Node ${demand.origin}`);
    }
  }
}
