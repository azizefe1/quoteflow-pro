"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiRequest, TokenResponse } from "@/lib/api";
import { saveAccessToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Test12345");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const tokenResponse = await apiRequest<TokenResponse>("/api/auth/login", {
        method: "POST",
        body: {
          email,
          password,
        },
      });

      saveAccessToken(tokenResponse.access_token);
      router.push("/dashboard");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Login failed. Please try again.";

      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-10 lg:grid-cols-[0.95fr_1.05fr]">
        <section>
          <Link className="text-sm font-bold text-cyan-300" href="/">
            ← Back to QuoteFlow Pro
          </Link>

          <h1 className="mt-8 text-5xl font-black tracking-tight">
            Login to your quote workspace.
          </h1>

          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Continue managing customers, products, calculated quotes and PDF
            exports from one professional dashboard.
          </p>

          <div className="mt-8 rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-6">
            <p className="text-sm font-black uppercase tracking-[0.3em] text-cyan-300">
              Backend required
            </p>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Make sure FastAPI is running on{" "}
              <span className="font-bold text-white">http://127.0.0.1:8000</span>.
            </p>
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-white/[0.06] p-6 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="rounded-[1.5rem] bg-slate-950 p-6">
            <h2 className="text-2xl font-black">Welcome back</h2>
            <p className="mt-2 text-sm text-slate-400">
              Enter your account information to continue.
            </p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="text-sm font-bold text-slate-300">Email</span>
                <input
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300"
                  onChange={(event) => setEmail(event.target.value)}
                  type="email"
                  value={email}
                />
              </label>

              <label className="block">
                <span className="text-sm font-bold text-slate-300">Password</span>
                <input
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300"
                  onChange={(event) => setPassword(event.target.value)}
                  type="password"
                  value={password}
                />
              </label>

              {errorMessage ? (
                <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
                  {errorMessage}
                </div>
              ) : null}

              <button
                className="w-full rounded-2xl bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isSubmitting}
                type="submit"
              >
                {isSubmitting ? "Logging in..." : "Login"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-400">
              Need an account?{" "}
              <Link className="font-bold text-cyan-300" href="/register">
                Create one
              </Link>
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
