"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthBrandPanel from "@/components/layout/AuthBrandPanel";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api/client";
import type { Session } from "@/lib/types";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const session = await api<Session>("/api/auth/login", { method: "POST", json: { email, password } });
      router.push(session.user.role === "auditor" ? "/auditor-dashboard" : "/dashboard");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "Invalid email or password.");
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="flex flex-col justify-center px-8 py-12 md:px-20">
        <h1 className="text-3xl font-extrabold text-brand-navy">Sign in</h1>
        <p className="mt-2 text-sm text-gray-500">Welcome back to TaxEaseLK</p>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <Field label="Email">
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" required autoComplete="email" />
          </Field>
          <Field label="Password">
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Your password" required autoComplete="current-password" />
          </Field>

          <Button type="submit" disabled={loading} className="mt-2 w-full bg-brand-blue-dark py-3 hover:bg-brand-navy">
            {loading ? "Signing in..." : "Sign in"}
          </Button>

          <p className="text-sm text-gray-500">
            Don&apos;t have an account?{" "}
            <Link href="/role" className="text-brand-blue hover:underline">
              Sign up
            </Link>
          </p>
        </form>
      </div>

      <AuthBrandPanel />
    </div>
  );
}
