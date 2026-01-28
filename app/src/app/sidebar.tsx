"use client";

import { useRef, useState } from "react";
import { RectangleManager } from "@/lib/rectangle";
import { Coordinates } from "@/lib/types";
import { fetch_roads, fetch_intersections } from "@/lib/network/osm";
import { RenderRoads } from "@/lib/network/roads";
import { RenderBridges } from "@/lib/network/bridges";
import { RenderEarthquakes } from "@/lib/network/earthquakes";
import { MapProps, ShakemapData, EarthquakeElements } from "@/lib/types";
import { fetch_shakemap } from "@/lib/network/shakemap";
import Legend from "./legend";

export default function Sidebar({ map }: MapProps) {
  const rectangle_manager_ref = useRef<RectangleManager | null>(null);
  const road_renderer_ref = useRef<RenderRoads | null>(null);
  const earthquake_renderer_ref = useRef<RenderEarthquakes | null>(null);
  const bridge_renderer_ref = useRef<RenderBridges | null>(null);
  const [selected_coords, set_selected_coords] = useState<Coordinates | null>(null);
  const [show_road_legend, set_show_road_legend] = useState(false);
  const [shakemap_data, set_shakemap_data] = useState<ShakemapData | null>(null);
  const [target_magnitude, set_target_magnitude] = useState<number | null>(null);
  const [loading, set_loading] = useState<string | null>(null);
  const [error, set_error] = useState<string | null>(null);
  const [bridge_failures, set_bridge_failures] = useState<Array<{bridge_id: number; failure_probability: number; latitude: number; longitude: number}>>([]);

  const handle_select_location = async () => {
    if (!map) {
      set_error("Map not initialized");
      return;
    }
    try {
      set_error(null);
      if (!rectangle_manager_ref.current) {
        const manager = new RectangleManager(map, (coords) => {
          if (coords) {
            set_selected_coords(coords);
          }
        });
        await manager.initialize();
        rectangle_manager_ref.current = manager;
      }
      rectangle_manager_ref.current.enable_drawing();
    } catch (err) {
      set_error("Failed to enable location selection");
    }
  };

  const display_roads = async () => {
    if (!selected_coords || !map) {
      set_error("Please select a location first");
      return;
    }

    try {
      set_error(null);
      set_loading("roads");
      const road_data = await fetch_roads(selected_coords);
      const intersection_data = await fetch_intersections(selected_coords);

      if (!road_renderer_ref.current) {
        road_renderer_ref.current = new RenderRoads(map);
      }

      road_renderer_ref.current.draw_roads(road_data.elements);
      road_renderer_ref.current.draw_intersections(intersection_data.elements);
      set_show_road_legend(true);
    } catch {
      set_error("Failed to fetch roads");
    } finally {
      set_loading(null);
    }
  };

  const display_bridges = async () => {
    if (!selected_coords || !map) {
      set_error("Please select a location first");
      return;
    }

    try {
      set_error(null);
      set_loading("bridges");
      if (!bridge_renderer_ref.current) {
        bridge_renderer_ref.current = new RenderBridges(map);
      }

      await bridge_renderer_ref.current.draw_bridges(selected_coords);
    } catch {
      set_error("Failed to load bridges");
    } finally {
      set_loading(null);
    }
  };

  const display_bridge_failures = async () => {
    if (!shakemap_data) {
      set_error("Please fetch earthquakes first");
      return;
    }

    const bridges = bridge_renderer_ref.current?.get_bridges_data();

    if (!bridges || bridges.length === 0) {
      set_error("Please fetch bridges first");
      return;
    }

    try {
      set_error(null);
      set_loading("failures");
      interface BridgeFailurePayload {
        shakemap_data: ShakemapData;
        bridges: unknown[];
        target_magnitude?: number;
      }
      const payload: BridgeFailurePayload = { shakemap_data, bridges };

      if (target_magnitude !== null) {
        payload.target_magnitude = target_magnitude;
      }
      const failures_response = await fetch(`http://localhost:8000/api/bridge_failures`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const failures = await failures_response.json();
      set_bridge_failures(failures);
    } catch (error) {
      set_error("Failed to calculate bridge failures");
    } finally {
      set_loading(null);
    }
  };

  const display_earthquakes = async () => {
    if (!selected_coords || !map) return;

    try {
      set_error(null);
      set_loading("earthquakes");
      if (!earthquake_renderer_ref.current) {
        earthquake_renderer_ref.current = new RenderEarthquakes(map);
      }

      const earthquake = await earthquake_renderer_ref.current.get_earthquakes(selected_coords);
      
      if (earthquake) {
        const shakemap = await fetch_shakemap(earthquake);
        set_shakemap_data(shakemap);
      } else {
        set_error("No earthquakes found in selected area");
      }
    } catch {
      set_error("Failed to load earthquakes");
    } finally {
      set_loading(null);
    }
  };

  const handle_toggle_monochrome = () => {
    if (road_renderer_ref.current) {
      road_renderer_ref.current.toggle_monochrome();
    }
  };

  const handle_reset = () => {
    if (road_renderer_ref.current) {
      road_renderer_ref.current.clear_all();
    }
    if (bridge_renderer_ref.current) {
      bridge_renderer_ref.current.clear_bridges();
    }
    if (rectangle_manager_ref.current) {
      rectangle_manager_ref.current.clear_rectangle();
    }
    set_show_road_legend(false);
    set_selected_coords(null);
    set_shakemap_data(null);
    set_bridge_failures([]);
    set_error(null);
  };

  const sidebarStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    width: "320px",
    height: "100%",
    backgroundColor: "#ffffff",
    zIndex: 2000,
    pointerEvents: "auto",
    overflowY: "auto",
    boxShadow: "2px 0 8px rgba(0,0,0,0.1)",
    display: "flex",
    flexDirection: "column",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  };

  const headerStyle: React.CSSProperties = {
    padding: "20px",
    borderBottom: "1px solid #e5e7eb",
    backgroundColor: "#f9fafb",
  };

  const titleStyle: React.CSSProperties = {
    fontSize: "20px",
    fontWeight: "600",
    color: "#111827",
    marginBottom: "4px",
  };

  const subtitleStyle: React.CSSProperties = {
    fontSize: "13px",
    color: "#6b7280",
  };

  const sectionStyle: React.CSSProperties = {
    padding: "16px 20px",
    borderBottom: "1px solid #e5e7eb",
  };

  const sectionTitleStyle: React.CSSProperties = {
    fontSize: "12px",
    fontWeight: "600",
    color: "#6b7280",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    marginBottom: "12px",
  };

  const buttonStyle: React.CSSProperties = {
    width: "100%",
    padding: "10px 16px",
    marginBottom: "8px",
    backgroundColor: "#ffffff",
    borderWidth: "1px",
    borderStyle: "solid",
    borderColor: "#d1d5db",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151",
    cursor: "pointer",
    transition: "all 0.2s",
    textAlign: "left",
  };

  const buttonHoverStyle: React.CSSProperties = {
    backgroundColor: "#f3f4f6",
    borderColor: "#9ca3af",
  };

  const buttonPrimaryStyle: React.CSSProperties = {
    ...buttonStyle,
    backgroundColor: "#3b82f6",
    color: "#ffffff",
    borderColor: "#3b82f6",
  };

  const buttonPrimaryHoverStyle: React.CSSProperties = {
    backgroundColor: "#2563eb",
    borderColor: "#2563eb",
  };

  const buttonDangerStyle: React.CSSProperties = {
    ...buttonStyle,
    backgroundColor: "#ef4444",
    color: "#ffffff",
    borderColor: "#ef4444",
  };

  const buttonDangerHoverStyle: React.CSSProperties = {
    backgroundColor: "#dc2626",
    borderColor: "#dc2626",
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "10px 12px",
    marginBottom: "8px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "14px",
    color: "#374151",
    backgroundColor: "#ffffff",
  };

  const statusStyle: React.CSSProperties = {
    padding: "8px 12px",
    marginBottom: "8px",
    borderRadius: "6px",
    fontSize: "13px",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  };

  const statusSuccessStyle: React.CSSProperties = {
    ...statusStyle,
    backgroundColor: "#d1fae5",
    color: "#065f46",
  };

  const errorStyle: React.CSSProperties = {
    ...statusStyle,
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    margin: "0 20px 16px 20px",
  };

  const Button = ({ 
    children, 
    onClick, 
    isLoading = false, 
    variant = "default",
    disabled = false 
  }: { 
    children: React.ReactNode; 
    onClick: () => void; 
    isLoading?: boolean;
    variant?: "default" | "primary" | "danger";
    disabled?: boolean;
  }) => {
    const baseStyle = variant === "primary" ? buttonPrimaryStyle : variant === "danger" ? buttonDangerStyle : buttonStyle;
    const [hovered, setHovered] = useState(false);
    
    return (
      <button
        onClick={onClick}
        disabled={disabled || isLoading}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          ...baseStyle,
          ...(hovered && !disabled && !isLoading 
            ? (variant === "primary" ? buttonPrimaryHoverStyle : variant === "danger" ? buttonDangerHoverStyle : buttonHoverStyle)
            : {}),
          opacity: disabled || isLoading ? 0.6 : 1,
          cursor: disabled || isLoading ? "not-allowed" : "pointer",
        }}
      >
        {isLoading ? "Loading..." : children}
      </button>
    );
  };

  return (
    <div style={sidebarStyle}>
      <div style={headerStyle}>
        <div style={titleStyle}>Resilient Routes</div>
        <div style={subtitleStyle}>Map Analysis Tool</div>
      </div>

      {error && (
        <div style={errorStyle}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div style={sectionStyle}>
        <div style={sectionTitleStyle}>Step 1: Select Area</div>
        <Button onClick={handle_select_location} variant="primary">
          📍 Select Location
        </Button>
        {selected_coords && (
          <div style={statusSuccessStyle}>
            <span>✓</span>
            <span>Area selected</span>
          </div>
        )}
      </div>

      <div style={sectionStyle}>
        <div style={sectionTitleStyle}>Step 2: Load Data</div>
        <Button 
          onClick={display_roads} 
          isLoading={loading === "roads"}
          disabled={!selected_coords}
        >
          🛣️ Load Roads
        </Button>
        <Button 
          onClick={display_bridges} 
          isLoading={loading === "bridges"}
          disabled={!selected_coords}
        >
          🌉 Load Bridges
        </Button>
        <Button 
          onClick={display_earthquakes} 
          isLoading={loading === "earthquakes"}
          disabled={!selected_coords}
        >
          🌍 Load Earthquake
        </Button>
        {show_road_legend && (
          <Button onClick={handle_toggle_monochrome} variant="default">
            🎨 Toggle Monochrome
          </Button>
        )}
      </div>

      {shakemap_data && (
        <div style={sectionStyle}>
          <div style={sectionTitleStyle}>Earthquake Information</div>
          <div style={{ fontSize: "13px", color: "#374151", marginBottom: "6px" }}>
            <div style={{ fontWeight: "500", marginBottom: "4px" }}>{shakemap_data.location}</div>
            <div>Magnitude: {shakemap_data.actual_magnitude.toFixed(1)}</div>
            {shakemap_data.ground_motions.PGA?.max && (
              <div>PGA: {parseFloat(String(shakemap_data.ground_motions.PGA.max)).toFixed(3)} {shakemap_data.ground_motions.PGA.units}</div>
            )}
            {shakemap_data.ground_motions.PGV?.max && (
              <div>PGV: {parseFloat(String(shakemap_data.ground_motions.PGV.max)).toFixed(3)} {shakemap_data.ground_motions.PGV.units}</div>
            )}
            {shakemap_data.ground_motions.MMI?.max && (
              <div>MMI: {parseFloat(String(shakemap_data.ground_motions.MMI.max)).toFixed(1)}</div>
            )}
          </div>
        </div>
      )}

      <div style={sectionStyle}>
        <div style={sectionTitleStyle}>Step 3: Analyze</div>
        <input
          type="number"
          value={target_magnitude || ""}
          onChange={(e) => {
            const val = e.target.value;
            set_target_magnitude(val ? parseFloat(val) : null);
          }}
          placeholder="Target Magnitude (optional)"
          style={inputStyle}
          step="0.1"
          min="0"
          max="10"
        />
        <Button 
          onClick={display_bridge_failures} 
          isLoading={loading === "failures"}
          disabled={!shakemap_data}
        >
          ⚠️ Calculate Bridge Failures
        </Button>
      </div>

      {bridge_failures.length > 0 && (
        <div style={sectionStyle}>
          <div style={sectionTitleStyle}>Bridge Failure Probabilities</div>
          {bridge_failures.map((failure: {bridge_id: number; failure_probability: number}) => (
            <div key={failure.bridge_id} style={{ fontSize: "13px", color: "#374151", marginBottom: "4px" }}>
              Bridge {failure.bridge_id}: {(failure.failure_probability * 100).toFixed(8)}%
            </div>
          ))}
        </div>
      )}

      <div style={{ ...sectionStyle, marginTop: "auto", borderTop: "2px solid #e5e7eb" }}>
        <Button onClick={handle_reset} variant="danger">
          🔄 Reset All
        </Button>
      </div>

      <Legend show={show_road_legend} />
    </div>
  );
}
