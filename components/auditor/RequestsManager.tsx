"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import Card from "@/components/ui/Card";
import StatCard from "@/components/ui/StatCard";
import Button from "@/components/ui/Button";
import RequestCard from "./RequestCard";
import NewRequestForm from "./NewRequestForm";
import type { EngagementRow, RequestRow } from "@/lib/types";

const FILTERS = [
  ["all", "All"],
  ["responded", "Needs my review"],
  ["waiting", "Waiting on client"],
  ["resolved", "Resolved"],
] as const;
type Filter = (typeof FILTERS)[number][0];

// Cross-company queue of every request the auditor has raised.
export default function RequestsManager({ requests, engagements, initialStatus }: { requests: RequestRow[]; engagements: EngagementRow[]; initialStatus?: string }) {
  const router = useRouter();
  const [filter, setFilter] = useState<Filter>(FILTERS.some(([f]) => f === initialStatus) ? (initialStatus as Filter) : "all");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const matches = (r: RequestRow) =>
    (filter === "all" || (filter === "waiting" ? r.status === "pending" || r.status === "revision_requested" : r.status === filter)) &&
    (r.companyName + r.title + r.referenceCode).toLowerCase().includes(query.toLowerCase());
  const rows = requests.filter(matches);
  const count = (f: Filter) => requests.filter((r) => f === "all" || (f === "waiting" ? r.status === "pending" || r.status === "revision_requested" : r.status === f)).length;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Requests</h1>
          <p className="mt-1 text-sm text-gray-500">Everything you have asked your clients for, and their answers.</p>
        </div>
        <Button icon={<Plus className="h-4 w-4" />} onClick={() => setOpen(true)} disabled={!engagements.length} title={engagements.length ? undefined : "No active engagements"}>New Request</Button>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Needs my review" value={count("responded")} valueClassName={count("responded") ? "text-brand-blue" : ""} />
        <StatCard label="Waiting on client" value={count("waiting")} valueClassName={count("waiting") ? "text-status-warning" : ""} />
        <StatCard label="Resolved" value={count("resolved")} valueClassName="text-status-success" />
        <StatCard label="Total" value={requests.length} />
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {FILTERS.map(([f, label]) => (
          <button key={f} onClick={() => setFilter(f)} className={`rounded-full px-3 py-1 text-xs font-semibold ${filter === f ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
            {label} <span className="opacity-70">({count(f)})</span>
          </button>
        ))}
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search company, title or reference" className="ml-auto w-72 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
      </div>

      <div className="mt-4 space-y-3">
        {rows.length === 0 && <Card className="p-10 text-center text-sm text-gray-400">{requests.length ? "Nothing in this view." : "You have not raised any requests yet."}</Card>}
        {rows.map((r) => (
          <RequestCard key={r.id} request={r} companyName={r.companyName} companyHref={`/companies/${r.engagementId}?tab=requests`} onChanged={() => router.refresh()} />
        ))}
      </div>

      {open && <NewRequestForm engagements={engagements.map((e) => ({ id: e.id, companyName: `${e.companyName} (${e.taxYear})` }))} onClose={() => setOpen(false)} onCreated={() => { setOpen(false); router.refresh(); }} />}
    </div>
  );
}
