import Link from "next/link";

export default function Traffic() {
  return (
    <main className="min-h-screen w-full bg-slate-50 text-slate-800">
      <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col justify-center px-6 py-16">
        <Link
          href="/"
          className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-slate-500 transition-colors hover:text-slate-800"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M19 12H5M11 6l-6 6 6 6" />
          </svg>
          All studies
        </Link>

        <span className="mt-10 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M4 20c0-8 5-12 5-16" />
            <path d="M20 20c0-8-5-12-5-16" />
            <path d="M9 4l0 0M15 4l0 0" />
            <path d="M8 12h8M7 16h10" />
          </svg>
        </span>

        <div className="mt-5 flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Traffic Assignment</h1>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold text-slate-500">
            Coming soon
          </span>
        </div>

        <p className="mt-3 max-w-lg text-base leading-relaxed text-slate-500 text-pretty">
          A heterogeneous graph neural network that predicts traffic flow across road networks. This study is in development — it will land here alongside the seismic model.
        </p>

        <div className="mt-8 border-t border-slate-900/[0.05] pt-5">
          <a
            href="https://arxiv.org/abs/2310.13193"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex w-fit items-start gap-1.5 text-xs leading-relaxed text-slate-400 transition-colors hover:text-teal-700"
          >
            <span>End-to-End Heterogeneous Graph Neural Networks for Traffic Assignment</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="mt-0.5 shrink-0">
              <path d="M7 17L17 7M7 7h10v10" />
            </svg>
          </a>
        </div>
      </div>
    </main>
  );
}
