"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { UserPlus, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { inviteAuditor } from "@/lib/api/business";
import { errorMessage, toast } from "@/lib/toast";

const TAX_YEARS = ["2025/26", "2024/25", "2023/24"];

// Invites an auditor already registered on TaxEaseLK by their sign-up email.
export default function InviteAuditorButton() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ auditorEmail: "", taxYear: TAX_YEARS[0], message: "" });
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await inviteAuditor(form);
      toast.success("Invitation sent. You'll be notified when the auditor responds.");
      setOpen(false);
      setForm({ auditorEmail: "", taxYear: TAX_YEARS[0], message: "" });
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Button icon={<UserPlus className="h-4 w-4" />} onClick={() => setOpen(true)}>
        Invite Auditor
      </Button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-lg p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <div>
                <h2 className="text-base font-bold text-gray-900">Invite Statutory Auditor</h2>
                <p className="text-xs text-gray-500">The auditor must already have a TaxEaseLK auditor account.</p>
              </div>
              <button onClick={() => setOpen(false)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={submit} className="space-y-4 p-6">
              <Field label="Auditor's registered email" required>
                <Input type="email" value={form.auditorEmail} onChange={(e) => setForm({ ...form, auditorEmail: e.target.value })} placeholder="auditor@firm.lk" required />
              </Field>
              <Field label="Tax year" required>
                <Select value={form.taxYear} onChange={(e) => setForm({ ...form, taxYear: e.target.value })}>
                  {TAX_YEARS.map((y) => (
                    <option key={y}>{y}</option>
                  ))}
                </Select>
              </Field>
              <Field label="Message (optional)">
                <textarea
                  rows={3}
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  placeholder="Context for the auditor, e.g. expected turnover, filing deadline..."
                  className="w-full rounded-lg border border-gray-300 p-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
                />
              </Field>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="secondary" onClick={() => setOpen(false)} disabled={busy}>
                  Cancel
                </Button>
                <Button type="submit" disabled={busy}>
                  {busy ? "Sending..." : "Send Invitation"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </>
  );
}
