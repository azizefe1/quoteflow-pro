const features = [
  ["Customer workspace", "Manage customers, contacts, tax details and notes inside the correct company workspace."],
  ["Product catalog", "Track SKUs, pricing, tax rates, stock quantities and service items."],
  ["Quote workflow", "Create calculated quotes and move them through draft, sent, accepted and rejected stages."],
  ["PDF export", "Generate professional PDF quotes that can be sent directly to customers."],
];

const workflow = [
  "Create company workspace",
  "Add customers and products",
  "Build calculated quote",
  "Export PDF and track status",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="relative overflow-hidden px-6 py-8 sm:px-10 lg:px-16">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.22),_transparent_32%),radial-gradient(circle_at_top_right,_rgba(99,102,241,0.22),_transparent_30%)]" />

        <div className="relative mx-auto max-w-7xl">
          <nav className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-5 py-4 shadow-2xl shadow-cyan-950/20 backdrop-blur">
            <div>
              <p className="text-lg font-black tracking-tight">QuoteFlow Pro</p>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
                B2B Quote Platform
              </p>
            </div>

            <div className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
              <a className="transition hover:text-white" href="#features">Features</a>
              <a className="transition hover:text-white" href="#workflow">Workflow</a>
              <a className="transition hover:text-white" href="#demo">Demo</a>
            </div>

            <a
              className="rounded-full bg-cyan-400 px-5 py-2 text-sm font-bold text-slate-950 shadow-lg shadow-cyan-500/30 transition hover:bg-cyan-300"
              href="#demo"
            >
              View demo
            </a>
          </nav>

          <div className="grid items-center gap-12 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:py-28">
            <div>
              <div className="mb-6 inline-flex rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-sm font-semibold text-cyan-200">
                Built for B2B sales teams
              </div>

              <h1 className="max-w-4xl text-5xl font-black leading-[0.95] tracking-tight sm:text-6xl lg:text-7xl">
                Create professional quotes without Excel chaos.
              </h1>

              <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300">
                QuoteFlow Pro centralizes customers, products, pricing,
                quote calculations and PDF export in a modern SaaS workflow.
              </p>

              <div className="mt-9 flex flex-col gap-4 sm:flex-row">
                <a
                  href="#features"
                  className="rounded-2xl bg-white px-6 py-4 text-center text-sm font-black text-slate-950 shadow-xl transition hover:-translate-y-0.5 hover:bg-cyan-100"
                >
                  Explore platform
                </a>
                <a
                  href="#workflow"
                  className="rounded-2xl border border-white/15 bg-white/10 px-6 py-4 text-center text-sm font-black text-white backdrop-blur transition hover:-translate-y-0.5 hover:bg-white/15"
                >
                  See workflow
                </a>
              </div>

              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {[
                  ["3x", "Quote speed"],
                  ["PDF", "Export ready"],
                  ["SaaS", "Workspace based"],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.06] p-5 backdrop-blur">
                    <p className="text-3xl font-black text-cyan-300">{value}</p>
                    <p className="mt-2 text-sm font-bold text-white">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div id="demo" className="relative">
              <div className="absolute -inset-4 rounded-[2rem] bg-cyan-400/20 blur-3xl" />
              <div className="relative rounded-[2rem] border border-white/10 bg-slate-900/90 p-4 shadow-2xl shadow-black/40">
                <div className="rounded-[1.5rem] border border-white/10 bg-slate-950 p-5">
                  <div className="mb-6 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Current quote</p>
                      <h2 className="text-2xl font-black">Q-2026-0001</h2>
                    </div>
                    <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-bold text-emerald-300">
                      Sent
                    </span>
                  </div>

                  <div className="grid gap-4">
                    <div className="rounded-2xl bg-white/[0.04] p-4">
                      <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Customer</p>
                      <p className="mt-2 font-bold">ABC Industrial Ltd.</p>
                      <p className="text-sm text-slate-400">contact@abcindustrial.com</p>
                    </div>

                    <QuoteLine title="Industrial Generator" meta="2 × 125,000 TRY" total="300,000 TRY" />
                    <QuoteLine title="Installation Service" meta="1 × 10,000 TRY" total="12,000 TRY" />

                    <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-5">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-bold text-cyan-100">Total amount</p>
                        <p className="text-2xl font-black">312,000 TRY</p>
                      </div>
                      <button className="mt-5 w-full rounded-xl bg-cyan-400 px-4 py-3 text-sm font-black text-slate-950">
                        Export PDF Quote
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="px-6 py-16 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">Core modules</p>
          <h2 className="mt-4 max-w-2xl text-4xl font-black tracking-tight">
            Everything needed before a quote becomes revenue.
          </h2>

          <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {features.map(([title, description]) => (
              <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-xl shadow-black/20">
                <div className="mb-5 h-10 w-10 rounded-2xl bg-cyan-400/20" />
                <h3 className="text-lg font-black">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="workflow" className="px-6 pb-20 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl rounded-[2rem] border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
          <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">Workflow</p>
          <h2 className="mt-4 max-w-2xl text-4xl font-black tracking-tight">
            From customer data to PDF quote in one flow.
          </h2>

          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {workflow.map((step, index) => (
              <div key={step} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                <p className="text-sm font-black text-cyan-300">Step {index + 1}</p>
                <p className="mt-3 text-lg font-bold">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

function QuoteLine({
  title,
  meta,
  total,
}: {
  title: string;
  meta: string;
  total: string;
}) {
  return (
    <div className="rounded-2xl bg-white/[0.04] p-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="font-bold">{title}</p>
          <p className="text-sm text-slate-400">{meta}</p>
        </div>
        <p className="font-black text-cyan-300">{total}</p>
      </div>
    </div>
  );
}
