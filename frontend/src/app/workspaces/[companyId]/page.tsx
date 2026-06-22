"use client";

import { useParams } from "next/navigation";

import { WorkspaceShell } from "./_components/workspace-shell";

export default function WorkspaceOverviewPage() {
  const params = useParams<{ companyId: string }>();
  const companyId = params.companyId;

  return (
    <WorkspaceShell companyId={companyId}>
      <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
        <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
          Workspace overview
        </p>

        <h2 className="mt-4 text-4xl font-black tracking-tight">
          Manage customers, products and quotes from one company workspace.
        </h2>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <ModuleCard
            title="Customers"
            description="Create customer records and keep contact details ready for quotes."
          />
          <ModuleCard
            title="Products"
            description="Prepare sellable products and services with price and tax information."
          />
          <ModuleCard
            title="Quotes"
            description="Build calculated quotes, update status and export professional PDFs."
          />
        </div>
      </section>
    </WorkspaceShell>
  );
}

function ModuleCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-6">
      <div className="mb-5 h-10 w-10 rounded-2xl bg-cyan-400/20" />
      <h3 className="text-xl font-black">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
    </div>
  );
}
