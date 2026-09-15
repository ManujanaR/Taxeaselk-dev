"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { updateAuditorProfile } from "@/lib/api/auditor";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { AuditorProfileFull } from "@/lib/types";

const FIELDS: [keyof Omit<AuditorProfileFull, "id" | "email">, TranslationKey, TranslationKey | ""][] = [
  ["fullName", "audcomp.profile.fullName", "audcomp.profile.fullNamePlaceholder"],
  ["firmName", "audcomp.profile.firmName", ""],
  ["phone", "audcomp.profile.phone", "audcomp.profile.phonePlaceholder"],
  ["licenseNumber", "audcomp.profile.licenseNumber", ""],
  ["icaslMemberNo", "audcomp.profile.icaslMemberNo", ""],
  ["irdPractitionerNo", "audcomp.profile.irdPractitionerNo", ""],
  ["firmRegNo", "audcomp.profile.firmRegNo", ""],
  ["officeAddress", "audcomp.profile.officeAddress", ""],
];

export default function AuditorProfileForm({ initial }: { initial: AuditorProfileFull }) {
  const router = useRouter();
  const { t } = useLanguage();
  const [form, setForm] = useState(initial);
  const [saving, setSaving] = useState(false);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const { id: _, email: __, ...payload } = form;
      setForm(await updateAuditorProfile(payload));
      toast.success(t("audcomp.profile.profileSaved"));
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={save} className="space-y-6">
      <div className="border-b border-gray-100 pb-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-gray-900"><ShieldCheck className="h-5 w-5 text-brand-blue" /> {t("audcomp.profile.heading")}</h2>
        <p className="mt-0.5 text-xs text-gray-500">{t("audcomp.profile.signedInAs", { email: form.email })}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {FIELDS.map(([key, labelKey, placeholderKey]) => (
          <div key={key} className={key === "officeAddress" ? "md:col-span-2" : ""}>
            <Field label={t(labelKey)} required={key === "fullName" || key === "firmName"}>
              <Input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} placeholder={placeholderKey ? t(placeholderKey) : ""} required={key === "fullName" || key === "firmName"} />
            </Field>
          </div>
        ))}
      </div>
      <div className="flex justify-end border-t border-gray-100 pt-5">
        <Button type="submit" disabled={saving} className="px-6">{saving ? t("common.saving") : t("audcomp.profile.saveProfile")}</Button>
      </div>
    </form>
  );
}
