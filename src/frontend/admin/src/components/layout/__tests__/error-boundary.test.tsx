import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from '../error-boundary';

// A component that renders normally
function GoodChild() {
  return <div>All good here</div>;
}

// A component that throws during render
function BadChild({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test render error');
  }
  return <div>No error</div>;
}

// Suppress console.error output from ErrorBoundary's componentDidCatch
// so test output stays clean
const originalConsoleError = console.error;

beforeEach(() => {
  console.error = vi.fn();
});

afterEach(() => {
  console.error = originalConsoleError;
});

describe('ErrorBoundary', () => {
  describe('happy path', () => {
    it('renders children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <GoodChild />
        </ErrorBoundary>
      );
      expect(screen.getByText('All good here')).toBeInTheDocument();
    });

    it('does not render the error UI when children are healthy', () => {
      render(
        <ErrorBoundary>
          <GoodChild />
        </ErrorBoundary>
      );
      expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows the error heading when a child throws', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('shows the descriptive error description', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(
        screen.getByText(/An unexpected error occurred/i)
      ).toBeInTheDocument();
    });

    it('displays the error message from the thrown error', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(screen.getByText('Test render error')).toBeInTheDocument();
    });

    it('renders a "Try Again" button', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('renders a "Refresh Page" button', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(screen.getByRole('button', { name: /refresh page/i })).toBeInTheDocument();
    });

    it('does not render the children when an error occurred', () => {
      render(
        <ErrorBoundary>
          <BadChild shouldThrow />
        </ErrorBoundary>
      );
      expect(screen.queryByText('No error')).not.toBeInTheDocument();
    });
  });

  describe('"Try Again" button resets state', () => {
    it('hides the error UI and shows children again after clicking Try Again', () => {
      // We need a component whose throwing behaviour we can toggle.
      // We render a wrapper that starts throwing, click Try Again (which resets
      // ErrorBoundary state), and the child no longer throws on re-render.
      let shouldThrow = true;

      function ToggleChild() {
        if (shouldThrow) throw new Error('Temporary error');
        return <div>Recovered</div>;
      }

      const { rerender } = render(
        <ErrorBoundary>
          <ToggleChild />
        </ErrorBoundary>
      );

      // Error UI is visible
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Fix the child so it won't throw on next render
      shouldThrow = false;

      // Click "Try Again" — resets ErrorBoundary internal state
      fireEvent.click(screen.getByRole('button', { name: /try again/i }));

      // Re-render the tree so React reconciles with the fixed child
      rerender(
        <ErrorBoundary>
          <ToggleChild />
        </ErrorBoundary>
      );

      expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
      expect(screen.getByText('Recovered')).toBeInTheDocument();
    });

    it('removes the error message display after reset', () => {
      let shouldThrow = true;

      function ToggleChild() {
        if (shouldThrow) throw new Error('Reset me');
        return <div>Back to normal</div>;
      }

      const { rerender } = render(
        <ErrorBoundary>
          <ToggleChild />
        </ErrorBoundary>
      );

      expect(screen.getByText('Reset me')).toBeInTheDocument();

      shouldThrow = false;
      fireEvent.click(screen.getByRole('button', { name: /try again/i }));

      rerender(
        <ErrorBoundary>
          <ToggleChild />
        </ErrorBoundary>
      );

      expect(screen.queryByText('Reset me')).not.toBeInTheDocument();
    });
  });
});
