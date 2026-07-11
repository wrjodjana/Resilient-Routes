"use client";

import { useEffect, useRef, useState } from "react";
import { getLeaflet } from "../lib/leaflet_map";
import type { Map } from "leaflet";
import OpacitySlider from "./opacity";
import Sidebar from "./sidebar";

export default function Home() {
  const map_ref = useRef<HTMLDivElement>(null);
  const [map, set_map] = useState<Map | null>(null);

  useEffect(() => {
    if (!map_ref.current) return;

    const L = getLeaflet();
    if (!L) return;

    const new_map = L.map(map_ref.current, {
      center: [35.6205, -117.6718],
      zoom: 12,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(new_map);

    set_map(new_map);

    return () => {
      new_map.remove();
    };
  }, []);

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh", overflow: "hidden" }}>
      <div ref={map_ref} style={{ width: "100%", height: "100%" }}></div>
      <Sidebar map={map} />
      <OpacitySlider map={map} />
    </div>
  );
}
