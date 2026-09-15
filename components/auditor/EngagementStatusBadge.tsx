"use client";

import Badge, { BadgeTone } from "@/components/ui/Badge";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { EngagementStatus } from "@/lib/types";

export const ENGAGEMENT_STATUS: Record<EngagementStatus, { key: TranslationKey; tone: BadgeTone }> = {
  invited: { key: "audcomp.engagementStatus.invitation", tone: "warning" },
  declined: { key: "status.declined", tone: "neutral" },
  active: { key: "audcomp.engagementStatus.waitingForPack", tone: "pending" },
  under_review: { key: "status.underReview", tone: "info" },
  approved: { key: "status.approved", tone: "success" },
  terminated: { key: "audcomp.engagementStatus.terminated", tone: "neutral" },
};

export default function EngagementStatusBadge({ status }: { status: EngagementStatus }) {
  const { t } = useLanguage();
  const s = ENGAGEMENT_STATUS[status];
  return <Badge tone={s.tone}>{t(s.key)}</Badge>;
}
