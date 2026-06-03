# DRAMS Responsive Breakpoints

Mobile-first responsive design system following Tailwind CSS breakpoints.

---

## Mobile-First Philosophy

Write base styles for mobile (320px+), use prefixes for larger screens.

```css
/* Base: Mobile styles */
.component { padding: 16px; }

/* Tablet: 768px+ */
@media (min-width: 768px) {
  .component { padding: 24px; }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .component { padding: 32px; }
}
```

**With Tailwind:**

```tsx
<div className="p-4 md:p-6 lg:p-8">
```

---

## Breakpoint Scale

| Name | Min Width | Prefix | Device |
|------|-----------|--------|--------|
| Mobile | - | (base) | Phones, small tablets |
| Tablet | 768px | `md:` | Tablets, small laptops |
| Desktop | 1024px | `lg:` | Laptops, desktops |
| Wide | 1200px | `xl:` | Large desktops |

---

## Container Patterns

### Responsive Container

```tsx
<div className="w-full max-w-7xl mx-auto px-6">
```

### Fixed Max-Width Container

```tsx
<div className="max-w-1200px mx-auto px-6">
```

### Breakpoint-Based Widths

```tsx
<div className="w-full md:w-3/4 lg:w-2/3 xl:w-1/2">
```

---

## Layout Transformations

### Navigation: Stack → Row

```tsx
<nav className="flex flex-col md:flex-row gap-4 md:gap-8">
```

### Grid: 1 → 2 → 3 Columns

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
```

### Card Grid with Responsive Items

```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
```

---

## Typography Scale

### Responsive Font Sizes

```tsx
<h1 className="text-3xl md:text-4xl lg:text-5xl">
```

### Breakpoint Values

| Element | Mobile | Tablet (768px) | Desktop (1024px) |
|---------|--------|----------------|------------------|
| H1 | 28px | 36px | 48px |
| H2 | 24px | 30px | 36px |
| H3 | 20px | 24px | 28px |
| Body | 16px | 16px | 18px |

---

## Touch Targets

### Minimum Sizes

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Buttons | 44x44px | 48x48px |
| Links | 44x44px | 48x48px |
| Form inputs | 44px height | 48px height |
| Touch controls | 44x44px | 48x48px |

### Touch-Friendly Spacing

```tsx
<button className="min-h-[44px] min-w-[44px] p-3">
```

---

## Mobile-Specific Patterns

### Table to Cards (Mobile)

```tsx
<div className="md:hidden">
  {items.map(item => (
    <div className="card" key={item.id}>
      {/* Card layout for mobile */}
    </div>
  ))}
</div>

<table className="hidden md:table">
  {/* Table layout for desktop */}
</table>
```

### Responsive Sidebar

```tsx
<div className="fixed inset-y-0 left-0 z-50 w-64 transform -translate-x-full md:relative md:translate-x-0">
```

### Hamburger Menu (Mobile Only)

```tsx
<button className="md:hidden" aria-label="Open menu">
  <svg>{/* Hamburger icon */}</svg>
</button>

<nav className="hidden md:flex">
  {/* Desktop nav always visible */}
</nav>
```

---

## Safe Area Insets (iOS Notch)

### CSS with Safe Areas

```css
.header {
  padding-top: env(safe-area-inset-top);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
}
```

### Tailwind with Safe Areas

```tsx
<header className="pt-safe-top pb-safe-bottom">
```

---

## Responsive Utilities

### Hide/Show by Breakpoint

```tsx
<div className="hidden md:block">Desktop only</div>
<div className="block md:hidden">Mobile only</div>
```

### Text Alignment

```tsx
<p className="text-center md:text-left lg:text-justify">
```

### Flex Direction

```tsx
<div className="flex flex-col md:flex-row">
```

### Gap Scaling

```tsx
<div className="gap-4 md:gap-6 lg:gap-8">
```

---

## Testing Approach

### Common Device Sizes

| Device | Width | Height |
|--------|-------|--------|
| iPhone SE | 375px | 667px |
| iPhone 14 | 390px | 844px |
| iPhone 14 Pro Max | 430px | 932px |
| iPad | 768px | 1024px |
| iPad Pro | 1024px | 1366px |
| Desktop | 1280px+ | 720px+ |

### Validation Checklist

- [ ] Navigation accessible on all sizes
- [ ] Touch targets ≥44x44px on mobile
- [ ] Text readable without zoom (16px minimum)
- [ ] Horizontal scroll avoided
- [ ] Content fits viewport without excessive scrolling
- [ ] Forms usable on touch devices

---

## Performance Considerations

### Lazy Load Images

```tsx
<img loading="lazy" src="..." alt="...">
```

### Responsive Images

```tsx
<img
  src="small.jpg"
  srcSet="small.jpg 400w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
  alt="..."
>
```

### Code Splitting

```tsx
const LazyComponent = dynamic(() => import('./Component'), {
  loading: () => <div className="skeleton">Loading...</div>
});
```

---

## Accessibility (Mobile)

### Focus Management

```tsx
<button
  className="focus:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(255,97,26)]"
  onFocus={() => setFocused(true)}
  onBlur={() => setFocused(false)}
>
```

### Viewport Meta Tag

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Tap Highlight Color

```css
* {
  -webkit-tap-highlight-color: transparent;
}
```

### Touch Action

```css
.interactive {
  touch-action: manipulation;
}
```
