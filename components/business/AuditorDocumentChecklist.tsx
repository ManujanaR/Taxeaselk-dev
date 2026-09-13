"use client";

import { CheckCircle2, Circle, ClipboardList, Upload } from "lucide-react";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import type { ChecklistItem, DocumentsView } from "@/lib/types";

// The document list published by the assigned auditor; each missing item opens the upload dialog for it.
export default function AuditorDocumentChecklist({ checklist, onPickItem }: { checklist: DocumentsView["checklist"]; onPickItem: (item: ChecklistItem) => void }) {
  const { items, auditorName, auditorFirm } = checklist;
  const required = items.filter((i) => i.required);
  const provided = required.filter((i) => i.providedDocumentId).length;
  const pct = required.length ? Math.round((provided / required.length) * 100) : 0;

  return (
    <Card className="flex flex-col p-5">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-brand-blue">
          <ClipboardList className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-gray-800">Auditor Document Checklist</p>
          <p className="truncate text-xs text-gray-500">{auditorName ? `Requested by ${auditorName} · ${auditorFirm}` : "Published by your auditor once they accept your invitation"}</p>
        </div>
      </div>

      {items.length === 0 ? (
        <p className="mt-6 rounded-lg border border-dashed border-gray-200 p-4 text-center text-xs text-gray-400">No checklist yet. Upload your statutory pack (financial statements, trial balance, ledger, fixed assets, prior CIT return) in the meantime.</p>
      ) : (
        <>
          <div className="mt-4">
            <div className="mb-1 flex justify-between text-xs text-gray-500">
              <span>Audit pack readiness</span>
              <span className="font-semibold text-gray-700">{provided} / {required.length} · {pct}%</span>
            </div>
            <ProgressBar value={pct} />
          </div>
          <ul className="mt-4 space-y-1.5">
            {items.map((item) => {
              const done = !!item.providedDocumentId;
              return (
                <li key={item.id} className={`flex items-start gap-2.5 rounded-lg p-2 ${done ? "bg-emerald-50/50" : "hover:bg-gray-50"}`}>
                  {done ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" /> : <Circle className="mt-0.5 h-4 w-4 shrink-0 text-gray-300" />}
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm ${done ? "text-gray-500 line-through" : "font-medium text-gray-800"}`}>
                      {item.name}
                      {!item.required && <span className="ml-1 text-[10px] font-normal text-gray-400">(optional)</span>}
                    </p>
                    {item.description && !done && <p className="text-[11px] text-gray-400">{item.description}</p>}
                  </div>
                  {!done && (
                    <button onClick={() => onPickItem(item)} className="inline-flex shrink-0 items-center gap-1 rounded-md bg-brand-blue/10 px-2 py-1 text-[11px] font-semibold text-brand-blue hover:bg-brand-blue/20">
                      <Upload className="h-3 w-3" /> Upload
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </Card>
  );
}
