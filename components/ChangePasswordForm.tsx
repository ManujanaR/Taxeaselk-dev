"use client";

import { useState } from "react";
import { KeyRound } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input } from "@/components/ui/Input";
import { api } from "@/lib/api/client";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function ChangePasswordForm() {
  const { t } = useLanguage();
  const [form, setForm] = useState({ currentPassword: "", newPassword: "", confirm: "" });
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (form.newPassword !== form.confirm) return toast.error(t("shared.passwordMismatch"));
    if (form.newPassword.length < 8) return toast.error(t("shared.passwordTooShort"));
    setSaving(true);
    try {
      await api("/api/auth/change-password", { method: "POST", json: { currentPassword: form.currentPassword, newPassword: form.newPassword } });
      toast.success(t("shared.passwordChanged"));
      setForm({ currentPassword: "", newPassword: "", confirm: "" });
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="p-6">
      <h2 className="flex items-center gap-2 text-base font-semibold text-gray-900">
        <KeyRound className="h-5 w-5 text-brand-blue" />
        {t("shared.changePasswordTitle")}
      </h2>
      <form onSubmit={submit} className="mt-4 grid max-w-xl grid-cols-1 gap-4 md:grid-cols-3">
        <Field label={t("shared.currentPassword")} required>
          <Input type="password" value={form.currentPassword} onChange={(e) => setForm({ ...form, currentPassword: e.target.value })} required autoComplete="current-password" />
        </Field>
        <Field label={t("shared.newPassword")} required>
          <Input type="password" value={form.newPassword} onChange={(e) => setForm({ ...form, newPassword: e.target.value })} required autoComplete="new-password" />
        </Field>
        <Field label={t("shared.confirmNewPassword")} required>
          <Input type="password" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} required autoComplete="new-password" />
        </Field>
        <div className="md:col-span-3">
          <Button type="submit" disabled={saving}>
            {saving ? t("shared.updating") : t("shared.updatePassword")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
