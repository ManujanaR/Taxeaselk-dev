"""Sri Lanka CIT waterfall (Inland Revenue Act No. 24 of 2017).

Accounting PBT = revenue - cost of sales - opex
Taxable income = max(0, PBT + Sec.11 disallowables - 4th Schedule allowances)
CIT = taxable income x rate (30% standard, 14% SME/export concessionary)
"""
from dataclasses import dataclass

RATES = {"standard_30": 30.0, "sme_14": 14.0}


@dataclass
class Waterfall:
    gross_profit: float
    gross_margin_percent: float
    accounting_profit: float
    disallowables: float
    allowances: float
    taxable_income: float
    cit_rate_percent: float
    cit_liability: float


def compute(revenue: float, cost_of_sales: float, operating_expenses: float, accounting_depreciation: float,
            entertainment_expenses: float, tax_depreciation_allowances: float, rate_category: str = "standard_30") -> Waterfall:
    gross_profit = revenue - cost_of_sales
    accounting_profit = gross_profit - operating_expenses
    disallowables = accounting_depreciation + entertainment_expenses  # Sec 11(1)(b), 11(1)(c)
    allowances = tax_depreciation_allowances  # Fourth Schedule
    taxable = max(0.0, accounting_profit + disallowables - allowances)
    rate = RATES.get(rate_category, 30.0)
    return Waterfall(
        gross_profit=round(gross_profit, 2),
        gross_margin_percent=round(gross_profit / revenue * 100, 1) if revenue else 0.0,
        accounting_profit=round(accounting_profit, 2),
        disallowables=round(disallowables, 2),
        allowances=round(allowances, 2),
        taxable_income=round(taxable, 2),
        cit_rate_percent=rate,
        cit_liability=round(taxable * rate / 100, 2),
    )


if __name__ == "__main__":
    w = compute(25_000_000, 15_200_000, 5_200_000, 1_800_000, 300_000, 1_500_000)
    assert (w.accounting_profit, w.taxable_income, w.cit_liability) == (4_600_000, 5_200_000, 1_560_000), w
    assert compute(25_000_000, 15_200_000, 5_200_000, 1_800_000, 300_000, 1_500_000, "sme_14").cit_liability == 728_000
    assert compute(1, 5, 0, 0, 0, 0).taxable_income == 0
    print("tax_engine ok")
