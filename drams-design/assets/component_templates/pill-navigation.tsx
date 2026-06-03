'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export interface NavItem {
  href: string;
  label: string;
}

export interface PillNavigationProps {
  navItems: NavItem[];
  ariaLabel?: string;
}

export function PillNavigation({
  navItems,
  ariaLabel = 'Navigation',
}: PillNavigationProps) {
  const pathname = usePathname();

  return (
    <nav
      style={{
        display: 'flex',
        gap: '8px',
        flexWrap: 'wrap',
      }}
      role="navigation"
      aria-label={ariaLabel}
    >
      {navItems.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            style={{ textDecoration: 'none' }}
            className={`
              flex items-center justify-center h-10 px-4 rounded-full font-medium text-sm transition-all
              ${
                isActive
                  ? 'bg-[rgb(255,97,26)] text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)]'
                  : 'bg-[rgb(238,238,238)] text-[#333] hover:bg-[rgb(232,232,232)]'
              }
            `}
            aria-current={isActive ? 'page' : undefined}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
