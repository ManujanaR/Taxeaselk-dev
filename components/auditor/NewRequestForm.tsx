"use client";

import { useState } from "react";
import { X } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { createRequest } from "@/lib/api/auditor";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";

// Kept in English: these are submitted to the backend as the literal category value (not just a UI
// label), so translating them would change the stored data.
export const REQUEST_CATEGORIES = ["Financial Statements", "Fixed Assets", "Tax Reliefs", "Bank & Cash", "Expenses & Disallowables", "General Inquiry"];

// Modal to raise a request. `engagements` with more than one entry shows a company picker.
export default function NewRequestForm({ engagements, onClose, onCreated }: { engagements: { id: string; companyName: string }[]; onClose: () => void; onCreated: () => void }) {
  const { t } = useLanguage();
  const [form, setForm] = useState({ engagementId: engagements[0]?.id ?? "", title: "", description: "", category: REQUEST_CATEGORIES[0], priority: "MEDIUM", dueDate: "" });
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const { engagementId, ...payload } = form;
      await createRequest(engagementId, { ...payload, dueDate: payload.dueDate || null });
      toast.success(t("audcomp.newRequest.requestSent"));
      onCreated();
    } catch (err) {
      toast.error(errorMessage(err));
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="flex max-h-[90vh] w-full max-w-lg flex-col p-0">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <div>
            <h2 className="text-base font-bold text-gray-900">{t("audcomp.requestsManager.newRequest")}</h2>
            <p className="text-xs text-gray-500">{t("audcomp.newRequest.subtitle")}</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
        </div>
        <form onSubmit={submit} className="flex-1 space-y-4 overflow-y-auto p-6">
          {engagements.length > 1 ? (
            <Field label={t("audcomp.newRequest.clientCompany")} required>
              <Select value={form.engagementId} onChange={(e) => setForm({ ...form, engagementId: e.target.value })}>
                {engagements.map((e) => <option key={e.id} value={e.id}>{e.companyName}</option>)}
              </Select>
            </Field>
          ) : engagements.length === 1 ? (
            <Field label={t("audcomp.newRequest.clientCompany")}>
              <p className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-medium text-gray-800">{engagements[0].companyName}</p>
            </Field>
          ) : null}
          <Field label={t("audcomp.newRequest.whatDoYouNeed")} required><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required placeholder={t("audcomp.newRequest.titlePlaceholder")} /></Field>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <Field label={t("audcomp.newRequest.category")}><Select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{REQUEST_CATEGORIES.map((c) => <option key={c}>{c}</option>)}</Select></Field>
            <Field label={t("audcomp.newRequest.priority")}><Select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option>HIGH</option><option>MEDIUM</option><option>LOW</option></Select></Field>
            <Field label={t("audcomp.newRequest.dueDate")}><Input type="date" value={form.dueDate} onChange={(e) => setForm({ ...form, dueDate: e.target.value })} /></Field>
          </div>
          <Field label={t("audcomp.newRequest.details")}><textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder={t("audcomp.newRequest.detailsPlaceholder")} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" /></Field>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={onClose} disabled={busy}>{t("common.cancel")}</Button>
            <Button type="submit" disabled={busy || !form.engagementId}>{busy ? t("audcomp.newRequest.sending") : t("audcomp.newRequest.sendRequest")}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
