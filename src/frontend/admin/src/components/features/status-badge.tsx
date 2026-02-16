import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: 'answered' | 'unknown' | 'error';
}

const statusStyles = {
  answered: 'bg-green-100 text-green-800',
  unknown: 'bg-amber-100 text-amber-800',
  error: 'bg-red-100 text-red-800',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', statusStyles[status])}>
      {status}
    </span>
  );
}
