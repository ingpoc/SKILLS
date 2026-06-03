# DRAMS Layout Patterns

Proven layout patterns from FlatWatch, following Dieter Rams' "less, but better" philosophy.

---

## Layout Philosophy

- **Generous whitespace**: Breathing room between elements
- **Max-width containers**: Content constrained for readability
- **Sticky headers**: Navigation always accessible
- **Mobile-first**: Base styles for mobile, scale up

---

## Page Shell Structure

### Header Container

```tsx
<header style={{ position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgb(238,238,238)', backgroundColor: 'white' }}>
  <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', height: '72px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
    <Link href="/" style={{ textDecoration: 'none' }}>
      <h1 className="font-sacramento" style={{ fontSize: '36px', fontWeight: 400, color: '#333', margin: 0 }}>flatwatch</h1>
      <p style={{ fontSize: '12px', color: '#999', margin: '4px 0 0 0' }}>Society Cash Tracker</p>
    </Link>
    <nav style={{ display: 'flex', gap: '8px' }}>{/* Pills */}</nav>
  </div>
</header>
```

| Property | Value | Usage |
|----------|-------|-------|
| Position | `sticky` | Keeps header in view |
| Z-index | `50` | Above content |
| Border | `rgb(238,238,238)` | Subtle separator |
| Max width | `1200px` | Wide content |
| Padding | `0 24px` | Side spacing |

---

## Content Containers

### Narrow Container (Reading)

```css
.container-narrow {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### Wide Container (Dashboards)

```css
.container-wide {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

| Container | Max Width | Use Case |
|-----------|-----------|----------|
| Narrow | 800px | Articles, forms |
| Standard | 1024px | Standard pages |
| Wide | 1200px | Dashboards, grids |

---

## Hero Sections

### Centered Hero

```tsx
<div className="min-h-screen flex items-center justify-center">
  <main className="max-w-2xl flex flex-col items-center gap-12 text-center px-6">
    <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight">Title</h1>
    <p className="text-lg text-[#666] max-w-lg">Subtitle description</p>
  </main>
</div>
```

### Hero with Card

```tsx
<div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-50 to-white">
  <main className="flex flex-col items-center gap-12 text-center px-6">
    <div className="rounded-3xl bg-white p-8 shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.1)] hover:-translate-y-1">
      {/* Card content */}
    </div>
  </main>
</div>
```

---

## Card Grids

### Responsive Grid (1 → 2 → 3)

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
  {items.map(item => (
    <Card key={item.id} {...item} />
  ))}
</div>
```

### Two Column Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
```

---

## Navigation Patterns

### Pill Navigation (Horizontal)

```tsx
<nav style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }} role="navigation">
  {navItems.map(item => {
    const isActive = pathname === item.href;
    return (
      <Link
        key={item.href}
        href={item.href}
        className={`
          flex items-center justify-center h-10 px-4 rounded-full font-medium text-sm transition-all
          ${isActive ? 'bg-[rgb(255,97,26)] text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)]' : 'bg-[rgb(238,238,238)] text-[#333] hover:bg-[rgb(232,232,232)]'}
        `}
        aria-current={isActive ? 'page' : undefined}
      >
        {item.label}
      </Link>
    );
  })}
</nav>
```

### Pill Dimensions

| State | Height | Padding | Radius |
|-------|--------|---------|--------|
| Default | 40px | `0 16px` | 48px (50%) |

### Pill Colors

| State | Background | Text | Shadow |
|-------|------------|------|--------|
| Inactive | `rgb(238,238,238)` | `#333` | None |
| Hover | `rgb(232,232,232)` | `#333` | None |
| Active | `rgb(255,97,26)` | `white` | `0 2px 8px rgba(255,97,26,0.3)` |

---

## Status Indicators

### Status Pill with Dot

```tsx
<div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[rgb(238,238,238)]">
  <div className={`w-2 h-2 rounded-full ${statusColor}`}></div>
  <span className="text-sm font-medium">{statusLabel}</span>
</div>
```

### Status Colors

| Status | Color |
|--------|-------|
| Active | `rgb(255,97,26)` |
| Success | `rgb(34,197,94)` |
| Warning | `rgb(234,179,8)` |
| Error | `rgb(239,68,68)` |
| Neutral | `rgb(107,114,128)` |

---

## Typography Scale

### Heading Scale

| Level | Mobile | Desktop | Weight |
|-------|--------|---------|--------|
| H1 | 32px | 48px | 600 |
| H2 | 28px | 36px | 600 |
| H3 | 24px | 28px | 500 |
| H4 | 20px | 24px | 500 |

### Body Scale

| Use | Size | Weight | Line Height |
|-----|------|--------|-------------|
| Lead | 18px | 400 | 1.6 |
| Body | 16px | 400 | 1.5 |
| Small | 14px | 400 | 1.4 |
| Caption | 12px | 400 | 1.3 |

---

## Spacing System

### Gap Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Small gaps |
| md | 12px | Medium gaps |
| lg | 16px | Standard gaps |
| xl | 24px | Section padding |
| 2xl | 32px | Large sections |
| 3xl | 48px | Page sections |

### Padding Scale

| Element | Padding |
|---------|---------|
| Card | 32px |
| Section | 48px 0 |
| Container sides | 24px |
| Button | 12px 24px |

---

## Shadow Hierarchy

| Level | CSS | Usage |
|-------|-----|-------|
| Subtle | `0 2px 8px rgba(0,0,0,0.04)` | Component sections |
| Card | `0 4px 16px rgba(0,0,0,0.06)` | Product cards |
| Lift | `0 8px 24px rgba(0,0,0,0.1)` | Card hover |
| Focus | `0 4px 12px rgba(0,0,0,0.08)` | Input focus |
| Orange | `0 2px 8px rgba(255,97,26,0.3)` | Orange elements |

---

## Animation Timing

| Type | Duration | Easing |
|------|----------|--------|
| Hover | 0.2s | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Transition | 0.3s | `cubic-bezier(0.16, 1, 0.3, 1)` |
| 3D Transform | 0.6s | `cubic-bezier(0.16, 1, 0.3, 1)` |

---

## Accessibility Considerations

### Focus Management

```tsx
<button className="focus:outline-none focus-visible:outline-2 focus-visible:outline-[rgb(255,97,26)] focus-visible:outline-offset-2">
```

### Skip Links

```html
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-[rgb(255,97,26)] focus:text-white focus:rounded-full">
  Skip to main content
</a>
```

### Landmarks

```tsx
<header role="banner">
  <nav role="navigation" aria-label="Main">
  <main role="main" id="main-content">
  <footer role="contentinfo">
```
