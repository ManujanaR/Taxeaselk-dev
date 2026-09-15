"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { User, ShieldCheck, Clock, Star, XCircle, Mail } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import RateAuditorModal from "./RateAuditorModal";
import { cancelEngagement } from "@/lib/api/business";
import { date } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { EngagementView } from "@/lib/types";

const STATUS: Record<string, { label: TranslationKey; tone: BadgeTone }> = {
  invited: { label: "bizcomp.assignedAuditorCard.statusInvitationSent", tone: "warning" },
  active: { label: "bizcomp.assignedAuditorCard.statusEngagedPreparing", tone: "info" },
  under_review: { label: "status.underReview", tone: "info" },
  approved: { label: "status.approved", tone: "success" },
};

export default function AssignedAuditorCard({ view }: { view: EngagementView }) {
  const { t } = useLanguage();
  const router = useRouter();
  const [rateOpen, setRateOpen] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [busy, setBusy] = useState(false);
  const { engagement, auditor, review } = view;

  if (!engagement || !auditor) {
    return (
      <Card className="flex flex-col items-center justify-center p-8 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100 text-gray-400">
          <User className="h-7 w-7" />
        </div>
        <p className="mt-3 font-semibold text-gray-800">{t("bizcomp.assignedAuditorCard.noAuditorTitle")}</p>
        <p className="mt-1 max-w-sm text-sm text-gray-500">
          {t("bizcomp.assignedAuditorCard.noAuditorHint")}
        </p>
      </Card>
    );
  }

  const status = STATUS[engagement.status] ?? { label: engagement.status, tone: "neutral" as BadgeTone };
  const pending = engagement.status === "invited";

  async function cancel() {
    setBusy(true);
    try {
      await cancelEngagement();
      toast.success(t("bizcomp.assignedAuditorCard.cancelledToast"));
      setConfirmCancel(false);
      router.refresh();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Card className="p-6">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row">
          <div className="flex items-start gap-4">
            <div className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl text-white shadow-md ring-4 ${pending ? "bg-gradient-to-br from-amber-500 to-orange-600 ring-amber-50" : "bg-gradient-to-br from-blue-500 to-indigo-600 ring-blue-50"}`}>
              <User className="h-7 w-7" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-base font-bold text-gray-900">{auditor.name}</p>
                <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${pending ? "border-amber-200/60 bg-amber-50 text-amber-700" : "border-emerald-200/60 bg-emerald-50 text-emerald-700"}`}>
                  {pending ? <Clock className="h-3 w-3" /> : <ShieldCheck className="h-3 w-3" />}
                  {pending ? t("bizcomp.assignedAuditorCard.awaitingAcceptance") : t("bizcomp.assignedAuditorCard.appointedStatutoryAuditor")}
                </span>
              </div>
              <p className="mt-0.5 text-xs font-medium text-gray-500">{auditor.firm}</p>
              <p className="mt-1 flex items-center gap-1 text-[11px] text-gray-400">
                <Mail className="h-3 w-3" /> {auditor.email}
                <span className="mx-1">·</span>
                <Star className="h-3 w-3 fill-amber-400 text-amber-500" />
                {auditor.averageRating ? `${auditor.averageRating.toFixed(1)} (${auditor.totalReviews})` : t("bizcomp.assignedAuditorCard.noReviewsYet")}
              </p>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            {engagement.status !== "approved" && (
              <Button variant="secondary" icon={<XCircle className="h-4 w-4 text-red-500" />} className="px-3.5 py-2 text-xs text-red-600 hover:bg-red-50" onClick={() => setConfirmCancel(true)}>
                {pending ? t("bizcomp.assignedAuditorCard.cancelInvitation") : t("bizcomp.assignedAuditorCard.cancelEngagement")}
              </Button>
            )}
            {engagement.status === "approved" && !review && (
              <Button icon={<Star className="h-4 w-4" />} className="px-3.5 py-2 text-xs" onClick={() => setRateOpen(true)}>
                {t("bizcomp.assignedAuditorCard.rateAuditor")}
              </Button>
            )}
            {review && <Badge tone="success">{t("bizcomp.assignedAuditorCard.youRated", { rating: review.rating })}</Badge>}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-gray-100 pt-5 sm:grid-cols-4">
          <Meta label={t("bizcomp.assignedAuditorCard.metaEngagementStatus")}>
            <Badge tone={status.tone}>{t(status.label)}</Badge>
          </Meta>
          <Meta label={t("bizcomp.assignedAuditorCard.metaTaxYear")}>{engagement.taxYear}</Meta>
          <Meta label={t("bizcomp.assignedAuditorCard.metaPackSubmitted")}>{date(engagement.submittedAt)}</Meta>
          <Meta label={engagement.status === "approved" ? t("bizcomp.assignedAuditorCard.metaApprovedOn") : t("bizcomp.assignedAuditorCard.metaAcceptedOn")}>{date(engagement.status === "approved" ? engagement.approvedAt : engagement.acceptedAt)}</Meta>
        </div>
      </Card>

      {confirmCancel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md p-6">
            <h3 className="text-base font-bold text-gray-900">{pending ? t("bizcomp.assignedAuditorCard.cancelInvitationConfirmTitle") : t("bizcomp.assignedAuditorCard.cancelEngagementConfirmTitle")}</h3>
            <p className="mt-2 text-sm text-gray-600">
              {pending ? t("bizcomp.assignedAuditorCard.cancelInvitationBody") : t("bizcomp.assignedAuditorCard.cancelEngagementBody")}
            </p>
            <div className="mt-5 flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setConfirmCancel(false)} disabled={busy}>
                {t("bizcomp.assignedAuditorCard.keep")}
              </Button>
              <Button variant="danger" onClick={cancel} disabled={busy}>
                {busy ? t("bizcomp.assignedAuditorCard.cancelling") : t("bizcomp.assignedAuditorCard.yesCancel")}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {rateOpen && <RateAuditorModal auditorName={auditor.name} auditorFirm={auditor.firm} onClose={() => setRateOpen(false)} />}
    </>
  );
}

function Meta({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-[11px] font-medium uppercase tracking-wider text-gray-400">{label}</p>
      <div className="mt-1 text-sm font-semibold text-gray-800">{children}</div>
    </div>
  );
}
