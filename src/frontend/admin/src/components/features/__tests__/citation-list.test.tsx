import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CitationList } from '../citation-list';
import type { Citation } from '@/lib/types';

const makeCitation = (overrides: Partial<Citation> = {}): Citation => ({
  sourceDocument: 'product-manual.pdf',
  page: 5,
  chunkId: 'chunk-abc-123',
  relevanceScore: 0.95,
  ...overrides,
});

describe('CitationList', () => {
  describe('empty state', () => {
    it('renders "No citations available." when given an empty array', () => {
      render(<CitationList citations={[]} />);
      expect(screen.getByText('No citations available.')).toBeInTheDocument();
    });

    it('does not render any citation cards for an empty array', () => {
      render(<CitationList citations={[]} />);
      // The container div with space-y-3 only renders when citations exist
      expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
    });
  });

  describe('single citation', () => {
    it('renders the source document name', () => {
      render(<CitationList citations={[makeCitation()]} />);
      expect(screen.getByText('product-manual.pdf')).toBeInTheDocument();
    });

    it('renders the page number when present', () => {
      render(<CitationList citations={[makeCitation({ page: 5 })]} />);
      expect(screen.getByText('Page 5')).toBeInTheDocument();
    });

    it('does not render a page element when page is undefined', () => {
      render(<CitationList citations={[makeCitation({ page: undefined })]} />);
      expect(screen.queryByText(/^Page/)).not.toBeInTheDocument();
    });

    it('renders the chunk ID prefixed with "ID:"', () => {
      render(<CitationList citations={[makeCitation({ chunkId: 'chunk-abc-123' })]} />);
      expect(screen.getByText('ID: chunk-abc-123')).toBeInTheDocument();
    });

    it('renders the relevance score as a percentage match badge', () => {
      render(<CitationList citations={[makeCitation({ relevanceScore: 0.95 })]} />);
      expect(screen.getByText('95% match')).toBeInTheDocument();
    });

    it('rounds the relevance score to the nearest integer', () => {
      render(<CitationList citations={[makeCitation({ relevanceScore: 0.876 })]} />);
      expect(screen.getByText('88% match')).toBeInTheDocument();
    });

    it('applies the blue badge classes to the relevance score', () => {
      render(<CitationList citations={[makeCitation({ relevanceScore: 0.9 })]} />);
      const badge = screen.getByText('90% match');
      expect(badge).toHaveClass('bg-blue-100');
      expect(badge).toHaveClass('text-blue-800');
    });
  });

  describe('multiple citations', () => {
    const citations: Citation[] = [
      makeCitation({ sourceDocument: 'faq.pdf', chunkId: 'chunk-1', relevanceScore: 0.9, page: 1 }),
      makeCitation({ sourceDocument: 'guide.pdf', chunkId: 'chunk-2', relevanceScore: 0.75, page: 12 }),
      makeCitation({ sourceDocument: 'terms.pdf', chunkId: 'chunk-3', relevanceScore: 0.6, page: undefined }),
    ];

    it('renders all source document names', () => {
      render(<CitationList citations={citations} />);
      expect(screen.getByText('faq.pdf')).toBeInTheDocument();
      expect(screen.getByText('guide.pdf')).toBeInTheDocument();
      expect(screen.getByText('terms.pdf')).toBeInTheDocument();
    });

    it('renders all chunk IDs', () => {
      render(<CitationList citations={citations} />);
      expect(screen.getByText('ID: chunk-1')).toBeInTheDocument();
      expect(screen.getByText('ID: chunk-2')).toBeInTheDocument();
      expect(screen.getByText('ID: chunk-3')).toBeInTheDocument();
    });

    it('renders page numbers only for citations that have them', () => {
      render(<CitationList citations={citations} />);
      expect(screen.getByText('Page 1')).toBeInTheDocument();
      expect(screen.getByText('Page 12')).toBeInTheDocument();
      // terms.pdf has no page — only two "Page X" elements should appear
      const pageElements = screen.getAllByText(/^Page \d+$/);
      expect(pageElements).toHaveLength(2);
    });

    it('renders all relevance score badges', () => {
      render(<CitationList citations={citations} />);
      expect(screen.getByText('90% match')).toBeInTheDocument();
      expect(screen.getByText('75% match')).toBeInTheDocument();
      expect(screen.getByText('60% match')).toBeInTheDocument();
    });

    it('does not render the empty-state message', () => {
      render(<CitationList citations={citations} />);
      expect(screen.queryByText('No citations available.')).not.toBeInTheDocument();
    });
  });
});
