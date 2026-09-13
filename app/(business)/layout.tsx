import { LayoutGrid, FileText, DollarSign, UserCheck, MessagesSquare, Settings as SettingsIcon } from "lucide-react";
import Sidebar, { NavItem } from "@/components/layout/Sidebar";
import TopBar from "@/components/layout/TopBar";
import BusinessTopBarBadges from "@/components/layout/BusinessTopBarBadges";
import { formattedUserId, getSession, initials } from "@/lib/auth";
import { RealtimeProvider } from "@/lib/realtime";

const navItems: NavItem[] = [
  { href: "/dashboard", labelKey: "sidebar.dashboard", icon: <LayoutGrid className="h-4 w-4" /> },
  { href: "/documents", labelKey: "sidebar.documents", icon: <FileText className="h-4 w-4" /> },
  { href: "/financials", labelKey: "sidebar.financials", icon: <DollarSign className="h-4 w-4" /> },
  { href: "/auditor-review", labelKey: "sidebar.auditorReview", icon: <UserCheck className="h-4 w-4" /> },
  { href: "/discussions", labelKey: "sidebar.discussions", icon: <MessagesSquare className="h-4 w-4" /> },
  { href: "/settings", labelKey: "sidebar.settings", icon: <SettingsIcon className="h-4 w-4" /> },
];

// Shared shell for every page under the Business Owner portal.
export default async function BusinessLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession("business");
  const { user, company } = session;

  return (
    <RealtimeProvider>
    <div className="flex h-screen bg-brand-bgblue">
      <Sidebar workspaceLabelKey="sidebar.companyUser" navItems={navItems} settingsHref="/settings" badgeHrefs={["/auditor-review", "/discussions"]} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          roleLabel="Admin"
          userInitials={initials(user.fullName)}
          displayName={user.fullName}
          email={user.email}
          userId={formattedUserId(session)}
          settingsHref="/settings"
          leftContent={<BusinessTopBarBadges companyName={company?.companyName ?? ""} financialYear={company?.financialYear ?? ""} />}
        />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
    </RealtimeProvider>
  );
}
