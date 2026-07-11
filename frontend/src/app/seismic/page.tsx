"use client";

import { useEffect, useRef, useState } from "react";
import type { Map as LeafletMap, LayerGroup } from "leaflet";

import Sidebar from "./sidebar";
import { fetchGraph } from "@/lib/api";
import { getLeaflet, initMap, renderGraph } from "@/lib/map";
import { GraphResponse, GraphSize } from "@/lib/types";

export default function Home() {
  const [size, setSize] = useState<GraphSize>("small");
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const loading = !error && graph?.size !== size;

  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const layerGroupRef = useRef<LayerGroup | null>(null);

  useEffect(() => {
    let cancelled = false;

    getLeaflet().then((L) => {
      const container = containerRef.current;
      if (!L || cancelled || !container || mapRef.current) return;

      const map = initMap(L, container);
      if (!map) return;

      mapRef.current = map;
      layerGroupRef.current = L.layerGroup().addTo(map);
      setMapReady(true);
    });

    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
      layerGroupRef.current = null;
      setMapReady(false);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    fetchGraph(size)
      .then((data) => {
        if (!cancelled) setGraph(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load graph");
      });

    return () => {
      cancelled = true;
    };
  }, [size]);

  const handleSizeChange = (next: GraphSize) => {
    setError(null);
    setSize(next);
  };

  useEffect(() => {
    if (!graph || !mapReady || !mapRef.current || !layerGroupRef.current) return;
    renderGraph(mapRef.current, layerGroupRef.current, graph);
  }, [graph, mapReady]);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-slate-50">
      <div ref={containerRef} className="absolute inset-0 h-full w-full bg-slate-50" />
      <div className="pointer-events-none absolute inset-0 z-[1000] p-4">
        <div className="pointer-events-auto w-72">
          <Sidebar size={size} graph={graph} loading={loading} error={error} onSizeChange={handleSizeChange} />
        </div>
      </div>
    </main>
  );
}
