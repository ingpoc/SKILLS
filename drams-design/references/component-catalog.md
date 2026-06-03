# DRAMS Component Catalog

Complete reference for all Dieter Rams-inspired components.

---

## Layout Components

### 1. Sticky Header

Fixed header with logo (Sacramento 36px) and pill navigation.

```tsx
<header style={{ position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgb(238,238,238)', backgroundColor: 'white' }}>
  <div style={{ maxWidth: '1200px', padding: '0 24px', display: 'flex', justifyContent: 'space-between', gap: '48px' }} className="py-4">
    <Link href="/" style={{ textDecoration: 'none' }}>
      <h1 className="font-sacramento" style={{ fontSize: '36px', fontWeight: 400, color: '#333', margin: 0 }}>flatwatch</h1>
      <p style={{ fontSize: '12px', color: '#999', margin: '4px 0 0 0' }}>Society Cash Tracker</p>
    </Link>
    <nav style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }} role="navigation">
      {/* Pills */}
    </nav>
  </div>
</header>
```

| Property | Value |
|----------|-------|
| Position | `sticky` |
| Max width | `1200px` |
| Logo font | `Sacramento` 36px |
| Logo subtitle | 12px |

### 2. Pill Navigation

Horizontal pills: inactive gray, active orange.

```tsx
<Link href="/page" className={`h-10 px-4 rounded-full font-medium text-sm transition-all ${isActive ? 'bg-[rgb(255,97,26)] text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)]' : 'bg-[rgb(238,238,238)] text-[#333] hover:bg-[rgb(232,232,232)]'}`} aria-current={isActive ? 'page' : undefined}>
  Label
</Link>
```

| State | Background | Text | Shadow |
|-------|------------|------|--------|
| Inactive | `rgb(238,238,238)` | `#333` | None |
| Active | `rgb(255,97,26)` | `white` | `0 2px 8px rgba(255,97,26,0.3)` |

### 3. Hero Section

Centered with responsive typography.

```tsx
<div className="min-h-screen flex items-center justify-center">
  <main className="max-w-2xl flex flex-col items-center gap-12 text-center px-6">
    <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight">Title</h1>
    <p className="text-lg text-[#666] max-w-lg">Subtitle</p>
  </main>
</div>
```

| Property | Mobile | Desktop |
|----------|--------|---------|
| H1 size | 36px | 48px |
| Min height | 100vh | 100vh |

### 4. Card Grid

Responsive 1→2→3 columns.

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

| Breakpoint | Columns | Gap |
|------------|---------|-----|
| Mobile | 1 | 16px |
| Tablet (768px) | 2 | 24px |
| Desktop (1024px) | 3 | 24px |

### 5. DRAMS Card

White card, lift on hover.

```tsx
<div className="rounded-3xl bg-white p-8 shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.1)] hover:-translate-y-1">
  {children}
</div>
```

| State | Shadow | Transform |
|-------|--------|-----------|
| Default | `0 4px 16px rgba(0,0,0,0.06)` | None |
| Hover | `0 8px 24px rgba(0,0,0,0.1)` | `translateY(-4px)` |

---

## Form Components

### 6. Rolling Search

Expandable search with animated orange ball that slides to reveal input.

### HTML Structure

```html
<div class="search-container" id="searchContainer">
  <div class="gray-track"></div>
  <div class="shadow-layer-1"></div>
  <div class="shadow-layer-2"></div>
  <input type="text" class="search-input" placeholder="Search products...">
  <div class="orange-ball" id="orangeBall">
    <svg class="icon search-icon">...</svg>
    <svg class="icon arrow-icon">...</svg>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.search-container` | `position: relative; width: 234px; height: 44px` |
| `.gray-track` | Expands from 42px to 234px |
| `.orange-ball` | Slides from left: 96px to 192px |
| `.search-input` | `opacity: 0` → `1` on expand |

### Interaction States

| State | Class | Changes |
|-------|-------|---------|
| Collapsed | (default) | Ball centered, input hidden |
| Expanded | `.expanded` | Ball right, input visible |
| Focus | `input:focus` | Shows caret (orange) |

### JavaScript

```javascript
const searchContainer = document.getElementById('searchContainer');
const orangeBall = document.getElementById('orangeBall');
const searchInput = document.querySelector('.search-input');

function expandSearch() {
  searchContainer.classList.add('expanded');
  searchInput.focus();
}

function collapseSearch() {
  searchContainer.classList.remove('expanded');
  searchInput.value = '';
}

orangeBall.addEventListener('click', () => {
  if (searchContainer.classList.contains('expanded')) {
    // Submit search
  } else {
    expandSearch();
  }
});

searchInput.addEventListener('blur', () => setTimeout(collapseSearch, 150));
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') collapseSearch();
});
```

### Accessibility

- `aria-label="Search products"`
- `aria-expanded="false/true"` on container
- Keyboard: Enter to submit, Escape to close

---

## 2. Text Box

Input field with focus indicator dot.

### HTML Structure

```html
<div class="text-box">
  <div class="text-box-track">
    <input type="text" class="text-box-input" placeholder="Enter your email...">
    <div class="text-box-indicator"></div>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.text-box-track` | `height: 48px; background: rgb(238, 238, 238); border-radius: 48px` |
| `.text-box-input` | `flex: 1; border: none; background: transparent` |
| `.text-box-indicator` | `width: 12px; height: 12px; opacity: 0` |

### Interaction States

| State | Selector | Changes |
|-------|----------|---------|
| Default | (base) | Gray track, hidden indicator |
| Focus | `:focus-within` | Darker track, shadow, indicator visible |

---

## 3. Dropdown

Custom select with orange ball toggle that rotates when open.

### HTML Structure

```html
<div class="dropdown">
  <div class="dropdown-track">
    <span class="dropdown-label placeholder">Select size</span>
    <div class="dropdown-ball">
      <svg class="dropdown-arrow">...</svg>
    </div>
  </div>
  <div class="dropdown-menu">
    <div class="dropdown-item">XS - Extra Small</div>
    ...
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.dropdown-track` | `height: 48px; cursor: pointer` |
| `.dropdown-ball` | `width: 32px; transition: transform 0.3s` |
| `.dropdown.open .dropdown-ball` | `transform: rotate(180deg)` |
| `.dropdown-menu` | `opacity: 0; transform: translateY(-10px)` |

### Interaction States

| State | Class | Changes |
|-------|-------|---------|
| Closed | (default) | Menu hidden, ball pointing down |
| Open | `.open` | Menu visible, ball rotated |
| Hover | `:hover` on track | Darker background |
| Selected | `.selected` | Orange text, no placeholder class |

---

## 4. Select Box (Quantity)

Quantity selector with +/- buttons.

### HTML Structure

```html
<div class="select-box">
  <button class="select-btn minus-btn">
    <svg>...</svg>
  </button>
  <span class="select-value">1</span>
  <button class="select-btn plus-btn">
    <svg>...</svg>
  </button>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.select-box` | `display: inline-flex; background: rgb(238, 238, 238)` |
| `.select-btn` | `width: 40px; height: 40px; border-radius: 50%` |
| `.select-btn:hover` | `background: rgba(255, 97, 26, 0.1)` |
| `.select-btn:active` | `transform: scale(0.95)` |

---

## 5. Time Selector

Circular hours/minutes display with +/- buttons.

### HTML Structure

```html
<div class="time-selector">
  <div class="time-unit active">
    <span class="time-label">Hours</span>
    <div class="time-display">
      <span class="time-value hours">02</span>
    </div>
    <div class="time-controls">
      <button class="time-btn time-up">+</button>
      <button class="time-btn time-down">−</button>
    </div>
  </div>
  <span class="time-separator">:</span>
  <div class="time-unit active">
    <span class="time-label">Minutes</span>
    <div class="time-display">
      <span class="time-value minutes">30</span>
    </div>
    <div class="time-controls">
      <button class="time-btn time-up">+</button>
      <button class="time-btn time-down">−</button>
    </div>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.time-display` | `width: 80px; height: 80px; border-radius: 50%` |
| `.time-unit.active .time-display::before` | `border: 2px solid rgb(255, 97, 26)` |
| `.time-btn` | `width: 32px; background: rgb(255, 97, 26)` |

---

## 6. Toggle Switch

Animated on/off slider with orange active state.

### HTML Structure

```html
<div class="toggle-switch" id="toggle1">
  <div class="toggle-ball"></div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.toggle-switch` | `width: 56px; height: 32px; background: rgb(238, 238, 238)` |
| `.toggle-switch.active` | `background: rgb(255, 97, 26)` |
| `.toggle-ball` | `width: 26px; left: 3px → 27px` |

---

## 7. Product Card

Image + details + add button with hover lift.

### HTML Structure

```html
<div class="product-card">
  <div class="product-image">
    <span class="product-badge">New</span>
    <div class="product-placeholder"></div>
  </div>
  <div class="product-details">
    <div class="product-name">Minimal Watch</div>
    <div class="product-category">Accessories</div>
    <div class="product-footer">
      <span class="product-price">$189</span>
      <button class="product-add-btn">...</button>
    </div>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.product-card:hover` | `transform: translateY(-4px)` |
| `.product-placeholder` | Orange radial gradient ball |
| `.product-add-btn` | Orange gradient, shadow |

---

## 8. Flip Card

3D flip reveal with specs on back.

### HTML Structure

```html
<div class="flip-card-container">
  <div class="flip-card">
    <div class="flip-card-front">...</div>
    <div class="flip-card-back">...</div>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `.flip-card-container` | `perspective: 1000px` |
| `.flip-card` | `transform-style: preserve-3d` |
| `.flip-card.flipped` | `transform: rotateY(180deg)` |
| `.flip-card-back` | `transform: rotateY(180deg)` |

---

## 9. Radio Group

Pill-shaped radio options with dot indicators.

### HTML Structure

```html
<div class="radio-group">
  <div class="radio-option">
    <input type="radio" name="color" id="color1" checked>
    <label class="radio-label" for="color1">
      <div class="radio-dot"></div>
      <span class="radio-text">White</span>
    </label>
  </div>
</div>
```

### CSS Patterns

| Element | Key Styles |
|---------|-----------|
| `input` | `position: absolute; opacity: 0` |
| `.radio-label` | `padding: 12px 18px; border-radius: 48px` |
| `input:checked + .radio-label` | `background: rgb(255, 97, 26); color: white` |

---

## Common Patterns

### Orange Gradient Ball

```css
background: radial-gradient(
  50% 50% at 30% 30%,
  rgb(255, 150, 102) 0%,
  rgb(255, 97, 26) 100%
);
box-shadow:
  rgba(232, 61, 23, 0.4) 0px 0px 2px -1px inset,
  rgba(0, 0, 0, 0.2) -2px -1px 3px 0px inset;
```

### Gray Track Base

```css
background: rgb(238, 238, 238);
border-radius: 48px;
transition: all 0.3s ease;
```

### Hover State

```css
background: rgb(232, 232, 232);
```

### Primary Animation

```css
transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
```
