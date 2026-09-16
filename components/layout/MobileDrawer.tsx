"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { X } from "lucide-react";
import Sidebar, { NavItem } from "@/components/layout/Sidebar";
import { useMobileNav } from "@/lib/mobile-nav";
import { TranslationKey } from "@/lib/i18n/translations";

// Below `lg`, navigation lives in a left slide-in drawer opened by the TopBar
// hamburger. Reuses <Sidebar> so the nav stays identical to the desktop rail.
export default function MobileDrawer(props: {
  workspaceLabelKey: TranslationKey;
  navItems: NavItem[];
  settingsHref?: string;
  badgeHrefs?: string[];
}) {
  const { open, setOpen } = useMobileNav();
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
        <Sidebar {...props} />
      </div>
    </div>
  );
}
