'use client';

import { ReactNode } from 'react';

export interface HeroSectionProps {
  title: string;
  subtitle?: string;
  children?: ReactNode;
  backgroundGradient?: boolean;
}

export function HeroSection({
  title,
  subtitle,
  children,
  backgroundGradient = false,
}: HeroSectionProps) {
  return (
    <div
      className={`min-h-screen flex items-center justify-center ${
        backgroundGradient ? 'bg-gradient-to-b from-gray-50 to-white' : ''
      }`}
    >
      <main className="max-w-2xl flex flex-col items-center gap-12 text-center px-6">
        <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight text-[#333]">
          {title}
        </h1>
        {subtitle && (
          <p className="text-lg text-[#666] max-w-lg">{subtitle}</p>
        )}
        {children && <div className="w-full">{children}</div>}
      </main>
    </div>
  );
}
