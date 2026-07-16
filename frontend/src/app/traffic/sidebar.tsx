"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  TrafficCity,
  TrafficDemandResponse,
  TrafficMetric,
  TrafficMode,
  TrafficNetworkResponse,
  TrafficSeverity,
} from "@/lib/types";

const CITIES: { value: TrafficCity; label: string }[] = [
  { value: "anaheim", label: "Anaheim" },
  { value: "siouxfalls", label: "Sioux Falls" },
];

const SEVERITIES: { value: TrafficSeverity; label: string }[] = [
  { value: "baseline", label: "Baseline" },
  { value: "minor", label: "Minor" },
  { value: "moderate", label: "Moderate" },
  { value: "major", label: "Major" },
];

const MODES: { value: TrafficMode; label: string }[] = [
  { value: "network", label: "Network" },
  { value: "od", label: "OD demand" },
];

const METRICS: { value: TrafficMetric; label: string }[] = [
  { value: "ratio", label: "Ratio" },
  { value: "flow", label: "Flow" },
  { value: "capacity", label: "Capacity" },
];

interface SidebarProps {
  city: TrafficCity;
  severity: TrafficSeverity;
  mode: TrafficMode;
  metric: TrafficMetric;
  network: TrafficNetworkResponse | null;
  demand: TrafficDemandResponse | null;
  origin: number | null;
  loading: boolean;
  error: string | null;
  onCityChange: (city: TrafficCity) => void;
  onSeverityChange: (severity: TrafficSeverity) => void;
  onModeChange: (mode: TrafficMode) => void;
  onMetricChange: (metric: TrafficMetric) => void;
  onOriginChange: (origin: number) => void;
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs font-medium tabular-nums text-slate-600">{value}</span>
    </div>
  );
}

export default function Sidebar({ city, severity, mode, metric, network, demand, origin, loading, error, onCityChange, onSeverityChange, onModeChange, onMetricChange, onOriginChange }: SidebarProps) {
  const [originInput, setOriginInput] = useState("");

  useEffect(() => {
    setOriginInput(origin === null ? "" : String(origin));
  }, [origin]);

  const submitOrigin = () => {
    const parsed = Number(originInput);
    if (!network || !Number.isInteger(parsed) || parsed < 1 || parsed > network.n_node) return;
    onOriginChange(parsed);
  };

  return (
    <aside className="flex flex-col gap-4 rounded-2xl border border-slate-900/[0.07] bg-white p-4 text-slate-800 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_8px_30px_rgba(15,23,42,0.08)]">
      <Link href="/" className="inline-flex w-fit items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-slate-600">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M19 12H5M11 6l-6 6 6 6" />
        </svg>
        All studies
      </Link>

      <div className="flex flex-col gap-1">
        <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-teal-700">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M4 20c0-8 5-12 5-16" />
            <path d="M20 20c0-8-5-12-5-16" />
            <path d="M8 12h8M7 16h10" />
          </svg>
          Traffic Assignment
        </span>
        <h1 className="text-[13.5px] font-semibold leading-[1.3] tracking-tight text-slate-900 text-balance">Heterogeneous Graph Neural Networks for Traffic Assignment</h1>
        <a href="https://arxiv.org/abs/2310.13193" target="_blank" rel="noopener noreferrer" className="mt-0.5 inline-flex w-fit items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-teal-700">
          Read the paper
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M7 17L17 7M7 7h10v10" />
          </svg>
        </a>
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
          {CITIES.map((option) => (
            <button
              key={option.value}
              onClick={() => onCityChange(option.value)}
              className={`flex-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${city === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
            >
              {option.label}
            </button>
          ))}
        </div>
        <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
          {MODES.map((option) => (
            <button
              key={option.value}
              onClick={() => onModeChange(option.value)}
              className={`flex-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${mode === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="py-2 text-sm text-slate-400">Loading network…</p>}
      {error && <p className="py-2 text-sm text-red-600">{error}</p>}

      {network && !loading && mode === "network" && (
        <>
          <div className="flex flex-col gap-1.5">
            <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Disruption scenario</h2>
            <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
              {SEVERITIES.map((option) => {
                const unavailable = city === "anaheim" && option.value === "major";
                return (
                  <button
                    key={option.value}
                    onClick={() => onSeverityChange(option.value)}
                    disabled={unavailable}
                    title={unavailable ? "No major scenario data for Anaheim" : undefined}
                    className={`flex-1 rounded-lg px-1 py-1.5 text-[10.5px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${severity === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
                  >
                    {option.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Edge metric</h2>
            <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
              {METRICS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => onMetricChange(option.value)}
                  className={`flex-1 rounded-lg px-1 py-1.5 text-xs font-medium transition-colors ${metric === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-[28px] font-semibold leading-none tabular-nums text-red-600">{network.congested}</span>
              <span className="text-xs text-slate-400">of {network.n_link}</span>
            </div>
            <p className="mt-1.5 text-[11px] leading-snug text-slate-500">
              road links run above <span className="font-semibold text-slate-700">90%</span> of capacity at equilibrium
              {severity !== "baseline" && (
                <>
                  {" "}under a <span className="font-semibold text-slate-700">{severity}</span> disruption
                </>
              )}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-x-4 border-t border-slate-900/[0.05] pt-2">
            <Fact label="Nodes" value={String(network.n_node)} />
            <Fact label="Links" value={String(network.n_link)} />
            <Fact label="Trips" value={Math.round(network.total_demand).toLocaleString()} />
            <Fact label="Max V/C" value={network.max_ratio.toFixed(2)} />
            <Fact label="Total time" value={Math.round(network.total_time).toLocaleString()} />
            <Fact label="Scenario" value={severity} />
          </div>

          {metric === "ratio" ? (
            <div className="flex flex-col gap-1.5">
              <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Volume / capacity</h2>
              <div className="relative mt-1">
                <div className="h-2 w-full rounded-full" style={{ background: "linear-gradient(to right, #0d9488, #f59e0b 75%, #dc2626)" }} />
                <div className="absolute -top-0.5 -bottom-0.5 w-0.5 rounded bg-slate-900" style={{ left: "83%" }}>
                  <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-[9px] font-semibold tabular-nums text-slate-600">1.0</span>
                </div>
              </div>
              <div className="flex justify-between text-[10px] font-medium text-slate-500">
                <span>Free flow</span>
                <span>Congested</span>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-1.5">
              <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{metric === "flow" ? "Link flow" : "Link capacity"}</h2>
              <div className="mt-1 h-2 w-full rounded-full" style={{ background: "linear-gradient(to right, #99f6e4, #115e59)" }} />
              <div className="flex justify-between text-[10px] font-medium text-slate-500">
                <span>0</span>
                <span>{Math.round(Math.max(...network.links.map((link) => Math.max(...link.directions.map((d) => (metric === "flow" ? d.flow : d.capacity)))))).toLocaleString()}</span>
              </div>
            </div>
          )}
        </>
      )}

      {network && !loading && mode === "od" && (
        <>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="origin-input" className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Origin node
            </label>
            <div className="flex gap-1.5">
              <input
                id="origin-input"
                type="number"
                min={1}
                max={network.n_node}
                value={originInput}
                onChange={(e) => setOriginInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submitOrigin();
                }}
                placeholder={`1–${network.n_node}`}
                className="w-full rounded-lg border border-slate-900/[0.09] bg-slate-50 px-2.5 py-1.5 text-sm tabular-nums text-slate-800 placeholder:text-slate-300 focus:border-teal-600/40 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              />
              <button onClick={submitOrigin} className="rounded-lg bg-teal-700 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-teal-800 active:scale-[0.97]">
                Go
              </button>
            </div>
            <p className="text-[10.5px] leading-snug text-slate-400">or click any node on the map</p>
          </div>

          {demand && (
            <>
              <div>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-[28px] font-semibold leading-none tabular-nums text-teal-700">{Math.round(demand.total).toLocaleString()}</span>
                </div>
                <p className="mt-1.5 text-[11px] leading-snug text-slate-500">
                  trips leave <span className="font-semibold text-slate-700">Node {demand.origin}</span> for {demand.destinations.length} destinations
                </p>
              </div>

              <div className="grid grid-cols-2 gap-x-4 border-t border-slate-900/[0.05] pt-2">
                <Fact label="Origin" value={`Node ${demand.origin}`} />
                <Fact label="Destinations" value={String(demand.destinations.length)} />
                <Fact label="Largest flow" value={Math.round(demand.max).toLocaleString()} />
                <Fact label="Share" value={`${((demand.total / network.total_demand) * 100).toFixed(1)}%`} />
              </div>
            </>
          )}

          <div className="flex flex-col gap-2">
            <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Legend</h2>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-teal-600/60" />
                <span className="h-3 w-3 rounded-full bg-teal-600/60" />
                <span className="h-[18px] w-[18px] rounded-full bg-teal-600/60" />
              </span>
              <span className="text-[10.5px] text-slate-500">Circle size = trips to that node</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-block h-3 w-3 rounded-full bg-indigo-600" style={{ boxShadow: "0 0 0 2px #fff, 0 0 0 3.5px #4f46e5" }} />
              <span className="text-[10.5px] text-slate-500">Selected origin</span>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}
