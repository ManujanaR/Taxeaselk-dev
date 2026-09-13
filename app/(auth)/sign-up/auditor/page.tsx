"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import AuthBrandPanel from "@/components/layout/AuthBrandPanel";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api/client";

export default function AuditorSignUpPage() {
  const router = useRouter();
  const [form, setForm] = useState({ fullName: "", firmName: "", licenseNumber: "", email: "", password: "", confirmPassword: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function update<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
    setError("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (form.password !== form.confirmPassword) return setError("Passwords do not match.");
    if (form.password.length < 8) return setError("Password must be at least 8 characters.");
    setLoading(true);
    try {
      const { confirmPassword: _, ...payload } = form;
      await api("/api/auth/register/auditor", { method: "POST", json: payload });
      router.push("/auditor-dashboard");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="flex flex-col justify-center px-8 py-12 md:px-20">
        <Link href="/role" className="mb-6 inline-flex w-fit items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
          <ChevronLeft className="h-4 w-4" />
          Back
        </Link>

        <h1 className="text-3xl font-extrabold text-brand-navy">Sign up</h1>
        <p className="mt-2 text-sm text-gray-500">Create your auditor account</p>

        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <Field label="Full name">
            <Input value={form.fullName} onChange={(e) => update("fullName", e.target.value)} placeholder="K.L. Perera, FCA" required autoComplete="name" />
          </Field>
          <Field label="Audit firm">
            <Input value={form.firmName} onChange={(e) => update("firmName", e.target.value)} placeholder="BDO Partners" required autoComplete="organization" />
          </Field>
          <Field label="Professional license number">
            <Input value={form.licenseNumber} onChange={(e) => update("licenseNumber", e.target.value)} placeholder="Optional, can be added later" />
          </Field>
          <Field label="Email">
            <Input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="you@firm.com" required autoComplete="email" />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Password">
              <Input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder="Min 8 characters" required autoComplete="new-password" />
            </Field>
            <Field label="Confirm Password">
              <Input type="password" value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} placeholder="Repeat password" required autoComplete="new-password" />
            </Field>
          </div>

          <Button type="submit" disabled={loading} className="mt-2 w-full bg-brand-blue-dark py-3 hover:bg-brand-navy">
            {loading ? "Creating account..." : "Sign up"}
          </Button>

          <p className="text-sm text-gray-500">
            Already have an account?{" "}
            <Link href="/sign-in" className="text-brand-blue hover:underline">
              Sign In
            </Link>
          </p>
        </form>
      </div>

      <AuthBrandPanel />
    </div>
  );
}
