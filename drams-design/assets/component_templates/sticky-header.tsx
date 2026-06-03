'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export interface NavItem {
  href: string;
  label: string;
}

export interface StickyHeaderProps {
  logoText?: string;
  logoSubtitle?: string;
  navItems: NavItem[];
}

export function StickyHeader({
  logoText = 'flatwatch',
  logoSubtitle = 'Society Cash Tracker',
  navItems,
}: StickyHeaderProps) {
  const pathname = usePathname();

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        borderBottom: '1px solid rgb(238,238,238)',
        backgroundColor: 'white',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '48px',
        }}
        className="py-4"
      >
        <Link href="/" style={{ textDecoration: 'none', flexShrink: 0 }}>
          <h1
            className="font-sacramento"
            style={{
              fontSize: '36px',
              fontWeight: 400,
              color: '#333',
              margin: 0,
            }}
          >
            {logoText}
          </h1>
          <p
            style={{
              fontSize: '12px',
              color: '#999',
              margin: '4px 0 0 0',
            }}
          >
            {logoSubtitle}
          </p>
        </Link>

        <nav
          style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap',
          }}
          role="navigation"
          aria-label="Main navigation"
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
      </div>
    </header>
  );
}
