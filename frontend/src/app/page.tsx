import Link from "next/link";

interface Study {
  href: string;
  title: string;
  blurb: string;
  paper: string;
  paperUrl?: string;
  status: "available" | "soon";
  icon: React.ReactNode;
}

const STUDIES: Study[] = [
  {
    href: "/seismic",
    title: "Seismic Reliability",
    blurb: "Post-earthquake connectivity of highway bridge networks.",
    paper: "Graph Neural Network Surrogate for Seismic Reliability Analysis of Highway Bridge Systems",
    paperUrl: "https://arxiv.org/abs/2210.06404",
    status: "available",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="6" cy="6" r="2.5" />
        <circle cx="18" cy="8" r="2.5" />
        <circle cx="9" cy="18" r="2.5" />
        <path d="M8 7l8 1M8 8l0 8M17 10l-7 7" />
      </svg>
    ),
  },
  {
    href: "/traffic",
    title: "Traffic Assignment",
    blurb: "Predicting traffic flow across road networks with a heterogeneous graph neural network.",
    paper: "End-to-End Heterogeneous Graph Neural Networks for Traffic Assignment",
    paperUrl: "https://arxiv.org/abs/2310.13193",
    status: "available",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M4 20c0-8 5-12 5-16" />
        <path d="M20 20c0-8-5-12-5-16" />
        <path d="M9 4l0 0M15 4l0 0" />
        <path d="M8 12h8M7 16h10" />
      </svg>
    ),
  },
];

function StudyCard({ study }: { study: Study }) {
  const available = study.status === "available";
  return (
    <div
      className={`group relative flex flex-col rounded-2xl border border-slate-900/[0.07] bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_8px_30px_rgba(15,23,42,0.06)] transition-[transform,box-shadow] duration-200 ease-out hover:-translate-y-0.5 hover:shadow-[0_1px_2px_rgba(15,23,42,0.05),0_16px_40px_rgba(15,23,42,0.12)] ${available ? "" : "opacity-70 hover:opacity-100"}`}
    >
      <div className="flex items-start justify-between">
        <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-teal-50 text-teal-700">{study.icon}</span>
      </div>

      <h2 className="mt-5 text-lg font-semibold tracking-tight text-slate-900">{study.title}</h2>
      <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{study.blurb}</p>

      <div className="mt-5 border-t border-slate-900/[0.05] pt-4">
        {study.paperUrl ? (
          <a href={study.paperUrl} target="_blank" rel="noopener noreferrer" className="relative z-10 inline-flex w-fit items-start gap-1.5 text-xs leading-relaxed text-slate-400 transition-colors hover:text-teal-700">
            <span>{study.paper}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="mt-0.5 shrink-0">
              <path d="M7 17L17 7M7 7h10v10" />
            </svg>
          </a>
        ) : (
          <p className="text-xs leading-relaxed text-slate-400">{study.paper}</p>
        )}
      </div>

      <span className={`mt-4 inline-flex items-center gap-1.5 text-sm font-medium ${available ? "text-teal-700" : "text-slate-400"}`}>
        {available ? "Explore" : "In development"}
        {available && (
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-transform duration-200 ease-out group-hover:translate-x-0.5"
            aria-hidden="true"
          >
            <path d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        )}
      </span>

      <Link href={study.href} aria-label={`Open ${study.title}`} className="absolute inset-0 rounded-2xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/50" />
    </div>
  );
}

export default function Landing() {
  return (
    <main className="flex min-h-screen w-full flex-col bg-slate-50 text-slate-800">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-6 pt-16 pb-8">
        <h1 className="mt-8 text-3xl font-semibold leading-tight tracking-tight text-slate-900 text-balance sm:text-4xl">Graph neural network surrogates for transportation resilience</h1>
        <p className="mt-3 max-w-xl text-base leading-relaxed text-slate-500 text-pretty">Interactive surrogates that model how transportation networks hold up under stress. Choose a study to explore.</p>

        <h2 className="mt-12 mb-4 text-[11px] font-semibold uppercase tracking-wider text-slate-400">Studies</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {STUDIES.map((study) => (
            <StudyCard key={study.href} study={study} />
          ))}
        </div>
      </div>

      <footer className="mx-auto w-full max-w-3xl px-6 pb-8 text-[13px] text-slate-500">
        A project of the{" "}
        <a
          href="https://uq.cee.illinois.edu/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-medium text-slate-700 underline decoration-slate-300 underline-offset-2 transition-colors hover:text-teal-700 hover:decoration-teal-400"
        >
          Uncertainty Quantification Group, University of Illinois
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M7 17L17 7M7 7h10v10" />
          </svg>
        </a>
      </footer>
    </main>
  );
}
