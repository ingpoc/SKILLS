# Dieter Rams' 10 Principles for Digital UI

Each principle translated to React/Next.js + Tailwind CSS patterns.

## 1. Innovative

Push boundaries, don't copy.

**Digital:**

- Custom gestures (drag, swipe, long-press)
- Microinteractions (button ripples, input reveals)
- New patterns (command palette, AI assistants)

**Anti-patterns:**

- Copying Apple/Google without thought
- Trend-driven design (gradients, glassmorphism)

**Code:**

```tsx
// Innovative: Gesture-based slider
import { motion } from "framer-motion"

<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 100 }}
  whileDrag={{ scale: 1.1 }}
/>
```

## 2. Useful

Solve real problems, not decoration.

**Digital:**

- Action-driven labels ("Save" vs "Submit")
- Clear CTAs (primary vs secondary)
- Progressive disclosure (show what's needed)

**Anti-patterns:**

- Decorative animations
- Fake loading states
- Gratuitous 3D effects

**Code:**

```tsx
// Useful: Clear purpose button
<button className="bg-slate-900 text-white px-4 py-2 hover:bg-slate-800">
  Create account
</button>

// NOT useful: Decorative
<button className="bg-gradient-to-r from-pink-500 to-purple-500 animate-pulse">
  Click me
</button>
```

## 3. Aesthetic

Form follows function, timeless appeal.

**Digital:**

- Neutral palette (slate, gray, zinc)
- Generous spacing (p-4, m-4, gap-4)
- Minimal borders (border-slate-200)

**Anti-patterns:**

- Bright/vibrant colors
- Dense information
- Trendy gradients

**Code:**

```tsx
// Aesthetic: Minimal card
<div className="border border-slate-200 rounded-lg p-6 space-y-4">
  <h3 className="text-slate-900 font-medium">Card title</h3>
  <p className="text-slate-600">Description</p>
</div>
```

## 4. Understandable

Self-explanatory, intuitive.

**Digital:**

- Icon + text (not just icons)
- Clear affordances (button = clickable)
- Tooltips for complex actions

**Anti-patterns:**

- Icon-only buttons (except standard icons)
- Hidden gestures
- Confusing layouts

**Code:**

```tsx
// Understandable: Icon + text
<button className="flex items-center gap-2">
  <SearchIcon />
  <span>Search</span>
</button>

// NOT understandable: Icon only
<button><SearchIcon /></button>
```

## 5. Unobtrusive

Tools, not distractions.

**Digital:**

- Subtle hover (scale-105, not scale-125)
- Smooth transitions (transition-all duration-200)
- Non-intrusive notifications (bottom-right toast)

**Anti-patterns:**

- Jarring animations (bounce, shake)
- Auto-playing videos
- Center-screen popups

**Code:**

```tsx
// Unobtrusive: Subtle hover
<motion.button
  whileHover={{ scale: 1.05 }}
  transition={{ duration: 0.2 }}
>
  Click
</motion.button>
```

## 6. Honest

No false promises, clear what it does.

**Digital:**

- Accurate loading states (progress bars)
- Real constraints (disabled when invalid)
- Transparent errors ("Network timeout" vs "Something went wrong")

**Anti-patterns:**

- Fake loading delays
- Generic error messages
- Misleading buttons

**Code:**

```tsx
// Honest: Accurate loading
{isLoading ? (
  <div className="flex items-center gap-2">
    <Spinner />
    <span>Uploading {progress}%</span>
  </div>
) : (
  <button>Upload file</button>
)}
```

## 7. Long-lasting

Avoid trends, build for longevity.

**Digital:**

- Stable tech stack (React, Tailwind)
- Semantic HTML (button, input, nav)
- Framework-agnostic patterns (utility classes)

**Anti-patterns:**

- Experimental frameworks
- Proprietary tech
- Complex abstractions

**Code:**

```tsx
// Long-lasting: Semantic HTML
<button className="px-4 py-2 bg-slate-900 text-white">
  Click me
</button>

// NOT: Custom div
<div onClick={...} className="...">Click me</div>
```

## 8. Thorough

Attention to every detail.

**Digital:**

- Error states (validation messages)
- Empty states (helpful illustrations)
- Loading states (skeletons, spinners)
- Disabled states (opacity-50)

**Anti-patterns:**

- Only happy path
- Missing error handling
- Incomplete states

**Code:**

```tsx
// Thorough: All states
{isLoading && <Skeleton />}
{error && <ErrorMessage message={error} />}
{isEmpty && <EmptyState />}
{data && <Content data={data} />}
```

## 9. Environmentally friendly

Efficient, lightweight code.

**Digital:**

- Tree-shakeable imports (import specific components)
- Minimal dependencies (avoid heavy libraries)
- Optimized images (webp, lazy loading)

**Anti-patterns:**

- 500kb component libraries
- Unoptimized images
- Duplicate dependencies

**Code:**

```tsx
// Environmentally friendly: Tree-shakeable
import { Button } from "@/components/ui/button"
// NOT: import * from "huge-ui-lib"
```

## 10. Little design

Less is more, essential only.

**Digital:**

- Remove until removal breaks function
- Single-purpose components
- Minimal props

**Anti-patterns:**

- Swiss-army-knife components
- Configurable everything
- Theme engines

**Code:**

```tsx
// Little design: Essential only
function Button({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return <button onClick={onClick} className="bg-slate-900 px-4 py-2">{children}</button>
}

// NOT: Configurable everything
function Button({ variant, size, color, shadow, border, icon, position, ... })
```

## Quick Reference

| Principle | Key Pattern | Tailwind |
|-----------|-------------|----------|
| Innovative | New interactions | Custom gestures |
| Useful | Clear purpose | Action labels |
| Aesthetic | Minimal | `slate` palette |
| Understandable | Self-evident | Icon + text |
| Unobtrusive | Subtle | `hover:scale-105` |
| Honest | Accurate | Real states |
| Long-lasting | Stable | React/Tailwind |
| Thorough | Complete | All states |
| Environmentally friendly | Lightweight | Tree-shake |
| Little design | Essential | Remove until breaks |
