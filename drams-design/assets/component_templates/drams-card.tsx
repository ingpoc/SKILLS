'use client';

import { ReactNode } from 'react';

export interface DRAMSCardProps {
  children: ReactNode;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
  className?: string;
}

export function DRAMSCard({
  children,
  padding = 'lg',
  hover = true,
  className = '',
}: DRAMSCardProps) {
  const paddingMap = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`
        rounded-3xl bg-white ${paddingMap[padding]}
        shadow-[0_4px_16px_rgba(0,0,0,0.06)]
        ${hover ? 'transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.1)] hover:-translate-y-1' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
