'use client';

import { ReactNode } from 'react';

export interface CardGridProps {
  children: ReactNode;
  columns?: {
    mobile?: 1 | 2;
    tablet?: 1 | 2 | 3;
    desktop?: 1 | 2 | 3 | 4;
  };
  gap?: {
    mobile?: string;
    tablet?: string;
    desktop?: string;
  };
}

export function CardGrid({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = { mobile: '1rem', tablet: '1.5rem', desktop: '1.5rem' },
}: CardGridProps) {
  const gridCols = {
    mobile: columns.mobile || 1,
    tablet: columns.tablet || 2,
    desktop: columns.desktop || 3,
  };

  const gaps = {
    mobile: gap.mobile || '1rem',
    tablet: gap.tablet || '1.5rem',
    desktop: gap.desktop || '1.5rem',
  };

  return (
    <div
      className={`grid grid-cols-${gridCols.mobile} md:grid-cols-${gridCols.tablet} lg:grid-cols-${gridCols.desktop}`}
      style={{
        gap: gaps.mobile,
      }}
      // Using inline styles for responsive gaps that match Tailwind breakpoints
      className={`grid grid-cols-${gridCols.mobile} md:grid-cols-${gridCols.tablet} lg:grid-cols-${gridCols.desktop} gap-4 md:gap-6`}
    >
      {children}
    </div>
  );
}
