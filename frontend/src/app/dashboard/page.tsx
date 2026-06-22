"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiRequest, UserResponse } from "@/lib/api";
import { getAccessToken, removeAccessToken } from "@/lib/auth";
import {
  CompanyWorkspaceResponse,
  createCompanyWorkspace,
  listMyCompanyWorkspaces,
} from "@/lib/companies";

export default function DashboardPage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [workspaces, setWorkspaces] = useState<CompanyWorkspaceResponse[]>([]);
  const [companyName, setCompanyName] = useState("Aziz Machinery");
  const [industry, setIndustry] = useState("Machinery");
  const [email, setEmail] = useState("info@example.com");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      window.location.href = "/login";
      return;
    }

    Promise.all([
      apiRequest<UserResponse>("/api/auth/me", {
        token,
      }),
      listMyCompanyWorkspaces(token),
    ])
      .then(([currentUser, currentWorkspaces]) => {
        setUser(currentUser);
        setWorkspaces(currentWorkspaces);
      })
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Could not load dashboard.";

        setErrorMessage(message);
        removeAccessToken();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  async function handleCreateWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      window.location.href = "/login";
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsCreating(true);

    try {
      const workspace = await createCompanyWorkspace(token, {
        name: companyName,
        industry,
        email,
      });

      setWorkspaces((currentWorkspaces) => [workspace, ...currentWorkspaces]);
      setSuccessMessage(`${workspace.company.name} workspace created.`);
      setCompanyName("");
      setIndustry("");
      setEmail("");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Workspace could not be created.";

      setErrorMessage(message);
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <nav className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.05] px-5 py-4">
          <div>
            <p className="text-lg font-black">QuoteFlow Pro</p>
            <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
              Dashboard
            </p>
          </div>

          <button
            className="rounded-full border border-white/10 px-4 py-2 text-sm font-bold text-slate-300 transition hover:bg-white/10 hover:text-white"
            onClick={() => {
              removeAccessToken();
              window.location.href = "/login";
            }}
          >
            Logout
          </button>
        </nav>

        <section className="mt-10 grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
          <div className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
            <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
              Account
            </p>

            <h1 className="mt-4 text-3xl font-black tracking-tight">
              Workspace dashboard
            </h1>

            {user ? (
              <div className="mt-6 grid gap-4">
                <InfoCard label="User" value={user.full_name} />
                <InfoCard label="Email" value={user.email} />
                <InfoCard label="Status" value={user.is_active ? "Active" : "Inactive"} />
              </div>
            ) : (
              <div className="mt-6 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-5 text-amber-100">
                {isLoading ? "Loading account..." : errorMessage}
              </div>
            )}

            <div className="mt-6 flex flex-col gap-3">
              <Link
                className="rounded-2xl bg-cyan-400 px-5 py-3 text-center text-sm font-black text-slate-950"
                href="/"
              >
                Back to landing
              </Link>
              <Link
                className="rounded-2xl border border-white/10 px-5 py-3 text-center text-sm font-black text-white"
                href="/login"
              >
                Login page
              </Link>
            </div>
          </div>

          <div className="grid gap-6">
            <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                <div>
                  <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
                    Company workspace
                  </p>
                  <h2 className="mt-4 text-3xl font-black tracking-tight">
                    Create and manage your companies.
                  </h2>
                  <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
                    Open a workspace to manage its customers, products and quote screens.
                  </p>
                </div>

                <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-5 py-4 text-center">
                  <p className="text-3xl font-black text-cyan-300">
                    {workspaces.length}
                  </p>
                  <p className="text-xs font-bold uppercase tracking-[0.25em] text-cyan-100">
                    Workspaces
                  </p>
                </div>
              </div>

              <form className="mt-8 grid gap-4 lg:grid-cols-4" onSubmit={handleCreateWorkspace}>
                <label className="block lg:col-span-2">
                  <span className="text-sm font-bold text-slate-300">Company name</span>
                  <input
                    className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                    onChange={(event) => setCompanyName(event.target.value)}
                    type="text"
                    value={companyName}
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-bold text-slate-300">Industry</span>
                  <input
                    className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                    onChange={(event) => setIndustry(event.target.value)}
                    type="text"
                    value={industry}
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-bold text-slate-300">Email</span>
                  <input
                    className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                    onChange={(event) => setEmail(event.target.value)}
                    type="email"
                    value={email}
                  />
                </label>

                <button
                  className="rounded-2xl bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60 lg:col-span-4"
                  disabled={isCreating}
                  type="submit"
                >
                  {isCreating ? "Creating workspace..." : "Create workspace"}
                </button>
              </form>

              {errorMessage ? (
                <div className="mt-5 rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
                  {errorMessage}
                </div>
              ) : null}

              {successMessage ? (
                <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
                  {successMessage}
                </div>
              ) : null}
            </section>

            <section className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-6 shadow-2xl shadow-black/20">
              <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
                My workspaces
              </p>
              <h2 className="mt-4 text-3xl font-black tracking-tight">
                Select a company
              </h2>

              <div className="mt-8 grid gap-4">
                {workspaces.length === 0 ? (
                  <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-6 text-slate-400">
                    No company workspace yet. Create your first workspace above.
                  </div>
                ) : (
                  workspaces.map((workspace) => (
                    <div
                      className="rounded-2xl border border-white/10 bg-slate-950/80 p-5"
                      key={workspace.membership_id}
                    >
                      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                        <div>
                          <p className="text-xl font-black">
                            {workspace.company.name}
                          </p>
                          <p className="mt-1 text-sm text-slate-400">
                            /{workspace.company.slug}
                          </p>
                          <p className="mt-3 text-sm text-slate-300">
                            {workspace.company.industry ?? "No industry"}
                          </p>
                        </div>

                        <div className="flex flex-wrap gap-3">
                          <span className="rounded-full bg-cyan-300/10 px-4 py-2 text-xs font-black uppercase tracking-[0.2em] text-cyan-300">
                            {workspace.role}
                          </span>
                          <Link
                            className="rounded-full bg-white px-4 py-2 text-xs font-black text-slate-950 transition hover:bg-cyan-100"
                            href={`/workspaces/${workspace.company.id}`}
                          >
                            Open workspace
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>
        </section>
      </div>
    </main>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.25em] text-slate-500">{label}</p>
      <p className="mt-3 text-lg font-black">{value}</p>
    </div>
  );
}
