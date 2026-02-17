'use client';

import { useEffect, useState } from 'react';
import { Shell } from '@/components/layout/shell';
import { StatusBadge } from '@/components/features/status-badge';
import { CitationList } from '@/components/features/citation-list';
import { api } from '@/lib/api/client';
import type { KnowledgeBase, QueryResponse } from '@/lib/types';
import { Send, Loader2, Copy, Check, History } from 'lucide-react';
import Link from 'next/link';

interface HistoryEntry {
  id: string;
  question: string;
  response: QueryResponse;
  timestamp: Date;
}

export default function PlaygroundPage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [kbsLoading, setKbsLoading] = useState(true);

  const [selectedKbId, setSelectedKbId] = useState('');
  const [question, setQuestion] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [copiedId, setCopiedId] = useState(false);

  useEffect(() => {
    async function fetchKBs() {
      try {
        setKbsLoading(true);
        const data = await api.listKnowledgeBases();
        setKnowledgeBases(data);
        // Auto-select first KB - use functional setter to avoid stale closure
        if (data.length > 0) {
          setSelectedKbId((current) => current || data[0].id);
        }
      } catch {
        // Non-fatal - show empty dropdown
      } finally {
        setKbsLoading(false);
      }
    }
    void fetchKBs();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedKbId || !question.trim() || submitting) return;

    try {
      setSubmitting(true);
      setSubmitError(null);
      setResponse(null);

      const result = await api.query({
        knowledgeBaseId: selectedKbId,
        question: question.trim(),
      });

      setResponse(result);
      setHistory((prev) => [
        {
          id: result.interactionId,
          question: question.trim(),
          response: result,
          timestamp: new Date(),
        },
        ...prev.slice(0, 9), // Keep last 10 entries
      ]);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to submit question');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCopyInteractionId() {
    if (!response) return;
    try {
      await navigator.clipboard.writeText(response.interactionId);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    } catch {
      // clipboard not available
    }
  }

  function loadHistoryEntry(entry: HistoryEntry) {
    setResponse(entry.response);
    setQuestion(entry.question);
  }

  const canSubmit = selectedKbId && question.trim() && !submitting;

  return (
    <Shell title="Playground">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left panel: Input */}
        <div className="lg:col-span-2 space-y-4">
          {/* KB selector */}
          <div className="rounded-lg bg-white p-6 shadow">
            <label
              htmlFor="kb-select"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Knowledge Base
            </label>
            {kbsLoading ? (
              <div className="mt-1 h-9 bg-gray-100 rounded animate-pulse" />
            ) : knowledgeBases.length === 0 ? (
              <div className="mt-1 rounded-md bg-amber-50 px-3 py-2">
                <p className="text-sm text-amber-700">
                  No knowledge bases available.{' '}
                  <Link
                    href="/knowledge-bases"
                    className="font-medium underline hover:no-underline"
                  >
                    Create one first
                  </Link>
                  .
                </p>
              </div>
            ) : (
              <select
                id="kb-select"
                value={selectedKbId}
                onChange={(e) => setSelectedKbId(e.target.value)}
                disabled={submitting}
                className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500"
              >
                {knowledgeBases.map((kb) => (
                  <option key={kb.id} value={kb.id}>
                    {kb.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Question input */}
          <div className="rounded-lg bg-white p-6 shadow">
            <form onSubmit={(e) => void handleSubmit(e)}>
              <label
                htmlFor="question"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Question
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={5}
                disabled={submitting || knowledgeBases.length === 0}
                placeholder="Ask a question about the knowledge base..."
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500 resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    if (canSubmit) void handleSubmit(e as unknown as React.FormEvent);
                  }
                }}
              />
              <div className="mt-3 flex items-center justify-between">
                <p className="text-xs text-gray-400">
                  Press Cmd+Enter to submit
                </p>
                <button
                  type="submit"
                  disabled={!canSubmit}
                  className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  {submitting ? 'Asking...' : 'Ask Question'}
                </button>
              </div>
            </form>
          </div>

          {/* Response area */}
          {submitError && (
            <div className="rounded-lg bg-red-50 border border-red-200 p-6">
              <p className="text-sm text-red-800">Error: {submitError}</p>
            </div>
          )}

          {response && (
            <div className="rounded-lg bg-white p-6 shadow space-y-6">
              {/* Response header */}
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-semibold text-gray-700">Response</h3>
                  <StatusBadge status={response.status} />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">ID:</span>
                  <code className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono text-gray-900">
                    {response.interactionId}
                  </code>
                  <button
                    type="button"
                    onClick={() => void handleCopyInteractionId()}
                    title="Copy interaction ID for Grafana"
                    className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                  >
                    {copiedId ? (
                      <Check className="h-3.5 w-3.5 text-green-600" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                    {copiedId ? 'Copied!' : 'Copy'}
                  </button>
                  <Link
                    href={`/interactions/${response.interactionId}`}
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    View detail
                  </Link>
                </div>
              </div>

              {/* Answer text */}
              <div>
                {response.status === 'answered' && response.answer ? (
                  <p className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
                    {response.answer}
                  </p>
                ) : response.status === 'unknown' ? (
                  <div className="rounded-md bg-amber-50 px-4 py-3">
                    <p className="text-sm text-amber-800">
                      {response.answer ?? "I don't have that information in the provided knowledge base."}
                    </p>
                  </div>
                ) : (
                  <div className="rounded-md bg-red-50 px-4 py-3">
                    <p className="text-sm text-red-800">
                      {response.error ?? 'An error occurred while processing this question.'}
                    </p>
                  </div>
                )}
              </div>

              {/* Citations */}
              {response.citations && response.citations.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
                    Citations ({response.citations.length})
                  </h4>
                  <CitationList citations={response.citations} />
                </div>
              )}
            </div>
          )}

          {!response && !submitError && !submitting && (
            <div className="rounded-lg bg-white p-8 shadow text-center">
              <p className="text-sm text-gray-400">
                Submit a question to see the response here.
              </p>
            </div>
          )}
        </div>

        {/* Right panel: Session history */}
        <div className="space-y-4">
          <div className="rounded-lg bg-white shadow overflow-hidden">
            <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-gray-400" />
                <h3 className="text-sm font-medium text-gray-700">
                  Session History
                </h3>
              </div>
              {history.length > 0 && (
                <button
                  type="button"
                  onClick={() => setHistory([])}
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  Clear
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <p className="text-xs text-gray-400">No queries yet in this session.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
                {history.map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    onClick={() => loadHistoryEntry(entry)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <StatusBadge status={entry.response.status} />
                      <span className="text-xs text-gray-400 shrink-0">
                        {entry.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-xs text-gray-700 line-clamp-2">
                      {entry.question}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
