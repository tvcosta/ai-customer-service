'use client';

import { Shell } from '@/components/layout/shell';

export default function PlaygroundPage() {
  return (
    <Shell title="Playground">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="rounded-lg bg-white p-6 shadow">
            <label htmlFor="kb-select" className="block text-sm font-medium text-gray-700">Knowledge Base</label>
            <select id="kb-select" disabled className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 py-2 pl-3 pr-10 text-sm text-gray-500 shadow-sm">
              <option>No knowledge bases available</option>
            </select>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <label htmlFor="question" className="block text-sm font-medium text-gray-700">Question</label>
            <textarea id="question" rows={4} disabled placeholder="Type your question here..." className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-sm shadow-sm placeholder:text-gray-400" />
            <button type="button" disabled className="mt-4 rounded-md bg-gray-300 px-4 py-2 text-sm font-medium text-white">
              Ask Question
            </button>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h3 className="text-sm font-medium text-gray-700">Response</h3>
          <p className="mt-4 text-sm text-gray-400">Submit a question to see the response here.</p>
        </div>
      </div>
    </Shell>
  );
}
