# GSAP Animation Recipes

## Setup

```typescript
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);
```

## Chapter Animation Pattern

```typescript
export const useChapterAnimations = () => {
  useEffect(() => {
    const chapters = document.querySelectorAll('.chapter');
    if (chapters.length === 0) return;

    const ctx = gsap.context(() => {
      chapters.forEach((chapter) => {
        const illustration = chapter.querySelector('.illustration');
        if (!illustration) return;

        const fillPaths = illustration.querySelectorAll('.fill-path');
        const drawPaths = illustration.querySelectorAll('.draw-path');
        const labels = illustration.querySelectorAll('.label-path');

        // Fill paths: opacity + scale
        if (fillPaths.length > 0) {
          gsap.to(fillPaths, {
            opacity: 0.9,
            scale: 1,
            duration: 0.8,
            stagger: 0.1,
            ease: 'back.out(1.5)',
            scrollTrigger: {
              trigger: illustration,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          });
        }

        // Draw paths: stroke animation
        if (drawPaths.length > 0) {
          drawPaths.forEach(path => {
            const length = (path as SVGPathElement).getTotalLength() || 1000;
            (path as SVGPathElement).style.strokeDasharray = String(length);
            (path as SVGPathElement).style.strokeDashoffset = String(length);
          });

          gsap.to(drawPaths, {
            strokeDashoffset: 0,
            opacity: 0.6,
            duration: 1.5,
            stagger: 0.1,
            ease: 'power2.inOut',
            scrollTrigger: {
              trigger: illustration,
              start: 'top 75%',
              toggleActions: 'play none none reverse',
            },
          });
        }

        // Labels fade in last
        if (labels.length > 0) {
          gsap.to(labels, {
            opacity: 0.7,
            duration: 0.5,
            stagger: 0.08,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: illustration,
              start: 'top 70%',
              toggleActions: 'play none none reverse',
            },
          });
        }
      });
    });

    return () => ctx.revert();
  }, []);
};
```

## Hero Animation Pattern

```typescript
export const useHeroAnimations = () => {
  useEffect(() => {
    const ctx = gsap.context(() => {
      const heroTl = gsap.timeline({ delay: 0.3 });

      // Fragmented paths fade in
      const fragmentedPaths = document.querySelectorAll('.fragmented-identity .fill-path');
      if (fragmentedPaths.length > 0) {
        heroTl.to(fragmentedPaths, {
          opacity: (i) => 0.1 + (i * 0.05),
          duration: 1.2,
          stagger: 0.15,
          ease: 'power2.out',
        });
      }

      // Unified core scale in
      const unifiedCore = document.querySelector('.unified-identity .fill-path');
      if (unifiedCore) {
        heroTl.to(unifiedCore, {
          opacity: 0.2,
          scale: 1,
          duration: 0.8,
          ease: 'back.out(1.3)',
        }, 0.2);
      }

      // Radiating lines draw
      const drawPaths = document.querySelectorAll('.unified-identity .draw-path');
      if (drawPaths.length > 0) {
        drawPaths.forEach(path => {
          const length = (path as SVGPathElement).getTotalLength() || 200;
          (path as SVGPathElement).style.strokeDasharray = String(length);
          (path as SVGPathElement).style.strokeDashoffset = String(length);
        });

        heroTl.to(drawPaths, {
          strokeDashoffset: 0,
          opacity: 0.15,
          duration: 1.2,
          stagger: 0.1,
          ease: 'power2.inOut',
        }, 0.4);
      }

      // Word reveal
      const words = document.querySelectorAll('.hero-title .word');
      if (words.length > 0) {
        heroTl.to(words, {
          y: 0,
          opacity: 1,
          duration: 1,
          stagger: 0.06,
          ease: 'power3.out',
        }, 0.3);
      }
    });

    return () => ctx.revert();
  }, []);
};
```

## Progress Bar

```typescript
export const useProgressBar = () => {
  useEffect(() => {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;

    gsap.to(progressBar, {
      scaleX: 1,
      ease: 'none',
      scrollTrigger: {
        trigger: 'body',
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.3,
      },
    });
  }, []);
};
```

## Key Rules

| Rule | Why |
|------|-----|
| Always use `gsap.context()` | Cleanup on unmount |
| `toggleActions: 'play none none reverse'` | Reversible on scroll |
| Never inline `style={{ scale }}` | Let GSAP handle transforms |
| Initialize strokeDasharray in effect | Not inline styles |
| `stagger: 0.1` | Sequential element animation |

## Common ScrollTrigger Settings

| Pattern | start | toggleActions |
|---------|-------|---------------|
| Content reveal | `top 70%` | `play none none reverse` |
| Fill paths | `top 80%` | `play none none reverse` |
| Draw paths | `top 75%` | `play none none reverse` |
| Labels | `top 70%` | `play none none reverse` |
