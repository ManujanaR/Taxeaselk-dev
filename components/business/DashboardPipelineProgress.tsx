import Link from "next/link";
import { FolderOpen, Calculator, ShieldCheck, Send, MessagesSquare, Clock, CheckCircle2, ChevronRight } from "lucide-react";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import T from "@/components/layout/T";
import type { DashboardView } from "@/lib/types";
import type { TranslationKey } from "@/lib/i18n/translations";

const ICONS: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; bg: string }> = {
  documents: { icon: FolderOpen, color: "text-blue-600", bg: "bg-blue-50" },
  financials: { icon: Calculator, color: "text-purple-600", bg: "bg-purple-50" },
  verification: { icon: ShieldCheck, color: "text-indigo-600", bg: "bg-indigo-50" },
  handover: { icon: Send, color: "text-amber-600", bg: "bg-amber-50" },
  signoff: { icon: MessagesSquare, color: "text-emerald-600", bg: "bg-emerald-50" },
};

export default function DashboardPipelineProgress({ data }: { data: DashboardView }) {
  const pct = data.progressPercent;
  const chip: [TranslationKey, string] = pct >= 100 ? ["bizpage.pipeline.signedOff", "border-emerald-200 bg-emerald-100 text-emerald-800"] : pct >= 60 ? ["bizpage.pipeline.inProgress", "border-blue-200 bg-blue-50 text-brand-blue"] : ["bizpage.pipeline.awaitingDocuments", "border-amber-200 bg-amber-50 text-amber-800"];

  return (
    <Card className="mt-6 border border-gray-200/90 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-gray-900"><T k="bizpage.pipeline.title" /></h2>
            <span className={`rounded-full border px-2.5 py-0.5 text-xs font-bold ${chip[1]}`}><T k={chip[0]} /></span>
          </div>
          <p className="mt-1 text-xs text-gray-400"><T k="bizpage.pipeline.subtitle" /></p>
        </div>
        <div className="text-right">
          <div className="flex items-baseline justify-end gap-1">
            <span className="text-3xl font-extrabold tracking-tight text-brand-blue">{pct}%</span>
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500"><T k="business.dashboard.complete" /></span>
          </div>
          <p className="mt-0.5 text-[11px] text-gray-400"><T k="bizpage.pipeline.fiveStages" /></p>
        </div>
      </div>

      <div className="mt-4">
        <ProgressBar value={pct} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-5">
        {data.steps.map((step, index) => {
          const cfg = ICONS[step.key] ?? ICONS.documents;
          const Icon = cfg.icon;
          const done = step.state === "done";
          return (
            <Link key={step.key} href={step.href} className="group flex flex-col justify-between rounded-xl border border-gray-200/90 bg-white p-3.5 transition-all hover:border-brand-blue/50 hover:shadow-md">
              <div>
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${cfg.bg} ${cfg.color}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="text-[11px] font-bold text-gray-400"><T k="bizpage.pipeline.stageNumber" params={{ number: index + 1 }} /></span>
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-bold ${done ? "bg-emerald-50 text-emerald-700" : "bg-blue-50 text-brand-blue"}`}>
                    {done ? <CheckCircle2 className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                    {step.progressPercent}%
                  </span>
                </div>
                <h4 className="mt-2.5 flex items-center justify-between text-xs font-bold text-gray-900 group-hover:text-brand-blue">
                  <span>{step.label}</span>
                  <ChevronRight className="h-3 w-3 text-gray-300 transition-all group-hover:translate-x-0.5 group-hover:text-brand-blue" />
                </h4>
                <p className="mt-0.5 text-[11px] font-semibold text-gray-600">{step.ratioLabel}</p>
              </div>
              <div className="mt-3 border-t border-gray-100 pt-2">
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                  <div className={`h-full rounded-full ${done ? "bg-emerald-500" : "bg-brand-blue"}`} style={{ width: `${step.progressPercent}%` }} />
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </Card>
  );
}
