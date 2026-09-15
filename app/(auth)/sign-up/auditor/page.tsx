"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import AuthBrandPanel from "@/components/layout/AuthBrandPanel";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api/client";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function AuditorSignUpPage() {
  const { t } = useLanguage();
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
    if (form.password !== form.confirmPassword) return setError(t("auth.error.passwordMismatch"));
    if (form.password.length < 8) return setError(t("auth.error.passwordTooShort"));
    setLoading(true);
    try {
      const { confirmPassword: _, ...payload } = form;
      await api("/api/auth/register/auditor", { method: "POST", json: payload });
      router.push("/auditor-dashboard");
      router.refresh();
    } catch (err: any) {
      setError(err.message || t("auth.error.generic"));
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="flex flex-col justify-center px-8 py-12 md:px-20">
        <Link href="/role" className="mb-6 inline-flex w-fit items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
          <ChevronLeft className="h-4 w-4" />
          {t("common.back")}
        </Link>

        <h1 className="text-3xl font-extrabold text-brand-navy">{t("auth.signUp.title")}</h1>
        <p className="mt-2 text-sm text-gray-500">{t("auth.signUp.auditor.subtitle")}</p>

        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <Field label={t("auth.field.fullName")}>
            <Input value={form.fullName} onChange={(e) => update("fullName", e.target.value)} placeholder={t("auth.signUp.auditor.fullNamePlaceholder")} required autoComplete="name" />
          </Field>
          <Field label={t("auth.field.auditFirm")}>
            <Input value={form.firmName} onChange={(e) => update("firmName", e.target.value)} placeholder={t("auth.signUp.auditor.firmPlaceholder")} required autoComplete="organization" />
          </Field>
          <Field label={t("auth.field.licenseNumber")}>
            <Input value={form.licenseNumber} onChange={(e) => update("licenseNumber", e.target.value)} placeholder={t("auth.signUp.auditor.licensePlaceholder")} />
          </Field>
          <Field label={t("auth.field.email")}>
            <Input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} placeholder={t("auth.signUp.auditor.emailPlaceholder")} required autoComplete="email" />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label={t("auth.field.password")}>
              <Input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder={t("auth.signUp.passwordPlaceholder")} required autoComplete="new-password" />
            </Field>
            <Field label={t("auth.field.confirmPassword")}>
              <Input type="password" value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} placeholder={t("auth.signUp.confirmPasswordPlaceholder")} required autoComplete="new-password" />
            </Field>
          </div>

          <Button type="submit" disabled={loading} className="mt-2 w-full bg-brand-blue-dark py-3 hover:bg-brand-navy">
            {loading ? t("auth.signUp.submitting") : t("auth.signUp.title")}
          </Button>

          <p className="text-sm text-gray-500">
            {t("auth.signUp.hasAccount")}{" "}
            <Link href="/sign-in" className="text-brand-blue hover:underline">
              {t("auth.signUp.signInLink")}
            </Link>
          </p>
        </form>
      </div>

      <AuthBrandPanel />
    </div>
  );
}
