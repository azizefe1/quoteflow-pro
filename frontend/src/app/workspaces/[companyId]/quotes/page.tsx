"use client";

import { useParams } from "next/navigation";

import { WorkspaceShell } from "../_components/workspace-shell";

export default function QuotesPage() {
  const params = useParams<{ companyId: string }>();

  return (
    <WorkspaceShell companyId={params.companyId}>
      <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
        <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
          Quotes
        </p>
        <h2 className="mt-4 text-4xl font-black tracking-tight">
          Quote workflow screen
        </h2>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400">
          Next step will connect this page to quote create, status workflow and
          PDF export endpoints.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {["Draft", "Sent", "Accepted", "PDF export"].map((item) => (
            <div
              className="rounded-2xl border border-white/10 bg-slate-950/80 p-5 text-sm font-bold text-slate-300"
              key={item}
            >
              {item}
            </div>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
