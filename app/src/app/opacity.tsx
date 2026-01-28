"use client";

import { useEffect, useState } from "react";
import { MapProps } from "@/lib/types";
import type { ImageOverlay } from "leaflet";
import { getLeaflet } from "@/lib/leaflet_map";

export default function OpacitySlider({ map }: MapProps) {
  const [opacity, set_opacity] = useState(0);
  const [overlay, set_overlay] = useState<ImageOverlay | null>(null);

  useEffect(() => {
    if (!map) return;

    const L = getLeaflet();
    if (!L) return;

    const bounds = L.latLngBounds([-85, -180], [85, 180]);
    const whiteImage = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IndoaXRlIi8+PC9zdmc+";

    const ground_overlay = L.imageOverlay(whiteImage, bounds, {
      opacity: 0,
      interactive: false,
    }).addTo(map);

    set_overlay(ground_overlay);

    return () => {
      map.removeLayer(ground_overlay);
    };
  }, [map]);

  const handle_opacity_change = (e: React.ChangeEvent<HTMLInputElement>) => {
    const new_opacity = parseFloat(e.target.value);
    set_opacity(new_opacity);

    if (overlay) {
      overlay.setOpacity(new_opacity);
    }
  };

  return (
    <div
      style={{
        position: "absolute",
        bottom: "20px",
        left: "340px",
        zIndex: 1000,
        backgroundColor: "white",
        padding: "8px 16px",
        borderRadius: "8px",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
      }}
    >
      <input type="range" min="0" max="1" step="0.01" value={opacity} onChange={handle_opacity_change} />
    </div>
  );
}
