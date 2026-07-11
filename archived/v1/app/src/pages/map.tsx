import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Popup, Polyline, CircleMarker, Rectangle, useMap, Marker, Tooltip, ScaleControl, ZoomControl } from "react-leaflet";
import { Sidebar } from "../components/sidebar.tsx";
import { BoundingBox, VisualizationFilter } from "../types/sidebar.ts";
import "leaflet/dist/leaflet.css";
import { NetworkNode, NetworkWay, BridgeData } from "../types/map.ts";
import { API_URL } from "../config.ts";
import "leaflet-draw/dist/leaflet.draw.css";
import * as L from "leaflet";
import "leaflet-draw";
import axios from "axios";

const BoundsUpdater = ({ boundingBox }: { boundingBox: BoundingBox | null }) => {
  const map = useMap();

  useEffect(() => {
    if (boundingBox) {
      const bounds = [
        [boundingBox.southWest.lat, boundingBox.southWest.lng],
        [boundingBox.northEast.lat, boundingBox.northEast.lng],
      ] as L.LatLngBoundsLiteral;
      map.fitBounds(bounds);
    }
  }, [boundingBox, map]);

  return null;
};

const DrawControl = ({ setBoundingBox }: { setBoundingBox: (box: BoundingBox | null) => void }) => {
  const map = useMap();

  useEffect(() => {
    (window as any).leafletMap = map;

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
      draw: {
        polyline: false,
        polygon: false,
        circle: false,
        circlemarker: false,
        marker: false,
        rectangle: {
          shapeOptions: {
            color: "black",
            weight: 1,
            fillOpacity: 0,
          },
        },
      },
      edit: {
        featureGroup: drawnItems,
        remove: true,
      },
    });

    (window as any).drawControl = drawControl;
    (window as any).drawnItems = drawnItems;

    map.on(L.Draw.Event.CREATED, (e: any) => {
      const layer = e.layer;
      drawnItems.addLayer(layer);

      const bounds = layer.getBounds();
      setBoundingBox({
        southWest: {
          lat: bounds.getSouth(),
          lng: bounds.getWest(),
        },
        northEast: {
          lat: bounds.getNorth(),
          lng: bounds.getEast(),
        },
      });
    });

    map.on(L.Draw.Event.DELETED, () => {
      setBoundingBox(null);
    });

    return () => {
      map.removeLayer(drawnItems);
      delete (window as any).drawControl;
      delete (window as any).drawnItems;
      delete (window as any).leafletMap;
    };
  }, [map, setBoundingBox]);

  return null;
};

const MapLegend = ({ visualizationFilter }: { visualizationFilter: VisualizationFilter }) => {
  // Only show legend for network-related views
  if (visualizationFilter.viewMode === "bridges-only") {
    return (
      <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg z-[1000] max-w-xs">
        <h3 className="font-bold text-sm mb-2">Bridge Damage Probability</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#dc2626] border border-gray-300" />
            <span className="text-sm">High Risk (&gt;75%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#f59e0b] border border-gray-300" />
            <span className="text-sm">Medium Risk (25-75%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-[#059669] border border-gray-300" />
            <span className="text-sm">Low Risk (&lt;25%)</span>
          </div>
        </div>
      </div>
    );
  }

  const roadColors = {
    motorway: "#d73027",
    trunk: "#fc8d59",
    primary: "#fee090",
    secondary: "#91bfdb",
    tertiary: "#4575b4",
    residential: "#999999",
    unclassified: "#666666",
  };

  return (
    <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg z-[1000] max-w-xs">
      <h3 className="font-bold text-sm mb-2">Road Types</h3>
      <div className="space-y-2">
        {Object.entries(roadColors).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{
                backgroundColor: visualizationFilter.isMonochrome ? "#000000" : color,
                border: "1px solid #ccc",
              }}
            />
            <span className="text-sm capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const BaseMap = () => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [boundingBox, setBoundingBox] = useState<BoundingBox | null>(null);
  const [networkNodes, setNetworkNodes] = useState<NetworkNode[]>([]);
  const [networkWays, setNetworkWays] = useState<NetworkWay[]>([]);
  const [metaNetwork, setMetaNetwork] = useState<{ nodes: { id: number; lat: number; lon: number }[]; edges: { source: number; target: number }[] }>({ nodes: [], edges: [] });
  const [visualizationFilter, setVisualizationFilter] = useState<VisualizationFilter>({
    showWays: true,
    isMonochrome: false,
    roadTypes: {
      motorway: true,
      trunk: true,
      primary: true,
      secondary: true,
      tertiary: true,
      residential: true,
      unclassified: true,
    },
    viewMode: null,
  });
  const [bridgeData, setBridgeData] = useState<BridgeData | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleReset = () => {
    setError("");
    setBoundingBox(null);
    setBridgeData(null);
    setNetworkNodes([]);
    setNetworkWays([]);

    const drawnItems = (window as any).drawnItems;
    if (drawnItems) {
      drawnItems.clearLayers();
    }

    const map = (window as any).leafletMap;
    if (map) {
      map.eachLayer((layer: any) => {
        if (layer instanceof L.Rectangle) {
          map.removeLayer(layer);
        }
      });
      map.setView([40.7128, -74.006], 12);
    }
  };

  const getBridgeColor = (probability: number) => {
    if (probability > 0.75) return "#dc2626"; // red-600
    if (probability > 0.25) return "#f59e0b"; // amber-500
    return "#059669"; // emerald-600
  };

  return (
    <div className="flex h-screen">
      {error && <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-[1000]">{error}</div>}
      {isLoading && <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded z-[1000]">Loading...</div>}
      <div className={`${isSidebarCollapsed ? "w-full" : "w-3/4"} h-full relative transition-all duration-300`}>
        <MapContainer center={[40.7128, -74.006]} zoom={12} className="h-full w-full">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <ScaleControl position="bottomleft" />
          <ZoomControl position="topright" />

          <DrawControl setBoundingBox={setBoundingBox} />
          <BoundsUpdater boundingBox={boundingBox} />

          {boundingBox && (
            <Rectangle
              bounds={[
                [boundingBox.southWest.lat, boundingBox.southWest.lng],
                [boundingBox.northEast.lat, boundingBox.northEast.lng],
              ]}
              pathOptions={{
                color: "black",
                weight: 1,
                fillColor: "transparent",
                fillOpacity: 0,
              }}
            />
          )}
          {(visualizationFilter.viewMode === "network-only" || visualizationFilter.viewMode === "network-and-bridges") &&
            networkWays.map((way) => {
              if (!visualizationFilter.showWays) return null;
              if (!way.tags?.highway) return null;
              if (!visualizationFilter.roadTypes[way.tags.highway as keyof typeof visualizationFilter.roadTypes]) return null;

              const wayPoints = way.nodes
                .map((nodeId) => {
                  const node = networkNodes.find((n) => n.id === nodeId);
                  return node ? [node.lat, node.lon] : null;
                })
                .filter((point) => point !== null);

              const roadColors = {
                motorway: "#d73027",
                trunk: "#fc8d59",
                primary: "#fee090",
                secondary: "#91bfdb",
                tertiary: "#4575b4",
                residential: "#999999",
                unclassified: "#666666",
              };

              const roadColor = visualizationFilter.isMonochrome ? "#000000" : roadColors[way.tags.highway as keyof typeof roadColors] || "#FF4B4B";

              return (
                <Polyline key={way.id} positions={wayPoints as [number, number][]} color={roadColor} weight={4} opacity={1}>
                  <Popup>
                    Link ID: {way.id}
                    <br />
                    Type: {way.tags?.highway}
                    <br />
                    Name: {way.tags?.name || "Unnamed"}
                  </Popup>
                </Polyline>
              );
            })}
          {visualizationFilter.viewMode === "network-only" && metaNetwork.nodes.length > 0 && (
            <>
              {metaNetwork.nodes.map((node) => (
                <CircleMarker
                  key={node.id}
                  center={[node.lat, node.lon]}
                  radius={8}
                  pathOptions={{
                    color: "#FF0000",
                    fillColor: "#FF0000",
                    fillOpacity: 1,
                    weight: 2,
                  }}
                >
                  <Popup>
                    <div>
                      Meta Node ID: {node.id}
                      <br />
                      Location: {node.lat.toFixed(6)}, {node.lon.toFixed(6)}
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
              {metaNetwork.edges.map((edge, index) => {
                const sourceNode = metaNetwork.nodes.find((n) => n.id === edge.source);
                const targetNode = metaNetwork.nodes.find((n) => n.id === edge.target);
                if (!sourceNode || !targetNode) return null;

                return (
                  <Polyline
                    key={`meta-edge-${index}`}
                    positions={[
                      [sourceNode.lat, sourceNode.lon],
                      [targetNode.lat, targetNode.lon],
                    ]}
                    color="#FF0000"
                    weight={2}
                    opacity={0.8}
                  >
                    <Popup>
                      <div>
                        Meta Edge: {edge.source} → {edge.target}
                      </div>
                    </Popup>
                  </Polyline>
                );
              })}
            </>
          )}
          {(visualizationFilter.viewMode === "bridges-only" || visualizationFilter.viewMode === "network-and-bridges") &&
            bridgeData?.bridge_coordinates.map((bridge, index) => {
              const damageProbability = bridge.damage_probabilities?.extensive || 0;
              const color = getBridgeColor(damageProbability);

              return (
                <CircleMarker
                  key={index}
                  center={[bridge.latitude, bridge.longitude]}
                  radius={10}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 1,
                    weight: 1,
                  }}
                >
                  <Popup>
                    <div>
                      Bridge ID: {bridge.name}
                      <br />
                      Year Built: {bridge.year_built}
                      <br />
                      Location: {bridge.latitude.toFixed(6)}, {bridge.longitude.toFixed(6)}
                      <br />
                      {bridge.damage_probabilities && (
                        <>
                          Failure Probability: {(bridge.damage_probabilities.extensive * 100).toFixed(1)}%
                          <br />
                          Risk Level: {damageProbability > 0.75 ? "High" : damageProbability > 0.25 ? "Medium" : "Low"}
                        </>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
        </MapContainer>
        {/* Only show legend if a view mode is selected */}
        {visualizationFilter.viewMode && <MapLegend visualizationFilter={visualizationFilter} />}
      </div>
      <Sidebar
        boundingBox={boundingBox}
        setBoundingBox={setBoundingBox}
        setNetworkNodes={setNetworkNodes}
        setNetworkWays={setNetworkWays}
        visualizationFilter={visualizationFilter}
        setVisualizationFilter={setVisualizationFilter}
        setBridgeData={setBridgeData}
        networkWays={networkWays}
        networkNodes={networkNodes}
        metaNetwork={metaNetwork}
        setMetaNetwork={setMetaNetwork}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />
    </div>
  );
};
