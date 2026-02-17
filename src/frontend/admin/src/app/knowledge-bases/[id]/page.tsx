'use client';

import { useCallback, useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { Shell } from '@/components/layout/shell';
import { api } from '@/lib/api/client';
import type { KnowledgeBase, Document as KbDocument } from '@/lib/types';
import {
  ArrowLeft,
  Upload,
  Trash2,
  RefreshCw,
  Loader2,
  FileText,
  X,
} from 'lucide-react';
import Link from 'next/link';

type DocStatus = 'pending' | 'processing' | 'indexed' | 'error';

const docStatusStyles: Record<DocStatus, string> = {
  pending: 'bg-gray-100 text-gray-700',
  processing: 'bg-blue-100 text-blue-700',
  indexed: 'bg-green-100 text-green-700',
  error: 'bg-red-100 text-red-700',
};

export default function KnowledgeBaseDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [kb, setKb] = useState<KnowledgeBase | null>(null);
  const [documents, setDocuments] = useState<KbDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Delete document state
  const [deleteTarget, setDeleteTarget] = useState<KbDocument | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Re-index state
  const [indexing, setIndexing] = useState(false);
  const [indexMessage, setIndexMessage] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [kbData, docsData] = await Promise.all([
        api.getKnowledgeBase(id),
        api.listDocuments(id),
      ]);
      setKb(kbData);
      setDocuments(docsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  async function handleFileUpload(file: File) {
    try {
      setUploading(true);
      setUploadError(null);
      const doc = await api.uploadDocument(id, file);
      setDocuments((prev) => [doc, ...prev]);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) void handleFileUpload(file);
    e.target.value = '';
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) void handleFileUpload(file);
  }

  async function handleDeleteDocument() {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      await api.deleteDocument(id, deleteTarget.id);
      setDocuments((prev) => prev.filter((d) => d.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete document');
    } finally {
      setDeleting(false);
    }
  }

  async function handleReindex() {
    try {
      setIndexing(true);
      setIndexMessage(null);
      await api.triggerIndexing(id);
      setIndexMessage('Re-indexing started. Documents will be updated shortly.');
      void fetchData();
    } catch (err) {
      setIndexMessage(err instanceof Error ? err.message : 'Failed to trigger re-indexing');
    } finally {
      setIndexing(false);
    }
  }

  if (loading) {
    return (
      <Shell title="Knowledge Base">
        <div className="space-y-6 animate-pulse">
          <div className="h-24 rounded-lg bg-white shadow" />
          <div className="h-64 rounded-lg bg-white shadow" />
        </div>
      </Shell>
    );
  }

  if (error || !kb) {
    return (
      <Shell title="Knowledge Base">
        <div className="rounded-lg bg-red-50 border border-red-200 p-6">
          <p className="text-sm text-red-800">{error ?? 'Knowledge base not found'}</p>
          <div className="mt-3 flex gap-3">
            <button
              type="button"
              onClick={() => void fetchData()}
              className="text-sm font-medium text-red-700 underline hover:no-underline"
            >
              Retry
            </button>
            <Link
              href="/knowledge-bases"
              className="text-sm font-medium text-red-700 underline hover:no-underline"
            >
              Go back
            </Link>
          </div>
        </div>
      </Shell>
    );
  }

  return (
    <Shell title={kb.name}>
      {/* Back navigation */}
      <div className="mb-6">
        <Link
          href="/knowledge-bases"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Knowledge Bases
        </Link>
      </div>

      {/* KB metadata card */}
      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{kb.name}</h2>
            {kb.description && (
              <p className="mt-1 text-sm text-gray-600">{kb.description}</p>
            )}
            <p className="mt-2 text-xs text-gray-400">
              Created {new Date(kb.createdAt).toLocaleString()}
            </p>
            <p className="mt-0.5 text-xs text-gray-400 font-mono">ID: {kb.id}</p>
          </div>
          <button
            type="button"
            onClick={() => void handleReindex()}
            disabled={indexing}
            className="inline-flex items-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
          >
            {indexing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Re-index
          </button>
        </div>
        {indexMessage && (
          <div className="mt-4 rounded-md bg-blue-50 px-4 py-3">
            <p className="text-sm text-blue-800">{indexMessage}</p>
          </div>
        )}
      </div>

      {/* Documents section */}
      <div className="rounded-lg bg-white shadow overflow-hidden">
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900">
            Documents ({documents.length})
          </h3>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
          >
            {uploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            Upload Document
          </button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileChange}
            accept=".pdf,.txt,.md,.docx,.doc"
          />
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`mx-6 my-4 rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
            dragOver
              ? 'border-indigo-400 bg-indigo-50'
              : 'border-gray-300 bg-gray-50'
          }`}
        >
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
              <p className="text-sm text-gray-600">Uploading...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <FileText className="h-6 w-6 text-gray-400" />
              <p className="text-sm text-gray-600">
                Drag and drop a file here, or{' '}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="font-medium text-indigo-600 hover:text-indigo-500"
                >
                  browse
                </button>
              </p>
              <p className="text-xs text-gray-400">PDF, TXT, MD, DOCX supported</p>
            </div>
          )}
          {uploadError && (
            <p className="mt-2 text-sm text-red-600">{uploadError}</p>
          )}
        </div>

        {/* Documents table */}
        {documents.length === 0 ? (
          <div className="px-6 pb-12 text-center">
            <p className="text-sm text-gray-500">
              No documents yet. Upload one to get started.
            </p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Filename
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Chunks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-400 shrink-0" />
                      <span className="truncate max-w-xs">{doc.filename}</span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${docStatusStyles[doc.status]}`}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {doc.chunksCount}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    {new Date(doc.uploadedAt).toLocaleString()}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-right">
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(doc)}
                      className="inline-flex items-center gap-1.5 rounded-md bg-white px-3 py-1.5 text-xs font-medium text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-50"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Delete Document Confirmation */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => !deleting && setDeleteTarget(null)}
          />
          <div className="relative z-10 w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Delete Document</h2>
              <button
                type="button"
                onClick={() => !deleting && setDeleteTarget(null)}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600">
              Are you sure you want to delete{' '}
              <span className="font-medium">&ldquo;{deleteTarget.filename}&rdquo;</span>? This
              cannot be undone.
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
                onClick={() => void handleDeleteDocument()}
                disabled={deleting}
                className="inline-flex items-center gap-2 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-500 disabled:opacity-50"
              >
                {deleting && <Loader2 className="h-4 w-4 animate-spin" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </Shell>
  );
}
