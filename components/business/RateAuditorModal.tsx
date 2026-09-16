"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Star, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { rateAuditor } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";

const LABEL_KEYS: Record<number, TranslationKey> = {
  1: "bizcomp.rateAuditorModal.labelNeedsImprovement",
  2: "bizcomp.rateAuditorModal.labelFair",
  3: "bizcomp.rateAuditorModal.labelGood",
  4: "bizcomp.rateAuditorModal.labelVeryGood",
  5: "bizcomp.rateAuditorModal.labelExceptional",
};
const DIMENSIONS: ["timeliness" | "communication" | "technical", TranslationKey, TranslationKey][] = [
  ["timeliness", "bizcomp.rateAuditorModal.dimTimeliness", "bizcomp.rateAuditorModal.dimTimelinessHint"],
  ["communication", "bizcomp.rateAuditorModal.dimCommunication", "bizcomp.rateAuditorModal.dimCommunicationHint"],
  ["technical", "bizcomp.rateAuditorModal.dimTaxRigor", "bizcomp.rateAuditorModal.dimTaxRigorHint"],
];

export default function RateAuditorModal({ auditorName, auditorFirm, onClose }: { auditorName: string; auditorFirm: string; onClose: () => void }) {
  const { t } = useLanguage();
  const router = useRouter();
  const [rating, setRating] = useState(5);
  const [hover, setHover] = useState(0);
  const [dims, setDims] = useState({ timeliness: 5, communication: 5, technical: 5 });
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await rateAuditor({ rating, ...dims, comment });
      toast.success(t("bizcomp.rateAuditorModal.thankYouToast"));
      onClose();
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <Card className="flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden p-0 shadow-2xl">
        <div className="flex shrink-0 items-center justify-between border-b border-gray-100 bg-gradient-to-r from-blue-50/70 to-white px-6 py-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-blue/10 ring-4 ring-blue-50">
              <Star className="h-5 w-5 fill-amber-400 text-amber-500" />
            </div>
            <div className="min-w-0">
              <h2 className="text-base font-bold text-gray-900">{t("bizcomp.rateAuditorModal.title")}</h2>
              <p className="truncate text-xs text-gray-500">
                {auditorName} • {auditorFirm}
              </p>
            </div>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={submit} className="flex-1 space-y-6 overflow-y-auto p-6">
          <div className="rounded-xl border border-gray-100 bg-gray-50/80 p-5 text-center">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">{t("bizcomp.rateAuditorModal.overallSatisfaction")}</p>
            <div className="flex items-center justify-center gap-2">
              {[1, 2, 3, 4, 5].map((s) => (
                <button key={s} type="button" onMouseEnter={() => setHover(s)} onMouseLeave={() => setHover(0)} onClick={() => setRating(s)} className="p-1 transition-transform hover:scale-110">
                  <Star className={`h-9 w-9 transition-colors ${(hover || rating) >= s ? "fill-amber-400 text-amber-400" : "fill-gray-200 text-gray-300"}`} />
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs font-medium text-brand-blue">{t(LABEL_KEYS[hover || rating])}</p>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {DIMENSIONS.map(([key, label, hint]) => (
              <div key={key} className="rounded-lg border border-gray-100 bg-white p-3 shadow-sm">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600">{t(label)}</span>
                  <span className="text-xs font-bold text-amber-600">{dims[key]} ★</span>
                </div>
                <input type="range" min={1} max={5} value={dims[key]} onChange={(e) => setDims({ ...dims, [key]: Number(e.target.value) })} className="h-1.5 w-full cursor-pointer accent-brand-blue" />
                <span className="mt-1 block text-[10px] text-gray-400">{t(hint)}</span>
              </div>
            ))}
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold text-gray-700">{t("bizcomp.rateAuditorModal.reviewCommentLabel")}</label>
            <textarea
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder={t("bizcomp.rateAuditorModal.reviewCommentPlaceholder")}
              className="w-full rounded-lg border border-gray-300 p-2.5 text-xs text-gray-900 placeholder:text-gray-400 focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
            />
          </div>

          <div className="flex items-center justify-end gap-3">
            <Button type="button" variant="secondary" onClick={onClose} disabled={busy}>
              {t("common.cancel")}
            </Button>
            <Button type="submit" disabled={busy}>
              {busy ? t("bizcomp.rateAuditorModal.submitting") : t("bizcomp.rateAuditorModal.submitReview", { rating })}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
