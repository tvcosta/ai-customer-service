import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '../status-badge';

describe('StatusBadge', () => {
  describe('answered status', () => {
    it('renders "answered" text', () => {
      render(<StatusBadge status="answered" />);
      expect(screen.getByText('answered')).toBeInTheDocument();
    });

    it('applies green background and text classes', () => {
      render(<StatusBadge status="answered" />);
      const badge = screen.getByText('answered');
      expect(badge).toHaveClass('bg-green-100');
      expect(badge).toHaveClass('text-green-800');
    });

    it('does not apply amber or red classes', () => {
      render(<StatusBadge status="answered" />);
      const badge = screen.getByText('answered');
      expect(badge).not.toHaveClass('bg-amber-100');
      expect(badge).not.toHaveClass('bg-red-100');
    });
  });

  describe('unknown status', () => {
    it('renders "unknown" text', () => {
      render(<StatusBadge status="unknown" />);
      expect(screen.getByText('unknown')).toBeInTheDocument();
    });

    it('applies amber background and text classes', () => {
      render(<StatusBadge status="unknown" />);
      const badge = screen.getByText('unknown');
      expect(badge).toHaveClass('bg-amber-100');
      expect(badge).toHaveClass('text-amber-800');
    });

    it('does not apply green or red classes', () => {
      render(<StatusBadge status="unknown" />);
      const badge = screen.getByText('unknown');
      expect(badge).not.toHaveClass('bg-green-100');
      expect(badge).not.toHaveClass('bg-red-100');
    });
  });

  describe('error status', () => {
    it('renders "error" text', () => {
      render(<StatusBadge status="error" />);
      expect(screen.getByText('error')).toBeInTheDocument();
    });

    it('applies red background and text classes', () => {
      render(<StatusBadge status="error" />);
      const badge = screen.getByText('error');
      expect(badge).toHaveClass('bg-red-100');
      expect(badge).toHaveClass('text-red-800');
    });

    it('does not apply green or amber classes', () => {
      render(<StatusBadge status="error" />);
      const badge = screen.getByText('error');
      expect(badge).not.toHaveClass('bg-green-100');
      expect(badge).not.toHaveClass('bg-amber-100');
    });
  });

  describe('shared styling', () => {
    it('renders as a span element', () => {
      render(<StatusBadge status="answered" />);
      const badge = screen.getByText('answered');
      expect(badge.tagName).toBe('SPAN');
    });

    it('applies base pill classes on all statuses', () => {
      const statuses = ['answered', 'unknown', 'error'] as const;
      statuses.forEach((status) => {
        const { unmount } = render(<StatusBadge status={status} />);
        const badge = screen.getByText(status);
        expect(badge).toHaveClass('inline-flex');
        expect(badge).toHaveClass('rounded-full');
        expect(badge).toHaveClass('text-xs');
        expect(badge).toHaveClass('font-medium');
        unmount();
      });
    });
  });
});
