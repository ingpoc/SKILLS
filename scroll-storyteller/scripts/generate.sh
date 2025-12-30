#!/usr/bin/env bash
# Generate a new scroll storytelling HTML page with Anthropic design language
# Usage: bash scripts/generate.sh <story-name> [palette-number] [--gsap] [--chapters 3|4|5]
# Palettes: 1=Anthropic, 2=Midnight, 3=Sepia, 4=Forest, 5=Dusk, 6=Ember, 7=Steel, 8=Ocean

set -e

NAME="${1:-story}"
PALETTE="${2:-1}"
USE_GSAP="false"
CHAPTER_COUNT=3  # Default to 3 chapters

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --gsap) USE_GSAP="true" ;;
    --chapters)
      # Next argument will be the count
      ;;
    3|4|5)
      # Check if previous arg was --chapters
      if [[ "${prev_arg}" == "--chapters" ]]; then
        CHAPTER_COUNT="$arg"
      fi
      ;;
  esac
  prev_arg="$arg"
done

# Handle legacy position: bash generate.sh name 1 --gsap
if [[ "$PALETTE" == "--gsap" ]]; then
  PALETTE="1"
  USE_GSAP="true"
elif [[ "$3" == "--gsap" ]]; then
  USE_GSAP="true"
fi

OUTPUT="${NAME}.html"

# Set colors based on palette choice
case $PALETTE in
  1) LIGHT="#FAF9F5"; DARK="#141413" ;;  # Anthropic
  2) LIGHT="#E8F4F8"; DARK="#0D1B2A" ;;  # Midnight
  3) LIGHT="#F5F0E6"; DARK="#2C1810" ;;  # Sepia
  4) LIGHT="#F0F4F0"; DARK="#1A2E1A" ;;  # Forest
  5) LIGHT="#F4F0F8"; DARK="#1E1A2E" ;;  # Dusk
  6) LIGHT="#FFF5F0"; DARK="#2A1A14" ;;  # Ember
  7) LIGHT="#F0F2F5"; DARK="#1A1C20" ;;  # Steel
  8) LIGHT="#F0F8F8"; DARK="#0A1A1A" ;;  # Ocean
  *) LIGHT="#FAF9F5"; DARK="#141413" ;;  # Default: Anthropic
esac

# Chapter number words (bash 3.2 compatible - using function)
get_chapter_word() {
  local num=$1
  case "$num" in
    1) echo "One" ;;
    2) echo "Two" ;;
    3) echo "Three" ;;
    4) echo "Four" ;;
    5) echo "Five" ;;
    *) echo "Chapter_$num" ;;
  esac
}

# Get theme for chapter (alternates light/dark starting with light)
get_chapter_theme() {
  local num=$1
  local remainder=$(expr $num % 2)
  if [ "$remainder" -eq 1 ]; then
    echo "light"
  else
    echo "dark"
  fi
}

# Get reverse class for dark chapters (content/illustration swap)
get_reverse_class() {
  local num=$1
  local remainder=$(expr $num % 2)
  if [ "$remainder" -eq 0 ]; then
    echo "reverse"
  else
    echo ""
  fi
}

# Generate GSAP chapter HTML
generate_gsap_chapter() {
  local num=$1
  local theme=$(get_chapter_theme "$num")
  local reverse=$(get_reverse_class "$num")
  local padded=$(printf "%02d" "$num")
  local word="$(get_chapter_word "$num")"

  # Color vars based on theme
  local fill_color="var(--deep)"
  local accent_color="var(--foam)"
  if [[ "$theme" == "dark" ]]; then
    fill_color="var(--foam)"
    accent_color="var(--deep)"
  fi

  cat << CHAPTER
  <!-- Chapter $num -->
  <section class="chapter $theme">
    <span class="chapter-number">$padded</span>
    <div class="chapter-inner${reverse:+ $reverse}">
CHAPTER

  # For dark chapters, illustration comes first
  if [[ "$theme" == "dark" ]]; then
    cat << CHAPTER
      <div class="illustration">
        <svg viewBox="0 0 500 500" fill="none">
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.2"
            d="M100 120 Q150 100 200 130 Q260 160 300 200 Q330 240 300 290 Q260 330 200 360 Q140 380 100 340 Q70 290 80 230 Q85 170 100 120 Z"/>
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.15"
            d="M380 140 Q420 110 450 150 Q480 200 460 260 Q430 320 370 350 Q320 360 280 330 Q250 290 270 240 Q290 190 330 160 Q350 145 380 140 Z"/>
          <path class="organic-path fade-path draw-path" fill="$fill_color" opacity="0.3"
            d="M150 200 Q200 180 250 220 Q300 260 350 220 Q380 190 360 150 Q330 110 280 140 Q240 170 200 210 Q170 240 140 210 Q120 180 150 200 Z"/>
          <path class="organic-path fade-path scale-path" fill="$fill_color"
            d="M130 190 Q150 180 160 200 Q165 220 150 230 Q130 235 115 220 Q105 200 115 185 Q120 180 130 190 Z"/>
        </svg>
      </div>
      <div class="chapter-content">
        <p class="chapter-label">Chapter $word</p>
        <h2 class="chapter-title">Section $num Title</h2>
        <div class="chapter-description">
          <p>Your content for chapter $num goes here.</p>
        </div>
      </div>
CHAPTER
  else
    cat << CHAPTER
      <div class="chapter-content">
        <p class="chapter-label">Chapter $word</p>
        <h2 class="chapter-title">Section $num Title</h2>
        <div class="chapter-description">
          <p>Your content for chapter $num goes here.</p>
        </div>
      </div>
      <div class="illustration">
        <svg viewBox="0 0 500 500" fill="none">
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.3"
            d="M100 150 Q130 120 170 140 Q210 160 190 200 Q170 240 130 220 Q90 200 100 150 Z"/>
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.3"
            d="M350 120 Q390 100 420 130 Q450 170 410 200 Q370 220 340 190 Q310 160 350 120 Z"/>
          <path class="organic-path fade-path draw-path" fill="$fill_color" opacity="0.4"
            d="M150 180 Q200 150 250 200 Q300 250 370 160 Q320 220 280 250 Q230 270 160 240 Q130 210 150 180 Z"/>
          <path class="organic-path fade-path scale-path" fill="$fill_color"
            d="M250 180 Q290 160 320 200 Q340 250 300 290 Q260 320 220 290 Q180 260 190 220 Q200 190 250 180 Z"/>
        </svg>
      </div>
CHAPTER
  fi

  cat << CHAPTER
    </div>
  </section>

  <!-- Transition -->
  <div class="transition-section">
    <div class="transition-line"></div>
  </div>

CHAPTER
}

# Generate CSS-only chapter HTML
generate_css_chapter() {
  local num=$1
  local theme=$(get_chapter_theme "$num")
  local reverse=$(get_reverse_class "$num")
  local padded=$(printf "%02d" "$num")
  local word="$(get_chapter_word "$num")"

  # Color vars based on theme
  local fill_color="var(--charcoal)"
  local accent_color="var(--cream)"
  if [[ "$theme" == "dark" ]]; then
    fill_color="var(--cream)"
    accent_color="var(--charcoal)"
  fi

  cat << CHAPTER
  <!-- Chapter $num -->
  <section class="chapter $theme" data-chapter="$num">
    <span class="chapter-number">$padded</span>
    <div class="chapter-inner${reverse:+ $reverse}">
      <div class="chapter-content">
        <p class="chapter-label">Chapter $word</p>
        <h2 class="chapter-title">Section $num Title</h2>
        <div class="chapter-description">
          <p>Your content for chapter $num goes here.</p>
        </div>
      </div>
      <div class="illustration">
        <svg viewBox="0 0 500 500" fill="none">
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.3"
            d="M100 150 Q130 120 170 140 Q210 160 190 200 Q170 240 130 220 Q90 200 100 150 Z"/>
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.3"
            d="M350 120 Q390 100 420 130 Q450 170 410 200 Q370 220 340 190 Q310 160 350 120 Z"/>
          <path class="organic-path fade-path" fill="$fill_color" opacity="0.4"
            d="M150 180 Q200 150 250 200 Q300 250 370 160 Q320 220 280 250 Q230 270 160 240 Q130 210 150 180 Z"/>
          <path class="organic-path fade-path" fill="$fill_color"
            d="M250 180 Q290 160 320 200 Q340 250 300 290 Q260 320 220 290 Q180 260 190 220 Q200 190 250 180 Z"/>
        </svg>
      </div>
    </div>
  </section>

  <div class="transition-section $theme">
    <div class="transition-line"></div>
  </div>

CHAPTER
}

# Generate all chapters for GSAP version
generate_all_gsap_chapters() {
  for i in $(seq 1 "$CHAPTER_COUNT"); do
    generate_gsap_chapter "$i"
  done
}

# Generate all chapters for CSS-only version
generate_all_css_chapters() {
  for i in $(seq 1 "$CHAPTER_COUNT"); do
    generate_css_chapter "$i"
  done
}

if [[ "$USE_GSAP" == "true" ]]; then
  # GSAP Version
  cat > "$OUTPUT" << HEREDOC
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$NAME</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --cream: $LIGHT;
      --charcoal: $DARK;
      --foam: $LIGHT;
      --deep: $DARK;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: var(--charcoal);
      color: var(--cream);
      overflow-x: hidden;
    }

    /* Custom Cursor */
    .cursor-ring {
      position: fixed;
      width: 40px;
      height: 40px;
      border: 2px solid var(--cream);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      mix-blend-mode: difference;
      display: none;
    }

    .cursor-dot {
      position: fixed;
      width: 8px;
      height: 8px;
      background: var(--cream);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      mix-blend-mode: difference;
      display: none;
    }

    @media (pointer: fine) {
      .cursor-ring, .cursor-dot { display: block; }
    }

    /* Progress Bar */
    .progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--cream), var(--cream)cc);
      transform-origin: left;
      transform: scaleX(0);
      z-index: 1000;
    }

    /* Spotlight Layer */
    .spotlight-layer {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
      opacity: 0;
      transition: opacity 0.5s ease;
    }

    .spotlight-layer.active {
      opacity: 1;
    }

    /* Hero Section */
    .hero {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px;
      background: var(--charcoal);
      position: relative;
      overflow: hidden;
    }

    .hero-background {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 0;
      pointer-events: none;
    }

    .hero-line {
      animation-duration: 20s;
      animation-iteration-count: infinite;
      animation-timing-function: ease-in-out;
      animation-name: float;
    }

    .hero-line:nth-child(2) {
      animation-delay: -10s;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-20px); }
    }

    .hero-content {
      text-align: center;
      max-width: 900px;
      z-index: 2;
      position: relative;
    }

    .hero-title {
      font-family: 'Instrument Serif', serif;
      font-size: clamp(3rem, 8vw, 7rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      line-height: 1.2;
      margin-bottom: 30px;
      color: var(--cream);
    }

    .hero-title .line { display: block; }
    .hero-title .word {
      display: inline-block;
      opacity: 0;
      transform: translateY(30px);
      margin: 0 0.1em;
    }

    .hero-subtitle {
      font-size: clamp(1rem, 2vw, 1.5rem);
      color: rgba(250, 249, 245, 0.8);
      font-weight: 300;
      line-height: 1.6;
      margin-bottom: 50px;
      opacity: 0;
    }

    .scroll-indicator {
      position: absolute;
      bottom: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      opacity: 0;
    }

    .scroll-indicator span {
      font-size: 0.75rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: rgba(250, 249, 245, 0.6);
    }

    .scroll-line {
      width: 1px;
      height: 60px;
      background: linear-gradient(to bottom, var(--cream), transparent);
    }

    @keyframes scroll-bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(10px); }
    }

    /* Chapter Sections */
    .chapter {
      min-height: 100vh;
      display: flex;
      align-items: center;
      padding: 80px 60px;
      position: relative;
      overflow: hidden;
    }

    .chapter.light { background: var(--foam); color: var(--deep); }
    .chapter.dark { background: var(--deep); color: var(--foam); }

    .chapter-number {
      position: absolute;
      top: 60px;
      left: 60px;
      font-size: 3rem;
      font-weight: 300;
      opacity: 0.15;
      font-family: 'Instrument Serif', serif;
    }

    .chapter-inner {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 60px;
      align-items: center;
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
    }

    .chapter.dark .chapter-inner.reverse {
      grid-template-columns: 1fr 1fr;
    }

    .chapter-content {
      /* Initial state handled by GSAP */
    }

    .chapter-label {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      opacity: 0.6;
      margin-bottom: 15px;
      font-weight: 500;
    }

    .chapter-title {
      font-family: 'Instrument Serif', serif;
      font-size: clamp(2rem, 5vw, 3.5rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      line-height: 1.3;
      margin-bottom: 25px;
    }

    .chapter-description {
      font-size: 1.1rem;
      line-height: 1.8;
      opacity: 0.85;
    }

    .chapter-description p { margin-bottom: 15px; }

    /* Illustration */
    .illustration {
      position: relative;
      height: 400px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .illustration svg {
      width: 100%;
      height: 100%;
      max-width: 500px;
      max-height: 500px;
    }

    /* Transition Section */
    .transition-section {
      height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--charcoal);
    }

    .transition-line {
      width: 1px;
      height: 0;
      background: var(--cream);
      opacity: 0.2;
    }

    /* Quote Section */
    .quote-section {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 80px 60px;
      background: var(--deep);
      color: var(--foam);
    }

    .quote {
      max-width: 800px;
      font-family: 'Instrument Serif', serif;
      font-size: clamp(2rem, 4vw, 2.8rem);
      font-weight: 400;
      line-height: 1.6;
      text-align: center;
      position: relative;
    }

    .quote-mark {
      font-size: 4rem;
      opacity: 0.3;
      display: block;
      margin-bottom: 20px;
    }

    /* Finale */
    .finale {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 60px;
      background: var(--deep);
      color: var(--foam);
      text-align: center;
    }

    .finale-rings {
      position: relative;
      width: 300px;
      height: 300px;
      margin-bottom: 60px;
    }

    .ring {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      border: 2px solid var(--foam);
      border-radius: 50%;
      opacity: 0.3;
    }

    .finale-title {
      font-family: 'Instrument Serif', serif;
      font-size: clamp(2.5rem, 6vw, 4rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      line-height: 1.3;
      margin-bottom: 30px;
    }

    .finale-text {
      font-size: 1.1rem;
      line-height: 1.8;
      max-width: 600px;
      opacity: 0.8;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .chapter-inner { grid-template-columns: 1fr; }
      .chapter { padding: 60px 30px; }
      .hero { padding: 40px 30px; }
      .chapter-number { left: 30px; }
      @media (pointer: coarse) {
        .cursor-ring, .cursor-dot { display: none; }
      }
    }

    @media (prefers-reduced-motion: reduce) {
      * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    }
  </style>
</head>
<body>
  <!-- Cursor -->
  <div class="cursor-ring"></div>
  <div class="cursor-dot"></div>

  <!-- Progress Bar -->
  <div class="progress-bar"></div>

  <!-- Spotlight Layer -->
  <svg class="spotlight-layer">
    <defs>
      <radialGradient id="spotlight-grad">
        <stop offset="0%" stop-color="var(--foam)" stop-opacity="0.08"/>
        <stop offset="100%" stop-color="transparent"/>
      </radialGradient>
    </defs>
    <circle id="spotlight-circle" r="200" fill="url(#spotlight-grad)"/>
  </svg>

  <!-- Hero Section -->
  <section class="hero">
    <!-- Hero Background SVG -->
    <svg class="hero-background" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
      <path class="hero-line" fill="var(--foam)" opacity="0.03" d="M100,500 Q250,300 400,500 T700,500 T1000,500"/>
      <path class="hero-line" fill="var(--foam)" opacity="0.02" d="M0,400 Q150,600 300,400 T600,400 T900,400"/>
    </svg>

    <div class="hero-content">
      <h1 class="hero-title">
        <span class="line">
          <span class="word">Your</span>
          <span class="word">Story</span>
        </span>
        <span class="line">
          <span class="word">Title</span>
        </span>
      </h1>
      <p class="hero-subtitle">A subtitle goes here</p>
    </div>
    <div class="scroll-indicator">
      <span>Scroll to explore</span>
      <div class="scroll-line"></div>
    </div>
  </section>

HEREDOC

# Generate chapters dynamically
generate_all_gsap_chapters >> "$OUTPUT"

# Continue with quote section and rest
cat >> "$OUTPUT" << 'HEREDOC'
  <!-- Quote Section -->
  <section class="quote-section">
    <blockquote class="quote">
      <span class="quote-mark">"</span>
      Add a meaningful quote here to break up the content and provide emphasis.
    </blockquote>
  </section>

  <!-- Finale -->
  <section class="finale">
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

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

  <script>
    gsap.registerPlugin(ScrollTrigger);

    // Custom Cursor
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

    // Spotlight Layer - Follow cursor on dark sections
    const spotlightLayer = document.querySelector('.spotlight-layer');
    const spotlightCircle = document.getElementById('spotlight-circle');
    const darkSections = document.querySelectorAll('.hero, .chapter.dark, .quote-section, .finale');

    document.addEventListener('mousemove', (e) => {
      if (spotlightCircle) {
        spotlightCircle.setAttribute('cx', e.clientX);
        spotlightCircle.setAttribute('cy', e.clientY);
      }
    });

    // Toggle spotlight on dark sections
    ScrollTrigger.create({
      trigger: '.hero, .chapter, .quote-section, .finale',
      start: 'top center',
      end: 'bottom center',
      onEnter: () => spotlightLayer?.classList.add('active'),
      onLeave: () => spotlightLayer?.classList.remove('active'),
      toggleActions: 'play reverse play reverse'
    });

    // Hero Animations
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

    // SVG Draw Animations Setup
    document.querySelectorAll('.draw-path').forEach(path => {
      const length = path.getTotalLength();
      path.style.strokeDasharray = length;
      path.style.strokeDashoffset = length;
    });

    // Draw animations on scroll
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

    // Chapter Content Fade-In (using set + to pattern)
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

    // Quote Animation
    gsap.set('.quote', { opacity: 0, y: 30 });
    gsap.to('.quote', {
      opacity: 1,
      y: 0,
      duration: 1.2,
      scrollTrigger: {
        trigger: '.quote-section',
        start: 'top 60%'
      }
    });

    // Transition Line Animations
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

    // Finale Animations
    gsap.set('.finale-rings, .finale-title, .finale-text', { opacity: 0, y: 40 });

    gsap.to('.finale-rings', {
      opacity: 1,
      scale: 1,
      y: 0,
      duration: 1,
      scrollTrigger: {
        trigger: '.finale',
        start: 'top 60%'
      }
    });

    gsap.to('.finale-title', {
      opacity: 1,
      y: 0,
      duration: 1,
      delay: 0.3,
      scrollTrigger: {
        trigger: '.finale',
        start: 'top 60%'
      }
    });

    gsap.to('.finale-text', {
      opacity: 0.8,
      y: 0,
      duration: 1,
      delay: 0.5,
      scrollTrigger: {
        trigger: '.finale',
        start: 'top 60%'
      }
    });

    // Spinning rings in finale
    gsap.to('.ring:nth-child(1)', {
      rotation: 360,
      duration: 15,
      repeat: -1,
      ease: 'none'
    });

    gsap.to('.ring:nth-child(2)', {
      rotation: -360,
      duration: 20,
      repeat: -1,
      ease: 'none'
    });

    gsap.to('.ring:nth-child(3)', {
      rotation: 360,
      duration: 25,
      repeat: -1,
      ease: 'none'
    });

    // Progress Bar
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

    // Parallax effects on illustrations
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
  </script>
</body>
</html>
HEREDOC
else
  # CSS-only Version
  cat > "$OUTPUT" << HEREDOC
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$NAME</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --cream: $LIGHT;
      --charcoal: $DARK;
      --transition-smooth: cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: var(--charcoal);
      color: var(--cream);
      overflow-x: hidden;
      cursor: none;
    }

    /* Custom Cursor */
    .cursor {
      position: fixed;
      width: 20px;
      height: 20px;
      border: 1px solid var(--cream);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      transition: transform 0.1s ease;
      mix-blend-mode: difference;
    }

    .cursor-dot {
      position: fixed;
      width: 4px;
      height: 4px;
      background: var(--cream);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
    }

    .cursor.hovering {
      transform: scale(2);
      background: rgba(250, 249, 245, 0.1);
    }

    /* Hero Section */
    .hero {
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }

    .lamp-container {
      position: relative;
      width: 200px;
      height: 300px;
      margin-bottom: 40px;
    }

    .lamp-svg { width: 100%; height: 100%; }

    .light-cone {
      position: absolute;
      bottom: -50px;
      left: 50%;
      transform: translateX(-50%);
      width: 300px;
      height: 400px;
      background: radial-gradient(ellipse at top, rgba(250, 249, 245, 0.15) 0%, transparent 70%);
      clip-path: polygon(40% 0%, 60% 0%, 100% 100%, 0% 100%);
      pointer-events: none;
      opacity: 0;
      transition: opacity 1s ease;
    }

    .light-cone.visible { opacity: 1; }

    .hero-title {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: clamp(3rem, 8vw, 7rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      text-align: center;
      line-height: 1.1;
      max-width: 900px;
      padding: 0 20px;
    }

    .hero-title .line { display: block; overflow: hidden; }

    .hero-title .word {
      display: inline-block;
      opacity: 0;
      transform: translateY(100%);
      transition: opacity 0.8s var(--transition-smooth), transform 0.8s var(--transition-smooth);
    }

    .hero-title .word.revealed {
      opacity: 1;
      transform: translateY(0);
    }

    .hero-subtitle {
      margin-top: 30px;
      font-size: 1.1rem;
      font-weight: 300;
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 1s ease 0.5s, transform 1s ease 0.5s;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .hero-subtitle.visible {
      opacity: 0.6;
      transform: translateY(0);
    }

    .scroll-indicator {
      position: absolute;
      bottom: 60px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      opacity: 0;
      animation: fadeInUp 1s ease 1.5s forwards;
    }

    .scroll-indicator span {
      font-size: 0.75rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      opacity: 0.4;
    }

    .scroll-line {
      width: 1px;
      height: 60px;
      background: linear-gradient(to bottom, var(--cream), transparent);
      animation: scrollPulse 2s ease infinite;
    }

    @keyframes scrollPulse {
      0%, 100% { transform: scaleY(1); opacity: 0.4; }
      50% { transform: scaleY(0.5); opacity: 0.8; }
    }

    @keyframes fadeInUp { to { opacity: 1; } }

    /* Chapter Sections */
    .chapter {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      padding: 100px 40px;
    }

    .chapter.light { background: var(--cream); color: var(--charcoal); }
    .chapter.dark { background: var(--charcoal); color: var(--cream); }

    .chapter-inner {
      max-width: 1400px;
      width: 100%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 100px;
      align-items: center;
    }

    .chapter-inner.reverse { direction: rtl; }
    .chapter-inner.reverse > * { direction: ltr; }

    .chapter-number {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: 8rem;
      font-style: italic;
      opacity: 0.1;
      position: absolute;
      top: 40px;
      left: 40px;
      line-height: 1;
    }

    .chapter.light .chapter-number { color: var(--charcoal); }

    .chapter-content {
      opacity: 0;
      transform: translateY(60px);
      transition: opacity 1s var(--transition-smooth), transform 1s var(--transition-smooth);
    }

    .chapter-content.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .chapter-label {
      font-size: 0.75rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      opacity: 0.5;
      margin-bottom: 20px;
    }

    .chapter-title {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: clamp(2.5rem, 5vw, 4rem);
      font-weight: 400;
      line-height: 1.2;
      margin-bottom: 30px;
    }

    .chapter-description {
      font-size: 1.1rem;
      line-height: 1.8;
      opacity: 0.8;
      max-width: 500px;
    }

    .chapter-description p { margin-bottom: 1.5em; }
    .chapter-description p:last-child { margin-bottom: 0; }

    /* Illustration */
    .illustration {
      position: relative;
      width: 100%;
      aspect-ratio: 1;
      opacity: 0;
      transform: scale(0.9);
      transition: opacity 1.2s var(--transition-smooth), transform 1.2s var(--transition-smooth);
    }

    .illustration.visible {
      opacity: 1;
      transform: scale(1);
    }

    .illustration svg { width: 100%; height: 100%; }

    .illustration .organic-path {
      opacity: 0;
      transition: opacity 0.8s ease;
    }

    .illustration.visible .organic-path { opacity: 1; }
    .illustration.visible .organic-path:nth-child(1) { transition-delay: 0.2s; }
    .illustration.visible .organic-path:nth-child(2) { transition-delay: 0.4s; }
    .illustration.visible .organic-path:nth-child(3) { transition-delay: 0.6s; }

    /* Spotlight Layer */
    .spotlight-layer {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
      opacity: 0;
      transition: opacity 0.5s ease;
    }

    .spotlight-layer.active { opacity: 1; }

    /* Transition Section */
    .transition-section {
      height: 50vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }

    .transition-line {
      width: 1px;
      height: 0;
      background: currentColor;
      opacity: 0.2;
      transition: height 1s var(--transition-smooth);
    }

    .transition-line.visible { height: 150px; }

    /* Quote Section */
    .quote-section {
      min-height: 80vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 100px 40px;
    }

    .quote {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: clamp(1.8rem, 4vw, 3rem);
      font-style: italic;
      text-align: center;
      max-width: 900px;
      line-height: 1.5;
      opacity: 0;
      transform: translateY(40px);
      transition: opacity 1s ease, transform 1s ease;
    }

    .quote.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .quote-mark {
      font-size: 6rem;
      opacity: 0.1;
      line-height: 0;
      display: block;
      margin-bottom: -20px;
    }

    /* Finale */
    .finale {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 100px 40px;
    }

    .finale-illustration {
      width: 400px;
      height: 400px;
      margin-bottom: 60px;
      opacity: 0;
      transform: scale(0.8);
      transition: opacity 1.5s ease, transform 1.5s ease;
    }

    .finale-illustration.visible {
      opacity: 1;
      transform: scale(1);
    }

    .finale-title {
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: clamp(2rem, 5vw, 4rem);
      margin-bottom: 30px;
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 1s ease 0.3s, transform 1s ease 0.3s;
    }

    .finale-title.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .finale-text {
      font-size: 1.2rem;
      opacity: 0;
      max-width: 600px;
      line-height: 1.8;
      transition: opacity 1s ease 0.6s;
    }

    .finale-text.visible { opacity: 0.7; }

    /* Responsive */
    @media (max-width: 900px) {
      .chapter-inner { grid-template-columns: 1fr; gap: 60px; }
      .chapter-inner.reverse { direction: ltr; }
      .illustration { max-width: 400px; margin: 0 auto; }
      .chapter-number { font-size: 5rem; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
      }
    }
  </style>
</head>
<body>
  <!-- Custom Cursor -->
  <div class="cursor"></div>
  <div class="cursor-dot"></div>

  <!-- Spotlight Layer -->
  <svg class="spotlight-layer">
    <defs>
      <radialGradient id="spotlight-grad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="rgba(250, 249, 245, 0.08)"/>
        <stop offset="100%" stop-color="transparent"/>
      </radialGradient>
    </defs>
    <circle id="spotlight-circle" r="200" fill="url(#spotlight-grad)"/>
  </svg>

  <!-- Hero Section -->
  <section class="hero">
    <div class="lamp-container">
      <svg class="lamp-svg" viewBox="0 0 200 300" fill="none">
        <ellipse cx="100" cy="280" rx="50" ry="12" fill="#FAF9F5" opacity="0.1"/>
        <path d="M70 280 L75 260 L125 260 L130 280 Z" fill="#FAF9F5"/>
        <path d="M100 260 L100 180 Q100 160 85 150 L60 130" stroke="#FAF9F5" stroke-width="4" fill="none" stroke-linecap="round"/>
        <path d="M30 140 Q60 110 90 130 L60 160 Q40 150 30 140 Z" fill="#FAF9F5"/>
        <ellipse cx="55" cy="145" rx="8" ry="5" fill="#FAF9F5" opacity="0.6"/>
      </svg>
      <div class="light-cone" id="light-cone"></div>
    </div>

    <h1 class="hero-title">
      <span class="line"><span class="word">Your</span> <span class="word">Story</span></span>
      <span class="line"><span class="word">Title</span></span>
    </h1>

    <p class="hero-subtitle">A subtitle goes here</p>

    <div class="scroll-indicator">
      <span>Scroll to begin</span>
      <div class="scroll-line"></div>
    </div>
  </section>

HEREDOC

# Generate chapters dynamically
generate_all_css_chapters >> "$OUTPUT"

# Continue with quote and finale
cat >> "$OUTPUT" << 'HEREDOC'
  <!-- Quote -->
  <section class="quote-section dark">
    <blockquote class="quote">
      <span class="quote-mark">"</span>
      Add a meaningful quote here to break up the content and provide emphasis.
    </blockquote>
  </section>

  <!-- Finale -->
  <section class="finale dark">
    <div class="finale-illustration">
      <svg viewBox="0 0 400 400" fill="none">
        <!-- Concentric symbol - Outer -->
        <path class="organic-path fade-path" fill="var(--cream)" opacity="0.3"
          d="M200 50 Q280 80 320 150 Q360 220 320 290 Q280 360 200 380 Q120 360 80 290 Q40 220 80 150 Q120 80 200 50 Z"/>
        <!-- Middle ring -->
        <path class="organic-path fade-path" fill="var(--cream)" opacity="0.5"
          d="M200 100 Q250 120 280 170 Q300 230 270 280 Q230 330 200 340 Q160 330 130 280 Q100 230 130 170 Q160 120 200 100 Z"/>
        <!-- Center core -->
        <path class="organic-path fade-path" fill="var(--cream)"
          d="M200 170 Q220 160 235 180 Q245 205 230 225 Q210 240 190 230 Q170 215 175 195 Q180 175 195 168 Q197 167 200 170 Z"/>
      </svg>
    </div>
    <h2 class="finale-title">Your Conclusion</h2>
    <p class="finale-text">
      End with a powerful summary that ties everything together.
    </p>
  </section>

  <script>
    // Custom Cursor
    const cursor = document.querySelector('.cursor');
    const cursorDot = document.querySelector('.cursor-dot');
    let mouseX = 0, mouseY = 0, cursorX = 0, cursorY = 0, dotX = 0, dotY = 0;

    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    function animateCursor() {
      cursorX += (mouseX - cursorX) * 0.15;
      cursorY += (mouseY - cursorY) * 0.15;
      cursor.style.left = cursorX - 10 + 'px';
      cursor.style.top = cursorY - 10 + 'px';

      dotX += (mouseX - dotX) * 0.4;
      dotY += (mouseY - dotY) * 0.4;
      cursorDot.style.left = dotX - 2 + 'px';
      cursorDot.style.top = dotY - 2 + 'px';

      const spotlight = document.getElementById('spotlight-circle');
      spotlight.setAttribute('cx', mouseX);
      spotlight.setAttribute('cy', mouseY);

      requestAnimationFrame(animateCursor);
    }
    animateCursor();

    document.querySelectorAll('a, button, .chapter-title').forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('hovering'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('hovering'));
    });

    // Hero Animation
    window.addEventListener('load', () => {
      const words = document.querySelectorAll('.hero-title .word');
      words.forEach((word, i) => {
        setTimeout(() => word.classList.add('revealed'), 300 + i * 150);
      });

      setTimeout(() => {
        document.querySelector('.hero-subtitle').classList.add('visible');
      }, 800);

      setTimeout(() => {
        document.getElementById('light-cone').classList.add('visible');
      }, 1200);
    });

    // Scroll Animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -100px 0px' });

    document.querySelectorAll('.chapter-content, .illustration, .quote, .transition-line, .finale-illustration, .finale-title, .finale-text').forEach(el => {
      observer.observe(el);
    });

    // Spotlight on dark sections
    const spotlightLayer = document.querySelector('.spotlight-layer');
    const darkSections = document.querySelectorAll('.chapter.dark, .quote-section.dark, .finale.dark');

    const spotlightObserver = new IntersectionObserver((entries) => {
      let anyDarkVisible = entries.some(e => e.isIntersecting && e.intersectionRatio > 0.3);
      spotlightLayer.classList.toggle('active', anyDarkVisible);
    }, { threshold: [0, 0.3, 0.6, 1] });

    darkSections.forEach(section => spotlightObserver.observe(section));

    // Parallax
    document.addEventListener('scroll', () => {
      document.querySelectorAll('.illustration').forEach(ill => {
        const rect = ill.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
          const yPos = (rect.top - window.innerHeight / 2) * 0.05;
          ill.style.transform = \`translateY(\${yPos}px) scale(\${ill.classList.contains('visible') ? 1 : 0.9})\`;
        }
      });
    });

    // Touch device support
    if ('ontouchstart' in window) {
      cursor.style.display = 'none';
      cursorDot.style.display = 'none';
      document.body.style.cursor = 'auto';
    }
  </script>
</body>
</html>
HEREDOC
fi

echo "Created: $OUTPUT"
echo ""
echo "Next steps:"
echo "  1. Edit the HTML to customize content"
echo "  2. Replace SVG paths with organic illustrations"
echo "  3. Open in browser to preview"
