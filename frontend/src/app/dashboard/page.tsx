"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiRequest, UserResponse } from "@/lib/api";
import { getAccessToken, removeAccessToken } from "@/lib/auth";

export default function DashboardPage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      window.location.href = "/login";
      return;
    }

    apiRequest<UserResponse>("/api/auth/me", {
      token,
    })
      .then(setUser)
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Could not load user.";

        setErrorMessage(message);
        removeAccessToken();
      });
  }, []);

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

        <section className="mt-10 rounded-[2rem] border border-white/10 bg-white/[0.05] p-8 shadow-2xl shadow-black/20">
          <p className="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">
            Auth connected
          </p>

          <h1 className="mt-4 text-4xl font-black tracking-tight">
            Frontend is now talking to FastAPI.
          </h1>

          {user ? (
            <div className="mt-8 grid gap-4 md:grid-cols-3">
              <InfoCard label="User" value={user.full_name} />
              <InfoCard label="Email" value={user.email} />
              <InfoCard label="Status" value={user.is_active ? "Active" : "Inactive"} />
            </div>
          ) : (
            <div className="mt-8 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-5 text-amber-100">
              {errorMessage || "Loading account..."}
            </div>
          )}

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
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
