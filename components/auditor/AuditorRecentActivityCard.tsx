import { CheckCircle2, AlertTriangle, Info } from "lucide-react";
import Card from "@/components/ui/Card";
import { relative, titleCase } from "@/lib/format";
import type { AuditLogEntry } from "@/lib/types";

const ICON = {
  success: { icon: CheckCircle2, cls: "bg-emerald-50 text-emerald-600" },
  warning: { icon: AlertTriangle, cls: "bg-amber-50 text-amber-600" },
  info: { icon: Info, cls: "bg-blue-50 text-brand-blue" },
};

export default function AuditorRecentActivityCard({ activity }: { activity: AuditLogEntry[] }) {
  return (
    <Card className="p-5">
      <p className="mb-3 font-semibold text-gray-800">Recent Activity</p>
      {activity.length === 0 ? (
        <p className="py-4 text-center text-sm text-gray-400">No activity yet.</p>
      ) : (
        <ul className="space-y-3">
          {activity.map((a) => {
            const t = ICON[a.tone] ?? ICON.info;
            const Icon = t.icon;
            return (
              <li key={a.id} className="flex items-start gap-2.5">
                <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${t.cls}`}><Icon className="h-3.5 w-3.5" /></span>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-gray-800">{titleCase(a.eventType.toLowerCase())}</p>
                  <p className="truncate text-[11px] text-gray-500">{a.companyName} · {a.details}</p>
                  <p className="text-[10px] text-gray-400">{relative(a.createdAt)}</p>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
