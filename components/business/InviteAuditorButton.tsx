"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { UserPlus, X, Star, Search, Award } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { getAuditorDirectory, inviteAuditor } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { DirectoryAuditor } from "@/lib/types";

const TAX_YEARS = ["2025/26", "2024/25", "2023/24"];

// Two ways to engage an auditor: browse the ranked directory, or invite a known auditor by email.
export default function InviteAuditorButton() {
  const { t } = useLanguage();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<"directory" | "email">("directory");
  const [taxYear, setTaxYear] = useState(TAX_YEARS[0]);
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [auditors, setAuditors] = useState<DirectoryAuditor[] | null>(null);

  useEffect(() => {
    if (!open || tab !== "directory") return;
    const t = setTimeout(() => {
      getAuditorDirectory(search).then(setAuditors).catch((e) => toast.error(errorMessage(e)));
    }, search ? 250 : 0);
    return () => clearTimeout(t);
  }, [open, tab, search]);

  function reset() {
    setOpen(false);
    setEmail("");
    setMessage("");
    setSearch("");
    setTaxYear(TAX_YEARS[0]);
    setAuditors(null);
    setTab("directory");
  }

  async function invite(auditorEmail: string, key: string) {
    if (!auditorEmail) return;
    setBusy(key);
    try {
      await inviteAuditor({ auditorEmail, taxYear, message });
      toast.success(t("bizcomp.inviteAuditorButton.invitationSentToast"));
      reset();
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <Button icon={<UserPlus className="h-4 w-4" />} onClick={() => setOpen(true)}>
        {t("bizcomp.inviteAuditorButton.inviteAuditor")}
      </Button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="flex max-h-[90vh] w-full max-w-lg flex-col p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <div>
                <h2 className="text-base font-bold text-gray-900">{t("bizcomp.inviteAuditorButton.modalTitle")}</h2>
                <p className="text-xs text-gray-500">{t("bizcomp.inviteAuditorButton.modalSubtitle")}</p>
              </div>
              <button onClick={reset} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex gap-1 border-b border-gray-100 px-6 pt-3">
              {(["directory", "email"] as const).map((tabKey) => (
                <button key={tabKey} onClick={() => setTab(tabKey)}
                  className={`rounded-t-lg px-3 py-2 text-sm font-medium ${tab === tabKey ? "border-b-2 border-brand-blue text-brand-blue" : "text-gray-500 hover:text-gray-700"}`}>
                  {tabKey === "directory" ? t("bizcomp.inviteAuditorButton.tabTopAuditors") : t("bizcomp.inviteAuditorButton.tabByEmail")}
                </button>
              ))}
            </div>

            <div className="space-y-4 overflow-y-auto p-6">
              <div className="grid grid-cols-2 gap-3">
                <Field label={t("bizcomp.inviteAuditorButton.taxYearLabel")} required>
                  <Select value={taxYear} onChange={(e) => setTaxYear(e.target.value)}>
                    {TAX_YEARS.map((y) => <option key={y}>{y}</option>)}
                  </Select>
                </Field>
                <Field label={t("bizcomp.inviteAuditorButton.messageLabel")}>
                  <Input value={message} onChange={(e) => setMessage(e.target.value)} placeholder={t("bizcomp.inviteAuditorButton.messagePlaceholder")} />
                </Field>
              </div>

              {tab === "directory" ? (
                <>
                  <div className="relative">
                    <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                    <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={t("bizcomp.inviteAuditorButton.searchPlaceholder")} className="pl-9" />
                  </div>
                  {auditors === null ? (
                    <p className="py-6 text-center text-sm text-gray-400">{t("bizcomp.inviteAuditorButton.loadingAuditors")}</p>
                  ) : auditors.length === 0 ? (
                    <p className="py-6 text-center text-sm text-gray-400">{t("bizcomp.inviteAuditorButton.noAuditorsFound")}</p>
                  ) : (
                    <div className="space-y-2">
                      {auditors.map((a) => (
                        <div key={a.id} className="flex items-center gap-3 rounded-lg border border-gray-100 p-3">
                          <div className="min-w-0 flex-1">
                            <p className="truncate font-medium text-gray-800">{a.name}</p>
                            <p className="truncate text-xs text-gray-500">{a.firm}</p>
                            <p className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                              <span className="inline-flex items-center gap-1">
                                <Star className={`h-3.5 w-3.5 ${a.averageRating ? "fill-amber-400 text-amber-400" : "text-gray-300"}`} />
                                {a.averageRating ? `${a.averageRating.toFixed(1)} (${a.totalReviews})` : t("bizcomp.inviteAuditorButton.noRatingsYet")}
                              </span>
                              <span className="inline-flex items-center gap-1"><Award className="h-3.5 w-3.5 text-gray-400" />{t("bizcomp.inviteAuditorButton.completedCount", { count: a.completedAudits })}</span>
                            </p>
                          </div>
                          <Button className="px-3 py-1.5 text-xs" disabled={busy !== null} onClick={() => invite(a.email, a.id)}>
                            {busy === a.id ? t("bizcomp.inviteAuditorButton.sendingEllipsis") : t("bizcomp.inviteAuditorButton.invite")}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <form onSubmit={(e) => { e.preventDefault(); invite(email, "email"); }} className="space-y-4">
                  <Field label={t("bizcomp.inviteAuditorButton.emailLabel")} required>
                    <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="auditor@firm.lk" required />
                  </Field>
                  <p className="text-xs text-gray-500">{t("bizcomp.inviteAuditorButton.emailHint")}</p>
                  <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="secondary" onClick={reset} disabled={busy !== null}>{t("common.cancel")}</Button>
                    <Button type="submit" disabled={busy !== null}>{busy === "email" ? t("bizcomp.inviteAuditorButton.sendingDots") : t("bizcomp.inviteAuditorButton.sendInvitation")}</Button>
                  </div>
                </form>
              )}
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
