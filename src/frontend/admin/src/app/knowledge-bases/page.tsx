import { Shell } from "@/components/layout/shell";

export default function KnowledgeBasesPage() {
  return (
    <Shell title="Knowledge Bases">
      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="text-xl font-semibold text-gray-900">Knowledge Bases</h2>
        <p className="mt-2 text-gray-600">Manage your knowledge base collections here.</p>
      </div>
    </Shell>
  );
}
