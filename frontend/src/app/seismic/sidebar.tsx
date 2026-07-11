"use client";

import Link from "next/link";
import { GraphResponse, GraphSize } from "@/lib/types";

const SIZES: { value: GraphSize; label: string }[] = [
  { value: "small", label: "Small" },
  { value: "middle", label: "Middle" },
  { value: "large", label: "Large" },
];

interface SidebarProps {
  size: GraphSize;
  graph: GraphResponse | null;
  loading: boolean;
  error: string | null;
  onSizeChange: (size: GraphSize) => void;
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs font-medium tabular-nums text-slate-600">{value}</span>
    </div>
  );
}

function median(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

export default function Sidebar({ size, graph, loading, error, onSizeChange }: SidebarProps) {
  const reliabilities = graph ? graph.nodes.filter((n) => !n.is_target).map((n) => n.value) : [];
  const atRisk = graph ? graph.nodes.filter((n) => !n.is_target && n.value < graph.threshold).length : 0;
  const thresholdPct = graph ? Math.round(graph.threshold * 100) : 75;

  return (
    <aside className="flex flex-col gap-4 rounded-2xl border border-slate-900/[0.07] bg-white p-4 text-slate-800 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_8px_30px_rgba(15,23,42,0.08)]">
      <Link
        href="/"
        className="inline-flex w-fit items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-slate-600"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M19 12H5M11 6l-6 6 6 6" />
        </svg>
        All studies
      </Link>
      <div className="flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="6" cy="6" r="2.5" />
            <circle cx="18" cy="8" r="2.5" />
            <circle cx="9" cy="18" r="2.5" />
            <path d="M8 7l8 1M8 8l0 8M17 10l-7 7" />
          </svg>
        </span>
        <div className="leading-tight">
          <h1 className="text-sm font-semibold tracking-tight">Resilient Routes</h1>
          <p className="text-[11px] text-slate-400">Post-earthquake connectivity</p>
        </div>
      </div>

      <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
        {SIZES.map((option) => (
          <button
            key={option.value}
            onClick={() => onSizeChange(option.value)}
            className={`flex-1 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              size === option.value
                ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {loading && <p className="py-2 text-sm text-slate-400">Loading network…</p>}
      {error && <p className="py-2 text-sm text-red-600">{error}</p>}

      {graph && !loading && (
        <>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-[28px] font-semibold leading-none tabular-nums text-red-600">{atRisk}</span>
              <span className="text-xs text-slate-400">of {graph.n_node}</span>
            </div>
            <p className="mt-1.5 text-[11px] leading-snug text-slate-500">
              nodes fall below <span className="font-semibold text-slate-700">{graph.threshold.toFixed(2)}</span> — likely cut off from the destination
            </p>
          </div>

          <div className="grid grid-cols-2 gap-x-4 border-t border-slate-900/[0.05] pt-2">
            <Fact label="Edges" value={String(graph.n_edge)} />
            <Fact label="Bridges" value={String(graph.n_bridge)} />
            <Fact label="Roads" value={String(graph.n_road)} />
            <Fact label="Median rel." value={median(reliabilities).toFixed(2)} />
          </div>

          <div className="flex flex-col gap-1.5">
            <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Connectivity reliability</h2>
            <div className="relative mt-1">
              <div
                className="h-2 w-full rounded-full"
                style={{ background: "linear-gradient(to right, #dc2626, #f59e0b 55%, #0d9488)" }}
              />
              <div
                className="absolute -top-0.5 -bottom-0.5 w-0.5 rounded bg-slate-900"
                style={{ left: `${thresholdPct}%` }}
              >
                <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-[9px] font-semibold tabular-nums text-slate-600">
                  {graph.threshold.toFixed(2)}
                </span>
              </div>
            </div>
            <div className="flex justify-between text-[10px] font-medium text-slate-500">
              <span>Likely cut off</span>
              <span>Stays connected</span>
            </div>
            <div className="mt-1.5 flex items-center gap-2">
              <span
                className="inline-block h-3 w-3 rounded-full bg-indigo-600"
                style={{ boxShadow: "0 0 0 2px #fff, 0 0 0 3.5px #4f46e5" }}
              />
              <span className="text-[10.5px] text-slate-500">Critical destination</span>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}
