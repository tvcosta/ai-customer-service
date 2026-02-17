'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shell } from '@/components/layout/shell';
import { StatsCard } from '@/components/features/stats-card';
import { StatusBadge } from '@/components/features/status-badge';
import { MessageSquare, CheckCircle, HelpCircle, Database, FileText } from 'lucide-react';
import { api } from '@/lib/api/client';
import type { DashboardStats, Interaction } from '@/lib/types';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentInteractions, setRecentInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const [statsData, interactionsData] = await Promise.all([
          api.getDashboardStats(),
          api.listInteractions(),
        ]);
        setStats(statsData);
        setRecentInteractions(interactionsData.slice(0, 5));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    void fetchData();
  }, []);

  if (loading) {
    return (
      <Shell title="Dashboard">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="rounded-lg bg-white p-6 shadow animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-8 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
        <div className="mt-8 rounded-lg bg-white p-6 shadow animate-pulse">
          <div className="h-5 bg-gray-200 rounded w-1/4 mb-4" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 rounded" />
            ))}
          </div>
        </div>
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell title="Dashboard">
        <div className="rounded-lg bg-red-50 border border-red-200 p-6">
          <p className="text-sm text-red-800">Error loading dashboard: {error}</p>
          <button
            type="button"
            onClick={() => router.refresh()}
            className="mt-3 text-sm font-medium text-red-700 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      </Shell>
    );
  }

  return (
    <Shell title="Dashboard">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <StatsCard
          title="Total Interactions"
          value={stats?.totalInteractions ?? 0}
          icon={<MessageSquare className="h-5 w-5" />}
        />
        <StatsCard
          title="Answered"
          value={stats?.answeredCount ?? 0}
          icon={<CheckCircle className="h-5 w-5" />}
        />
        <StatsCard
          title="Unknown"
          value={stats?.unknownCount ?? 0}
          icon={<HelpCircle className="h-5 w-5" />}
        />
        <StatsCard
          title="Knowledge Bases"
          value={stats?.knowledgeBaseCount ?? 0}
          icon={<Database className="h-5 w-5" />}
        />
        <StatsCard
          title="Documents"
          value={stats?.documentCount ?? 0}
          icon={<FileText className="h-5 w-5" />}
        />
      </div>

      <div className="mt-8 rounded-lg bg-white shadow">
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Recent Interactions</h2>
          <Link
            href="/interactions"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            View all
          </Link>
        </div>
        {recentInteractions.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-sm text-gray-500">
              No interactions yet.{' '}
              <Link href="/playground" className="font-medium text-indigo-600 hover:text-indigo-500">
                Use the Playground
              </Link>{' '}
              to ask your first question.
            </p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Question
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {recentInteractions.map((interaction) => (
                <tr
                  key={interaction.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => router.push(`/interactions/${interaction.id}`)}
                >
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {interaction.question.length > 100
                      ? `${interaction.question.slice(0, 100)}...`
                      : interaction.question}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <StatusBadge status={interaction.status} />
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {new Date(interaction.createdAt).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Shell>
  );
}
