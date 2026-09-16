"use client";

import { HelpCircle, Menu } from "lucide-react";
import { ReactNode } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { useMobileNav } from "@/lib/mobile-nav";
import LanguageToggle from "./LanguageToggle";
import NotificationBell from "./NotificationBell";
import ProfileMenu from "./ProfileMenu";

interface TopBarProps {
  // Left-side content differs per portal: company + FY pickers for the
  // Business view, "All Companies" + year pickers for the Auditor view.
  leftContent: ReactNode;
  roleLabel: ReactNode; // "Admin" or "Auditor" — shown as the small chip next to the avatar
  userInitials: string;
  displayName: string;
  email: string;
  userId: string;
  settingsHref: string;
  extraContent?: ReactNode;
}

export default function TopBar({
  leftContent,
  roleLabel,
  userInitials,
  displayName,
  email,
  userId,
  settingsHref,
  extraContent,
}: TopBarProps) {
  const { t } = useLanguage();
  const { setOpen } = useMobileNav();

  return (
    <header className="flex h-16 shrink-0 items-center justify-between gap-2 border-b border-gray-100 bg-white px-4 sm:px-6">
      <div className="flex min-w-0 items-center gap-2 sm:gap-3">
        <button
          onClick={() => setOpen(true)}
          aria-label="Open menu"
          className="-ml-1 rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
        {leftContent}
        <LanguageToggle />
      </div>

      <div className="flex shrink-0 items-center gap-2 sm:gap-4">
        {extraContent}

        <NotificationBell />

        <a
          href="https://taxeaselk-marketing.vercel.app/#contact"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t("common.help")}
          title="TaxEaseLK Help & Contact"
          className="hidden text-gray-400 transition-colors hover:text-gray-600 sm:block"
        >
          <HelpCircle className="h-5 w-5" />
        </a>

        <ProfileMenu
          displayName={displayName}
          email={email}
          userInitials={userInitials}
          userId={userId}
          roleLabel={roleLabel}
          settingsHref={settingsHref}
        />
      </div>
    </header>
  );
}
