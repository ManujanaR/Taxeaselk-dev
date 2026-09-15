import { CheckCircle2, AlertTriangle, Clock, Loader2, Lock } from "lucide-react";
import Badge from "@/components/ui/Badge";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { DocStatus } from "@/lib/types";

export default function DocumentStatusBadge({ status, unsent = false }: { status: DocStatus | "uploading"; unsent?: boolean }) {
  const { t } = useLanguage();
  if (status === "uploading")
    return (
      <Badge tone="info">
        <Loader2 className="mr-1 h-3 w-3 animate-spin" /> {t("bizcomp.documentStatusBadge.uploading")}
      </Badge>
    );
  if (unsent)
    return (
      <Badge tone="neutral">
        <Lock className="mr-1 h-3 w-3" /> {t("bizcomp.documentStatusBadge.notSentToAuditor")}
      </Badge>
    );
  if (status === "verified")
    return (
      <Badge tone="success">
        <CheckCircle2 className="mr-1 h-3 w-3" /> {t("status.verified")}
      </Badge>
    );
  if (status === "review_required")
    return (
      <Badge tone="warning">
        <AlertTriangle className="mr-1 h-3 w-3" /> {t("status.reviewRequired")}
      </Badge>
    );
  return (
    <Badge tone="pending">
      <Clock className="mr-1 h-3 w-3" /> {t("bizcomp.documentStatusBadge.awaitingVerification")}
    </Badge>
  );
}
