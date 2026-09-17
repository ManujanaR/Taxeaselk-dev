"use client";

import { Printer } from "lucide-react";
import StatCard from "@/components/ui/StatCard";
import Button from "@/components/ui/Button";
import T from "@/components/layout/T";
import CitTaxComputationBanner from "./CitTaxComputationBanner";
import CitComputationPrintout from "./CitComputationPrintout";
import FinancialInputsForm from "./FinancialInputsForm";
import { lkr } from "@/lib/format";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { Company, FinancialsView as FinancialsData, StatutoryDocument } from "@/lib/types";

export default function FinancialsView({ data, documents, company }: { data: FinancialsData; documents: StatutoryDocument[]; company: Company }) {
  const { t } = useLanguage();
  const c = data.computed;
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-gray-900">
            <T k="pages.financials.title" />
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            <T k="pages.financials.subtitle" />
          </p>
        </div>
        {c && (
          <Button variant="secondary" icon={<Printer className="h-4 w-4" />} onClick={() => window.print()}>
            {t("bizcomp.financialsView.printComputation")}
          </Button>
        )}
      </div>

      {c ? (
        <>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-5">
            <StatCard label={t("bizcomp.financialsView.statGrossTurnover")} value={lkr(c.grossProfit + (data.inputs?.costOfSales ?? 0), { compact: true })} hint={t("bizcomp.financialsView.hintCommercialInflows")} />
            <StatCard label={t("bizcomp.financialsView.statCostOfSales")} value={lkr(data.inputs?.costOfSales, { compact: true })} hint={t("bizcomp.financialsView.hintDirectProductionCosts")} />
            <StatCard label={t("bizcomp.financialsView.statGrossProfit")} value={lkr(c.grossProfit, { compact: true })} hint={t("bizcomp.financialsView.hintTradingMargin", { percent: c.grossMarginPercent })} />
            <StatCard label={t("bizcomp.financialsView.statOperatingOpex")} value={lkr(data.inputs?.operatingExpenses, { compact: true })} hint={t("bizcomp.financialsView.hintAdminSalesOverheads")} />
            <StatCard label={t("bizcomp.financialsView.statAccountingProfit")} value={lkr(c.accountingProfit, { compact: true })} hint={t("bizcomp.financialsView.hintRevenueMinusExpenses")} valueClassName="text-brand-blue" />
          </div>
          <div className="mt-6">
            <CitTaxComputationBanner computed={c} inputs={data.inputs!} rateCategory={data.rateCategory} />
          </div>
          <CitComputationPrintout computed={c} inputs={data.inputs!} company={company} rateCategory={data.rateCategory} />
        </>
      ) : (
        <div className="mt-6 rounded-card border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-500">
          {t("bizcomp.financialsView.emptyStateHint")}
        </div>
      )}

      <div className="mt-6">
        <FinancialInputsForm initial={data.inputs} documents={documents} />
      </div>
    </div>
  );
}
