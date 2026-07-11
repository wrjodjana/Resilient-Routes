import type { Map as LeafletMap, LayerGroup, default as Leaflet } from "leaflet";
import { GraphResponse } from "./types";

type LeafletModule = typeof Leaflet;

const EDGE_COLOR = "rgba(71, 85, 105, 0.35)";
const DEST_COLOR = "#4f46e5";

// Reliability risk ramp, anchored at the model's risk threshold.
// Below the threshold a node is likely cut off from the destination (warm);
// at/above it holds (teal). red -> amber -> teal.
const RISK_LOW = [220, 38, 38]; // #dc2626 — likely cut off
const RISK_MID = [245, 158, 11]; // #f59e0b — borderline (at threshold)
const RISK_HIGH = [13, 148, 136]; // #0d9488 — reliably connected

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

// Map a reliability value to the risk ramp. The threshold sits at the amber
// pivot: warmer below it (at risk), cooler above it (resilient).
export function valueToColor(value: number, threshold = 0.75): string {
  const v = Math.min(1, Math.max(0, value));
  const t = Math.min(1, Math.max(0.01, threshold));
  if (v < t) return mix(RISK_LOW, RISK_MID, v / t);
  return mix(RISK_MID, RISK_HIGH, (v - t) / (1 - t));
}

// Synchronous once Leaflet is loaded: the caller passes L so there is no `await`
// between the "already initialized?" guard and L.map(), which is what lets React's
// double-invoked effect (StrictMode / Fast Refresh) init the same container twice.
export function initMap(L: LeafletModule, container: HTMLElement): LeafletMap | null {
  // Container still owns a Leaflet instance from a prior mount — bail rather than
  // throw "Map container is already initialized".
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
      // Destination beacon: a faint outer ring behind a solid indigo core so it
      // reads as "the goal" without colliding with the red = at-risk ramp.
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
