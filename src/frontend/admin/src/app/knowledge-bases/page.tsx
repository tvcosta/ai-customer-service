import { Shell } from '@/components/layout/shell';
import type { KnowledgeBase } from '@/lib/types';

const mockKnowledgeBases: KnowledgeBase[] = [];

export default function KnowledgeBasesPage() {
  const knowledgeBases = mockKnowledgeBases;

  return (
    <Shell title="Knowledge Bases">
      <div className="rounded-lg bg-white shadow">
        {knowledgeBases.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-sm text-gray-500">No knowledge bases yet. Create one to get started.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {knowledgeBases.map((kb) => (
                <tr key={kb.id}>
                  <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">{kb.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{kb.description ?? '—'}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">{new Date(kb.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Shell>
  );
}
