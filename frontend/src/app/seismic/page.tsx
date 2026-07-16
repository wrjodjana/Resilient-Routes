"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Map as LeafletMap, LayerGroup } from "leaflet";

import Sidebar from "./sidebar";
import { fetchGraph, fetchTrainingJob, startTraining } from "@/lib/api";
import { getLeaflet, initMap, renderGraph, renderTrainingResult, renderTrainingSelection } from "@/lib/map";
import { EarthquakeType, GraphResponse, GraphSize, SeismicMode, TrainingDisplay, TrainingJobResponse } from "@/lib/types";

export default function Home() {
  const [mode, setMode] = useState<SeismicMode>("precomputed");
  const [size, setSize] = useState<GraphSize>("small");
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [selectedNode, setSelectedNode] = useState<number | null>(null);
  const [severity, setSeverity] = useState<EarthquakeType>("moderate");
  const [display, setDisplay] = useState<TrainingDisplay>("both");
  const [job, setJob] = useState<TrainingJobResponse | null>(null);
  const [trainError, setTrainError] = useState<string | null>(null);
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

  const handleModeChange = (next: SeismicMode) => {
    setError(null);
    setTrainError(null);
    setMode(next);
  };

  const handleSizeChange = (next: GraphSize) => {
    setError(null);
    setSelectedNode(null);
    setJob(null);
    setTrainError(null);
    setSize(next);
  };

  const handleNodeSelect = useCallback((id: number) => {
    setSelectedNode(id);
  }, []);

  const handleTrain = () => {
    if (selectedNode === null) return;
    setTrainError(null);
    setJob(null);
    startTraining(size, selectedNode, severity)
      .then(setJob)
      .catch((err) => setTrainError(err instanceof Error ? err.message : "Failed to start training"));
  };

  const handleReset = () => {
    setJob(null);
    setTrainError(null);
  };

  const jobId = job?.job_id ?? null;
  const jobRunning = job?.status === "running";

  useEffect(() => {
    if (!jobId || !jobRunning) return;

    const interval = setInterval(() => {
      fetchTrainingJob(jobId)
        .then(setJob)
        .catch((err) => {
          setTrainError(err instanceof Error ? err.message : "Lost connection to training job");
          setJob(null);
        });
    }, 1000);

    return () => clearInterval(interval);
  }, [jobId, jobRunning]);

  const trainingResult = job?.status === "completed" ? job.result : null;

  useEffect(() => {
    if (!mapReady || !mapRef.current || !layerGroupRef.current) return;
    if (mode === "train") {
      if (trainingResult) {
        renderTrainingResult(mapRef.current, layerGroupRef.current, trainingResult, display);
      } else if (graph && graph.size === size) {
        renderTrainingSelection(mapRef.current, layerGroupRef.current, graph, handleNodeSelect, selectedNode);
      } else {
        layerGroupRef.current.clearLayers();
      }
    } else {
      if (!graph || graph.size !== size) return;
      renderGraph(mapRef.current, layerGroupRef.current, graph);
    }
  }, [graph, mapReady, mode, size, trainingResult, display, selectedNode, handleNodeSelect]);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-slate-50">
      <div ref={containerRef} className="absolute inset-0 h-full w-full bg-slate-50" />
      <div className="pointer-events-none absolute inset-0 z-[1000] p-4">
        <div className="pointer-events-auto flex max-h-full w-72">
          <Sidebar
            mode={mode}
            size={size}
            graph={graph}
            loading={loading}
            error={error}
            onModeChange={handleModeChange}
            onSizeChange={handleSizeChange}
            training={{
              selectedNode,
              severity,
              display,
              job,
              trainError,
              onSeverityChange: setSeverity,
              onDisplayChange: setDisplay,
              onTrain: handleTrain,
              onReset: handleReset,
            }}
          />
        </div>
      </div>
    </main>
  );
}
