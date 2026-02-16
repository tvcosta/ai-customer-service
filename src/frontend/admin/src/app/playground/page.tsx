"use client";

import { Shell } from "@/components/layout/shell";

export default function PlaygroundPage() {
  return (
    <Shell title="Playground">
      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="text-xl font-semibold text-gray-900">Playground</h2>
        <p className="mt-2 text-gray-600">Test your knowledge bases with sample questions.</p>
      </div>
    </Shell>
  );
}
