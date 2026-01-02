# Typography Reference

## Font Loading

### Next.js app directory

```tsx
// app/layout.tsx
import { Instrument_Serif, Inter } from 'next/font/google';

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  variable: '--font-instrument-serif',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});
```

### CSS Variables

```css
:root {
  --font-instrument-serif: 'Instrument Serif', Georgia, serif;
  --font-inter: 'Inter', -apple-system, sans-serif;
}
```

## Type Scale

| Role | Font | Size | Line Height | Tracking |
|------|------|------|-------------|----------|
| **H1** | Instrument Serif | `clamp(3rem, 12vw, 8rem)` | 1 | -0.02em |
| **H2** | Instrument Serif | `clamp(2rem, 6vw, 4.5rem)` | 1.15 | -0.02em |
| **H3** | Instrument Serif | `clamp(1.5rem, 4vw, 2.5rem)` | 1.2 | -0.02em |
| **Body** | Inter | 1rem (16px) | 1.6 | -0.01em |
| **Small** | Inter | 0.875rem (14px) | 1.5 | -0.01em |

## Landing Page Classes

```css
.landing-h1 {
  font-size: clamp(3rem, 12vw, 8rem);
  line-height: 1;
  letter-spacing: -0.02em;
}

.landing-h2 {
  font-size: clamp(2rem, 6vw, 4.5rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.landing-label {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  opacity: 0.5;
}
```

## Chapter Labels

Pattern: 40px dash + uppercase text + 0.2em letter-spacing

```tsx
<p className="text-xs md:text-sm font-semibold uppercase tracking-[0.2em] opacity-50 flex items-center gap-4">
  <span className="w-10 h-px bg-current opacity-50"></span>
  {label}
</p>
```

## Chapter Numbers

```tsx
<span className="font-serif italic opacity-[0.08]"
      style={{ fontSize: 'clamp(6rem, 15vw, 12rem)', lineHeight: 1 }}>
  {String(number).padStart(2, '0')}
</span>
```

**Positioning:** `absolute top-4 left-4 md:top-8 md:left-8`

## Word-by-Word Reveal

```tsx
// Split title into words for staggered animation
<h1 className="hero-title">
  {title.split(' ').map((word, i) => (
    <span key={i} className="word inline-block opacity-0 translate-y-8">
      {word}{' '}
    </span>
  ))}
</h1>
```
