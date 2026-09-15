import DiscussionsManager from "@/components/DiscussionsManager";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import { getSession } from "@/lib/auth";
import type { EngagementRow, Thread } from "@/lib/types";

export default async function AuditorDiscussionsPage() {
  const [session, threads, engagements] = await Promise.all([getSession("auditor"), apiServer<Thread[]>("/api/threads"), apiServer<EngagementRow[]>("/api/auditor/engagements")]);
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900"><T k="audpage.discussions.title" /></h1>
      <p className="mb-6 mt-1 text-sm text-gray-500"><T k="audpage.discussions.subtitle" /></p>
      <DiscussionsManager role="auditor" initialThreads={threads} userId={session.user.id} engagements={engagements.filter((e) => e.status !== "invited").map((e) => ({ id: e.id, companyName: e.companyName }))} />
    </div>
  );
}
