"use client";

import { useEffect, useState } from "react";
import { X, Plus, Trash2, ClipboardList } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { getChecklistPresets, publishChecklist } from "@/lib/api/auditor";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { ChecklistItem, ChecklistPreset } from "@/lib/types";

type Item = ChecklistPreset["items"][number];

export default function AuditorChecklistModal({ engagementId, companyName, existing, onClose, onPublished }: { engagementId: string; companyName: string; existing: ChecklistItem[]; onClose: () => void; onPublished: () => void }) {
  const { t } = useLanguage();
  const [presets, setPresets] = useState<ChecklistPreset[]>([]);
  const [items, setItems] = useState<Item[]>(existing.map(({ name, category, description, required }) => ({ name, category, description, required })));
  const [custom, setCustom] = useState({ name: "", category: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getChecklistPresets().then(setPresets).catch(() => {});
  }, []);

  async function publish() {
    setBusy(true);
    try {
      await publishChecklist(engagementId, items);
      toast.success(t("audcomp.checklist.publishedTo", { company: companyName }));
      onPublished();
    } catch (e) {
      toast.error(errorMessage(e));
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4">
      <Card className="flex max-h-[90vh] w-full max-w-2xl flex-col p-0">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <div className="flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-brand-blue" />
            <div>
              <h2 className="text-base font-bold text-gray-900">{t("audcomp.checklist.headingWithCompany", { company: companyName })}</h2>
              <p className="text-xs text-gray-500">{t("audcomp.checklist.subtitle")}</p>
            </div>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
        </div>

        <div className="flex flex-wrap gap-2 border-b border-gray-100 px-6 py-3">
          {presets.map((p) => (
            <button key={p.id} onClick={() => setItems(p.items)} className="rounded-full border border-gray-200 px-3 py-1 text-xs font-medium text-gray-700 hover:border-brand-blue hover:text-brand-blue">{p.name}</button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {items.length === 0 && <p className="py-6 text-center text-sm text-gray-400">{t("audcomp.checklist.emptyState")}</p>}
          <ul className="space-y-2">
            {items.map((it, idx) => (
              <li key={idx} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-800">{it.name}</p>
                  <p className="text-[11px] text-gray-400">{it.category}{it.description ? ` · ${it.description}` : ""}</p>
                </div>
                <button onClick={() => setItems(items.map((x, i) => (i === idx ? { ...x, required: !x.required } : x)))} className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${it.required ? "bg-red-50 text-red-700" : "bg-gray-100 text-gray-600"}`}>{it.required ? t("common.required") : t("common.optional")}</button>
                <button onClick={() => setItems(items.filter((_, i) => i !== idx))} className="rounded-lg p-1 text-gray-400 hover:bg-red-50 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>
              </li>
            ))}
          </ul>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!custom.name.trim()) return;
              setItems([...items, { name: custom.name.trim(), category: custom.category.trim() || t("audcomp.checklist.customCategory"), description: "", required: true }]);
              setCustom({ name: "", category: "" });
            }}
            className="mt-4 flex gap-2"
          >
            <Input value={custom.name} onChange={(e) => setCustom({ ...custom, name: e.target.value })} placeholder={t("audcomp.checklist.customNamePlaceholder")} />
            <Input value={custom.category} onChange={(e) => setCustom({ ...custom, category: e.target.value })} placeholder={t("audcomp.checklist.categoryPlaceholder")} className="w-40" />
            <Button type="submit" variant="secondary" icon={<Plus className="h-4 w-4" />}>{t("audcomp.checklist.add")}</Button>
          </form>
        </div>

        <div className="flex items-center justify-between border-t border-gray-100 px-6 py-4">
          <p className="text-xs text-gray-500">{t("audcomp.checklist.itemsSummary", { count: items.length, required: items.filter((i) => i.required).length })}</p>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={onClose} disabled={busy}>{t("common.cancel")}</Button>
            <Button onClick={publish} disabled={busy || items.length === 0}>{busy ? t("audcomp.checklist.publishing") : t("audcomp.checklist.savePublish")}</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
