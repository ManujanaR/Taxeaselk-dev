"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Save } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { extractFinancials, saveFinancials } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { FinancialInputs, StatutoryDocument } from "@/lib/types";

const FIELDS: [keyof Omit<FinancialInputs, "sourceDocumentId">, TranslationKey, TranslationKey][] = [
  ["revenue", "bizcomp.financialInputsForm.fieldRevenue", "bizcomp.financialInputsForm.hintRevenue"],
  ["costOfSales", "bizcomp.financialInputsForm.fieldCostOfSales", "bizcomp.financialInputsForm.hintCostOfSales"],
  ["operatingExpenses", "bizcomp.financialInputsForm.fieldOperatingExpenses", "bizcomp.financialInputsForm.hintOperatingExpenses"],
  ["accountingDepreciation", "bizcomp.financialInputsForm.fieldAccountingDepreciation", "bizcomp.financialInputsForm.hintAccountingDepreciation"],
  ["entertainmentExpenses", "bizcomp.financialInputsForm.fieldEntertainmentExpenses", "bizcomp.financialInputsForm.hintEntertainmentExpenses"],
  ["taxDepreciationAllowances", "bizcomp.financialInputsForm.fieldCapitalAllowances", "bizcomp.financialInputsForm.hintCapitalAllowances"],
];

type Draft = Record<keyof Omit<FinancialInputs, "sourceDocumentId">, string> & { sourceDocumentId: string | null };
const toDraft = (v: FinancialInputs | null): Draft => ({
  revenue: v ? String(v.revenue) : "", costOfSales: v ? String(v.costOfSales) : "", operatingExpenses: v ? String(v.operatingExpenses) : "",
  accountingDepreciation: v ? String(v.accountingDepreciation) : "", entertainmentExpenses: v ? String(v.entertainmentExpenses) : "",
  taxDepreciationAllowances: v ? String(v.taxDepreciationAllowances) : "", sourceDocumentId: v?.sourceDocumentId ?? null,
});

// The six CIT inputs. "Extract" asks Gemini to read an uploaded statement and prefill; the user confirms and saves.
export default function FinancialInputsForm({ initial, documents }: { initial: FinancialInputs | null; documents: StatutoryDocument[] }) {
  const { t } = useLanguage();
  const router = useRouter();
  const [form, setForm] = useState<Draft>(toDraft(initial));
  const [confidence, setConfidence] = useState<Partial<Record<string, number>>>({});
  const [notes, setNotes] = useState("");
  const [docId, setDocId] = useState(initial?.sourceDocumentId ?? documents[0]?.id ?? "");
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);

  async function extract() {
    if (!docId) return toast.error(t("bizcomp.financialInputsForm.uploadFirstToast"));
    setExtracting(true);
    try {
      const r = await extractFinancials(docId);
      setForm((f) => {
        const next = { ...f, sourceDocumentId: docId };
        for (const [k] of FIELDS) if (r.inputs[k] != null) next[k] = String(r.inputs[k]);
        return next;
      });
      setConfidence(r.confidence);
      setNotes(r.notes);
      const found = FIELDS.filter(([k]) => r.inputs[k] != null).length;
      toast.success(t("bizcomp.financialInputsForm.extractedToast", { count: found }));
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
      const payload = Object.fromEntries(FIELDS.map(([k]) => [k, Number(form[k] || 0)])) as unknown as FinancialInputs;
      await saveFinancials({ ...payload, sourceDocumentId: form.sourceDocumentId });
      toast.success(t("bizcomp.financialInputsForm.savedToast"));
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
          <p className="font-semibold text-gray-800">{t("bizcomp.financialInputsForm.heading")}</p>
          <p className="text-xs text-gray-500">{t("bizcomp.financialInputsForm.subheading")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={docId} onChange={(e) => setDocId(e.target.value)} className="w-64" disabled={!documents.length}>
            {documents.length ? documents.map((d) => <option key={d.id} value={d.id}>{d.name}</option>) : <option value="">{t("bizcomp.financialInputsForm.noDocuments")}</option>}
          </Select>
          <Button type="button" variant="secondary" icon={<Sparkles className="h-4 w-4 text-brand-blue" />} onClick={extract} disabled={extracting || !documents.length}>
            {extracting ? t("bizcomp.financialInputsForm.readingDocument") : t("bizcomp.financialInputsForm.extractWithAi")}
          </Button>
        </div>
      </div>

      <form onSubmit={save} className="mt-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {FIELDS.map(([key, label, hint]) => {
            const conf = confidence[key];
            return (
              <Field key={key} label={t(label)}>
                <Input type="number" min={0} step="1" inputMode="numeric" placeholder="0" value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
                <p className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>{t(hint)}</span>
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
        {notes && <p className="mt-3 rounded-lg bg-amber-50 p-2.5 text-xs text-amber-800">{t("bizcomp.financialInputsForm.aiNotes", { notes })}</p>}
        <div className="mt-5 flex justify-end">
          <Button type="submit" icon={<Save className="h-4 w-4" />} disabled={saving}>
            {saving ? t("common.saving") : t("bizcomp.financialInputsForm.saveAndCompute")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
