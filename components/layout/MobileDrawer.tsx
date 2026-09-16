"use client";

import { ReactNode, useEffect } from "react";
import { usePathname } from "next/navigation";
import { HelpCircle, X } from "lucide-react";
import Sidebar, { NavItem } from "@/components/layout/Sidebar";
import LanguageToggle from "@/components/layout/LanguageToggle";
import { useMobileNav } from "@/lib/mobile-nav";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { TranslationKey } from "@/lib/i18n/translations";

// Below `lg`, navigation lives in a left slide-in drawer opened by the TopBar
// hamburger. Reuses <Sidebar> so the nav stays identical to the desktop rail,
// and gives the top-bar's desktop-only chrome (context, rating, help, language)
// a home on mobile.
export default function MobileDrawer({
  context,
  extra,
  ...props
}: {
  workspaceLabelKey: TranslationKey;
  navItems: NavItem[];
  settingsHref?: string;
  badgeHrefs?: string[];
  context?: ReactNode; // company/FY (business) or firm (auditor) — same node as the TopBar
  extra?: ReactNode; // auditor rating pill
}) {
  const { open, setOpen } = useMobileNav();
  const { t } = useLanguage();
  const pathname = usePathname();

  // Close on navigation.
  useEffect(() => setOpen(false), [pathname, setOpen]);

  // Close on Esc.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  return (
    <div className="lg:hidden" aria-hidden={!open}>
      {open && <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setOpen(false)} />}
      <div
        className={`fixed inset-y-0 left-0 z-50 transition-transform duration-200 ${open ? "translate-x-0" : "-translate-x-full"}`}
      >
        <button
          onClick={() => setOpen(false)}
          aria-label="Close menu"
          className="absolute right-2 top-3 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"
        >
          <X className="h-5 w-5" />
        </button>
        <Sidebar
          {...props}
          header={
            context || extra ? (
              // Context + rating sit up top so the rating's downward popover has room.
              <div className="space-y-2 border-b border-gray-100 px-4 py-3">
                {context && <div className="flex flex-wrap items-center gap-2">{context}</div>}
                {extra}
              </div>
            ) : undefined
          }
          footer={
            <div className="space-y-3 border-t border-gray-100 p-4">
              <a
                href="https://taxeaselk-marketing.vercel.app/#contact"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-brand-blue"
              >
                <HelpCircle className="h-4 w-4" />
                {t("common.help")}
              </a>
              <LanguageToggle />
            </div>
          }
        />
      </div>
    </div>
  );
}
