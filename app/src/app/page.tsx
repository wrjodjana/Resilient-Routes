"use client";

import { useEffect, useRef, useState } from "react";
import { load_google_maps } from "../lib/google_maps";
import OpacitySlider from "./opacity";
import Sidebar from "./sidebar";

export default function Home() {
  const map_ref = useRef<HTMLDivElement>(null);
  const [map, set_map] = useState<google.maps.Map | null>(null);

  useEffect(() => {
    load_google_maps();
    async function init_map() {
      const { Map } = (await google.maps.importLibrary("maps")) as google.maps.MapsLibrary;
      const { ColorScheme } = (await google.maps.importLibrary("core")) as google.maps.CoreLibrary;

      if (map_ref.current) {
        const new_map = new Map(map_ref.current, {
          center: { lat: 35.6205, lng: -117.6718 },
          zoom: 12,
          colorScheme: ColorScheme.LIGHT,
          mapTypeControlOptions: {
            position: google.maps.ControlPosition.TOP_RIGHT,
          },
        });
        set_map(new_map);
      }
    }
    init_map();
  }, []);

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      <Sidebar map={map} />
      <OpacitySlider map={map} />
      <div ref={map_ref} style={{ width: "100%", height: "100%" }}></div>
    </div>
  );
}
