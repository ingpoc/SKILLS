# Component Patterns: React + Tailwind + Framer Motion

15 component patterns following Dieter Rams' principles.

## Form Components

### Button

**Principles:** Useful, Understandable, Unobtrusive

**Variants:**

| Variant | Tailwind |
|---------|----------|
| Primary | `bg-slate-900 text-white hover:bg-slate-800` |
| Secondary | `bg-slate-100 text-slate-900 hover:bg-slate-200` |
| Text | `text-slate-700 hover:text-slate-900` |
| Icon | `p-2 rounded-md hover:bg-slate-100` |

**States:**

```tsx
// States: default, hover, focus, disabled, loading
<button
  disabled={isLoading}
  className="bg-slate-900 text-white px-4 py-2 rounded-md
    disabled:opacity-50 disabled:cursor-not-allowed
    focus:ring-2 focus:ring-slate-400
    hover:bg-slate-800 transition-colors"
>
  {isLoading ? <Spinner /> : children}
</button>
```

**Template:** `assets/component_templates/button.tsx`

---

### Input

**Principles:** Useful, Understandable, Honest

**Types:** text, email, password, number, search

**States:**

```tsx
<input
  type="text"
  className="border border-slate-300 rounded-md px-3 py-2
    focus:ring-2 focus:ring-slate-400 focus:border-transparent
    disabled:opacity-50 disabled:bg-slate-50"
  aria-describedby={error ? "error" : description}
/>
```

**With label + error:**

```tsx
<Field>
  <FieldLabel htmlFor="email">Email</FieldLabel>
  <Input id="email" type="email" error={hasError} />
  {error && <FieldError id="error">{error}</FieldError>}
</Field>
```

**Template:** `assets/component_templates/input.tsx`

---

### Select

**Principles:** Useful, Understandable

**Radix UI + Tailwind:**

```tsx
import { Select, SelectTrigger, SelectContent, SelectItem } from "@/components/ui/select"

<Select>
  <SelectTrigger className="border border-slate-300 rounded-md px-3 py-2" />
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
  </SelectContent>
</Select>
```

**Template:** `assets/component_templates/select.tsx`

---

### Checkbox

**Principles:** Useful, Understandable

**Radix UI + Tailwind:**

```tsx
<Checkbox className="h-4 w-4 rounded border-slate-300" />
<Label>Accept terms</Label>
```

**Template:** `assets/component_templates/checkbox.tsx`

---

### Toggle

**Principles:** Understandable, Unobtrusive

**Radix UI + Tailwind:**

```tsx
<Switch className="h-6 w-11 bg-slate-200 rounded-full" />
```

**States:**

```tsx
<Switch
  checked={enabled}
  onCheckedChange={setEnabled}
  className={`${
    enabled ? "bg-slate-900" : "bg-slate-200"
  } h-6 w-11 rounded-full transition-colors`}
/>
```

**Template:** `assets/component_templates/toggle.tsx`

---

## Navigation Components

### Menu

**Principles:** Useful, Understandable

**Radix UI Dropdown:**

```tsx
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <button>Menu</button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

**Template:** `assets/component_templates/menu.tsx`

---

### Tabs

**Principles:** Useful, Understandable

**Framer Motion + Radix:**

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

<Tabs defaultValue="tab1">
  <TabsList className="border-b border-slate-200">
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

**Template:** `assets/component_templates/tabs.tsx`

---

## Feedback Components

### Toast

**Principles:** Unobtrusive, Honest

**Framer Motion AnimatePresence:**

```tsx
import { AnimatePresence } from "framer-motion"
import { Toast } from "@/components/ui/toast"

<AnimatePresence>
  {toasts.map(toast => (
    <Toast
      key={toast.id}
      className="fixed bottom-4 right-4 bg-slate-900 text-white px-4 py-3 rounded-md shadow-lg"
    >
      {toast.message}
    </Toast>
  ))}
</AnimatePresence>
```

**Variants:**

| Type | Tailwind |
|------|----------|
| Success | `bg-green-600` |
| Error | `bg-red-600` |
| Info | `bg-slate-900` |

**Template:** `assets/component_templates/toast.tsx`

---

### Modal

**Principles:** Thorough, Honest

**Radix UI Dialog:**

```tsx
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <button>Open</button>
  </DialogTrigger>
  <DialogContent className="bg-white rounded-lg shadow-xl p-6 max-w-md">
    <h2 className="text-lg font-medium">Modal title</h2>
    <p>Modal content</p>
  </DialogContent>
</Dialog>
```

**States:** Open, closed, closing animation

**Template:** `assets/component_templates/modal.tsx`

---

### Alert

**Principles:** Honest, Understandable

**ARIA alert:**

```tsx
<div role="alert" className="bg-red-50 border border-red-200 rounded-md p-4">
  <div className="flex items-start gap-3">
    <AlertCircleIcon className="text-red-600 mt-0.5" />
    <div>
      <h3 className="font-medium text-red-900">Error</h3>
      <p className="text-red-700 text-sm">{message}</p>
    </div>
  </div>
</div>
```

**Variants:**

| Type | Background | Border | Text |
|------|------------|--------|------|
| Error | `bg-red-50` | `border-red-200` | `text-red-900` |
| Warning | `bg-yellow-50` | `border-yellow-200` | `text-yellow-900` |
| Success | `bg-green-50` | `border-green-200` | `text-green-900` |
| Info | `bg-blue-50` | `border-blue-200` | `text-blue-900` |

**Template:** `assets/component_templates/alert.tsx`

---

### Loading

**Principles:** Honest, Unobtrusive

**Patterns:**

1. **Spinner:**

```tsx
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
  className="h-6 w-6 border-2 border-slate-200 border-t-slate-900 rounded-full"
/>
```

1. **Skeleton:**

```tsx
<div className="animate-pulse bg-slate-200 rounded h-4 w-full" />
```

1. **Progress bar:**

```tsx
<div className="h-2 bg-slate-200 rounded-full overflow-hidden">
  <motion.div
    initial={{ width: 0 }}
    animate={{ width: `${progress}%` }}
    className="h-full bg-slate-900"
  />
</div>
```

**Template:** `assets/component_templates/loading.tsx`

---

## Display Components

### Card

**Principles:** Aesthetic, Little Design

**Minimal card:**

```tsx
<div className="border border-slate-200 rounded-lg p-6 space-y-4">
  <h3 className="text-slate-900 font-medium">{title}</h3>
  <p className="text-slate-600">{description}</p>
</div>
```

**Variants:**

| Type | Additions |
|------|-----------|
| Content card | Image, title, description |
| Interactive card | Hover effect, onClick |
| Media card | Image/video, caption |

**Template:** `assets/component_templates/card.tsx`

---

### Slider

**Principles:** Useful, Understandable

**Radix UI Slider:**

```tsx
import { Slider } from "@/components/ui/slider"

<Slider
  value={[value]}
  onValueChange={[setValue]}
  className="w-full"
/>
```

**With Framer Motion:**

```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 100 }}
  whileDrag={{ scale: 1.05 }}
  className="h-2 bg-slate-200 rounded-full cursor-grab"
/>
```

**Template:** `assets/component_templates/slider.tsx`

---

## Form Container

### Form

**Principles:** Thorough, Useful

**Structure:**

```tsx
<form onSubmit={handleSubmit} className="space-y-6">
  <FieldGroup>
    <Field>
      <FieldLabel htmlFor="name">Name</FieldLabel>
      <Input id="name" required />
      <FieldDescription>Enter your full name</FieldDescription>
    </Field>
    <Field>
      <FieldLabel htmlFor="email">Email</FieldLabel>
      <Input id="email" type="email" required />
      <FieldError>{errors.email}</FieldError>
    </Field>
  </FieldGroup>

  <Button type="submit">Submit</Button>
</form>
```

**Validation:** Zod, react-hook-form

**Template:** `assets/component_templates/form.tsx`

---

## Quick Patterns

| Component | Base | Motion | Accessibility |
|-----------|------|--------|---------------|
| Button | Tailwind classes | Optional hover | `aria-label` |
| Input | Tailwind classes | None | `aria-describedby` |
| Select | Radix UI | Built-in | Built-in |
| Checkbox | Radix UI | None | Built-in |
| Toggle | Radix UI | Transition | Built-in |
| Menu | Radix UI | Built-in | Built-in |
| Tabs | Radix UI | Optional swipe | Built-in |
| Toast | Tailwind + Framer | Slide in | `role="status"` |
| Modal | Radix UI | Scale in | Built-in |
| Alert | Tailwind | None | `role="alert"` |
| Loading | Tailwind + Framer | Rotate/pulse | `aria-busy` |
| Card | Tailwind | Optional hover | Semantic heading |
| Slider | Radix UI | Optional drag | Built-in |
| Form | Radix Field | None | Labels + errors |
