"use client";

import { useParams } from "next/navigation";

import { WorkspaceShell } from "../_components/workspace-shell";

export default function CustomersPage() {
  const params = useParams<{ companyId: string }>();

  return (
    <WorkspaceShell companyId={params.companyId}>
      <ModulePlaceholder
        eyebrow="Customers"
        title="Customer management screen"
        description="Next step will connect this page to GET and POST customer endpoints."
        bullets={[
          "Customer list with search and pagination",
          "Create customer form",
          "Customer detail and update workflow",
        ]}
      />
    </WorkspaceShell>
  );
}

function ModulePlaceholder({
  eyebrow,
  title,
  description,
  bullets,
}: {
  eyebrow: string;
  title: string;
  description: string;
  bullets: string[];
}) {
  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
      <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
        {eyebrow}
      </p>
      <h2 className="mt-4 text-4xl font-black tracking-tight">{title}</h2>
      <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400">
        {description}
      </p>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {bullets.map((bullet) => (
          <div
            className="rounded-2xl border border-white/10 bg-slate-950/80 p-5 text-sm font-bold text-slate-300"
            key={bullet}
          >
            {bullet}
          </div>
        ))}
      </div>
    </section>
  );
}
