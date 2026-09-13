import Link from "next/link";
import Card from "@/components/ui/Card";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import ProgressBar from "@/components/ui/ProgressBar";
import { daysUntil } from "@/lib/format";
import type { AuditorDashboard } from "@/lib/types";

const TAG: Record<string, BadgeTone> = { CRITICAL: "critical", ATTENTION: "warning", READY: "success", ACTIVE: "info" };

export default function AuditorPriorityReviews({ reviews }: { reviews: AuditorDashboard["priorityReviews"] }) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="font-semibold text-gray-800">Priority Reviews</p>
        <Link href="/companies" className="text-xs font-medium text-brand-blue hover:underline">All companies →</Link>
      </div>
      {reviews.length === 0 ? (
        <p className="py-8 text-center text-sm text-gray-400">No active engagements. Accept a client invitation to get started.</p>
      ) : (
        <div className="divide-y divide-gray-50">
          {reviews.map((r) => {
            const days = daysUntil(r.dueDate);
            return (
              <Link key={r.engagementId} href={`/companies?engagementId=${r.engagementId}`} className="-mx-2 flex items-center gap-4 rounded-lg px-2 py-3 hover:bg-gray-50">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-medium text-gray-800">{r.companyName}</p>
                    <Badge tone={TAG[r.tag] ?? "neutral"}>{r.tag}</Badge>
                    {days !== null && <span className={`text-[11px] ${days < 0 ? "font-semibold text-red-600" : "text-gray-400"}`}>{days < 0 ? `${-days}d overdue` : `Due in ${days}d`}</span>}
                  </div>
                  <p className="mt-0.5 text-xs text-gray-500">{r.detail}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1"><ProgressBar value={r.progressPercent} /></div>
                    <span className="w-9 text-right text-[11px] font-semibold text-gray-600">{r.progressPercent}%</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </Card>
  );
}
