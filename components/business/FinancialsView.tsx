"use client";

import { Printer } from "lucide-react";
import StatCard from "@/components/ui/StatCard";
import Button from "@/components/ui/Button";
import T from "@/components/layout/T";
import CitTaxComputationBanner from "./CitTaxComputationBanner";
import FinancialInputsForm from "./FinancialInputsForm";
import { lkr } from "@/lib/format";
import type { FinancialsView as FinancialsData, StatutoryDocument } from "@/lib/types";

export default function FinancialsView({ data, documents }: { data: FinancialsData; documents: StatutoryDocument[] }) {
  const c = data.computed;
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            <T k="pages.financials.title" />
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            <T k="pages.financials.subtitle" />
          </p>
        </div>
        {c && (
          <Button variant="secondary" icon={<Printer className="h-4 w-4" />} onClick={() => window.print()}>
            Print Computation
          </Button>
        )}
      </div>

      {c ? (
        <>
          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-5">
            <StatCard label="Gross Turnover" value={lkr(c.grossProfit + (data.inputs?.costOfSales ?? 0), { compact: true })} hint="Commercial inflows" />
            <StatCard label="Cost of Sales" value={lkr(data.inputs?.costOfSales, { compact: true })} hint="Direct production costs" />
            <StatCard label="Gross Profit" value={lkr(c.grossProfit, { compact: true })} hint={`${c.grossMarginPercent}% trading margin`} />
            <StatCard label="Operating OPEX" value={lkr(data.inputs?.operatingExpenses, { compact: true })} hint="Admin & sales overheads" />
            <StatCard label="Accounting Profit" value={lkr(c.accountingProfit, { compact: true })} hint="Revenue − expenses" valueClassName="text-brand-blue" />
          </div>
          <div className="mt-6">
            <CitTaxComputationBanner computed={c} inputs={data.inputs!} rateCategory={data.rateCategory} />
          </div>
        </>
      ) : (
        <div className="mt-6 rounded-card border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-500">
          Enter your figures below (or extract them from an uploaded financial statement) to see the statutory CIT computation.
        </div>
      )}

      <div className="mt-6">
        <FinancialInputsForm initial={data.inputs} documents={documents} />
      </div>
    </div>
  );
}
