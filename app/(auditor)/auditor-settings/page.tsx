import Card from "@/components/ui/Card";
import AuditorProfileForm from "@/components/auditor/AuditorProfileForm";
import ChangePasswordForm from "@/components/ChangePasswordForm";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import type { AuditorProfileFull } from "@/lib/types";

export default async function AuditorSettingsPage() {
  const profile = await apiServer<AuditorProfileFull>("/api/auditor/profile");
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900"><T k="audpage.settings.title" /></h1>
        <p className="mt-1 text-sm text-gray-500"><T k="audpage.settings.subtitle" /></p>
      </div>
      <Card className="p-6">
        <AuditorProfileForm initial={profile} />
      </Card>
      <ChangePasswordForm />
    </div>
  );
}
