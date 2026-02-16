import { Shell } from '@/components/layout/shell';
import { StatsCard } from '@/components/features/stats-card';
import { MessageSquare, CheckCircle, HelpCircle, Database, FileText } from 'lucide-react';
import type { DashboardStats } from '@/lib/types';

const mockStats: DashboardStats = {
  totalInteractions: 0,
  answeredCount: 0,
  unknownCount: 0,
  knowledgeBaseCount: 0,
  documentCount: 0,
};

export default function DashboardPage() {
  const stats = mockStats;

  return (
    <Shell title="Dashboard">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <StatsCard title="Total Interactions" value={stats.totalInteractions} icon={<MessageSquare className="h-5 w-5" />} />
        <StatsCard title="Answered" value={stats.answeredCount} icon={<CheckCircle className="h-5 w-5" />} />
        <StatsCard title="Unknown" value={stats.unknownCount} icon={<HelpCircle className="h-5 w-5" />} />
        <StatsCard title="Knowledge Bases" value={stats.knowledgeBaseCount} icon={<Database className="h-5 w-5" />} />
        <StatsCard title="Documents" value={stats.documentCount} icon={<FileText className="h-5 w-5" />} />
      </div>

      <div className="mt-8 rounded-lg bg-white p-6 shadow">
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        <p className="mt-2 text-sm text-gray-500">No interactions yet. Use the Playground to ask your first question.</p>
      </div>
    </Shell>
  );
}
