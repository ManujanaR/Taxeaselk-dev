import { LayoutGrid, Building2, FileText, FolderDown, Inbox, MessagesSquare, ScrollText, Settings as SettingsIcon } from "lucide-react";
import Sidebar, { NavItem } from "@/components/layout/Sidebar";
import TopBar from "@/components/layout/TopBar";
import AuditorRankRating from "@/components/layout/AuditorRankRating";
import { formattedUserId, getSession, initials } from "@/lib/auth";

const navItems: NavItem[] = [
  { href: "/auditor-dashboard", labelKey: "sidebar.dashboard", icon: <LayoutGrid className="h-4 w-4" /> },
  { href: "/companies", labelKey: "sidebar.companies", icon: <Building2 className="h-4 w-4" /> },
  { href: "/auditor-documents", labelKey: "sidebar.documents", icon: <FileText className="h-4 w-4" /> },
  { href: "/responses", labelKey: "sidebar.responses", icon: <FolderDown className="h-4 w-4" /> },
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
    <div className="flex h-screen bg-gray-50">
      <Sidebar workspaceLabelKey="sidebar.auditorWorkspace" navItems={navItems} settingsHref="/auditor-settings" badgeHrefs={["/requests", "/responses", "/auditor-discussions"]} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          roleLabel="Auditor"
          userInitials={initials(user.fullName)}
          displayName={user.fullName}
          email={user.email}
          userId={formattedUserId(session)}
          settingsHref="/auditor-settings"
          extraContent={<AuditorRankRating />}
          leftContent={
            <span className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-600">{auditorProfile?.firmName}</span>
          }
        />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
