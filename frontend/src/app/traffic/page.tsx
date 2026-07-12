"use client";

import { useEffect, useRef, useState } from "react";
import type { Map as LeafletMap, LayerGroup } from "leaflet";

import Sidebar from "./sidebar";
import { fetchTrafficDemand, fetchTrafficNetwork } from "@/lib/api";
import { getLeaflet, initMap, renderTrafficDemand, renderTrafficNetwork } from "@/lib/map";
import { TrafficCity, TrafficDemandResponse, TrafficMetric, TrafficMode, TrafficNetworkResponse } from "@/lib/types";

export default function Traffic() {
  const [city, setCity] = useState<TrafficCity>("anaheim");
  const [mode, setMode] = useState<TrafficMode>("network");
  const [metric, setMetric] = useState<TrafficMetric>("ratio");
  const [network, setNetwork] = useState<TrafficNetworkResponse | null>(null);
  const [origin, setOrigin] = useState<number | null>(null);
  const [demand, setDemand] = useState<TrafficDemandResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const loading = !error && network?.city !== city;

  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const layerGroupRef = useRef<LayerGroup | null>(null);
  const lastFittedCityRef = useRef<TrafficCity | null>(null);
  const onNodeClickRef = useRef<(id: number) => void>(() => {});

  onNodeClickRef.current = (id: number) => {
    setOrigin(id);
    setMode("od");
  };

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

    fetchTrafficNetwork(city)
      .then((data) => {
        if (!cancelled) setNetwork(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load network");
      });

    return () => {
      cancelled = true;
    };
  }, [city]);

  useEffect(() => {
    if (mode !== "od" || origin === null || demand?.origin === origin) return;
    let cancelled = false;

    fetchTrafficDemand(city, origin)
      .then((data) => {
        if (!cancelled) setDemand(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load demand");
      });

    return () => {
      cancelled = true;
    };
  }, [mode, origin, demand, city]);

  const handleCityChange = (next: TrafficCity) => {
    setError(null);
    setOrigin(null);
    setDemand(null);
    setCity(next);
  };

  const handleModeChange = (next: TrafficMode) => {
    setError(null);
    setMode(next);
  };

  const handleOriginChange = (next: number) => {
    setError(null);
    setOrigin(next);
  };

  useEffect(() => {
    if (!network || network.city !== city || !mapReady || !mapRef.current || !layerGroupRef.current) return;

    const handleClick = (id: number) => onNodeClickRef.current(id);
    const fit = lastFittedCityRef.current !== network.city;
    lastFittedCityRef.current = network.city;

    if (mode === "network") {
      renderTrafficNetwork(mapRef.current, layerGroupRef.current, network, metric, handleClick, fit);
    } else {
      renderTrafficDemand(mapRef.current, layerGroupRef.current, network, demand?.city === city ? demand : null, handleClick, fit);
    }
  }, [network, city, mode, metric, demand, mapReady]);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-slate-50">
      <div ref={containerRef} className="absolute inset-0 h-full w-full bg-slate-50" />
      <div className="pointer-events-none absolute inset-0 z-[1000] p-4">
        <div className="pointer-events-auto w-72">
          <Sidebar
            city={city}
            mode={mode}
            metric={metric}
            network={network}
            demand={demand?.city === city ? demand : null}
            origin={origin}
            loading={loading}
            error={error}
            onCityChange={handleCityChange}
            onModeChange={handleModeChange}
            onMetricChange={setMetric}
            onOriginChange={handleOriginChange}
          />
        </div>
      </div>
    </main>
  );
}
