"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, Download, FileText, RefreshCw } from "lucide-react";
import Card from "@/components/ui/Card";
import StatCard from "@/components/ui/StatCard";
import DocumentUploadZone from "./DocumentUploadZone";
import DocumentStatusBadge from "./DocumentStatusBadge";
import AuditorDocumentChecklist from "./AuditorDocumentChecklist";
import { deleteDocument, replaceDocument, uploadDocument } from "@/lib/api/business";
import { validateFiles, ACCEPT_ATTR } from "@/lib/files";
import { date, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { ChecklistItem, DocumentsView } from "@/lib/types";

export default function DocumentsManager({ data }: { data: DocumentsView }) {
  const router = useRouter();
  const [target, setTarget] = useState<ChecklistItem | null>(null);
  const [uploading, setUploading] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const replaceInputRef = useRef<HTMLInputElement>(null);
  const [replacingId, setReplacingId] = useState<string | null>(null);

  async function onReplacePicked(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    const id = replacingId;
    if (!file || !id) return;
    const { valid, rejected } = validateFiles([file]);
    if (rejected.length) return toast.error(rejected[0].reason);
    try {
      await replaceDocument(id, valid[0]);
      toast.success(`Replaced with ${file.name}. Your auditor will re-check it.`);
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setReplacingId(null);
    }
  }

  async function onFilesAccepted(files: File[]) {
    setUploading((u) => [...u, ...files.map((f) => f.name)]);
    for (const file of files) {
      try {
        await uploadDocument(file, target?.category || "General", target?.id);
        toast.success(`${file.name} uploaded.`);
      } catch (e) {
        toast.error(`${file.name}: ${errorMessage(e)}`);
      } finally {
        setUploading((u) => u.filter((n) => n !== file.name));
      }
    }
    setTarget(null);
    router.refresh();
  }

  async function remove(id: string, name: string) {
    if (!confirm(`Delete ${name}?`)) return;
    try {
      await deleteDocument(id);
      toast.success(`${name} deleted.`);
      router.refresh();
    } catch (e) {
      toast.error(errorMessage(e));
    }
  }

  return (
    <>
      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Uploaded" value={data.uploadedCount} hint={data.unsentCount ? `${data.unsentCount} not yet sent to auditor` : "All sent to auditor"} />
        <StatCard label="Verified by Auditor" value={data.verifiedCount} valueClassName="text-status-success" />
        <StatCard label="Review Required" value={data.reviewRequiredCount} valueClassName={data.reviewRequiredCount ? "text-status-warning" : ""} />
        <StatCard label="Missing from Checklist" value={data.missingCount} valueClassName={data.missingCount ? "text-status-critical" : "text-status-success"} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_380px]">
        <DocumentUploadZone onFilesAccepted={onFilesAccepted} preselectedType={target?.name ?? null} onClearPreselectedType={() => setTarget(null)} fileInputRef={fileInputRef} />
        <AuditorDocumentChecklist checklist={data.checklist} onPickItem={(item) => { setTarget(item); fileInputRef.current?.click(); }} />
      </div>

      <Card className="mt-6 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-4 py-3">Document</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Uploaded</th>
              <th className="px-4 py-3">Size</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {uploading.map((name) => (
              <tr key={`up-${name}`} className="bg-blue-50/30">
                <td className="px-4 py-3 font-medium text-gray-700">{name}</td>
                <td className="px-4 py-3 text-gray-400">{target?.category ?? "—"}</td>
                <td className="px-4 py-3"><DocumentStatusBadge status="uploading" /></td>
                <td className="px-4 py-3 text-gray-400">—</td>
                <td className="px-4 py-3 text-gray-400">—</td>
                <td />
              </tr>
            ))}
            {data.documents.map((d) => (
              <tr key={d.id} className="hover:bg-gray-50/60">
                <td className="px-4 py-3">
                  <span className="flex items-center gap-2 font-medium text-gray-800">
                    <FileText className="h-4 w-4 text-gray-400" /> {d.name}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{d.docType}</td>
                <td className="px-4 py-3"><DocumentStatusBadge status={d.status} unsent={d.submittedAt === null} /></td>
                <td className="px-4 py-3 text-gray-600">{date(d.createdAt)}</td>
                <td className="px-4 py-3 text-gray-600">{fileSize(d.sizeBytes)}</td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-1">
                    <a href={`/api/documents/${d.id}/file`} title="Download" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700">
                      <Download className="h-4 w-4" />
                    </a>
                    {d.status === "review_required" && (
                      <button onClick={() => { setReplacingId(d.id); replaceInputRef.current?.click(); }} title="Replace with a corrected file" className="rounded-lg p-1.5 text-gray-400 hover:bg-blue-50 hover:text-brand-blue">
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                    {d.status !== "verified" && (
                      <button onClick={() => remove(d.id, d.name)} title="Delete" className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {data.documents.length === 0 && uploading.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-sm text-gray-400">No documents uploaded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </Card>
      <input ref={replaceInputRef} type="file" className="hidden" accept={ACCEPT_ATTR} onChange={onReplacePicked} />
    </>
  );
}
