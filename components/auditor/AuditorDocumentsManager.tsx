"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, FolderOpen } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProgressBar from "@/components/ui/ProgressBar";
import EngagementStatusBadge from "./EngagementStatusBadge";
import EngagementDrawer from "./EngagementDrawer";
import type { EngagementRow } from "@/lib/types";

// One card per client company; opening a pack goes to the engagement drawer's Documents tab.
export default function AuditorDocumentsManager({ engagements, openEngagementId }: { engagements: EngagementRow[]; openEngagementId?: string }) {
  const router = useRouter();
  const [openId, setOpenId] = useState<string | null>(openEngagementId ?? null);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Client Document Packs</h1>
      <p className="mt-1 text-sm text-gray-500">Statutory documents uploaded by each client, with verification status against your checklist.</p>

      {engagements.length === 0 ? (
        <Card className="mt-6 p-10 text-center text-sm text-gray-400">No active clients yet.</Card>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {engagements.map((e) => {
            const pct = e.documentsCount ? Math.round((e.verifiedCount / e.documentsCount) * 100) : 0;
            return (
              <Card key={e.id} className="flex flex-col p-5">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-brand-blue"><Building2 className="h-5 w-5" /></div>
                    <div>
                      <p className="font-semibold text-gray-800">{e.companyName}</p>
                      <p className="text-xs text-gray-400">Tax year {e.taxYear}</p>
                    </div>
                  </div>
                  <EngagementStatusBadge status={e.status} />
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <Stat label="Files" value={e.documentsCount} />
                  <Stat label="Verified" value={e.verifiedCount} cls="text-status-success" />
                  <Stat label="Pending" value={e.documentsCount - e.verifiedCount} cls={e.documentsCount - e.verifiedCount ? "text-status-warning" : ""} />
                </div>
                <div className="mt-4">
                  <div className="mb-1 flex justify-between text-[11px] text-gray-500"><span>Verification</span><span>{pct}%</span></div>
                  <ProgressBar value={pct} />
                </div>
                <Button variant="secondary" icon={<FolderOpen className="h-4 w-4" />} className="mt-4 w-full" onClick={() => setOpenId(e.id)}>Open Company Pack</Button>
              </Card>
            );
          })}
        </div>
      )}

      {openId && <EngagementDrawer engagementId={openId} initialTab="documents" onClose={() => { setOpenId(null); router.refresh(); }} />}
    </div>
  );
}

function Stat({ label, value, cls = "" }: { label: string; value: number; cls?: string }) {
  return (
    <div className="rounded-lg bg-gray-50 py-2">
      <p className={`text-lg font-bold ${cls || "text-gray-800"}`}>{value}</p>
      <p className="text-[10px] uppercase tracking-wide text-gray-400">{label}</p>
    </div>
  );
}
