"use client";

import { LegendProps } from "@/lib/types";

export default function Legend({ show }: LegendProps) {
  if (!show) return null;

  const roads = [
    { type: "Motorway", color: "#d73027" },
    { type: "Trunk", color: "#fc8d59" },
    { type: "Primary", color: "#fee090" },
    { type: "Secondary", color: "#91bfdb" },
    { type: "Tertiary", color: "#4575b4" },
    { type: "Residential", color: "#999999" },
    { type: "Unclassified", color: "#123456" },
  ];

  return (
    <div
      style={{
        position: "absolute",
        bottom: "60px",
        left: "340px",
        backgroundColor: "white",
        padding: "12px 16px",
        borderRadius: "8px",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        zIndex: 1000,
        fontSize: "13px",
        minWidth: "200px",
      }}
    >
      <div style={{ color: "#111827", fontWeight: "600", marginBottom: "10px", fontSize: "14px" }}>Road Types</div>
      {roads.map((road) => (
        <div key={road.type} style={{ color: "#374151", display: "flex", alignItems: "center", marginBottom: "6px" }}>
          <div
            style={{
              width: "24px",
              height: "4px",
              backgroundColor: road.color,
              marginRight: "10px",
              borderRadius: "2px",
            }}
          />
          <span>{road.type}</span>
        </div>
      ))}
    </div>
  );
}
