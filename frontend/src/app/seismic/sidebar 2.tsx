"use client";

import Link from "next/link";
import { EarthquakeType, GraphResponse, GraphSize, TrainingJobResponse } from "@/lib/types";

const SIZES: { value: GraphSize; label: string }[] = [
  { value: "small", label: "Small" },
  { value: "middle", label: "Middle" },
  { value: "large", label: "Large" },
];

const SEVERITIES: { value: EarthquakeType; label: string }[] = [
  { value: "minor", label: "Minor" },
  { value: "moderate", label: "Moderate" },
  { value: "major", label: "Major" },
];

export interface TrainingControls {
  selectedNode: number | null;
  severity: EarthquakeType;
  job: TrainingJobResponse | null;
  trainError: string | null;
  onSeverityChange: (severity: EarthquakeType) => void;
  onTrain: () => void;
  onReset: () => void;
}

interface SidebarProps {
  size: GraphSize;
  graph: GraphResponse | null;
  loading: boolean;
  error: string | null;
  onSizeChange: (size: GraphSize) => void;
  training: TrainingControls | null;
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

function LossChart({ train, test }: { train: number[]; test: number[] }) {
  const clamp = (v: number) => Math.min(1, Math.max(0, v));
  const scale = Math.max(...train.map(clamp), ...test.map(clamp), 0.05);
  const toPoints = (values: number[]) => values.map((v, i) => `${(i / Math.max(values.length - 1, 1)) * 100},${30 - (clamp(v) / scale) * 28}`).join(" ");
  return (
    <div className="flex flex-col gap-1">
      <svg viewBox="0 0 100 32" className="h-14 w-full rounded-md bg-slate-50" preserveAspectRatio="none">
        <polyline points={toPoints(train)} fill="none" stroke="#0d9488" strokeWidth="1" vectorEffect="non-scaling-stroke" />
        <polyline points={toPoints(test)} fill="none" stroke="#f59e0b" strokeWidth="1" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="flex gap-3 text-[10px] font-medium text-slate-500">
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-3 rounded bg-teal-600" />
          Train L1
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-3 rounded bg-amber-500" />
          Test L1
        </span>
      </div>
    </div>
  );
}

function TrainingPanel({ selectedNode, severity, job, trainError, onSeverityChange, onTrain, onReset }: TrainingControls) {
  const running = job?.status === "running";
  const completed = job?.status === "completed";
  const failed = job?.status === "failed";
  const lastTrain = job && job.train_loss.length > 0 ? job.train_loss[job.train_loss.length - 1] : null;
  const lastTest = job && job.test_loss.length > 0 ? job.test_loss[job.test_loss.length - 1] : null;

  return (
    <div className="flex flex-col gap-2.5 border-t border-slate-900/[0.05] pt-3">
      <h2 className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Train the GNN</h2>
      <p className="text-[11px] leading-snug text-slate-500">Click a node on the map to set the destination, pick an earthquake scenario, then train a GraphSAGE surrogate on 100 simulated earthquakes.</p>

      <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
        {SEVERITIES.map((option) => (
          <button
            key={option.value}
            onClick={() => onSeverityChange(option.value)}
            disabled={running}
            className={`flex-1 rounded-lg px-1 py-1 text-[11px] font-medium transition-colors disabled:opacity-50 ${severity === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400">Destination</span>
        <span className="text-xs font-medium tabular-nums text-slate-600">{selectedNode === null ? "click a map node" : `Node ${selectedNode}`}</span>
      </div>

      <button
        onClick={onTrain}
        disabled={selectedNode === null || running}
        className="rounded-lg bg-teal-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
      >
        {running ? "Training…" : completed ? "Train again" : "Train model"}
      </button>

      {trainError && <p className="text-[11px] text-red-600">{trainError}</p>}
      {failed && <p className="text-[11px] text-red-600">Training failed: {job?.error}</p>}

      {job && !failed && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>
              Epoch <span className="font-semibold tabular-nums text-slate-700">{job.epoch}</span> / {job.total_epochs}
            </span>
            {lastTrain !== null && lastTest !== null && (
              <span className="tabular-nums">
                L1 {lastTrain.toFixed(3)} / {lastTest.toFixed(3)}
              </span>
            )}
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-teal-600 transition-[width] duration-500" style={{ width: `${(job.epoch / job.total_epochs) * 100}%` }} />
          </div>
          {job.train_loss.length > 1 && <LossChart train={job.train_loss} test={job.test_loss} />}
        </div>
      )}

      {completed && job?.result && (
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline gap-1.5">
            <span className="text-[22px] font-semibold leading-none tabular-nums text-teal-700">{job.result.mae.toFixed(3)}</span>
            <span className="text-xs text-slate-400">MAE on {job.earthquake_type} scenario</span>
          </div>
          <p className="text-[11px] leading-snug text-slate-500">Map shows predicted connectivity to Node {job.target_node_id}. Click nodes to compare against the simulation.</p>
          <button onClick={onReset} className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50">
            Back to precomputed view
          </button>
        </div>
      )}
    </div>
  );
}

export default function Sidebar({ size, graph, loading, error, onSizeChange, training }: SidebarProps) {
  const reliabilities = graph ? graph.nodes.filter((n) => !n.is_target).map((n) => n.value) : [];
  const atRisk = graph ? graph.nodes.filter((n) => !n.is_target && n.value < graph.threshold).length : 0;
  const thresholdPct = graph ? Math.round(graph.threshold * 100) : 75;

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
            <circle cx="6" cy="6" r="2.5" />
            <circle cx="18" cy="8" r="2.5" />
            <circle cx="9" cy="18" r="2.5" />
            <path d="M8 7l8 1M8 8l0 8M17 10l-7 7" />
          </svg>
          Seismic Reliability
        </span>
        <h1 className="text-[13.5px] font-semibold leading-[1.3] tracking-tight text-slate-900 text-balance">Graph Neural Networks for Highway Bridge Systems</h1>
        <a href="https://arxiv.org/abs/2210.06404" target="_blank" rel="noopener noreferrer" className="mt-0.5 inline-flex w-fit items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-teal-700">
          Read the paper
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M7 17L17 7M7 7h10v10" />
          </svg>
        </a>
      </div>

      <div className="flex gap-1 rounded-xl bg-slate-100 p-1">
        {SIZES.map((option) => (
          <button
            key={option.value}
            onClick={() => onSizeChange(option.value)}
            className={`flex-1 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${size === option.value ? "bg-white text-teal-700 shadow-[0_1px_2px_rgba(15,23,42,0.1)]" : "text-slate-500 hover:text-slate-700"}`}
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
              <div className="h-2 w-full rounded-full" style={{ background: "linear-gradient(to right, #dc2626, #f59e0b 55%, #0d9488)" }} />
              <div className="absolute -top-0.5 -bottom-0.5 w-0.5 rounded bg-slate-900" style={{ left: `${thresholdPct}%` }}>
                <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-[9px] font-semibold tabular-nums text-slate-600">{graph.threshold.toFixed(2)}</span>
              </div>
            </div>
            <div className="flex justify-between text-[10px] font-medium text-slate-500">
              <span>Likely cut off</span>
              <span>Stays connected</span>
            </div>
            <div className="mt-1.5 flex items-center gap-2">
              <span className="inline-block h-3 w-3 rounded-full bg-indigo-600" style={{ boxShadow: "0 0 0 2px #fff, 0 0 0 3.5px #4f46e5" }} />
              <span className="text-[10.5px] text-slate-500">Critical destination</span>
            </div>
          </div>

          {training && <TrainingPanel {...training} />}
        </>
      )}
    </aside>
  );
}
