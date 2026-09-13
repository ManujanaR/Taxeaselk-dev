"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, AlertTriangle, CheckCircle2, MessagesSquare, Check, ChevronRight, WifiOff } from "lucide-react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { useRealtime } from "@/lib/realtime";
import { relative } from "@/lib/format";
import type { AppNotification } from "@/lib/api/notifications";

const TONE = {
  critical: { bg: "bg-red-50", text: "text-red-600", icon: AlertTriangle },
  warning: { bg: "bg-amber-50", text: "text-amber-600", icon: AlertTriangle },
  info: { bg: "bg-blue-50", text: "text-brand-blue", icon: MessagesSquare },
  success: { bg: "bg-emerald-50", text: "text-emerald-600", icon: CheckCircle2 },
};

// Pure view over the realtime context: notifications arrive by push, never by polling.
export default function NotificationBell() {
  const { t } = useLanguage();
  const router = useRouter();
  const { notifications: items, unreadCount: unread, connected, markRead, markAll } = useRealtime();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  function onItemClick(n: AppNotification) {
    if (!n.isRead) markRead(n.id);
    setOpen(false);
    if (n.link) router.push(n.link);
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        aria-label={t("common.notifications")}
        onClick={() => setOpen((o) => !o)}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
        title={connected ? "Live updates connected" : "Reconnecting to live updates..."}
      >
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-critical px-1 text-[10px] font-bold text-white shadow-sm ring-2 ring-white">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
        {!connected && <WifiOff className="absolute -bottom-0.5 -right-0.5 h-3 w-3 text-amber-500" />}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-96 overflow-hidden rounded-xl border border-gray-100 bg-white shadow-xl">
          <div className="flex items-center justify-between border-b border-gray-100 bg-gray-50/50 px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-gray-900">{t("common.notifications")}</span>
              {unread > 0 ? (
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-bold text-brand-blue">{unread} new</span>
              ) : (
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-500">All read</span>
              )}
            </div>
            {unread > 0 && (
              <button onClick={markAll} className="flex items-center gap-1 text-xs font-semibold text-brand-blue hover:underline">
                <Check className="h-3 w-3" />
                {t("common.markAllRead")}
              </button>
            )}
          </div>

          <div className="max-h-96 divide-y divide-gray-50 overflow-y-auto">
            {items.length === 0 ? (
              <div className="px-4 py-10 text-center text-gray-400">
                <Bell className="mx-auto mb-2 h-8 w-8 stroke-1 text-gray-300" />
                <p className="text-sm font-medium text-gray-700">No notifications yet</p>
              </div>
            ) : (
              items.map((n) => {
                const tone = TONE[n.type] ?? TONE.info;
                const Icon = tone.icon;
                return (
                  <button
                    key={n.id}
                    onClick={() => onItemClick(n)}
                    className={`flex w-full items-start gap-3 px-4 py-3.5 text-left transition-colors hover:bg-blue-50/40 ${!n.isRead ? "bg-blue-50/20" : "bg-white"}`}
                  >
                    <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${tone.bg} ${tone.text}`}>
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-1">
                        <p className={`truncate text-xs ${!n.isRead ? "font-bold text-gray-900" : "font-medium text-gray-700"}`}>{n.title}</p>
                        <span className="shrink-0 text-[10px] text-gray-400">{relative(n.createdAt)}</span>
                      </div>
                      <p className="mt-0.5 line-clamp-2 text-xs leading-relaxed text-gray-500">{n.message}</p>
                    </div>
                    {!n.isRead ? <span className="h-2 w-2 shrink-0 self-center rounded-full bg-brand-blue" /> : <ChevronRight className="h-3.5 w-3.5 shrink-0 self-center text-gray-300" />}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
