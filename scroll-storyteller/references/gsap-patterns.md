# GSAP Animation Patterns

Reference for all GSAP + ScrollTrigger recipes used in scroll-storytelling.

---

## Core Setup

### Plugin Registration

```javascript
gsap.registerPlugin(ScrollTrigger);
```

Required before using any ScrollTrigger features.

---

## Hero Animations

### Staggered Word Reveal

```javascript
const heroTl = gsap.timeline();
heroTl.to('.hero-title .word', {
  y: 0,
  opacity: 1,
  duration: 1,
  stagger: 0.08,
  ease: 'power3.out'
})
.to('.hero-subtitle', {
  opacity: 1,
  duration: 1,
  ease: 'power2.out'
}, 0.3)
.to('.scroll-indicator', {
  opacity: 1,
  duration: 0.8,
  ease: 'power2.out'
}, 0.6);
```

**Pattern:** Timeline with staggered word animation, then subtitle, then scroll indicator.

---

## SVG Draw Animations

### Setup Stroke Dasharray

```javascript
document.querySelectorAll('.draw-path').forEach(path => {
  const length = path.getTotalLength();
  path.style.strokeDasharray = length;
  path.style.strokeDashoffset = length;
});
```

**Note:** Run before draw animation to prepare paths.

### Draw on Scroll

```javascript
gsap.to('.draw-path', {
  strokeDashoffset: 0,
  duration: 1.5,
  stagger: 0.15,
  ease: 'power2.inOut',
  scrollTrigger: {
    trigger: '.chapter',
    start: 'top 70%'
  }
});
```

**Effect:** Paths appear to draw themselves as user scrolls.

---

## ScrollTrigger Patterns

### Content Fade-In (Set + To Pattern)

```javascript
gsap.set('.chapter-content', { opacity: 0, y: 40 });
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

**Pattern:** Use `gsap.set()` for initial state, then `gsap.to()` for animation.

### Staggered Element Reveal

```javascript
gsap.to('.fade-path', {
  opacity: (i, target) => target.style.opacity || target.getAttribute('opacity') || 1,
  duration: 0.8,
  stagger: { each: 0.15, from: 'start' },
  scrollTrigger: {
    trigger: card,
    start: 'top 70%'
  }
});
```

**Note:** Uses function to read original opacity value.

### Scale Reveal with Back Ease

```javascript
gsap.to('.scale-path', {
  scale: 1,
  duration: 0.8,
  stagger: 0.1,
  ease: 'back.out(1.7)',
  scrollTrigger: {
    trigger: card,
    start: 'top 70%'
  }
});
```

**Effect:** Elements scale up with slight overshoot.

---

## Continuous Animations

### Orbit Rotation

```javascript
gsap.to('.orbit-group', {
  rotation: 360,
  duration: 25,
  repeat: -1,
  ease: 'none',
  transformOrigin: '250px 250px'
});
```

**Pattern:** `repeat: -1` for infinite loop, `ease: 'none'` for constant speed.

### Pulse Animation

```javascript
gsap.to('.pulse-ring', {
  scale: 1.5,
  opacity: 0,
  duration: 2,
  repeat: -1,
  ease: 'none'
});
```

**Effect:** Expanding and fading ring.

### Gentle Float (Yoyo)

```javascript
gsap.to('.keyhole-group', {
  y: -5,
  duration: 2,
  repeat: -1,
  yoyo: true,
  ease: 'power1.inOut'
});
```

**Effect:** Subtle up and down motion.

---

## Parallax Effects

### Illustration Parallax

```javascript
gsap.utils.toArray('.illustration svg').forEach(svg => {
  gsap.to(svg, {
    y: -50,
    scrollTrigger: {
      trigger: svg.closest('.chapter'),
      start: 'top center',
      end: 'bottom center',
      scrub: 1
    }
  });
});
```

**Pattern:** `scrub: 1` links animation to scroll position with smooth lag.

### Progress Bar Scrub

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

**Effect:** Bar fills based on total page scroll.

---

## Spotlight Layer

### Mouse Follow with Section Toggle

```javascript
const spotlightLayer = document.querySelector('.spotlight-layer');
const spotlightCircle = document.getElementById('spotlight-circle');
const darkSections = document.querySelectorAll('.hero, .chapter.dark, .quote-section, .finale');

// Follow cursor
document.addEventListener('mousemove', (e) => {
  if (spotlightCircle) {
    spotlightCircle.setAttribute('cx', e.clientX);
    spotlightCircle.setAttribute('cy', e.clientY);
  }
});

// Activate on dark sections
ScrollTrigger.create({
  trigger: '.hero, .chapter, .quote-section, .finale',
  start: 'top center',
  end: 'bottom center',
  onEnter: () => spotlightLayer?.classList.add('active'),
  onLeave: () => spotlightLayer?.classList.remove('active'),
  toggleActions: 'play reverse play reverse'
});
```

**Pattern:** Use `ScrollTrigger.create()` for non-animated triggers (state changes).

---

## Custom Cursor

### Smooth Follow Cursor

```javascript
const cursorRing = document.querySelector('.cursor-ring');
const cursorDot = document.querySelector('.cursor-dot');
let cursorX = 0, cursorY = 0;
let dotX = 0, dotY = 0;

document.addEventListener('mousemove', (e) => {
  const mouseX = e.clientX;
  const mouseY = e.clientY;

  cursorX += (mouseX - cursorX) * 0.15;
  cursorY += (mouseY - cursorY) * 0.15;

  dotX += (mouseX - dotX) * 0.4;
  dotY += (mouseY - dotY) * 0.4;

  cursorRing.style.left = cursorX - 20 + 'px';
  cursorRing.style.top = cursorY - 20 + 'px';

  cursorDot.style.left = dotX - 4 + 'px';
  cursorDot.style.top = dotY - 4 + 'px';
});
```

**Pattern:** Lerp (linear interpolation) for smooth delayed movement.

---

## Transition Animations

### Transition Line Grow

```javascript
gsap.utils.toArray('.transition-line').forEach(line => {
  gsap.to(line, {
    height: 150,
    duration: 1,
    ease: 'power2.inOut',
    scrollTrigger: {
      trigger: line.closest('.transition-section'),
      start: 'top 70%'
    }
  });
});
```

**Effect:** Vertical line grows when transition section enters viewport.

---

## Common Easing Functions

| Ease | Best For |
|------|----------|
| `power3.out` | Hero reveals, smooth deceleration |
| `power2.inOut` | Symmetric transitions |
| `back.out(1.7)` | Scale reveals with overshoot |
| `power1.inOut` | Gentle float animations |
| `none` | Continuous loops |

---

## ScrollTrigger Start Positions

| Position | When to Use |
|----------|-------------|
| `top 80%` | Content fades (early, before fully visible) |
| `top 70%` | SVG animations (standard timing) |
| `top 60%` | Quote reveals (later, more visible) |
| `top center` | Parallax triggers |

---

## Performance Tips

1. **Batch similar animations** with `stagger` instead of multiple tweens
2. **Use `scrub` sparingly** - computationally expensive
3. **Clean up on mobile** - consider simpler animations for touch devices
4. **Pin strategically** - avoid excessive `pin: true` usage
