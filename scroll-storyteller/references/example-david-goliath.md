# Example: David & Goliath Visual Story

Complete worked example demonstrating topic-relevant SVG illustrations for a Biblical/Spiritual narrative using the Anthropic (Warm) palette.

---

## Story Overview

| Attribute | Value |
|-----------|-------|
| **Topic** | Biblical/Spiritual |
| **Theme** | Faith vs. overwhelming odds |
| **Palette** | Anthropic (Warm) |
| **Mood** | Warm - inviting, organic, grounded |
| **Chapters** | 3, 4, or 5 + Hero + Finale (example shows 3) |

---

## Narrative Arc & SVG Strategy

| Position | Chapter | Purpose | SVG Elements | Composition |
|----------|---------|---------|--------------|-------------|
| **Hero** | Valley of Elah | Set the scene, show contrast | hills + figure-small (left) + figure-large (right) | Wide 1000x1000, distant silhouettes |
| **Ch 1** | The Underdog | Introduce David | figure-small + staff + sheep + hills + sun | Centered, pastoral |
| **Ch 2** | The Giant | Show the obstacle | figure-large + armor + helmet + spear + shield + shadow | Imposing, fills frame |
| **Ch 3** | The Victory | Resolution | figure-triumphant + fallen-mass + trajectory + radiate | Dynamic, radiating |
| **Finale** | Faith Triumphs | Symbolic summary | crown + light-rays + stone + dove | Centered symbol |

---

## Hero SVG: Valley of Elah

**Purpose:** Establish the dramatic confrontation to come
**ViewBox:** 1000x1000 (wide scene)
**Composition:** Two distant silhouettes separated by vertical line, hills in background

```svg
<svg class="hero-background" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
  <!-- Distant mountains/hills -->
  <path class="hero-line" fill="var(--foam)" opacity="0.06"
    d="M0 600 Q150 500 300 550 Q450 600 600 520 Q750 440 900 500 Q1000 550 1000 600 L1000 1000 L0 1000 Z"/>
  <path class="hero-line" fill="var(--foam)" opacity="0.04"
    d="M0 700 Q200 650 400 680 Q600 710 800 660 Q900 640 1000 680 L1000 1000 L0 1000 Z"/>

  <!-- Small David silhouette on left -->
  <g class="hero-line" opacity="0.12">
    <ellipse cx="200" cy="750" rx="20" ry="35" fill="var(--foam)"/>
    <circle cx="200" cy="705" r="12" fill="var(--foam)"/>
    <!-- Staff -->
    <path stroke="var(--foam)" stroke-width="3" fill="none" d="M220 720 Q225 680 220 640 Q215 620 200 615"/>
  </g>

  <!-- Giant Goliath silhouette on right -->
  <g class="hero-line" opacity="0.15">
    <path fill="var(--foam)"
      d="M750 550 Q780 520 820 530 Q860 540 880 580 Q900 640 890 720 Q880 780 850 800 Q800 820 760 800 Q720 780 710 720 Q700 640 710 580 Q720 550 750 550 Z"/>
    <ellipse cx="800" cy="510" rx="35" ry="45" fill="var(--foam)"/>
    <!-- Spear -->
    <path stroke="var(--foam)" stroke-width="4" fill="none" d="M870 800 L900 500 L910 400"/>
    <path fill="var(--foam)" d="M910 400 Q900 370 910 350 Q920 370 910 400 Z"/>
  </g>

  <!-- Dramatic vertical line separating them -->
  <path stroke="var(--foam)" stroke-width="1" opacity="0.08" d="M500 300 L500 900"/>

  <!-- Subtle stars/divine light -->
  <circle cx="500" cy="200" r="3" fill="var(--foam)" opacity="0.15"/>
  <circle cx="480" cy="250" r="2" fill="var(--foam)" opacity="0.1"/>
  <circle cx="520" cy="230" r="2" fill="var(--foam)" opacity="0.1"/>
</svg>
```

**Design Notes:**
- Scale contrast: David tiny (left), Goliath massive (right)
- Low opacity (0.04-0.15) for atmospheric, distant feel
- Vertical dividing line suggests the conflict/confrontation
- Divine light hints at heavenly presence

---

## Chapter 1 SVG: The Underdog (David)

**Purpose:** Introduce the humble shepherd protagonist
**ViewBox:** 500x500 (standard chapter)
**Composition:** Centered figure with pastoral context

```svg
<svg viewBox="0 0 500 500" fill="none">
  <!-- Scene: Young David the Shepherd Boy -->

  <!-- Background rolling hills -->
  <path class="organic-path fade-path" fill="var(--deep)" opacity="0.08"
    d="M0 380 Q80 340 160 360 Q240 380 320 350 Q400 320 500 360 L500 500 L0 500 Z"/>
  <path class="organic-path fade-path" fill="var(--deep)" opacity="0.05"
    d="M0 420 Q100 390 200 410 Q300 430 400 400 Q450 385 500 400 L500 500 L0 500 Z"/>

  <!-- Sheep cluster (3 fluffy sheep) -->
  <g class="organic-path fade-path" opacity="0.25">
    <!-- Sheep 1 -->
    <ellipse cx="120" cy="360" rx="35" ry="25" fill="var(--deep)"/>
    <circle cx="145" cy="350" r="12" fill="var(--deep)"/>
    <circle cx="100" cy="375" r="6" fill="var(--deep)" opacity="0.6"/>
    <circle cx="140" cy="375" r="6" fill="var(--deep)" opacity="0.6"/>
    <!-- Sheep 2 -->
    <ellipse cx="180" cy="380" rx="30" ry="20" fill="var(--deep)"/>
    <circle cx="200" cy="372" r="10" fill="var(--deep)"/>
    <!-- Sheep 3 -->
    <ellipse cx="80" cy="385" rx="25" ry="18" fill="var(--deep)"/>
    <circle cx="65" cy="378" r="9" fill="var(--deep)"/>
  </g>

  <!-- David - small, humble figure -->
  <g class="organic-path fade-path scale-path">
    <!-- Body/robe - simple tunic shape -->
    <path fill="var(--deep)" opacity="0.7"
      d="M250 220 Q270 225 280 260 Q285 300 280 340 Q270 360 250 365 Q230 360 220 340 Q215 300 220 260 Q230 225 250 220 Z"/>
    <!-- Head -->
    <circle cx="250" cy="195" r="22" fill="var(--deep)" opacity="0.8"/>
    <!-- Hair suggestion -->
    <path fill="var(--deep)" opacity="0.9"
      d="M235 185 Q250 175 265 185 Q270 195 265 200 Q250 195 235 200 Q230 195 235 185 Z"/>
    <!-- Arms -->
    <path fill="var(--deep)" opacity="0.6"
      d="M225 240 Q200 250 180 245 Q175 240 180 235 Q200 230 220 235 Z"/>
    <path fill="var(--deep)" opacity="0.6"
      d="M275 240 Q300 235 320 250 Q325 255 320 260 Q300 255 280 250 Z"/>
  </g>

  <!-- Shepherd's staff - tall, curved -->
  <path class="organic-path fade-path" stroke="var(--deep)" stroke-width="4" fill="none" opacity="0.6"
    d="M320 250 Q325 200 320 150 Q315 120 290 110 Q270 105 260 115"/>

  <!-- Sling in hand (hint of weapon) -->
  <path class="organic-path fade-path" stroke="var(--deep)" stroke-width="2" fill="none" opacity="0.4"
    d="M180 245 Q160 250 150 240 Q145 230 155 225"/>

  <!-- Sun/light source -->
  <circle class="organic-path fade-path" cx="400" cy="100" r="40" fill="var(--deep)" opacity="0.06"/>
  <circle cx="400" cy="100" r="25" fill="var(--deep)" opacity="0.04"/>
</svg>
```

**Design Notes:**
- David is small but centered (protagonist focus)
- Sheep establish his role as shepherd
- Staff uses stroke (allowed for linear elements)
- Sling hints at the weapon that will defeat the giant
- Warm mood: medium opacity (0.25-0.8), gentle curves

---

## Chapter 2 SVG: The Giant (Goliath)

**Purpose:** Show the overwhelming obstacle
**ViewBox:** 500x500 (standard chapter)
**Composition:** Imposing figure fills the frame

```svg
<svg viewBox="0 0 500 500" fill="none">
  <!-- Scene: Goliath the Giant Warrior - Imposing & Menacing -->

  <!-- Ground/shadow beneath giant -->
  <ellipse class="organic-path fade-path" cx="250" cy="450" rx="150" ry="30" fill="var(--foam)" opacity="0.1"/>

  <!-- Massive legs - planted wide -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.4"
    d="M180 320 Q175 370 170 420 Q165 450 185 455 Q205 450 200 420 Q195 380 200 340 Z"/>
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.4"
    d="M300 320 Q305 370 310 420 Q315 450 335 455 Q355 450 350 420 Q345 380 340 340 Z"/>

  <!-- Massive torso with armor plates -->
  <path class="organic-path fade-path scale-path" fill="var(--foam)" opacity="0.5"
    d="M150 180 Q160 140 200 120 Q250 100 300 120 Q340 140 350 180 Q360 240 350 300 Q340 340 300 350 Q250 360 200 350 Q160 340 150 300 Q140 240 150 180 Z"/>

  <!-- Armor chest plate detail -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.3"
    d="M200 160 Q250 150 300 160 Q310 200 300 240 Q250 250 200 240 Q190 200 200 160 Z"/>

  <!-- Massive shoulders/arms -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.45"
    d="M150 180 Q120 190 100 220 Q90 260 110 290 Q130 300 150 280 Q160 240 155 200 Z"/>
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.45"
    d="M350 180 Q380 190 400 220 Q410 260 390 290 Q370 300 350 280 Q340 240 345 200 Z"/>

  <!-- Helmet - imposing with crest -->
  <path class="organic-path fade-path scale-path" fill="var(--foam)" opacity="0.6"
    d="M200 80 Q220 50 250 45 Q280 50 300 80 Q310 110 300 130 Q280 145 250 150 Q220 145 200 130 Q190 110 200 80 Z"/>
  <!-- Helmet crest -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.4"
    d="M250 45 Q255 20 250 5 Q245 20 250 45 Z"/>
  <!-- Face guard shadow -->
  <path class="organic-path fade-path" fill="var(--deep)" opacity="0.3"
    d="M220 100 Q250 95 280 100 Q285 120 280 130 Q250 135 220 130 Q215 120 220 100 Z"/>

  <!-- Giant spear - towering -->
  <path class="organic-path fade-path" stroke="var(--foam)" stroke-width="6" fill="none" opacity="0.5"
    d="M400 450 L380 250 L370 50"/>
  <!-- Spear head -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.7"
    d="M370 50 Q360 30 370 10 Q380 30 370 50 Z"/>

  <!-- Shield on arm -->
  <ellipse class="organic-path fade-path" cx="100" cy="250" rx="45" ry="60" fill="var(--foam)" opacity="0.35"/>
  <ellipse cx="100" cy="250" rx="30" ry="40" fill="var(--deep)" opacity="0.15"/>

  <!-- Menacing shadow cast forward -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.08"
    d="M200 450 Q150 480 100 500 L400 500 Q350 480 300 450 Z"/>
</svg>
```

**Design Notes:**
- Goliath fills the frame (imposing scale)
- Multiple armor layers create visual weight
- Uses `var(--foam)` on dark background (Chapter 2 = dark section)
- Higher opacity (0.3-0.6) for intensity
- Spear extends beyond frame top (towering height)
- Shadow cast forward adds menace

---

## Chapter 3 SVG: The Victory

**Purpose:** Resolution - David triumphs
**ViewBox:** 500x500 (standard chapter)
**Composition:** Triumphant figure center, fallen mass below, radiating energy

```svg
<svg viewBox="0 0 500 500" fill="none">
  <!-- Scene: The Victory - David triumphs over fallen Goliath -->

  <!-- Radiating light burst from center -->
  <g class="organic-path fade-path" opacity="0.08">
    <path fill="var(--deep)" d="M250 200 L240 50 L260 50 Z"/>
    <path fill="var(--deep)" d="M250 200 L150 80 L170 70 Z"/>
    <path fill="var(--deep)" d="M250 200 L350 80 L330 70 Z"/>
    <path fill="var(--deep)" d="M250 200 L420 150 L410 170 Z"/>
    <path fill="var(--deep)" d="M250 200 L80 150 L90 170 Z"/>
  </g>

  <!-- Fallen Goliath - collapsed on ground -->
  <g class="organic-path fade-path">
    <!-- Fallen body mass -->
    <path fill="var(--deep)" opacity="0.2"
      d="M80 380 Q120 350 180 360 Q250 370 320 355 Q380 340 420 370 Q430 400 400 420 Q300 440 200 435 Q100 430 70 400 Q60 385 80 380 Z"/>
    <!-- Fallen helmet -->
    <ellipse cx="400" cy="360" rx="35" ry="25" fill="var(--deep)" opacity="0.25"/>
    <!-- Fallen shield -->
    <ellipse cx="120" cy="400" rx="40" ry="30" fill="var(--deep)" opacity="0.15"/>
    <!-- Fallen spear -->
    <path stroke="var(--deep)" stroke-width="4" fill="none" opacity="0.2"
      d="M50 450 Q150 420 250 440 Q350 460 450 430"/>
  </g>

  <!-- David standing victorious - small but triumphant -->
  <g class="organic-path fade-path scale-path">
    <!-- David's body - standing tall -->
    <path fill="var(--deep)" opacity="0.7"
      d="M250 180 Q270 185 278 220 Q282 260 278 300 Q270 320 250 325 Q230 320 222 300 Q218 260 222 220 Q230 185 250 180 Z"/>
    <!-- Head raised high -->
    <circle cx="250" cy="158" r="20" fill="var(--deep)" opacity="0.8"/>
    <!-- Arms raised in victory -->
    <path fill="var(--deep)" opacity="0.6"
      d="M230 200 Q210 180 195 160 Q190 150 200 148 Q215 155 235 180 Z"/>
    <path fill="var(--deep)" opacity="0.6"
      d="M270 200 Q290 180 305 160 Q310 150 300 148 Q285 155 265 180 Z"/>
    <!-- Sling held up -->
    <path stroke="var(--deep)" stroke-width="2" fill="none" opacity="0.5"
      d="M305 160 Q320 150 330 160 Q335 175 320 180"/>
  </g>

  <!-- The stone's trajectory arc - showing the winning shot -->
  <path class="organic-path fade-path" stroke="var(--deep)" stroke-width="2" stroke-dasharray="8 4" fill="none" opacity="0.3"
    d="M320 170 Q350 120 380 140 Q410 180 400 250 Q390 320 400 360"/>

  <!-- The stone at impact point -->
  <circle class="organic-path fade-path scale-path" cx="400" cy="360" r="8" fill="var(--deep)" opacity="0.6"/>

  <!-- Victory rings expanding -->
  <g class="organic-path fade-path" opacity="0.06">
    <circle cx="250" cy="200" r="80" fill="none" stroke="var(--deep)" stroke-width="1"/>
    <circle cx="250" cy="200" r="120" fill="none" stroke="var(--deep)" stroke-width="1"/>
    <circle cx="250" cy="200" r="160" fill="none" stroke="var(--deep)" stroke-width="1"/>
  </g>
</svg>
```

**Design Notes:**
- David now triumphant (arms raised V-shape)
- Goliath reduced to fallen mass at bottom
- Radiating light shows divine/victorious energy
- Stone trajectory arc tells the story
- Concentric rings expand outward (victory ripples)
- Full opacity range (0.06-0.8) for dramatic contrast

---

## Finale SVG: Faith Triumphs

**Purpose:** Symbolic summary of the entire story
**ViewBox:** 400x400 (smaller, iconic)
**Composition:** Centered crown symbol with radiating elements

```svg
<svg class="finale-illustration" viewBox="0 0 400 400" width="300" height="300">
  <!-- Radiating light rings -->
  <g opacity="0.15">
    <circle cx="200" cy="200" r="180" fill="none" stroke="var(--foam)" stroke-width="1"/>
    <circle cx="200" cy="200" r="140" fill="none" stroke="var(--foam)" stroke-width="1"/>
    <circle cx="200" cy="200" r="100" fill="none" stroke="var(--foam)" stroke-width="1"/>
    <circle cx="200" cy="200" r="60" fill="none" stroke="var(--foam)" stroke-width="1"/>
  </g>

  <!-- Light rays bursting outward -->
  <g opacity="0.1">
    <path fill="var(--foam)" d="M200 200 L195 50 L205 50 Z"/>
    <path fill="var(--foam)" d="M200 200 L195 350 L205 350 Z"/>
    <path fill="var(--foam)" d="M200 200 L50 195 L50 205 Z"/>
    <path fill="var(--foam)" d="M200 200 L350 195 L350 205 Z"/>
    <path fill="var(--foam)" d="M200 200 L90 90 L100 100 Z"/>
    <path fill="var(--foam)" d="M200 200 L310 90 L300 100 Z"/>
    <path fill="var(--foam)" d="M200 200 L90 310 L100 300 Z"/>
    <path fill="var(--foam)" d="M200 200 L310 310 L300 300 Z"/>
  </g>

  <!-- Crown of victory -->
  <g opacity="0.5">
    <!-- Crown base -->
    <path fill="var(--foam)"
      d="M130 220 Q140 200 160 195 Q200 190 240 195 Q260 200 270 220 Q260 235 240 240 Q200 245 160 240 Q140 235 130 220 Z"/>
    <!-- Crown points -->
    <path fill="var(--foam)" d="M145 200 Q155 170 165 195"/>
    <path fill="var(--foam)" d="M175 195 Q185 155 195 190"/>
    <path fill="var(--foam)" d="M200 190 Q210 145 220 190"/>
    <path fill="var(--foam)" d="M225 195 Q235 160 245 200"/>
    <path fill="var(--foam)" d="M250 205 Q260 175 265 210"/>
    <!-- Crown jewel center -->
    <circle cx="200" cy="215" r="10" fill="var(--foam)" opacity="0.8"/>
  </g>

  <!-- The smooth stone - symbol of faith -->
  <ellipse cx="200" cy="300" rx="25" ry="18" fill="var(--foam)" opacity="0.3"/>
  <ellipse cx="200" cy="300" rx="15" ry="10" fill="var(--foam)" opacity="0.2"/>

  <!-- Subtle dove/spirit suggestion above -->
  <path fill="var(--foam)" opacity="0.12"
    d="M200 100 Q180 110 170 105 Q160 95 175 90 Q190 85 200 80 Q210 85 225 90 Q240 95 230 105 Q220 110 200 100 Z"/>
</svg>
```

**Design Notes:**
- Crown = David becomes king (story payoff)
- Stone below crown = reminder of humble weapon
- Dove above = divine presence/Holy Spirit
- Radiating rings = eternal impact
- Uses `var(--foam)` on dark finale background
- Lower opacity (0.1-0.5) for elegant, calm resolution

---

## Design Checklist Summary

| Requirement | Hero | Ch1 | Ch2 | Ch3 | Finale |
|-------------|------|-----|-----|-----|--------|
| Uses CSS variables | ✅ | ✅ | ✅ | ✅ | ✅ |
| Organic Bézier paths | ✅ | ✅ | ✅ | ✅ | ✅ |
| Position-appropriate composition | ✅ | ✅ | ✅ | ✅ | ✅ |
| Topic-relevant elements | ✅ | ✅ | ✅ | ✅ | ✅ |
| Animation classes applied | ✅ | ✅ | ✅ | ✅ | ✅ |
| Opacity matches warm mood | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Extended Variants: 4 & 5 Chapters

### 4-Chapter Variant

**Narrative Adjustment:** Add "Preparation" chapter before the victory

| Position | Chapter | Purpose | SVG Elements | Background |
|----------|---------|---------|--------------|------------|
| **Hero** | Valley of Elah | Set the scene | hills + figure-small + figure-large | — |
| **Ch 1** | The Underdog | Introduce David | figure-small + staff + sheep | Light |
| **Ch 2** | The Giant | Show the obstacle | figure-large + armor + spear | Dark |
| **Ch 3** | The Challenge | Army assembles, threats multiply | multiple figures + clouds + spears | Light |
| **Ch 4** | The Victory | Resolution | figure-triumphant + fallen-mass + radiate | Dark |
| **Finale** | Faith Triumphs | Symbolic summary | crown + light-rays + stone + dove | — |

```svg
<!-- Chapter 3 SVG (4-chapter): The Challenge -->
<svg viewBox="0 0 500 500" fill="none">
  <!-- Dark storm clouds gathering -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.3"
    d="M50 60 Q80 30 120 45 Q160 25 200 55 Q240 35 280 65 Q300 85 280 100 Q240 115 200 105 Q160 125 120 95 Q80 125 50 95 Q30 75 50 60 Z"/>
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.25"
    d="M280 30 Q310 10 340 25 Q370 15 400 35 Q420 55 400 70 Q370 85 340 75 Q310 85 280 70 Q260 50 280 30 Z"/>

  <!-- Philistine army silhouettes (4 figures) -->
  <g class="organic-path fade-path">
    <ellipse cx="100" cy="340" rx="30" ry="50" fill="var(--foam)" opacity="0.4"/>
    <ellipse cx="200" cy="360" rx="30" ry="50" fill="var(--foam)" opacity="0.35"/>
    <ellipse cx="300" cy="350" rx="30" ry="50" fill="var(--foam)" opacity="0.45"/>
    <ellipse cx="400" cy="370" rx="30" ry="50" fill="var(--foam)" opacity="0.38"/>
  </g>

  <!-- Spears bristling -->
  <path stroke="var(--foam)" stroke-width="3" opacity="0.5" fill="none"
    d="M100 290 L100 240"/>
  <path stroke="var(--foam)" stroke-width="3" opacity="0.5" fill="none"
    d="M200 310 L200 260"/>
  <path stroke="var(--foam)" stroke-width="3" opacity="0.5" fill="none"
    d="M300 300 L300 250"/>
  <path stroke="var(--foam)" stroke-width="3" opacity="0.5" fill="none"
    d="M400 320 L400 270"/>

  <!-- Narrowing path for David -->
  <path class="organic-path fade-path" fill="var(--foam)" opacity="0.2"
    d="M150 450 Q200 420 250 380 Q250 420 300 450 Q350 470 400 450 L400 500 L150 500 Z"/>
</svg>
```

### 5-Chapter Variant

**Narrative Adjustment:** Epic version with "Preparation" and "Final Stand"

| Position | Chapter | Purpose | SVG Elements | Background |
|----------|---------|---------|--------------|------------|
| **Hero** | Valley of Elah | Set the scene | hills + figure-small + figure-large | — |
| **Ch 1** | The Underdog | Introduce David | figure-small + staff + sheep | Light |
| **Ch 2** | The Giant | Show the obstacle | figure-large + armor + spear | Dark |
| **Ch 3** | The Challenge | Army assembles | multiple figures + clouds + spears | Light |
| **Ch 4** | The Moment | Stone in flight, sling action | stone-flying + figure-action + impact | Dark |
| **Ch 5** | The Victory | Resolution | figure-triumphant + fallen-mass + radiate | Light |
| **Finale** | Faith Triumphs | Symbolic summary | crown + light-rays + stone + dove | — |

```svg
<!-- Chapter 4 SVG (5-chapter): The Moment -->
<svg viewBox="0 0 500 500" fill="none">
  <!-- Divine light breaking through clouds -->
  <path class="organic-path fade-path" fill="var(--deep)" opacity="0.15"
    d="M200 50 L220 150 L280 150 L300 50 Z"/>
  <path class="organic-path fade-path" fill="var(--deep)" opacity="0.1"
    d="M180 80 L200 180 L300 180 L320 80 Z"/>

  <!-- Stone flying toward target -->
  <g class="organic-path scale-path">
    <ellipse cx="220" cy="180" rx="18" ry="14" fill="var(--deep)" opacity="0.8"/>
    <!-- Motion trail -->
    <path stroke="var(--deep)" stroke-width="2" opacity="0.4" fill="none"
      d="M180 185 Q140 188 100 190"/>
    <path stroke="var(--deep)" stroke-width="1" opacity="0.3" fill="none"
      d="M175 175 Q135 172 95 170"/>
  </g>

  <!-- David in action pose (sling extended) -->
  <g class="organic-path fade-path" transform="translate(120, 280)">
    <circle cx="0" cy="0" r="20" fill="var(--deep)" opacity="0.7"/>
    <path fill="var(--deep)" opacity="0.7"
      d="M0 20 Q-5 50 -15 80 L-25 70 L-5 50 L5 50 L25 70 L15 80 Q5 50 0 20"/>
    <!-- Extended arm with sling -->
    <path fill="var(--deep)" opacity="0.7" d="M0 30 Q20 20 50 10"/>
    <path stroke="var(--deep)" stroke-width="2" opacity="0.7" fill="none"
      d="M50 10 Q70 -10 60 -30"/>
  </g>

  <!-- Goliath recoiling from impact -->
  <g class="organic-path fade-path" transform="translate(350, 200) scale(1.2)">
    <circle cx="0" cy="0" r="30" fill="var(--deep)" opacity="0.5"/>
    <path fill="var(--deep)" opacity="0.5"
      d="M0 30 Q20 70 30 120 L50 100 L20 60 L-20 60 L-50 100 L-30 120 Q-20 70 0 30"/>
    <!-- Arms thrown back -->
    <path fill="var(--deep)" opacity="0.5" d="M-15 40 Q-50 30 -70 50"/>
    <path fill="var(--deep)" opacity="0.5" d="M15 40 Q50 30 70 50"/>
  </g>

  <!-- Impact burst at contact point -->
  <g class="organic-path scale-path" transform="translate(320, 200)">
    <circle fill="var(--deep)" opacity="0.6" r="20"/>
    <!-- Burst rays -->
    <path fill="var(--deep)" opacity="0.36"
      d="M0 -30 L5 -45 L-5 -45 Z"/>
    <path fill="var(--deep)" opacity="0.36"
      d="M30 0 L45 5 L45 -5 Z"/>
    <path fill="var(--deep)" opacity="0.36"
      d="M0 30 L5 45 L-5 45 Z"/>
    <path fill="var(--deep)" opacity="0.36"
      d="M-30 0 L-45 5 L-45 -5 Z"/>
  </g>
</svg>
```

### Chapter Pattern Comparison

| Count | Structure | Light/Dark Pattern |
|-------|-----------|-------------------|
| **3** | Intro → Conflict → Victory | Light → Dark → Light |
| **4** | Intro → Conflict → Escalation → Victory | Light → Dark → Light → Dark |
| **5** | Intro → Conflict → Escalation → Climax → Victory | Light → Dark → Light → Dark → Light |

---

## Key Learnings

1. **Scale tells story:** Small David + massive Goliath creates instant narrative
2. **Position drives composition:** Hero = wide, Ch1 = introduce, Ch2 = impose, Ch3 = radiate
3. **Callback elements:** Stone appears in Ch1 (sling), Ch3 (trajectory), Finale (symbol)
4. **Mood consistency:** Warm palette = gentle Q curves, medium opacity, organic feel
5. **Animation classes:** Use `scale-path` for focal elements, `fade-path` for atmosphere
