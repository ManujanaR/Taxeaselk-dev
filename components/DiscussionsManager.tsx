"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Building2, MessagesSquare, Plus, Search, Send, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import { api } from "@/lib/api/client";
import { dateTime, relative } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import { useRealtime } from "@/lib/realtime";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { Role, Thread, ThreadMessage } from "@/lib/types";

const CATEGORIES = ["General", "Tax Computation", "Fixed Assets", "Documents", "Deadlines"];
const CATEGORY_LABEL_KEYS: Record<string, TranslationKey> = {
  General: "shared.categoryGeneral",
  "Tax Computation": "shared.categoryTaxComputation",
  "Fixed Assets": "shared.categoryFixedAssets",
  Documents: "shared.categoryDocuments",
  Deadlines: "shared.categoryDeadlines",
};
const FILTER_LABEL_KEYS: Record<"all" | "open" | "closed", TranslationKey> = {
  all: "shared.filterAll",
  open: "shared.filterOpen",
  closed: "shared.filterClosed",
};

// One component for both portals: threads on the left, message stream on the right, updated by push.
export default function DiscussionsManager({ role, initialThreads, userId, engagements = [] }: { role: Role; initialThreads: Thread[]; userId: string; engagements?: { id: string; companyName: string }[] }) {
  const { t } = useLanguage();
  const [threads, setThreads] = useState(initialThreads);
  const [activeId, setActiveId] = useState<string | null>(initialThreads[0]?.id ?? null);
  const [messages, setMessages] = useState<ThreadMessage[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "open" | "closed">("all");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const [newOpen, setNewOpen] = useState(false);
  const [draft, setDraft] = useState({ topic: "", category: CATEGORIES[0], text: "", engagementId: engagements[0]?.id ?? "" });
  const bottomRef = useRef<HTMLDivElement>(null);
  const { version } = useRealtime();

  const loadThreads = useCallback(async () => {
    try {
      setThreads(await api<Thread[]>("/api/threads"));
    } catch {}
  }, []);
  const loadMessages = useCallback(async (id: string) => {
    try {
      setMessages(await api<ThreadMessage[]>(`/api/threads/${id}/messages`));
      setThreads((ts) => ts.map((t) => (t.id === id ? { ...t, unreadCount: 0 } : t)));
    } catch {}
  }, []);

  useEffect(() => {
    if (activeId) loadMessages(activeId);
  }, [activeId, loadMessages]);

  useEffect(() => {
    if (version === 0) return; // initial data came from the server render
    loadThreads();
    if (activeId) loadMessages(activeId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  const active = threads.find((t) => t.id === activeId) ?? null;
  const visible = threads.filter((t) => (filter === "all" || t.status === filter) && (t.topic + t.companyName + t.auditorName).toLowerCase().includes(query.toLowerCase()));

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!active || !reply.trim()) return;
    setBusy(true);
    try {
      const m = await api<ThreadMessage>(`/api/threads/${active.id}/messages`, { method: "POST", json: { text: reply } });
      setMessages((ms) => [...ms, m]);
      setReply("");
      loadThreads();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function toggleStatus() {
    if (!active) return;
    try {
      const t = await api<Thread>(`/api/threads/${active.id}/status`, { method: "POST", json: { status: active.status === "open" ? "closed" : "open" } });
      setThreads((ts) => ts.map((x) => (x.id === t.id ? t : x)));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  }

  async function createThread(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const t = await api<Thread>("/api/threads", { method: "POST", json: draft });
      setThreads((ts) => [t, ...ts]);
      setActiveId(t.id);
      setNewOpen(false);
      setDraft({ topic: "", category: CATEGORIES[0], text: "", engagementId: engagements[0]?.id ?? "" });
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const canCreate = role === "business" || engagements.length > 0;

  return (
    <>
      <div className="grid h-[calc(100vh-11rem)] grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
        <Card className="flex flex-col overflow-hidden">
          <div className="border-b border-gray-100 p-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("shared.searchDiscussionsPlaceholder")} className="w-full rounded-lg border border-gray-200 py-2 pl-8 pr-2 text-sm focus:border-brand-blue focus:outline-none" />
              </div>
              {canCreate && (
                <button onClick={() => setNewOpen(true)} title={t("shared.newDiscussionTitle")} className="rounded-lg bg-brand-blue p-2 text-white hover:bg-brand-blue-dark">
                  <Plus className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="mt-2 flex gap-1">
              {(["all", "open", "closed"] as const).map((f) => (
                <button key={f} onClick={() => setFilter(f)} className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${filter === f ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                  {t(FILTER_LABEL_KEYS[f])}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 divide-y divide-gray-50 overflow-y-auto">
            {visible.length === 0 && <p className="p-6 text-center text-sm text-gray-400">{threads.length ? t("shared.noMatchingThreads") : role === "business" ? t("shared.startDiscussionBusiness") : t("shared.noClientDiscussionsYet")}</p>}
            {visible.map((t) => (
              <button key={t.id} onClick={() => setActiveId(t.id)} className={`flex w-full flex-col gap-1 px-3 py-3 text-left hover:bg-gray-50 ${t.id === activeId ? "bg-blue-50/60" : ""}`}>
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-semibold text-gray-800">{t.topic}</span>
                  {t.unreadCount > 0 && <span className="rounded-full bg-brand-blue px-1.5 text-[10px] font-bold text-white">{t.unreadCount}</span>}
                </div>
                <span className="flex items-center gap-1 text-[11px] text-gray-500">
                  <Building2 className="h-3 w-3" /> {role === "business" ? t.auditorName : t.companyName} · {t.category}
                </span>
                <span className="truncate text-xs text-gray-400">{t.lastMessage}</span>
                <span className="flex items-center gap-2 text-[10px] text-gray-400">
                  {relative(t.lastMessageAt)} <Badge tone={t.status === "open" ? "success" : "neutral"}>{t.status}</Badge>
                </span>
              </button>
            ))}
          </div>
        </Card>

        <Card className="flex flex-col overflow-hidden">
          {!active ? (
            <div className="flex flex-1 flex-col items-center justify-center text-gray-400">
              <MessagesSquare className="h-10 w-10 stroke-1" />
              <p className="mt-2 text-sm">{t("shared.selectDiscussion")}</p>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between border-b border-gray-100 px-5 py-3">
                <div>
                  <p className="font-semibold text-gray-800">{active.topic}</p>
                  <p className="text-xs text-gray-500">{role === "business" ? active.auditorName : active.companyName} · {active.category}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={active.status === "open" ? "success" : "neutral"}>{active.status}</Badge>
                  <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={toggleStatus}>
                    {active.status === "open" ? t("shared.markResolved") : t("shared.reopen")}
                  </Button>
                </div>
              </div>
              <div className="flex-1 space-y-3 overflow-y-auto bg-gray-50/50 p-5">
                {messages.map((m) => {
                  const mine = m.senderId === userId;
                  return (
                    <div key={m.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[70%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${mine ? "rounded-br-sm bg-brand-blue text-white" : "rounded-bl-sm border border-gray-100 bg-white text-gray-800"}`}>
                        {!mine && <p className="mb-0.5 text-[11px] font-semibold text-gray-500">{m.senderName}</p>}
                        <p className="whitespace-pre-wrap">{m.text}</p>
                        <p className={`mt-1 text-[10px] ${mine ? "text-white/70" : "text-gray-400"}`}>{dateTime(m.createdAt)}</p>
                      </div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>
              <form onSubmit={send} className="flex items-end gap-2 border-t border-gray-100 p-3">
                <textarea
                  rows={2}
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(e); } }}
                  placeholder={t("shared.replyToPlaceholder", { name: role === "business" ? active.auditorName : active.companyName })}
                  className="flex-1 resize-none rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
                />
                <Button type="submit" icon={<Send className="h-4 w-4" />} disabled={busy || !reply.trim()}>
                  {t("common.send")}
                </Button>
              </form>
            </>
          )}
        </Card>
      </div>

      {newOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="flex max-h-[90vh] w-full max-w-lg flex-col p-0">
            <div className="flex shrink-0 items-center justify-between border-b border-gray-100 px-6 py-4">
              <h2 className="text-base font-bold text-gray-900">{t("shared.newDiscussionHeading")}</h2>
              <button onClick={() => setNewOpen(false)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <form onSubmit={createThread} className="flex-1 space-y-4 overflow-y-auto p-6">
              {role === "auditor" && (
                <Field label={t("shared.clientCompany")} required>
                  <Select value={draft.engagementId} onChange={(e) => setDraft({ ...draft, engagementId: e.target.value })}>
                    {engagements.map((e) => <option key={e.id} value={e.id}>{e.companyName}</option>)}
                  </Select>
                </Field>
              )}
              <Field label={t("shared.topic")} required>
                <Input value={draft.topic} onChange={(e) => setDraft({ ...draft, topic: e.target.value })} required placeholder={t("shared.topicPlaceholder")} />
              </Field>
              <Field label={t("shared.category")}>
                <Select value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value })}>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{t(CATEGORY_LABEL_KEYS[c])}</option>)}
                </Select>
              </Field>
              <Field label={t("shared.message")} required>
                <textarea rows={4} required value={draft.text} onChange={(e) => setDraft({ ...draft, text: e.target.value })} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" />
              </Field>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setNewOpen(false)} disabled={busy}>{t("common.cancel")}</Button>
                <Button type="submit" disabled={busy}>{busy ? t("shared.posting") : t("shared.startDiscussion")}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </>
  );
}
