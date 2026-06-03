# Animation Patterns

Complete reference for GSAP and CSS-only animation patterns used in scroll-storytelling experiences.

---

## Shared: Custom Cursor (Dual Layer)

```javascript
// Outer ring follows with easing
cursorX += (mouseX - cursorX) * 0.15;
// Inner dot follows faster
dotX += (mouseX - dotX) * 0.4;
```

```css
.cursor {
  mix-blend-mode: difference;  /* Works on both themes */
}
```

---

## CSS-Only Patterns

### Staggered Word Reveal (CSS)

```javascript
words.forEach((word, i) => {
  setTimeout(() => word.classList.add('revealed'), 300 + i * 150);
});
```

```css
.word {
  opacity: 0;
  transform: translateY(100%);
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.word.revealed {
  opacity: 1;
  transform: translateY(0);
}
```

### Scroll-Triggered Content (IntersectionObserver)

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.2, rootMargin: '0px 0px -100px 0px' });
```

### SVG Path Stagger (CSS)

```css
.illustration.visible .organic-path:nth-child(1) { transition-delay: 0.2s; }
.illustration.visible .organic-path:nth-child(2) { transition-delay: 0.4s; }
.illustration.visible .organic-path:nth-child(3) { transition-delay: 0.6s; }
```

### Spotlight on Dark Sections

```javascript
const spotlightObserver = new IntersectionObserver((entries) => {
  let anyDarkVisible = entries.some(e =>
    e.isIntersecting && e.intersectionRatio > 0.3
  );
  spotlightLayer.classList.toggle('active', anyDarkVisible);
}, { threshold: [0, 0.3, 0.6, 1] });
```

---

## GSAP Patterns

### Setup (CDN)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
```

### Staggered Word Reveal (GSAP)

```javascript
gsap.registerPlugin(ScrollTrigger);

const heroTl = gsap.timeline();
heroTl.to('.hero-title .word', {
  y: 0,
  opacity: 1,
  duration: 1,
  stagger: 0.1,
  ease: 'power3.out'
});
```

### SVG Draw Animation

```javascript
// Setup: set initial stroke state
const drawPaths = document.querySelectorAll('.draw-path');
drawPaths.forEach(path => {
  const length = path.getTotalLength();
  path.style.strokeDasharray = length;
  path.style.strokeDashoffset = length;
});

// Animate on scroll
gsap.to('.draw-path', {
  strokeDashoffset: 0,
  duration: 1.5,
  stagger: 0.2,
  ease: 'power2.inOut',
  scrollTrigger: {
    trigger: '.illustration',
    start: 'top 70%'
  }
});
```

### Continuous Orbit Animation

```javascript
// Orbiting elements around center
gsap.to('.orbit-group', {
  rotation: 360,
  duration: 20,
  repeat: -1,
  ease: 'none',
  transformOrigin: '250px 250px'  // Center of 500x500 viewBox
});
```

### Parallax with Scrub

```javascript
gsap.to('.parallax-element', {
  y: -100,
  scrollTrigger: {
    trigger: '.chapter',
    start: 'top bottom',
    end: 'bottom top',
    scrub: 1  // Smooth scroll-linked animation
  }
});
```

### Chapter Fade-In

**IMPORTANT:** Use `gsap.set()` + `gsap.to()` pattern, NOT `gsap.from()`.
`gsap.from()` can conflict with CSS initial states and cause elements to remain invisible.

```javascript
// Set initial state explicitly
gsap.set('.chapter-content', { opacity: 0, y: 40 });

// Animate to visible on scroll trigger
gsap.utils.toArray('.chapter-content').forEach(content => {
  gsap.to(content, {
    opacity: 1,
    y: 0,
    duration: 1,
    scrollTrigger: {
      trigger: content,
      start: 'top 80%'
    }
  });
});
```

### Progress Bar

```javascript
gsap.to('.progress-bar', {
  scaleX: 1,
  ease: 'none',
  scrollTrigger: {
    trigger: 'body',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 0.3
  }
});
```

---

## Animation Classes

| Class | Description | Usage |
|-------|-------------|-------|
| `organic-path` | Base class for all SVG paths | Always applied |
| `fade-path` | Fade in animation | Default for most paths |
| `scale-path` | Scale up animation | Combined with fade-path |
| `draw-path` | Stroke draw animation (GSAP only) | For line/path drawing effects |

**Pattern:** Multiple classes combined: `<path class="organic-path fade-path draw-path">`
