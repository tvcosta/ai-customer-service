import { Shell } from "@/components/layout/shell";

export default function DashboardPage() {
  return (
    <Shell title="Dashboard">
      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
        <p className="mt-2 text-gray-600">Welcome to the AI Customer Service Admin Dashboard.</p>
      </div>
    </Shell>
  );
}
