import type { Citation } from '@/lib/types';

interface CitationListProps {
  citations: Citation[];
}

export function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return (
      <p className="text-sm text-gray-500">No citations available.</p>
    );
  }

  return (
    <div className="space-y-3">
      {citations.map((citation, index) => (
        <div
          key={`${citation.chunkId}-${index}`}
          className="rounded-lg border border-gray-200 bg-gray-50 p-4"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 truncate">
                {citation.sourceDocument}
              </p>
              <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                {citation.page !== undefined && (
                  <span>Page {citation.page}</span>
                )}
                <span className="font-mono">ID: {citation.chunkId}</span>
              </div>
            </div>
            <div className="shrink-0">
              <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                {(citation.relevanceScore * 100).toFixed(0)}% match
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
