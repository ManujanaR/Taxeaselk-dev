import T from "@/components/layout/T";

export default function BusinessTopBarBadges({ companyName, financialYear }: { companyName: string; financialYear: string }) {
  return (
    <>
      <span className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-sm font-medium text-brand-blue">{companyName}</span>
      <span className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-600"><T k="bizpage.topBar.fy" params={{ year: financialYear }} /></span>
    </>
  );
}
