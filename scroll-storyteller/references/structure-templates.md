# Structure Templates

HTML templates and narrative structure patterns for scroll-storytelling experiences.

---

## Narrative Structure

```
Hero Section (dark bg)
  ├── Staggered title reveal
  ├── Subtitle fade-in
  └── Scroll indicator

Chapter 1 (light bg)
  ├── Chapter number (large, faded)
  ├── Content: label, title, description
  └── Organic illustration

Transition (animated line)

Chapter 2 (dark bg, reversed layout)
  └── ...

Quote Section (dark bg)
  └── Large italic quote with quotation mark

[Repeat chapters...]

Finale (dark bg)
  ├── Combined symbol illustration
  ├── Closing title
  └── Summary text
```

---

## Section Templates

### Hero

**GSAP Version (Hero Background):**
```html
<section class="hero">
  <!-- Hero Background SVG -->
  <svg class="hero-background" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
    <path class="hero-line" fill="var(--foam)" opacity="0.03" d="..."/>
    <path class="hero-line" fill="var(--foam)" opacity="0.02" d="..."/>
  </svg>

  <h1 class="hero-title">
    <span class="line"><span class="word">Your</span> <span class="word">Title</span></span>
  </h1>
  <p class="hero-subtitle">Subtitle text</p>
  <div class="scroll-indicator">...</div>
</section>
```

**CSS-only Version (Desk Lamp):**
```html
<section class="hero">
  <div class="lamp-container">
    <svg class="lamp-svg" viewBox="0 0 200 300" fill="none">
      <!-- Desk lamp SVG -->
    </svg>
    <div class="light-cone" id="light-cone"></div>
  </div>
  <h1 class="hero-title">
    <span class="line"><span class="word">Your</span> <span class="word">Title</span></span>
  </h1>
  <p class="hero-subtitle">Subtitle text</p>
  <div class="scroll-indicator">...</div>
</section>
```

---

### Chapter

```html
<section class="chapter light" data-chapter="1">
  <span class="chapter-number">01</span>
  <div class="chapter-inner">
    <div class="chapter-content">
      <p class="chapter-label">Layer One</p>
      <h2 class="chapter-title">Title</h2>
      <div class="chapter-description">
        <p>Content...</p>
      </div>
    </div>
    <div class="illustration">
      <svg viewBox="0 0 500 500" fill="none">
        <path class="organic-path" fill="#141413" d="M..."/>
      </svg>
    </div>
  </div>
</section>
```

---

### Quote

```html
<section class="quote-section dark">
  <blockquote class="quote">
    <span class="quote-mark">"</span>
    Your quote text here.
  </blockquote>
</section>
```

---

### Finale

```html
<section class="finale dark">
  <div class="finale-rings">
    <div class="ring" style="width: 100px; height: 100px;"></div>
    <div class="ring" style="width: 180px; height: 180px;"></div>
    <div class="ring" style="width: 260px; height: 260px;"></div>
  </div>
  <h2 class="finale-title">Your Conclusion</h2>
  <p class="finale-text">
    End with a powerful summary that ties everything together.
  </p>
</section>
```

---

## Light/Dark Pattern by Chapter Count

| Chapters | Pattern |
|----------|---------|
| 3 | Ch1=Light → Ch2=Dark → Ch3=Light |
| 4 | Ch1=Light → Ch2=Dark → Ch3=Light → Ch4=Dark |
| 5 | Ch1=Light → Ch2=Dark → Ch3=Light → Ch4=Dark → Ch5=Light |
