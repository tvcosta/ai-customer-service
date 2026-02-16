import { Shell } from '@/components/layout/shell';
import { StatusBadge } from '@/components/features/status-badge';
import type { Interaction } from '@/lib/types';

const mockInteractions: Interaction[] = [];

export default function InteractionsPage() {
  const interactions = mockInteractions;

  return (
    <Shell title="Interactions">
      <div className="rounded-lg bg-white shadow">
        {interactions.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-sm text-gray-500">No interactions yet.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Question</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {interactions.map((interaction) => (
                <tr key={interaction.id}>
                  <td className="px-6 py-4 text-sm text-gray-900">{interaction.question.length > 80 ? `${interaction.question.slice(0, 80)}...` : interaction.question}</td>
                  <td className="whitespace-nowrap px-6 py-4"><StatusBadge status={interaction.status} /></td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">{new Date(interaction.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Shell>
  );
}
