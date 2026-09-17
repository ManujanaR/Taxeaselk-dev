"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { lkr, date } from "@/lib/format";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { Company, FinancialInputs, FinancialsView } from "@/lib/types";

type Computed = NonNullable<FinancialsView["computed"]>;

// Print-only CIT computation sheet, styled after the "Blue & White Corporate"
// template. Hidden on screen; @media print (globals.css) hides the app shell and
// shows only this. Portaled to <body> so it becomes a direct body child, which
// the print CSS isolates with `body > *:not(.taxease-print-root)`.
export default function CitComputationPrintout({
  computed: c,
  inputs,
  company,
  rateCategory,
}: {
  computed: Computed;
  inputs: FinancialInputs;
  company: Company;
  rateCategory: string;
}) {
  const { t } = useLanguage();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  // Amount shown in parentheses for figures that are subtracted in the waterfall.
  const neg = (n: number) => `(${lkr(n)})`;

  return createPortal(
    <div className="taxease-print-root">
      <div className="relative mx-auto min-h-screen w-full max-w-[820px] bg-white px-12 pb-12 pt-0 font-sans text-[#161950]">
        {/* Corporate wave header (top-right bleed) + brand mark */}
        <svg viewBox="0 0 400 210" preserveAspectRatio="none" className="pointer-events-none absolute right-0 top-0 h-[210px] w-[58%]">
          <path d="M400,0 L400,185 C300,205 255,120 175,90 C105,64 55,38 0,0 Z" fill="#C7D2E8" opacity="0.55" />
          <path d="M400,0 L400,150 C320,172 270,95 195,68 C130,46 90,28 55,0 Z" fill="#161950" />
          <path d="M400,0 L400,108 C340,128 300,68 250,48 C210,32 188,18 165,0 Z" fill="#155DFC" opacity="0.9" />
        </svg>
        {/* White vector brand lockup, sitting on the navy wave */}
        <div className="absolute right-9 top-8 flex items-center gap-2.5 text-white">
          <svg viewBox="47 164 773 650" className="h-9 w-auto" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" d="M691.6 813C728.6 803.8 769.9 762 806.2 696.9C814.9 681.3 821 669.5 821 668C821 667.3 751.8 667 604.7 667L388.4 667L377.6 693.8C363.8 727.9 360.6 734.5 351.8 747.7C334.1 774.2 305.7 795.5 274.1 806C258.4 811.2 246.9 813.1 225 814C214.8 814.4 313.9 814.7 445.1 814.8C679.7 815 683.8 815 691.6 813ZM248 802.6C296 791.3 333.1 763 353.3 722.1C356.2 716.3 391.6 630.2 432 530.8L505.5 350.1L580 349.7C651.1 349.4 654.9 349.3 664.1 347.3C710.1 337.2 747.8 308.6 768.3 268.2C773.5 257.9 811 167.5 811 165.1C811 163.6 229.2 163.5 212.2 165C158.8 169.7 112 201 88.7 247.5C86.8 251.3 76.8 275.4 66.5 301C56.2 326.6 47.6 348.1 47.3 348.8C46.9 349.7 73.3 350 177.5 350C281.7 350 308.1 350.3 307.7 351.2C307.4 351.9 267.4 450.4 218.7 570C170 689.6 128.6 791.5 126.7 796.3L123.1 805.1L181.8 804.7C233.5 804.4 241.4 804.1 248 802.6ZM567.9 587.3C601.3 574.4 635 536.9 666.3 477.9C670 471 673 464.8 673 464.1C673 463.3 647.5 463.1 572.3 463.2L471.6 463.5L445.8 526.9C431.6 561.7 420 590.4 420 590.7C420 590.9 451.4 590.9 489.8 590.8L559.5 590.5L567.9 587.3Z" />
          </svg>
          <span className="text-lg font-extrabold tracking-tight">TaxEaseLK</span>
        </div>

        {/* Headline */}
        <header className="relative pt-28">
          <h1 className="text-5xl font-extrabold leading-none tracking-tight text-[#161950]">
            {t("bizcomp.printout.title")}
          </h1>
          <p className="mt-2 text-sm font-medium text-[#155DFC]">
            {company.financialYear} · {t("bizcomp.printout.subtitle")}
          </p>
        </header>

        {/* Meta + company detail */}
        <section className="mt-10 flex justify-between gap-8">
          <dl className="space-y-2 text-sm">
            <div className="flex gap-3">
              <dt className="w-24 font-bold">{t("bizcomp.printout.issueDate")}:</dt>
              <dd>{date(new Date().toISOString())}</dd>
            </div>
            <div className="flex gap-3">
              <dt className="w-24 font-bold">{t("bizcomp.printout.currency")}:</dt>
              <dd>LKR (Rs.)</dd>
            </div>
            <div className="flex gap-3">
              <dt className="w-24 font-bold">{t("bizcomp.printout.fiscalYear")}:</dt>
              <dd>{company.financialYear}</dd>
            </div>
          </dl>
          <div className="max-w-[46%] text-sm leading-relaxed">
            <p className="text-lg font-extrabold text-[#161950]">{t("bizcomp.printout.companyDetail")}</p>
            <p className="mt-1 font-semibold">{company.companyName}</p>
            {company.registeredAddress && <p className="text-[#3a3f6b]">{company.registeredAddress}</p>}
            {company.tinNumber && <p className="text-[#3a3f6b]">{t("bizcomp.printout.tin")}: {company.tinNumber}</p>}
            {company.contactEmail && <p className="text-[#3a3f6b]">E: {company.contactEmail}</p>}
            {company.contactPhone && <p className="text-[#3a3f6b]">P: {company.contactPhone}</p>}
          </div>
        </section>

        {/* Computation table */}
        <table className="mt-10 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-[#161950] text-left text-xs font-bold uppercase tracking-wider text-[#161950]">
              <th className="py-2">{t("bizcomp.printout.colDescription")}</th>
              <th className="py-2">{t("bizcomp.printout.colReference")}</th>
              <th className="py-2 text-right">{t("bizcomp.printout.colAmount")}</th>
            </tr>
          </thead>
          <tbody>
            <Row label={t("bizcomp.printout.revenue")} amount={lkr(inputs.revenue)} />
            <Row label={t("bizcomp.printout.costOfSales")} amount={neg(inputs.costOfSales)} />
            <Row label={t("bizcomp.printout.grossProfit")} amount={lkr(c.grossProfit)} strong />
            <Row label={t("bizcomp.printout.operatingExpenses")} amount={neg(inputs.operatingExpenses)} />
            <Row label={t("bizpage.citBanner.accountingProfit")} amount={lkr(c.accountingProfit)} strong />
            <Row label={t("bizpage.citBanner.disallowables")} ref_="Sec 11" amount={lkr(c.disallowables)} />
            <Row sub label={t("bizpage.citBanner.accountingDepreciation")} amount={lkr(inputs.accountingDepreciation)} />
            <Row sub label={t("bizpage.citBanner.entertainmentExpenses")} amount={lkr(inputs.entertainmentExpenses)} />
            <Row label={t("bizpage.citBanner.allowances")} ref_="4th Sch." amount={neg(c.allowances)} />
            <Row label={t("bizpage.citBanner.taxableIncome")} amount={lkr(c.taxableIncome)} strong />
          </tbody>
        </table>

        {/* Totals block */}
        <section className="mt-8 space-y-1.5">
          <Total label={t("bizpage.citBanner.taxableIncome")} value={lkr(c.taxableIncome)} />
          <Total label={t("bizcomp.printout.citRate")} value={`${c.citRatePercent}%`} />
          <div className="flex items-baseline gap-4 pt-1">
            <span className="text-2xl font-extrabold text-[#161950]">{t("bizcomp.printout.citLiability")}:</span>
            <span className="text-2xl font-extrabold text-[#155DFC]">{lkr(c.citLiability)}</span>
          </div>
        </section>

        {/* Notes / disclaimer — always starts on page 2 */}
        <footer className="break-before-page pt-16">
          <p className="text-lg font-extrabold text-[#161950]">{t("bizcomp.printout.notesHeader")}</p>
          <p className="mt-1 text-xs leading-relaxed text-[#3a3f6b]">{t("bizcomp.printout.notesBody")}</p>
          <p className="mt-2 text-xs text-[#3a3f6b]">
            {rateCategory === "sme_14" ? t("bizpage.citBanner.concessionaryRate") : t("bizpage.citBanner.standardRate")} · {t("bizpage.citBanner.actReference")}
          </p>
        </footer>
      </div>
    </div>,
    document.body,
  );
}

function Row({ label, amount, ref_ = "", strong = false, sub = false }: { label: string; amount: string; ref_?: string; strong?: boolean; sub?: boolean }) {
  return (
    <tr className="border-b border-[#E5E9F2]">
      <td className={`py-2.5 ${sub ? "pl-6 text-xs text-[#6b6f92]" : strong ? "font-bold text-[#161950]" : "text-[#3a3f6b]"}`}>{label}</td>
      <td className="py-2.5 text-xs text-[#6b6f92]">{ref_}</td>
      <td className={`py-2.5 text-right tabular-nums ${sub ? "text-xs text-[#6b6f92]" : strong ? "font-bold text-[#161950]" : "text-[#3a3f6b]"}`}>{amount}</td>
    </tr>
  );
}

function Total({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline gap-4">
      <span className="text-base font-bold text-[#161950]">{label}:</span>
      <span className="text-base tabular-nums text-[#3a3f6b]">{value}</span>
    </div>
  );
}
