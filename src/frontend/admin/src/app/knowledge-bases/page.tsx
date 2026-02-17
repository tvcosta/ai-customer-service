'use client';

import { useCallback, useEffect, useState, useRef } from 'react';
import { Shell } from '@/components/layout/shell';
import { api } from '@/lib/api/client';
import type { KnowledgeBase } from '@/lib/types';
import { Plus, Trash2, Eye, X, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

export default function KnowledgeBasesPage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create dialog state
  const [createOpen, setCreateOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createDescription, setCreateDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Delete confirmation state
  const [deleteTarget, setDeleteTarget] = useState<KnowledgeBase | null>(null);
  const [deleting, setDeleting] = useState(false);

  const nameInputRef = useRef<HTMLInputElement>(null);

  const fetchKBs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listKnowledgeBases();
      setKnowledgeBases(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load knowledge bases';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchKBs();
  }, [fetchKBs]);

  useEffect(() => {
    if (createOpen) {
      setTimeout(() => nameInputRef.current?.focus(), 50);
    }
  }, [createOpen]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!createName.trim()) return;
    try {
      setCreating(true);
      setCreateError(null);
      const kb = await api.createKnowledgeBase({
        name: createName.trim(),
        description: createDescription.trim() || undefined,
      });
      setKnowledgeBases((prev) => [kb, ...prev]);
      setCreateOpen(false);
      setCreateName('');
      setCreateDescription('');
      toast.success(`Knowledge base "${kb.name}" created successfully`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create knowledge base';
      setCreateError(message);
      toast.error(message);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      await api.deleteKnowledgeBase(deleteTarget.id);
      const name = deleteTarget.name;
      setKnowledgeBases((prev) => prev.filter((kb) => kb.id !== deleteTarget.id));
      setDeleteTarget(null);
      toast.success(`Knowledge base "${name}" deleted`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete knowledge base';
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <Shell title="Knowledge Bases">
      {/* Header actions */}
      <div className="mb-6 flex items-center justify-end">
        <button
          type="button"
          onClick={() => setCreateOpen(true)}
          aria-label="Create a new knowledge base"
          className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <Plus className="h-4 w-4" aria-hidden="true" />
          Create Knowledge Base
        </button>
      </div>

      {/* Main content */}
      {loading ? (
        <div
          role="status"
          aria-label="Loading knowledge bases"
          className="rounded-lg bg-white shadow"
        >
          <div className="p-6 space-y-4 animate-pulse">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-12 bg-gray-100 rounded" />
            ))}
          </div>
        </div>
      ) : error ? (
        <div role="alert" className="rounded-lg bg-red-50 border border-red-200 p-6">
          <p className="text-sm text-red-800">Error: {error}</p>
          <button
            type="button"
            onClick={() => void fetchKBs()}
            className="mt-3 text-sm font-medium text-red-700 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      ) : (
        <div
          aria-live="polite"
          className="rounded-lg bg-white shadow overflow-hidden"
        >
          {knowledgeBases.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-sm text-gray-500">
                No knowledge bases yet. Create one to get started.
              </p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Description
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Created
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {knowledgeBases.map((kb) => (
                  <tr key={kb.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      {kb.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {kb.description ?? '—'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {new Date(kb.createdAt).toLocaleDateString()}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/knowledge-bases/${kb.id}`}
                          aria-label={`View knowledge base ${kb.name}`}
                          className="inline-flex items-center gap-1.5 rounded-md bg-white px-3 py-1.5 text-xs font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                        >
                          <Eye className="h-3.5 w-3.5" aria-hidden="true" />
                          View
                        </Link>
                        <button
                          type="button"
                          onClick={() => setDeleteTarget(kb)}
                          aria-label={`Delete knowledge base ${kb.name}`}
                          className="inline-flex items-center gap-1.5 rounded-md bg-white px-3 py-1.5 text-xs font-medium text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-50"
                        >
                          <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Create Dialog */}
      {createOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="create-kb-title"
          className="fixed inset-0 z-50 flex items-center justify-center"
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => !creating && setCreateOpen(false)}
          />
          <div className="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 id="create-kb-title" className="text-lg font-semibold text-gray-900">
                Create Knowledge Base
              </h2>
              <button
                type="button"
                onClick={() => !creating && setCreateOpen(false)}
                aria-label="Close dialog"
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
            <form onSubmit={(e) => void handleCreate(e)}>
              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="kb-name"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Name <span className="text-red-500" aria-hidden="true">*</span>
                  </label>
                  <input
                    ref={nameInputRef}
                    id="kb-name"
                    type="text"
                    value={createName}
                    onChange={(e) => setCreateName(e.target.value)}
                    required
                    aria-required="true"
                    disabled={creating}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="My Knowledge Base"
                  />
                </div>
                <div>
                  <label
                    htmlFor="kb-description"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Description
                  </label>
                  <textarea
                    id="kb-description"
                    value={createDescription}
                    onChange={(e) => setCreateDescription(e.target.value)}
                    rows={3}
                    disabled={creating}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="Optional description..."
                  />
                </div>
                {createError && (
                  <p role="alert" className="text-sm text-red-600">{createError}</p>
                )}
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => !creating && setCreateOpen(false)}
                  disabled={creating}
                  className="rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || !createName.trim()}
                  className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteTarget && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-kb-title"
          className="fixed inset-0 z-50 flex items-center justify-center"
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => !deleting && setDeleteTarget(null)}
          />
          <div className="relative z-10 w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
            <h2 id="delete-kb-title" className="text-lg font-semibold text-gray-900">
              Delete Knowledge Base
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Are you sure you want to delete{' '}
              <span className="font-medium">&ldquo;{deleteTarget.name}&rdquo;</span>? This action
              cannot be undone and will remove all associated documents.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => !deleting && setDeleteTarget(null)}
                disabled={deleting}
                className="rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => void handleDelete()}
                disabled={deleting}
                className="inline-flex items-center gap-2 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-500 disabled:opacity-50"
              >
                {deleting && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </Shell>
  );
}
