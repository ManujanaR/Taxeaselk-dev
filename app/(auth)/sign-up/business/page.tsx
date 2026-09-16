"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import AuthBrandPanel from "@/components/layout/AuthBrandPanel";
import { Field, Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api/client";
import { useLanguage } from "@/lib/i18n/LanguageContext";

// Kept in English: these are sent to the backend as the industrySector value,
// not just display labels, so translating them would change the data contract.
const BUSINESS_CATEGORIES = ["Manufacturing", "Trading / Retail", "Services", "Construction", "Hospitality", "Other"];

export default function BusinessSignUpPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [form, setForm] = useState({ companyName: "", fullName: "", email: "", password: "", confirmPassword: "", industrySector: "" });
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
      await api("/api/auth/register/business", { method: "POST", json: payload });
      router.push("/dashboard");
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
        <p className="mt-2 text-sm text-gray-500">{t("auth.signUp.business.subtitle")}</p>

        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <Field label={t("auth.field.companyName")}>
            <Input value={form.companyName} onChange={(e) => update("companyName", e.target.value)} placeholder={t("auth.signUp.business.companyPlaceholder")} required />
          </Field>
          <Field label={t("auth.field.yourName")}>
            <Input value={form.fullName} onChange={(e) => update("fullName", e.target.value)} placeholder={t("auth.signUp.business.fullNamePlaceholder")} required autoComplete="name" />
          </Field>
          <Field label={t("auth.field.email")}>
            <Input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} placeholder={t("auth.placeholder.emailCompany")} required autoComplete="email" />
          </Field>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label={t("auth.field.password")}>
              <Input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder={t("auth.signUp.passwordPlaceholder")} required autoComplete="new-password" />
            </Field>
            <Field label={t("auth.field.confirmPassword")}>
              <Input type="password" value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} placeholder={t("auth.signUp.confirmPasswordPlaceholder")} required autoComplete="new-password" />
            </Field>
          </div>
          <Field label={t("auth.field.businessCategory")}>
            <Select value={form.industrySector} onChange={(e) => update("industrySector", e.target.value)} required>
              <option value="" disabled>
                {t("auth.signUp.business.selectCategoryPlaceholder")}
              </option>
              {BUSINESS_CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </Select>
          </Field>

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
