"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { getAccessToken, removeAccessToken } from "@/lib/auth";
import { CompanyWorkspaceResponse, getCompanyWorkspace } from "@/lib/companies";

type WorkspaceShellProps = {
  companyId: string;
  children: ReactNode;
};

const navigationItems = [
  { label: "Overview", path: "" },
  { label: "Customers", path: "customers" },
  { label: "Products", path: "products" },
  { label: "Quotes", path: "quotes" },
];

export function WorkspaceShell({ companyId, children }: WorkspaceShellProps) {
  const pathname = usePathname();
  const [workspace, setWorkspace] = useState<CompanyWorkspaceResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      window.location.href = "/login";
      return;
    }

    getCompanyWorkspace(token, companyId)
      .then(setWorkspace)
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Could not load workspace.";

        setErrorMessage(message);
      });
  }, [companyId]);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto max-w-7xl">
        <nav className="rounded-[2rem] border border-white/10 bg-white/[0.05] p-5 shadow-2xl shadow-black/20">
          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
            <div>
              <Link className="text-sm font-bold text-cyan-300" href="/dashboard">
                ← Dashboard
              </Link>

              <h1 className="mt-4 text-3xl font-black tracking-tight">
                {workspace?.company.name ?? "Workspace"}
              </h1>

              <p className="mt-2 text-sm text-slate-400">
                {workspace
                  ? `${workspace.role.toUpperCase()} • /${workspace.company.slug}`
                  : errorMessage || "Loading workspace..."}
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
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            {navigationItems.map((item) => {
              const href = item.path
                ? `/workspaces/${companyId}/${item.path}`
                : `/workspaces/${companyId}`;

              const isActive = pathname === href;

              return (
                <Link
                  className={
                    isActive
                      ? "rounded-full bg-cyan-400 px-4 py-2 text-sm font-black text-slate-950"
                      : "rounded-full border border-white/10 px-4 py-2 text-sm font-bold text-slate-300 transition hover:bg-white/10 hover:text-white"
                  }
                  href={href}
                  key={item.label}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </nav>

        <div className="mt-8">{children}</div>
      </div>
    </main>
  );
}
