'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shell } from '@/components/layout/shell';
import { StatusBadge } from '@/components/features/status-badge';
import { api } from '@/lib/api/client';
import type { Interaction } from '@/lib/types';
import { ChevronLeft, ChevronRight } from 'lucide-react';

type StatusFilter = 'all' | 'answered' | 'unknown' | 'error';

const PAGE_SIZE = 10;

export default function InteractionsPage() {
  const router = useRouter();
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [page, setPage] = useState(0);

  const fetchInteractions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listInteractions();
      setInteractions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load interactions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchInteractions();
  }, [fetchInteractions]);

  // Reset page when filter changes
  useEffect(() => {
    setPage(0);
  }, [statusFilter]);

  const filtered = statusFilter === 'all'
    ? interactions
    : interactions.filter((i) => i.status === statusFilter);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const filterButtons: { label: string; value: StatusFilter }[] = [
    { label: 'All', value: 'all' },
    { label: 'Answered', value: 'answered' },
    { label: 'Unknown', value: 'unknown' },
    { label: 'Error', value: 'error' },
  ];

  return (
    <Shell title="Interactions">
      {/* Filters */}
      <div className="mb-6 flex items-center gap-2">
        {filterButtons.map((btn) => (
          <button
            key={btn.value}
            type="button"
            onClick={() => setStatusFilter(btn.value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              statusFilter === btn.value
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
            }`}
          >
            {btn.label}
            {btn.value === 'all' && (
              <span className="ml-1.5 text-xs opacity-75">({interactions.length})</span>
            )}
            {btn.value !== 'all' && (
              <span className="ml-1.5 text-xs opacity-75">
                ({interactions.filter((i) => i.status === btn.value).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Main content */}
      {loading ? (
        <div className="rounded-lg bg-white shadow">
          <div className="p-6 space-y-4 animate-pulse">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-gray-100 rounded" />
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="rounded-lg bg-red-50 border border-red-200 p-6">
          <p className="text-sm text-red-800">Error: {error}</p>
          <button
            type="button"
            onClick={() => void fetchInteractions()}
            className="mt-3 text-sm font-medium text-red-700 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="rounded-lg bg-white shadow overflow-hidden">
          {paginated.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-sm text-gray-500">
                {statusFilter === 'all'
                  ? 'No interactions yet. Use the Playground to ask your first question.'
                  : `No ${statusFilter} interactions found.`}
              </p>
            </div>
          ) : (
            <>
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
                  {paginated.map((interaction) => (
                    <tr
                      key={interaction.id}
                      className="cursor-pointer hover:bg-gray-50"
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

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t border-gray-200 bg-white px-6 py-4">
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">{page * PAGE_SIZE + 1}</span>
                    {' '}to{' '}
                    <span className="font-medium">
                      {Math.min((page + 1) * PAGE_SIZE, filtered.length)}
                    </span>{' '}
                    of <span className="font-medium">{filtered.length}</span> results
                  </p>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setPage((p) => Math.max(0, p - 1))}
                      disabled={page === 0}
                      className="inline-flex items-center rounded-md bg-white px-3 py-1.5 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </button>
                    <button
                      type="button"
                      onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                      disabled={page >= totalPages - 1}
                      className="inline-flex items-center rounded-md bg-white px-3 py-1.5 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </Shell>
  );
}
