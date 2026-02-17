'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Shell } from '@/components/layout/shell';
import { StatusBadge } from '@/components/features/status-badge';
import { CitationList } from '@/components/features/citation-list';
import { api } from '@/lib/api/client';
import type { Interaction } from '@/lib/types';
import { ArrowLeft, Copy, Check } from 'lucide-react';
import Link from 'next/link';

export default function InteractionDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [interaction, setInteraction] = useState<Interaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchInteraction() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getInteraction(id);
        setInteraction(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load interaction');
      } finally {
        setLoading(false);
      }
    }
    void fetchInteraction();
  }, [id]);

  async function handleCopyId() {
    if (!interaction) return;
    try {
      await navigator.clipboard.writeText(interaction.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard not available
    }
  }

  if (loading) {
    return (
      <Shell title="Interaction">
        <div role="status" aria-label="Loading interaction" className="space-y-6 animate-pulse">
          <div className="h-8 w-32 rounded bg-gray-200" />
          <div className="h-40 rounded-lg bg-white shadow" />
          <div className="h-60 rounded-lg bg-white shadow" />
        </div>
      </Shell>
    );
  }

  if (error || !interaction) {
    return (
      <Shell title="Interaction">
        <div role="alert" className="rounded-lg bg-red-50 border border-red-200 p-6">
          <p className="text-sm text-red-800">{error ?? 'Interaction not found'}</p>
          <Link
            href="/interactions"
            className="mt-3 inline-block text-sm font-medium text-red-700 underline hover:no-underline"
          >
            Go back
          </Link>
        </div>
      </Shell>
    );
  }

  return (
    <Shell title="Interaction Detail">
      {/* Back navigation */}
      <div className="mb-6">
        <Link
          href="/interactions"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to Interactions
        </Link>
      </div>

      {/* Header card - interaction ID + status */}
      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <StatusBadge status={interaction.status} />
              <span className="text-sm text-gray-500">
                {new Date(interaction.createdAt).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-500">Interaction ID:</span>
              <code className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono text-gray-900">
                {interaction.id}
              </code>
              <button
                type="button"
                onClick={() => void handleCopyId()}
                aria-label="Copy interaction ID"
                title="Copy interaction ID for Grafana lookup"
                className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-green-600" aria-hidden="true" />
                ) : (
                  <Copy className="h-3.5 w-3.5" aria-hidden="true" />
                )}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <p className="mt-1 text-xs text-gray-400">
              Use the Interaction ID in Grafana to look up OpenTelemetry traces.
            </p>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Question
        </h2>
        <p className="text-base text-gray-900 whitespace-pre-wrap">{interaction.question}</p>
      </div>

      {/* Answer */}
      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Answer
        </h2>
        {interaction.status === 'answered' && interaction.answer ? (
          <p className="text-base text-gray-900 whitespace-pre-wrap">{interaction.answer}</p>
        ) : interaction.status === 'unknown' ? (
          <div className="rounded-md bg-amber-50 px-4 py-3">
            <p className="text-sm text-amber-800">
              {interaction.answer ?? "I don't have that information in the provided knowledge base."}
            </p>
          </div>
        ) : (
          <div className="rounded-md bg-red-50 px-4 py-3">
            <p className="text-sm text-red-800">
              {interaction.answer ?? 'An error occurred while processing this question.'}
            </p>
          </div>
        )}
      </div>

      {/* Citations */}
      {interaction.citations && interaction.citations.length > 0 && (
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
            Citations ({interaction.citations.length})
          </h2>
          <CitationList citations={interaction.citations} />
        </div>
      )}
    </Shell>
  );
}
