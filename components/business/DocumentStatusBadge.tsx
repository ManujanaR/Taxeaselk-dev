import { CheckCircle2, AlertTriangle, Clock, Loader2 } from "lucide-react";
import Badge from "@/components/ui/Badge";
import type { DocStatus } from "@/lib/types";

export default function DocumentStatusBadge({ status }: { status: DocStatus | "uploading" }) {
  if (status === "uploading")
    return (
      <Badge tone="info">
        <Loader2 className="mr-1 h-3 w-3 animate-spin" /> Uploading
      </Badge>
    );
  if (status === "verified")
    return (
      <Badge tone="success">
        <CheckCircle2 className="mr-1 h-3 w-3" /> Verified
      </Badge>
    );
  if (status === "review_required")
    return (
      <Badge tone="warning">
        <AlertTriangle className="mr-1 h-3 w-3" /> Review Required
      </Badge>
    );
  return (
    <Badge tone="pending">
      <Clock className="mr-1 h-3 w-3" /> Awaiting Verification
    </Badge>
  );
}
