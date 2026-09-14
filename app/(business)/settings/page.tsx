import Card from "@/components/ui/Card";
import CompanySettingsForm from "@/components/business/CompanySettingsForm";
import ChangePasswordForm from "@/components/ChangePasswordForm";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import { getSession } from "@/lib/auth";
import type { Company } from "@/lib/types";

export default async function BusinessSettingsPage() {
  const [company, session] = await Promise.all([apiServer<Company>("/api/company"), getSession("business")]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          <T k="pages.settings.title" />
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          <T k="pages.settings.subtitle" />
        </p>
      </div>
      <Card className="p-6">
        <CompanySettingsForm initial={company} fullName={session.user.fullName} />
      </Card>
      <ChangePasswordForm />
    </div>
  );
}
