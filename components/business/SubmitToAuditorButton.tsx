"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Send, CheckCircle2, AlertTriangle } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { submitHandover } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import type { DashboardView } from "@/lib/types";

// Locks the pack and moves the engagement to "under review".
export default function SubmitToAuditorButton({ auditorStatus, hasFigures, missingCount, unsentCount }: { auditorStatus: DashboardView["auditorStatus"]; hasFigures: boolean; missingCount: number; unsentCount: number }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  if (auditorStatus === "under_review" || auditorStatus === "approved") {
    return (
      <span className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
        <CheckCircle2 className="h-4 w-4" /> {auditorStatus === "approved" ? "Audit signed off" : "Pack submitted — under review"}
      </span>
    );
  }
  const blockers = [
    auditorStatus !== "active" && "an accepted auditor engagement",
    !hasFigures && "your financial figures",
  ].filter(Boolean) as string[];

  async function submit() {
    setBusy(true);
    try {
      await submitHandover();
      toast.success("Handover pack submitted to your auditor.");
      setOpen(false);
      router.refresh();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Button icon={<Send className="h-4 w-4" />} onClick={() => setOpen(true)} disabled={blockers.length > 0} title={blockers.length ? `Needs ${blockers.join(" and ")}` : undefined}>
        Submit to Auditor{unsentCount ? ` (${unsentCount} document${unsentCount === 1 ? "" : "s"})` : ""}
      </Button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md p-6">
            <h3 className="text-base font-bold text-gray-900">Submit handover pack?</h3>
            <p className="mt-2 text-sm text-gray-600">{unsentCount ? `${unsentCount} uploaded document${unsentCount === 1 ? "" : "s"} will be sent to your auditor together with your CIT figures.` : "Your CIT figures will be sent to your auditor."} They can then begin the statutory review; documents you upload afterwards go to them immediately.</p>
            {missingCount > 0 && (
              <p className="mt-3 flex items-start gap-2 rounded-lg border border-amber-100 bg-amber-50 p-2.5 text-xs text-amber-800">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {missingCount} required checklist document{missingCount === 1 ? " is" : "s are"} still missing. The auditor may request them.
              </p>
            )}
            <div className="mt-5 flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setOpen(false)} disabled={busy}>
                Not yet
              </Button>
              <Button onClick={submit} disabled={busy}>
                {busy ? "Submitting..." : "Submit Pack"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
