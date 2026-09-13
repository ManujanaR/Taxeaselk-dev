"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { Field, Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { updateAuditorProfile } from "@/lib/api/auditor";
import { errorMessage, toast } from "@/lib/toast";
import type { AuditorProfileFull } from "@/lib/types";

const FIELDS: [keyof Omit<AuditorProfileFull, "id" | "email">, string, string][] = [
  ["fullName", "Full name", "As registered with CA Sri Lanka"],
  ["firmName", "Audit firm", ""],
  ["phone", "Phone", "+94 ..."],
  ["licenseNumber", "Professional license number", ""],
  ["icaslMemberNo", "CA Sri Lanka / ICASL member number", ""],
  ["irdPractitionerNo", "IRD tax practitioner registration number", ""],
  ["firmRegNo", "Firm registration number", ""],
  ["officeAddress", "Office address", ""],
];

export default function AuditorProfileForm({ initial }: { initial: AuditorProfileFull }) {
  const router = useRouter();
  const [form, setForm] = useState(initial);
  const [saving, setSaving] = useState(false);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const { id: _, email: __, ...payload } = form;
      setForm(await updateAuditorProfile(payload));
      toast.success("Profile saved.");
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
        <h2 className="flex items-center gap-2 text-base font-semibold text-gray-900"><ShieldCheck className="h-5 w-5 text-brand-blue" /> Profile &amp; Credentials</h2>
        <p className="mt-0.5 text-xs text-gray-500">Signed in as {form.email}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {FIELDS.map(([key, label, placeholder]) => (
          <div key={key} className={key === "officeAddress" ? "md:col-span-2" : ""}>
            <Field label={label} required={key === "fullName" || key === "firmName"}>
              <Input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} placeholder={placeholder} required={key === "fullName" || key === "firmName"} />
            </Field>
          </div>
        ))}
      </div>
      <div className="flex justify-end border-t border-gray-100 pt-5">
        <Button type="submit" disabled={saving} className="px-6">{saving ? "Saving..." : "Save Profile"}</Button>
      </div>
    </form>
  );
}
