"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthBrandPanel from "@/components/layout/AuthBrandPanel";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api/client";
import type { Session } from "@/lib/types";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function SignInPage() {
  const { t } = useLanguage();
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
      setError(err.message || t("auth.signIn.error.invalidCredentials"));
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="flex flex-col justify-center px-8 py-12 md:px-20">
        <h1 className="text-3xl font-extrabold text-brand-navy">{t("auth.signIn.title")}</h1>
        <p className="mt-2 text-sm text-gray-500">{t("auth.signIn.subtitle")}</p>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <Field label={t("auth.field.email")}>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={t("auth.placeholder.emailCompany")} required autoComplete="email" />
          </Field>
          <Field label={t("auth.field.password")}>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t("auth.signIn.passwordPlaceholder")} required autoComplete="current-password" />
          </Field>

          <Button type="submit" disabled={loading} className="mt-2 w-full bg-brand-blue-dark py-3 hover:bg-brand-navy">
            {loading ? t("auth.signIn.submitting") : t("auth.signIn.title")}
          </Button>

          <p className="text-sm text-gray-500">
            {t("auth.signIn.noAccount")}{" "}
            <Link href="/role" className="text-brand-blue hover:underline">
              {t("auth.signUp.title")}
            </Link>
          </p>
        </form>
      </div>

      <AuthBrandPanel />
    </div>
  );
}
