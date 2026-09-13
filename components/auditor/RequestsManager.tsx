"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Bell, X, Building2 } from "lucide-react";
import Card from "@/components/ui/Card";
import StatCard from "@/components/ui/StatCard";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { createRequest, remindRequest } from "@/lib/api/auditor";
import { date, daysUntil } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { EngagementRow, RequestRow } from "@/lib/types";

const STATUS: Record<RequestRow["status"], { label: string; tone: BadgeTone }> = {
  pending: { label: "Pending", tone: "warning" },
  responded: { label: "Responded", tone: "info" },
  revision_requested: { label: "Revision Requested", tone: "critical" },
  resolved: { label: "Resolved", tone: "success" },
};
const CATEGORIES = ["Financial Statements", "Fixed Assets", "Tax Reliefs", "Bank & Cash", "General Inquiry"];

export default function RequestsManager({ requests, engagements }: { requests: RequestRow[]; engagements: EngagementRow[] }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ engagementId: engagements[0]?.id ?? "", title: "", description: "", category: CATEGORIES[0], priority: "MEDIUM", dueDate: "" });
  const [busy, setBusy] = useState<string | null>(null);

  const rows = requests.filter((r) => (r.companyName + r.title + r.referenceCode).toLowerCase().includes(query.toLowerCase()));
  const count = (s: RequestRow["status"]) => requests.filter((r) => r.status === s).length;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy("new");
    try {
      const { engagementId, ...payload } = form;
      await createRequest(engagementId, { ...payload, dueDate: payload.dueDate || null });
      toast.success("Request sent; the client has been notified.");
      setOpen(false);
      setForm({ ...form, title: "", description: "", dueDate: "" });
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  async function remind(r: RequestRow) {
    setBusy(r.id);
    try {
      await remindRequest(r.id);
      toast.success(`Reminder sent to ${r.companyName}.`);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Requests for Information</h1>
          <p className="mt-1 text-sm text-gray-500">Formal RFIs issued to your clients and their clearance status.</p>
        </div>
        <Button icon={<Plus className="h-4 w-4" />} onClick={() => setOpen(true)} disabled={!engagements.length} title={engagements.length ? undefined : "No active engagements"}>New Request</Button>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Total" value={requests.length} />
        <StatCard label="Pending" value={count("pending") + count("revision_requested")} valueClassName="text-status-warning" />
        <StatCard label="Responded" value={count("responded")} valueClassName="text-brand-blue" />
        <StatCard label="Resolved" value={count("resolved")} valueClassName="text-status-success" />
      </div>

      <Card className="mt-6 overflow-hidden">
        <div className="border-b border-gray-100 p-3">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by company, title or reference" className="w-80 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-4 py-3">Reference</th>
              <th className="px-4 py-3">Client</th>
              <th className="px-4 py-3">Request</th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Due</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {rows.length === 0 && <tr><td colSpan={7} className="px-4 py-10 text-center text-gray-400">No requests yet.</td></tr>}
            {rows.map((r) => {
              const days = daysUntil(r.dueDate);
              const active = r.status === "pending" || r.status === "revision_requested";
              return (
                <tr key={r.id} className="hover:bg-gray-50/60">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{r.referenceCode}</td>
                  <td className="px-4 py-3"><span className="flex items-center gap-1.5 text-gray-800"><Building2 className="h-3.5 w-3.5 text-gray-400" />{r.companyName}</span></td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-800">{r.title}</p>
                    <p className="text-[11px] text-gray-400">{r.category}</p>
                  </td>
                  <td className="px-4 py-3"><Badge tone={r.priority === "HIGH" ? "critical" : r.priority === "MEDIUM" ? "warning" : "info"}>{r.priority}</Badge></td>
                  <td className={`px-4 py-3 text-xs ${active && days !== null && days < 0 ? "font-semibold text-red-600" : "text-gray-600"}`}>{r.dueDate ? date(r.dueDate) : "—"}{active && days !== null && days < 0 ? " (overdue)" : ""}</td>
                  <td className="px-4 py-3"><Badge tone={STATUS[r.status].tone}>{STATUS[r.status].label}</Badge></td>
                  <td className="px-4 py-3 text-right">
                    {active && <Button variant="secondary" className="px-2.5 py-1.5 text-xs" icon={<Bell className="h-3.5 w-3.5" />} disabled={busy === r.id} onClick={() => remind(r)}>Remind</Button>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-lg p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <h2 className="text-base font-bold text-gray-900">New Request for Information</h2>
              <button onClick={() => setOpen(false)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <form onSubmit={submit} className="space-y-4 p-6">
              <Field label="Target company" required>
                <Select value={form.engagementId} onChange={(e) => setForm({ ...form, engagementId: e.target.value })}>
                  {engagements.map((e) => <option key={e.id} value={e.id}>{e.companyName} ({e.taxYear})</option>)}
                </Select>
              </Field>
              <Field label="Request title" required><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required placeholder="e.g. Bank confirmation letters" /></Field>
              <div className="grid grid-cols-3 gap-3">
                <Field label="Category"><Select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{CATEGORIES.map((c) => <option key={c}>{c}</option>)}</Select></Field>
                <Field label="Priority"><Select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option>HIGH</option><option>MEDIUM</option><option>LOW</option></Select></Field>
                <Field label="Due date"><Input type="date" value={form.dueDate} onChange={(e) => setForm({ ...form, dueDate: e.target.value })} /></Field>
              </div>
              <Field label="Detailed instructions"><textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" /></Field>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setOpen(false)} disabled={busy === "new"}>Cancel</Button>
                <Button type="submit" disabled={busy === "new"}>{busy === "new" ? "Sending..." : "Send Request"}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
