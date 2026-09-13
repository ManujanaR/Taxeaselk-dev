"use client";

import { useState } from "react";
import { X } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { createRequest } from "@/lib/api/auditor";
import { errorMessage, toast } from "@/lib/toast";

export const REQUEST_CATEGORIES = ["Financial Statements", "Fixed Assets", "Tax Reliefs", "Bank & Cash", "Expenses & Disallowables", "General Inquiry"];

// Modal to raise a request. `engagements` with more than one entry shows a company picker.
export default function NewRequestForm({ engagements, onClose, onCreated }: { engagements: { id: string; companyName: string }[]; onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ engagementId: engagements[0]?.id ?? "", title: "", description: "", category: REQUEST_CATEGORIES[0], priority: "MEDIUM", dueDate: "" });
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const { engagementId, ...payload } = form;
      await createRequest(engagementId, { ...payload, dueDate: payload.dueDate || null });
      toast.success("Request sent; the client has been notified.");
      onCreated();
    } catch (err) {
      toast.error(errorMessage(err));
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="w-full max-w-lg p-0">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <div>
            <h2 className="text-base font-bold text-gray-900">New Request</h2>
            <p className="text-xs text-gray-500">Ask the client for a document, a voucher or an explanation. They answer once; you resolve or send it back.</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
        </div>
        <form onSubmit={submit} className="space-y-4 p-6">
          {engagements.length > 1 && (
            <Field label="Client company" required>
              <Select value={form.engagementId} onChange={(e) => setForm({ ...form, engagementId: e.target.value })}>
                {engagements.map((e) => <option key={e.id} value={e.id}>{e.companyName}</option>)}
              </Select>
            </Field>
          )}
          <Field label="What do you need?" required><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required placeholder="e.g. Bank confirmation letters, or Explain the Rs 450,000 entertainment expense" /></Field>
          <div className="grid grid-cols-3 gap-3">
            <Field label="Category"><Select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{REQUEST_CATEGORIES.map((c) => <option key={c}>{c}</option>)}</Select></Field>
            <Field label="Priority"><Select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option>HIGH</option><option>MEDIUM</option><option>LOW</option></Select></Field>
            <Field label="Due date"><Input type="date" value={form.dueDate} onChange={(e) => setForm({ ...form, dueDate: e.target.value })} /></Field>
          </div>
          <Field label="Details"><textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Reference the ledger account, schedule or statutory section so the client knows exactly what to provide." className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" /></Field>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={onClose} disabled={busy}>Cancel</Button>
            <Button type="submit" disabled={busy || !form.engagementId}>{busy ? "Sending..." : "Send Request"}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
