"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiRequest, UserResponse } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("Demo User");
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Test12345");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      const user = await apiRequest<UserResponse>("/api/auth/register", {
        method: "POST",
        body: {
          email,
          password,
          full_name: fullName,
        },
      });

      setSuccessMessage(`Account created for ${user.email}. Redirecting to login...`);

      window.setTimeout(() => {
        router.push("/login");
      }, 800);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Registration failed. Please try again.";

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
            Create your QuoteFlow account.
          </h1>

          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Start building a professional B2B quote workspace with customers,
            products, quote calculations and PDF exports.
          </p>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-white/[0.06] p-6 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="rounded-[1.5rem] bg-slate-950 p-6">
            <h2 className="text-2xl font-black">Create account</h2>
            <p className="mt-2 text-sm text-slate-400">
              Register a user account for local development.
            </p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <label className="block">
                <span className="text-sm font-bold text-slate-300">Full name</span>
                <input
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  onChange={(event) => setFullName(event.target.value)}
                  type="text"
                  value={fullName}
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

              <label className="block">
                <span className="text-sm font-bold text-slate-300">Password</span>
                <input
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-300"
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

              {successMessage ? (
                <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
                  {successMessage}
                </div>
              ) : null}

              <button
                className="w-full rounded-2xl bg-cyan-400 px-5 py-4 text-sm font-black text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isSubmitting}
                type="submit"
              >
                {isSubmitting ? "Creating account..." : "Create account"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-400">
              Already registered?{" "}
              <Link className="font-bold text-cyan-300" href="/login">
                Login
              </Link>
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
