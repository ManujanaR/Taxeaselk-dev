import DiscussionsManager from "@/components/DiscussionsManager";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import { getSession } from "@/lib/auth";
import type { Thread } from "@/lib/types";

export default async function DiscussionsPage() {
  const [session, threads] = await Promise.all([getSession("business"), apiServer<Thread[]>("/api/threads")]);
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">
        <T k="pages.discussions.title" />
      </h1>
      <p className="mb-6 mt-1 text-sm text-gray-500">
        <T k="pages.discussions.subtitle" />
      </p>
      <DiscussionsManager role="business" initialThreads={threads} userId={session.user.id} />
    </div>
  );
}
