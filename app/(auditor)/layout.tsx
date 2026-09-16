import { LayoutGrid, Building2, Inbox, MessagesSquare, ScrollText, Settings as SettingsIcon } from "lucide-react";
import Sidebar, { NavItem } from "@/components/layout/Sidebar";
import MobileDrawer from "@/components/layout/MobileDrawer";
import TopBar from "@/components/layout/TopBar";
import T from "@/components/layout/T";
import AuditorRankRating from "@/components/layout/AuditorRankRating";
import { formattedUserId, getSession, initials } from "@/lib/auth";
import { MobileNavProvider } from "@/lib/mobile-nav";
import { RealtimeProvider } from "@/lib/realtime";

const navItems: NavItem[] = [
  { href: "/auditor-dashboard", labelKey: "sidebar.dashboard", icon: <LayoutGrid className="h-4 w-4" /> },
  { href: "/companies", labelKey: "sidebar.companies", icon: <Building2 className="h-4 w-4" /> },
  { href: "/requests", labelKey: "sidebar.requests", icon: <Inbox className="h-4 w-4" /> },
  { href: "/auditor-discussions", labelKey: "sidebar.discussions", icon: <MessagesSquare className="h-4 w-4" /> },
  { href: "/audit-log", labelKey: "sidebar.auditLog", icon: <ScrollText className="h-4 w-4" /> },
  { href: "/auditor-settings", labelKey: "sidebar.settings", icon: <SettingsIcon className="h-4 w-4" /> },
];

// Shared shell for every page under the Auditor portal.
export default async function AuditorLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession("auditor");
  const { user, auditorProfile } = session;

  return (
    <RealtimeProvider>
    <MobileNavProvider>
    <div className="flex h-screen bg-gray-50">
      <Sidebar className="hidden lg:flex" workspaceLabelKey="sidebar.auditorWorkspace" navItems={navItems} settingsHref="/auditor-settings" badgeHrefs={["/requests", "/auditor-discussions"]} />
      <MobileDrawer workspaceLabelKey="sidebar.auditorWorkspace" navItems={navItems} settingsHref="/auditor-settings" badgeHrefs={["/requests", "/auditor-discussions"]} />
      <div className="flex min-w-0 flex-1 flex-col overflow-x-hidden">
        <TopBar
          roleLabel={<T k="shared.roleAuditor" />}
          userInitials={initials(user.fullName)}
          displayName={user.fullName}
          email={user.email}
          userId={formattedUserId(session)}
          settingsHref="/auditor-settings"
          extraContent={<AuditorRankRating />}
          leftContent={
            <span className="max-w-[40vw] truncate rounded-lg border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-600 sm:max-w-none">{auditorProfile?.firmName}</span>
          }
        />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
    </MobileNavProvider>
    </RealtimeProvider>
  );
}
