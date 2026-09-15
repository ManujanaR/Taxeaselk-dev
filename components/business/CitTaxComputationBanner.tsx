"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Scale } from "lucide-react";
import Card from "@/components/ui/Card";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import { lkr } from "@/lib/format";
import type { FinancialInputs, FinancialsView } from "@/lib/types";

type Computed = NonNullable<FinancialsView["computed"]>;

// Statutory CIT reconciliation waterfall per Inland Revenue Act No. 24 of 2017.
export default function CitTaxComputationBanner({ computed: c, inputs, rateCategory }: { computed: Computed; inputs: FinancialInputs; rateCategory: string }) {
  const [open, setOpen] = useState(false);
  const { t } = useLanguage();
  const rows: [TranslationKey, number, string][] = [
    ["bizpage.citBanner.accountingProfit", c.accountingProfit, ""],
    ["bizpage.citBanner.disallowables", c.disallowables, "+"],
    ["bizpage.citBanner.allowances", c.allowances, "−"],
    ["bizpage.citBanner.taxableIncome", c.taxableIncome, "="],
  ];

  return (
    <Card className="overflow-hidden border-brand-blue/20 bg-gradient-to-br from-brand-bgblue to-white p-0">
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-blue/10 text-brand-blue">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">{t("bizpage.citBanner.title")}</p>
            <p className="text-xs text-gray-500">{rateCategory === "sme_14" ? t("bizpage.citBanner.concessionaryRate") : t("bizpage.citBanner.standardRate")} · {t("bizpage.citBanner.actReference")}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[11px] font-medium uppercase tracking-wider text-gray-400">{t("bizpage.citBanner.indicativeLiability")}</p>
          <p className="text-2xl font-extrabold text-brand-navy">{lkr(c.citLiability)}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-px border-t border-gray-100 bg-gray-100 md:grid-cols-5">
        {rows.map(([label, value, sign]) => (
          <div key={label} className="bg-white px-4 py-3">
            <p className="text-[11px] text-gray-500">{t(label)}</p>
            <p className={`mt-1 text-sm font-bold ${sign === "+" ? "text-amber-600" : sign === "−" ? "text-emerald-600" : "text-gray-900"}`}>{sign && sign !== "=" ? sign : ""}{lkr(value)}</p>
          </div>
        ))}
        <div className="bg-brand-navy px-4 py-3 text-white">
          <p className="text-[11px] opacity-80">{t("bizpage.citBanner.rateLine", { rate: c.citRatePercent })}</p>
          <p className="mt-1 text-sm font-bold">{lkr(c.citLiability)}</p>
        </div>
      </div>

      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center justify-center gap-1 border-t border-gray-100 py-2 text-xs font-medium text-brand-blue hover:bg-blue-50/50">
        {open ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        {open ? t("bizpage.citBanner.hideBreakdown") : t("bizpage.citBanner.showBreakdown")}
      </button>
      {open && (
        <div className="grid grid-cols-1 gap-4 border-t border-gray-100 bg-white px-6 py-4 text-xs text-gray-600 md:grid-cols-2">
          <div>
            <p className="font-semibold text-gray-800">{t("bizpage.citBanner.section11Header")}</p>
            <ul className="mt-1 space-y-1">
              <li className="flex justify-between"><span>{t("bizpage.citBanner.accountingDepreciation")}</span><span>{lkr(inputs.accountingDepreciation)}</span></li>
              <li className="flex justify-between"><span>{t("bizpage.citBanner.entertainmentExpenses")}</span><span>{lkr(inputs.entertainmentExpenses)}</span></li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-gray-800">{t("bizpage.citBanner.fourthScheduleHeader")}</p>
            <ul className="mt-1 space-y-1">
              <li className="flex justify-between"><span>{t("bizpage.citBanner.capitalAllowancesLine")}</span><span>{lkr(inputs.taxDepreciationAllowances)}</span></li>
            </ul>
            <p className="mt-2 text-[11px] text-gray-400">{t("bizpage.citBanner.flooredNote")}</p>
          </div>
        </div>
      )}
    </Card>
  );
}
