import Badge, { BadgeTone } from "@/components/ui/Badge";
import type { EngagementStatus } from "@/lib/types";

export const ENGAGEMENT_STATUS: Record<EngagementStatus, { label: string; tone: BadgeTone }> = {
  invited: { label: "Invitation", tone: "warning" },
  declined: { label: "Declined", tone: "neutral" },
  active: { label: "Waiting for Pack", tone: "pending" },
  under_review: { label: "Under Review", tone: "info" },
  approved: { label: "Approved", tone: "success" },
  terminated: { label: "Terminated", tone: "neutral" },
};

export default function EngagementStatusBadge({ status }: { status: EngagementStatus }) {
  const s = ENGAGEMENT_STATUS[status];
  return <Badge tone={s.tone}>{s.label}</Badge>;
}
