# Accessibility Guide (ARIA First)

ARIA attributes and patterns for Rams-aligned components.

## Core Principles

1. **ARIA First**: Build accessibility in, not bolt on
2. **Semantic HTML**: Use button, input, nav, not div
3. **Keyboard Nav**: All interactions accessible via keyboard
4. **Screen Reader**: Announce state changes appropriately

## ARIA Attributes

### Relationships

| Attribute | Use | Example |
|-----------|-----|---------|
| `aria-label` | Hidden label | `<button aria-label="Close" />` |
| `aria-labelledby` | Reference label | `<div aria-labelledby="title">` |
| `aria-describedby` | Reference description | `<input aria-describedby="help" />` |
| `aria-controls` | Controlled element | `<button aria-controls="menu">` |

### States

| Attribute | Use | Example |
|-----------|-----|---------|
| `aria-expanded` | Open/closed | `<button aria-expanded={isOpen}>` |
| `aria-checked` | Check state | `<div role="checkbox" aria-checked />` |
| `aria-selected` | Tab selected | `<tab aria-selected="true">` |
| `aria-disabled` | Disabled state | `<button aria-disabled />` |
| `aria-busy` | Loading state | `<div aria-busy="true">` |

### Live Regions

| Attribute | Use | Example |
|-----------|-----|---------|
| `role="status"` | Polite update | `<div role="status">Saved!</div>` |
| `role="alert"` | Important alert | `<div role="alert">Error!</div>` |
| `aria-live` | Update priority | `<div aria-live="polite">` |
| `aria-atomic` | All content | `<div aria-atomic="true">` |

## Component Patterns

### Button

```tsx
// Icon button: needs aria-label
<button aria-label="Search">
  <SearchIcon />
</button>

// Loading: aria-busy
<button aria-busy={isLoading}>
  {isLoading ? <Spinner /> : "Submit"}
</button>

// Disabled: aria-disabled (or native disabled)
<button disabled aria-disabled="true">
  Disabled
</button>
```

### Input

```tsx
// With label + error + description
<Field>
  <FieldLabel htmlFor="email">Email</FieldLabel>
  <Input
    id="email"
    aria-describedby={error ? "email-error" : "email-help"}
    aria-invalid={!!error}
  />
  {!error && <FieldDescription id="email-help">We'll never spam</FieldDescription>}
  {error && <FieldError id="email-error">{error}</FieldError>}
</Field>
```

### Select

```tsx
// Radix UI handles ARIA, ensure:
<Select>
  <SelectTrigger aria-label="Select option" />
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
  </SelectContent>
</Select>
```

### Checkbox

```tsx
// Custom checkbox needs role + aria-checked
<div
  role="checkbox"
  aria-checked={checked}
  tabIndex={0}
  onClick={toggle}
  onKeyDown={e => e.key === "Enter" && toggle()}
>
  {checked && <CheckIcon />}
</div>
```

### Toggle

```tsx
// Switch role
<button
  role="switch"
  aria-checked={enabled}
  onClick={toggle}
>
  {enabled ? "On" : "Off"}
</button>
```

### Menu

```tsx
// Radix UI handles most
<DropdownMenu>
  <DropdownMenuTrigger aria-haspopup="true" />
  <DropdownMenuContent>
    <DropdownMenuItem>Item 1</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### Tabs

```tsx
// Radix UI handles
<Tabs>
  <TabsList aria-label="Settings tabs">
    <TabsTrigger value="general">General</TabsTrigger>
    <TabsTrigger value="advanced">Advanced</TabsTrigger>
  </TabsList>
  <TabsPanel value="general">Content</TabsPanel>
</Tabs>
```

### Toast

```tsx
// Live region for announcements
<div role="status" aria-live="polite">
  {message}
</div>

// For errors:
<div role="alert" aria-live="assertive">
  {error}
</div>
```

### Modal

```tsx
// Radix Dialog handles:
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
  >
    <h2 id="dialog-title">Title</h2>
    <p id="dialog-description">Description</p>
  </DialogContent>
</Dialog>
```

### Alert

```tsx
// Aria alert
<div role="alert">
  <AlertCircleIcon aria-hidden="true" />
  <span>Error message</span>
</div>
```

### Loading

```tsx
// Aria busy
<div aria-busy="true" aria-live="polite">
  <Spinner />
  <span className="sr-only">Loading...</span>
</div>
```

### Card

```tsx
// Semantic structure
<article>
  <header>
    <h3>Card title</h3>
  </header>
  <p>Card description</p>
  <footer>
    <button>Action</button>
  </footer>
</article>
```

### Slider

```tsx
// Radix handles, ensure:
<Slider
  aria-label="Volume"
  value={[value]}
  onValueChange={setValue}
/>
```

## Keyboard Navigation

### Tab Order

- Logical flow: left→right, top→bottom
- `tabIndex={0}` for custom interactive elements
- `tabIndex={-1}` for programmatic focus

### Key Handlers

| Key | Action | Pattern |
|-----|--------|---------|
| Enter | Activate | `onClick` + `onKeyDown` |
| Space | Activate/toggle | `onKeyDown` (e.key === " ") |
| Escape | Close/dismiss | Modal, menu, dropdown |
| Arrow keys | Navigate | Tabs, menus, sliders |

```tsx
// Custom interactive element
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={e => {
    if (e.key === "Enter" || e.key === " ") {
      handleClick()
    }
  }}
>
  Click me
</div>
```

### Focus Management

```tsx
// Trap focus in modal
useEffect(() => {
  const focusable = modalRef.current?.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const first = focusable[0] as HTMLElement
  const last = focusable[focusable.length - 1] as HTMLElement

  const handleTab = (e: KeyboardEvent) => {
    if (e.key !== "Tab") return
    if (e.shiftKey) {
      if (document.activeElement === first) last.focus()
    } else {
      if (document.activeElement === last) first.focus()
    }
    e.preventDefault()
  }

  document.addEventListener("keydown", handleTab)
  return () => document.removeEventListener("keydown", handleTab)
}, [])
```

## Screen Reader Only

```tsx
// Visually hidden but announced
<span className="sr-only">Loading data...</span>

// Tailwind CSS:
<span className="absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0">
  Screen reader text
</span>
```

## Color Contrast (WCAG AA)

| Contrast | Normal text | Large text (18pt+) |
|----------|-------------|-------------------|
| AA | 4.5:1 | 3:1 |
| AAA | 7:1 | 4.5:1 |

**Slate palette (AA compliant):**

| Foreground | Background | Ratio |
|------------|------------|-------|
| `text-slate-900` | `bg-white` | 15.5:1 |
| `text-slate-700` | `bg-white` | 8.4:1 |
| `text-slate-500` | `bg-white` | 4.7:1 |
| `text-white` | `bg-slate-900` | 15.5:1 |

## Testing Checklist

- [ ] Keyboard: Tab through all interactive elements
- [ ] Keyboard: Activate with Enter/Space
- [ ] Keyboard: Escape closes modals/menus
- [ ] Screen reader: Labels announced
- [ ] Screen reader: State changes announced
- [ ] Screen reader: Errors announced
- [ ] Color contrast: 4.5:1 minimum
- [ ] Focus visible: `focus:ring` or equivalent
- [ ] Semantic HTML: button, input, nav, etc.
- [ ] ARIA attributes: No missing/invalid

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Radix UI Accessibility](https://www.radix-ui.com/docs/primitives/overview/accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
