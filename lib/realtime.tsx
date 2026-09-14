"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AppNotification, getNotifications, markAllNotificationsAsRead, markNotificationAsRead } from "@/lib/api/notifications";
import { toast } from "@/lib/toast";

type RealtimeEvent = { id: number; type: "notification" | "refresh"; notification?: AppNotification };

interface Realtime {
  notifications: AppNotification[];
  unreadCount: number;
  /** Increments on every server event; components refetch client-side data with useEffect(..., [version]). */
  version: number;
  connected: boolean;
  markRead: (id: string) => void;
  markAll: () => void;
  disconnect: () => void;
}

const Ctx = createContext<Realtime | null>(null);

// One Server-Sent Events stream per tab. Every event re-renders the server components on the
// current page (debounced) and bumps `version` so client-fetched components refetch too.
export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [version, setVersion] = useState(0);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resync = useCallback(async () => {
    try {
      const data = await getNotifications();
      setNotifications(data.notifications);
      setUnreadCount(data.unreadCount);
    } catch {}
  }, []);

  const bump = useCallback(() => {
    setVersion((v) => v + 1);
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    refreshTimer.current = setTimeout(() => router.refresh(), 150);
  }, [router]);

  useEffect(() => {
    resync();
    let hadError = false;
    const es = new EventSource("/api/events");
    esRef.current = es;

    es.onopen = () => {
      setConnected(true);
      if (hadError) {
        hadError = false;
        resync();
        bump();
      }
    };
    es.onerror = () => {
      setConnected(false);
      hadError = true;
      // EventSource hides the HTTP status; a dead session is the one error worth acting on.
      fetch("/api/auth/me", { cache: "no-store" }).then((r) => {
        if (r.status === 401) {
          es.close();
          window.location.href = "/sign-in?reset=1";
        }
      }).catch(() => {});
    };
    const onNotification = (e: MessageEvent) => {
      const ev = JSON.parse(e.data) as RealtimeEvent;
      if (ev.notification) {
        const n = ev.notification;
        setNotifications((xs) => (xs.some((x) => x.id === n.id) ? xs : [n, ...xs].slice(0, 50)));
        setUnreadCount((u) => u + 1);
        toast[n.type === "critical" ? "error" : "success"](n.title);
      }
      bump();
    };
    const onRefresh = () => {
      resync(); // read-state may have changed in another tab
      bump();
    };
    es.addEventListener("notification", onNotification);
    es.addEventListener("refresh", onRefresh);

    return () => {
      es.close();
      esRef.current = null;
      if (refreshTimer.current) clearTimeout(refreshTimer.current);
    };
  }, [resync, bump]);

  const value = useMemo<Realtime>(
    () => ({
      notifications,
      unreadCount,
      version,
      connected,
      markRead: (id) => {
        setNotifications((xs) => xs.map((x) => (x.id === id && !x.isRead ? { ...x, isRead: true } : x)));
        setUnreadCount((u) => Math.max(0, u - 1));
        markNotificationAsRead(id).catch(() => {});
      },
      markAll: () => {
        setNotifications((xs) => xs.map((x) => ({ ...x, isRead: true })));
        setUnreadCount(0);
        markAllNotificationsAsRead().catch(() => {});
      },
      disconnect: () => esRef.current?.close(),
    }),
    [notifications, unreadCount, version, connected],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useRealtime(): Realtime {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useRealtime must be used inside RealtimeProvider");
  return ctx;
}
