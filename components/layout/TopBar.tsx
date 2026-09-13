"use client";

import { HelpCircle } from "lucide-react";
import { ReactNode } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import LanguageToggle from "./LanguageToggle";
import NotificationBell from "./NotificationBell";
import ProfileMenu from "./ProfileMenu";

interface TopBarProps {
  // Left-side content differs per portal: company + FY pickers for the
  // Business view, "All Companies" + year pickers for the Auditor view.
  leftContent: ReactNode;
  roleLabel: string; // "Admin" or "Auditor" — shown as the small chip next to the avatar
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

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-100 bg-white px-6">
      <div className="flex items-center gap-3">
        {leftContent}
        <LanguageToggle />
      </div>

      <div className="flex items-center gap-4">
        {extraContent}


        <NotificationBell />

        <a
          href="https://taxeaselk-marketing.vercel.app/#contact"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t("common.help")}
          title="TaxEaseLK Help & Contact"
          className="text-gray-400 hover:text-gray-600 transition-colors"
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
