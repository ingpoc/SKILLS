# CSS-Only Animation Patterns

Reference for IntersectionObserver patterns and CSS animations used in lightweight scroll-storytelling.

---

## Core Setup

### IntersectionObserver Initialization

```javascript
const observerOptions = {
  root: null,
  rootMargin: '0px',
  threshold: [0.1, 0.3, 0.6]
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const ratio = entry.intersectionRatio;
      // Handle based on visibility ratio
    }
  });
}, observerOptions);
```

**Multi-threshold:** Use for progressive animations based on scroll depth.

---

## Hero Animations

### Staggered Word Reveal (setTimeout)

```javascript
const words = document.querySelectorAll('.hero-title .word');
words.forEach((word, i) => {
  setTimeout(() => {
    word.style.opacity = '1';
    word.style.transform = 'translateY(0)';
  }, i * 100);
});

setTimeout(() => {
  document.querySelector('.hero-subtitle').style.opacity = '1';
}, words.length * 100 + 200);
```

**Pattern:** Use index-based setTimeout for simple stagger effect.

---

## Scroll-Based Reveals

### Simple Fade Observer

```javascript
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll('.chapter-content').forEach(el => {
  fadeObserver.observe(el);
});
```

**CSS:**
```css
.chapter-content {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 1s ease, transform 1s ease;
}
.chapter-content.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Direction-Aware Reveal

```javascript
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const rect = entry.target.getBoundingClientRect();
      const isFromLeft = rect.left < window.innerWidth / 2;

      entry.target.classList.add('visible');
      entry.target.classList.add(isFromLeft ? 'from-left' : 'from-right');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
```

---

## Spotlight Layer

### Mouse Follow with Class Toggle

```javascript
const spotlight = document.getElementById('spotlight');
const sections = document.querySelectorAll('.hero, .chapter, .quote-section, .finale');

document.addEventListener('mousemove', (e) => {
  requestAnimationFrame(() => {
    spotlight.style.left = e.clientX + 'px';
    spotlight.style.top = e.clientY + 'px';
  });
});

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const isDark = entry.target.classList.contains('dark') ||
                   entry.target.classList.contains('hero') ||
                   entry.target.classList.contains('finale');
    if (entry.isIntersecting && isDark) {
      spotlight.classList.add('active');
    } else if (!entry.isIntersecting) {
      spotlight.classList.remove('active');
    }
  });
}, { threshold: 0.5 });

sections.forEach(section => sectionObserver.observe(section));
```

**CSS:**
```css
#spotlight {
  position: fixed;
  width: 400px;
  height: 400px;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(250,249,245,0.08) 0%, transparent 70%);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s ease;
  z-index: 100;
}
#spotlight.active {
  opacity: 1;
}
```

---

## Transition Animations

### Transition Line Grow

```javascript
const transitionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const line = entry.target.querySelector('.transition-line');
    if (entry.isIntersecting && line) {
      line.classList.add('visible');
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.transition-section').forEach(el => {
  transitionObserver.observe(el);
});
```

**CSS:**
```css
.transition-line {
  width: 1px;
  height: 0;
  background: var(--cream);
  opacity: 0.2;
  transition: height 1s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.transition-line.visible {
  height: 150px;
}
```

---

## Parallax Effects

### Simple Parallax with CSS Variable

```javascript
window.addEventListener('scroll', () => {
  const scrolled = window.pageYOffset;
  document.querySelectorAll('.parallax').forEach(el => {
    const speed = el.dataset.speed || 0.5;
    el.style.transform = `translateY(${scrolled * speed}px)`;
  });
});
```

**Optimized:** Use `requestAnimationFrame` for smoother results.

```javascript
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      const scrolled = window.pageYOffset;
      document.querySelectorAll('.parallax').forEach(el => {
        const speed = el.dataset.speed || 0.5;
        el.style.transform = `translateY(${scrolled * speed}px)`;
      });
      ticking = false;
    });
    ticking = true;
  }
});
```

---

## SVG Animations

### Path Fill Reveal

```javascript
const svgObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const paths = entry.target.querySelectorAll('.organic-path');
      paths.forEach((path, i) => {
        setTimeout(() => {
          path.classList.add('visible');
        }, i * 150);
      });
      svgObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('svg').forEach(svg => svgObserver.observe(svg));
```

**CSS:**
```css
.organic-path {
  opacity: 0;
  transition: opacity 0.8s ease;
}
.organic-path.visible {
  opacity: var(--target-opacity);
}
```

**Note:** Store target opacity in CSS variable or data attribute.

### Scale Reveal for Center Elements

```css
.scale-path {
  transform: scale(0);
  transform-origin: center;
  transition: transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.scale-path.visible {
  transform: scale(1);
}
```

**Easing:** `cubic-bezier(0.34, 1.56, 0.64, 1)` creates back-out effect.

---

## Continuous Animations

### CSS-Only Rotation

```css
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.orbit-group {
  animation: rotate 25s linear infinite;
  transform-origin: 250px 250px;
}
```

### Float Animation

```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.hero-line {
  animation: float 20s ease-in-out infinite;
}
```

### Pulse Animation

```css
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  100% { transform: scale(1.5); opacity: 0; }
}

.pulse-ring {
  animation: pulse 2s ease-out infinite;
}
```

---

## Custom Cursor

### Simple Follow Cursor

```javascript
const cursor = document.querySelector('.cursor');
const cursorDot = document.querySelector('.cursor-dot');

document.addEventListener('mousemove', (e) => {
  requestAnimationFrame(() => {
    cursor.style.left = e.clientX - 10 + 'px';
    cursor.style.top = e.clientY - 10 + 'px';
    cursorDot.style.left = e.clientX - 2 + 'px';
    cursorDot.style.top = e.clientY - 2 + 'px';
  });
});

// Hover effects
document.querySelectorAll('a, button').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hovering'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('hovering'));
});
```

**CSS:**
```css
.cursor {
  position: fixed;
  width: 20px;
  height: 20px;
  border: 1px solid var(--cream);
  border-radius: 50%;
  pointer-events: none;
  z-index: 9999;
  transition: transform 0.1s ease, width 0.2s, height 0.2s;
  mix-blend-mode: difference;
}
.cursor.hovering {
  transform: scale(2);
  background: rgba(250, 249, 245, 0.1);
}
```

---

## Performance Tips

1. **Use `requestAnimationFrame`** for scroll-based animations
2. **Unobserve after reveal** to prevent redundant callbacks
3. **Throttle scroll handlers** with ticking pattern
4. **Use CSS transforms** instead of position changes
5. **Limit observer count** - one observer can watch many elements
6. **Use `will-change` sparingly** - only on elements that will animate

---

## Browser Support

| Feature | Fallback |
|---------|----------|
| IntersectionObserver | Scroll event listener |
| CSS Mix-blend-mode | Solid color cursor |
| CSS Custom properties | Hex values |
| `requestAnimationFrame` | Direct updates |
