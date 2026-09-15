"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Send, CheckCircle2, AlertTriangle } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { submitHandover } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { DashboardView } from "@/lib/types";

// Locks the pack and moves the engagement to "under review".
export default function SubmitToAuditorButton({ auditorStatus, hasFigures, missingCount, unsentCount }: { auditorStatus: DashboardView["auditorStatus"]; hasFigures: boolean; missingCount: number; unsentCount: number }) {
  const { t } = useLanguage();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  if (auditorStatus === "under_review" || auditorStatus === "approved") {
    return (
      <span className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
        <CheckCircle2 className="h-4 w-4" /> {auditorStatus === "approved" ? t("bizcomp.submitToAuditorButton.auditSignedOff") : t("bizcomp.submitToAuditorButton.packSubmitted")}
      </span>
    );
  }
  const blockers = [
    auditorStatus !== "active" && t("bizcomp.submitToAuditorButton.blockerEngagement"),
    !hasFigures && t("bizcomp.submitToAuditorButton.blockerFigures"),
  ].filter(Boolean) as string[];

  async function submit() {
    setBusy(true);
    try {
      await submitHandover();
      toast.success(t("bizcomp.submitToAuditorButton.submittedToast"));
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
      <Button icon={<Send className="h-4 w-4" />} onClick={() => setOpen(true)} disabled={blockers.length > 0} title={blockers.length ? t("bizcomp.submitToAuditorButton.needsTitle", { blockers: blockers.join(t("bizcomp.submitToAuditorButton.andSeparator")) }) : undefined}>
        {unsentCount ? t("bizcomp.submitToAuditorButton.submitWithCount", { count: unsentCount }) : t("bizcomp.submitToAuditorButton.submit")}
      </Button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md p-6">
            <h3 className="text-base font-bold text-gray-900">{t("bizcomp.submitToAuditorButton.confirmTitle")}</h3>
            <p className="mt-2 text-sm text-gray-600">{unsentCount ? t("bizcomp.submitToAuditorButton.confirmBodyWithDocs", { count: unsentCount }) : t("bizcomp.submitToAuditorButton.confirmBodyNoDocs")} {t("bizcomp.submitToAuditorButton.confirmBodyTail")}</p>
            {missingCount > 0 && (
              <p className="mt-3 flex items-start gap-2 rounded-lg border border-amber-100 bg-amber-50 p-2.5 text-xs text-amber-800">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {t("bizcomp.submitToAuditorButton.missingWarning", { count: missingCount })}
              </p>
            )}
            <div className="mt-5 flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setOpen(false)} disabled={busy}>
                {t("bizcomp.submitToAuditorButton.notYet")}
              </Button>
              <Button onClick={submit} disabled={busy}>
                {busy ? t("bizcomp.submitToAuditorButton.submitting") : t("bizcomp.submitToAuditorButton.submitPack")}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
