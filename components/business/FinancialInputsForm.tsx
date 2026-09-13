"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Save } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { extractFinancials, saveFinancials } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import type { FinancialInputs, StatutoryDocument } from "@/lib/types";

const FIELDS: [keyof Omit<FinancialInputs, "sourceDocumentId">, string, string][] = [
  ["revenue", "Revenue / Turnover", "Total sales for the year"],
  ["costOfSales", "Cost of Sales", "Direct production costs"],
  ["operatingExpenses", "Operating Expenses", "Admin, selling & distribution"],
  ["accountingDepreciation", "Accounting Depreciation", "Disallowed under Sec 11(1)(b)"],
  ["entertainmentExpenses", "Entertainment Expenses", "Disallowed under Sec 11(1)(c)"],
  ["taxDepreciationAllowances", "Capital Allowances", "Fourth Schedule tax depreciation"],
];

const EMPTY: FinancialInputs = { revenue: 0, costOfSales: 0, operatingExpenses: 0, accountingDepreciation: 0, entertainmentExpenses: 0, taxDepreciationAllowances: 0, sourceDocumentId: null };

// The six CIT inputs. "Extract" asks Gemini to read an uploaded statement and prefill; the user confirms and saves.
export default function FinancialInputsForm({ initial, documents }: { initial: FinancialInputs | null; documents: StatutoryDocument[] }) {
  const router = useRouter();
  const [form, setForm] = useState<FinancialInputs>(initial ?? EMPTY);
  const [confidence, setConfidence] = useState<Partial<Record<string, number>>>({});
  const [notes, setNotes] = useState("");
  const [docId, setDocId] = useState(initial?.sourceDocumentId ?? documents[0]?.id ?? "");
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);

  async function extract() {
    if (!docId) return toast.error("Upload a financial statement first.");
    setExtracting(true);
    try {
      const r = await extractFinancials(docId);
      setForm((f) => {
        const next = { ...f, sourceDocumentId: docId };
        for (const [k] of FIELDS) if (r.inputs[k] != null) next[k] = r.inputs[k] as number;
        return next;
      });
      setConfidence(r.confidence);
      setNotes(r.notes);
      const found = FIELDS.filter(([k]) => r.inputs[k] != null).length;
      toast.success(`Extracted ${found} of 6 figures. Review them, then save.`);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setExtracting(false);
    }
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await saveFinancials(form);
      toast.success("Figures saved. CIT computation updated.");
      setConfidence({});
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-semibold text-gray-800">Financial Inputs (LKR)</p>
          <p className="text-xs text-gray-500">Annual figures from your income statement and fixed asset schedule.</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={docId} onChange={(e) => setDocId(e.target.value)} className="w-64" disabled={!documents.length}>
            {documents.length ? documents.map((d) => <option key={d.id} value={d.id}>{d.name}</option>) : <option value="">No documents uploaded</option>}
          </Select>
          <Button type="button" variant="secondary" icon={<Sparkles className="h-4 w-4 text-brand-blue" />} onClick={extract} disabled={extracting || !documents.length}>
            {extracting ? "Reading document..." : "Extract with AI"}
          </Button>
        </div>
      </div>

      <form onSubmit={save} className="mt-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {FIELDS.map(([key, label, hint]) => {
            const conf = confidence[key];
            return (
              <Field key={key} label={label}>
                <Input type="number" min={0} step="1" value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })} />
                <p className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>{hint}</span>
                  {conf !== undefined && (
                    <span className={`rounded px-1.5 py-0.5 font-semibold ${conf >= 0.8 ? "bg-emerald-50 text-emerald-700" : conf >= 0.5 ? "bg-amber-50 text-amber-700" : "bg-red-50 text-red-700"}`}>
                      AI {Math.round(conf * 100)}%
                    </span>
                  )}
                </p>
              </Field>
            );
          })}
        </div>
        {notes && <p className="mt-3 rounded-lg bg-amber-50 p-2.5 text-xs text-amber-800">AI notes: {notes}</p>}
        <div className="mt-5 flex justify-end">
          <Button type="submit" icon={<Save className="h-4 w-4" />} disabled={saving}>
            {saving ? "Saving..." : "Save & Compute CIT"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
