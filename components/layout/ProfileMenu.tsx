"use client";

import { ReactNode, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronDown, Settings, LogOut, Copy, Check } from "lucide-react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api/client";
import { copyText } from "@/lib/format";
import { useRealtime } from "@/lib/realtime";

interface ProfileMenuProps {
  displayName: string;
  email: string;
  userInitials: string;
  userId: string;
  roleLabel: ReactNode; // small chip shown under the name, e.g. "Admin" or "Auditor"
  settingsHref: string;
}

export default function ProfileMenu({ displayName, email, userInitials, userId, roleLabel, settingsHref }: ProfileMenuProps) {
  const { t } = useLanguage();
  const router = useRouter();
  const { disconnect } = useRealtime();
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function logout() {
    setOpen(false);
    disconnect();
    try {
      await api("/api/auth/logout", { method: "POST" });
    } finally {
      // Clear anything the old prototype left behind in this browser.
      Object.keys(localStorage).filter((k) => k.startsWith("taxease_")).forEach((k) => localStorage.removeItem(k));
      router.push("/sign-in");
      router.refresh();
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <button onClick={() => setOpen((o) => !o)} className="flex items-center gap-2 rounded-lg px-1 py-1 hover:bg-gray-50 sm:px-2">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-600">{userInitials}</div>
        <span className="hidden text-sm font-medium text-gray-700 lg:inline">{roleLabel}</span>
        <ChevronDown className="hidden h-4 w-4 text-gray-400 lg:block" />
      </button>

      {open && (
        <div className="absolute right-0 z-40 mt-2 w-[calc(100vw-2rem)] max-w-xs rounded-card border border-gray-100 bg-white shadow-lg sm:w-72 sm:max-w-none">
          <div className="flex items-center gap-3 border-b border-gray-100 px-4 py-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-blue text-sm font-semibold text-white">{userInitials}</div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-gray-800">{displayName}</p>
              <p className="truncate text-xs text-gray-400">{email}</p>
              <div className="mt-1 flex items-center justify-between gap-1 rounded border border-gray-200/80 bg-gray-50 px-2 py-0.5">
                <span className="truncate font-mono text-[10px] font-bold text-gray-700">{userId}</span>
                <button
                  type="button"
                  onClick={async (e) => {
                    e.stopPropagation();
                    if (await copyText(userId)) {
                      setCopied(true);
                      setTimeout(() => setCopied(false), 1800);
                    }
                  }}
                  title="Copy User ID"
                  className="flex cursor-pointer items-center gap-0.5 text-[10px] font-semibold text-brand-blue hover:text-blue-700"
                >
                  {copied ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-600" />
                      <span className="text-emerald-600">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="p-1.5">
            <Link href={settingsHref} onClick={() => setOpen(false)} className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">
              <Settings className="h-4 w-4 text-gray-400" />
              {t("common.settings")}
            </Link>
          </div>

          <div className="border-t border-gray-100 p-1.5">
            <button type="button" onClick={logout} className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-status-critical hover:bg-red-50">
              <LogOut className="h-4 w-4" />
              {t("common.logout")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
