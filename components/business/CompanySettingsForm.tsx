"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, FileText } from "lucide-react";
import { Field, Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { updateCompany } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { Company } from "@/lib/types";

export default function CompanySettingsForm({ initial }: { initial: Company }) {
  const { t } = useLanguage();
  const router = useRouter();
  const [form, setForm] = useState<Company>(initial);
  const [saving, setSaving] = useState(false);

  function update<K extends keyof Company>(key: K, value: Company[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const { id: _, ...payload } = form;
      setForm(await updateCompany(payload));
      toast.success("Company profile saved.");
      router.refresh(); // top-bar badges read the company from the session
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSave} className="space-y-8">
      <div className="border-b border-gray-100 pb-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-gray-900">
          <Building2 className="h-5 w-5 text-brand-blue" />
          Corporate Entity &amp; Inland Revenue Registration
        </h2>
        <p className="mt-0.5 text-xs text-gray-500">Official company identity and IRD tax registrations. These drive your CIT rate and appear on your auditor&apos;s workpapers.</p>
      </div>

      <div>
        <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-gray-400">1. {t("business.settings.tabCompanyProfile")}</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label={t("business.settings.companyName")} required>
            <Input value={form.companyName} onChange={(e) => update("companyName", e.target.value)} required />
          </Field>
          <Field label={t("business.settings.tradingName")}>
            <Input value={form.tradingName} onChange={(e) => update("tradingName", e.target.value)} />
          </Field>
          <Field label={t("business.settings.sector")}>
            <Input value={form.industrySector} onChange={(e) => update("industrySector", e.target.value)} />
          </Field>
          <Field label={t("business.settings.financialYear")} required>
            <Select value={form.financialYear} onChange={(e) => update("financialYear", e.target.value)}>
              <option value="2025/26">2025/26 (Y/A 2025/2026)</option>
              <option value="2024/25">2024/25</option>
              <option value="2023/24">2023/24</option>
            </Select>
          </Field>
          <Field label="CIT rate category" required>
            <Select value={form.citTaxRateCategory} onChange={(e) => update("citTaxRateCategory", e.target.value as Company["citTaxRateCategory"])}>
              <option value="standard_30">Standard rate — 30%</option>
              <option value="sme_14">SME / export concessionary — 14%</option>
            </Select>
          </Field>
        </div>
      </div>

      <div className="border-t border-gray-100 pt-6">
        <h3 className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-gray-400">
          <FileText className="h-3.5 w-3.5" /> 2. {t("business.settings.brn")} &amp; {t("business.settings.tin")}
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label={t("business.settings.brn")}>
            <Input value={form.registrationNumber} onChange={(e) => update("registrationNumber", e.target.value)} placeholder="e.g. PV 00123456" />
          </Field>
          <Field label={t("business.settings.tin")}>
            <Input value={form.tinNumber} onChange={(e) => update("tinNumber", e.target.value)} placeholder="9-digit IRD TIN" />
          </Field>
          <Field label={t("business.settings.vat")}>
            <Input value={form.vatNumber} onChange={(e) => update("vatNumber", e.target.value)} />
          </Field>
          <Field label="SVAT number">
            <div className="flex items-center gap-3">
              <input type="checkbox" checked={form.isSvatRegistered} onChange={(e) => update("isSvatRegistered", e.target.checked)} className="h-4 w-4 accent-brand-blue" />
              <Input value={form.svatNumber} disabled={!form.isSvatRegistered} onChange={(e) => update("svatNumber", e.target.value)} placeholder="SVAT registered?" />
            </div>
          </Field>
        </div>
      </div>

      <div className="border-t border-gray-100 pt-6">
        <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-gray-400">3. Registered Office &amp; Tax Correspondence</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Official contact email">
            <Input type="email" value={form.contactEmail} onChange={(e) => update("contactEmail", e.target.value)} />
          </Field>
          <Field label="Official contact phone">
            <Input value={form.contactPhone} onChange={(e) => update("contactPhone", e.target.value)} placeholder="+94 11 234 5678" />
          </Field>
          <div className="md:col-span-2">
            <Field label="Registered office address">
              <Input value={form.registeredAddress} onChange={(e) => update("registeredAddress", e.target.value)} />
            </Field>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end border-t border-gray-100 pt-5">
        <Button type="submit" disabled={saving} className="px-6">
          {saving ? "Saving..." : "Save Profile Changes"}
        </Button>
      </div>
    </form>
  );
}
