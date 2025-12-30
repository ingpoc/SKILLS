# SVG Illustration Guide

Comprehensive guide for creating topic-relevant, cohesive SVG illustrations for scroll-storytelling experiences.

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Topic Relevance** | Every SVG must symbolically represent chapter content |
| **Narrative Arc** | Illustrations evolve across chapters (simple → complex → triumphant) |
| **Dual-Tone Only** | Use only `var(--deep)` and `var(--foam)` - no third colors |
| **Organic Paths** | Bézier curves only - no circles, rectangles, or geometric shapes |
| **Position-Aware** | Composition varies by chapter position (hero/ch1/ch2/ch3/finale) |

---

## SVG Element Library

### Characters

| Element | Use When | Key Features |
|---------|----------|--------------|
| `figure-small` | Protagonist, humble beginnings, underdog | Small scale, simple silhouette |
| `figure-large` | Antagonist, authority, giant, obstacle | Towering, imposing mass |
| `figure-group` | Community, team, crowd | Multiple small figures together |
| `figure-triumphant` | Victory, achievement, success | Arms raised, confident pose |
| `figure-seated` | Contemplation, learning, rest | Curved seated position |
| `figure-reaching` | Aspiration, growth, effort | Extended arm upward |

### Nature

| Element | Use When | Key Features |
|---------|----------|--------------|
| `hills` | Background, journey, landscape | Rolling Bézier waves |
| `sun` | Hope, beginning, energy | Radiating circle with rays |
| `tree` | Growth, life, knowledge | Trunk + organic crown |
| `water` | Flow, change, emotion | Wavy horizontal paths |
| `clouds` | Dreams, uncertainty, atmosphere | Soft blob clusters |
| `path` | Journey, direction, progress | Winding Bézier curve |
| `mountain` | Challenge, goal, achievement | Peaked triangular form |

### Objects

| Element | Use When | Key Features |
|---------|----------|--------------|
| `staff` | Guidance, authority, shepherd | Tall curved line with hook |
| `weapon` | Conflict, power, threat | Spear, sword silhouette |
| `shield` | Protection, defense, safety | Oval/rounded rectangle |
| `crown` | Victory, royalty, achievement | Band with pointed peaks |
| `stone` | Small power, David vs Goliath | Simple oval |
| `book` | Knowledge, learning, wisdom | Open pages silhouette |
| `key` | Solution, access, unlock | Classic key shape |
| `heart` | Love, care, health | Organic heart curve |
| `hourglass` | Time, urgency, passage | Double-triangle form |

### Abstract

| Element | Use When | Key Features |
|---------|----------|--------------|
| `radiate` | Victory, enlightenment, impact | Lines/shapes bursting outward |
| `converge` | Focus, unity, gathering | Lines pointing inward |
| `ascend` | Growth, progress, improvement | Upward motion paths |
| `descend` | Fall, decline, humility | Downward motion paths |
| `transform` | Change, metamorphosis | Before/after silhouettes |
| `spiral` | Journey inward, infinity | Curved spiral path |
| `orbit` | Cycle, system, rotation | Circular motion paths |

### Structures

| Element | Use When | Key Features |
|---------|----------|--------------|
| `arch` | Gateway, transition, entry | Curved doorway shape |
| `tower` | Aspiration, achievement, height | Tall vertical structure |
| `bridge` | Connection, transition, overcome | Spanning curved structure |
| `wall` | Obstacle, boundary, division | Thick vertical barrier |
| `gate` | Opportunity, access, threshold | Arch with doors |
| `foundation` | Stability, base, beginning | Wide horizontal base |

---

## Theme Categories (15+)

### 1. Biblical/Spiritual

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| David & Goliath | figure-small vs figure-large, hills | figure-small + staff + sheep | figure-large + armor + weapon | figure-triumphant + fallen mass + radiate | army masses + clouds + spears | sling action + stone flying + impact | crown + radiate + stone |
| Exodus/Journey | path stretching to horizon | figure-group + burden | wall/obstacle + figure-large | parted water + path | wilderness challenges + clouds | final stand + light rays | promised land + radiate |
| Parables | contrast scene | seed/beginning element | growth/conflict element | harvest/resolution | testing + deepening | breakthrough + action | wisdom symbol + radiate |

**Keywords:** faith, shepherd, giant, prophet, promise, covenant, miracle, blessing, redemption

### 2. Tech/Product

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| AI/Agents | human + AI silhouettes | single node + potential | network expanding | orchestrated system | system under attack + pulses | countermeasures + defense | unified intelligence |
| Security | shield + threat arrows | vulnerable state | attack/breach attempt | defense activated | threats converging | full counterattack | protected ecosystem |
| Cloud/API | earth + cloud connection | local device | scaling challenge | cloud integration | load stress + warnings | scale breakthrough | global network |

**Keywords:** automation, intelligence, security, scale, integration, platform, data, API, cloud, network

### 3. Nature/Environment

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Seasons | all 4 season hints | spring/new growth | summer/full bloom | autumn/harvest | winter dormancy | spring rebirth | full cycle |
| Growth | seed vs tree | seed planted | sprout emerging | growing tree | storm challenges | breaking through | full tree + fruit |
| Ocean | shore meeting water | calm surface | storm/waves | navigation | storm intensifies | breakthrough sun | peaceful harbor |

**Keywords:** growth, nature, seasons, ocean, forest, mountain, river, ecosystem, climate, renewal

### 4. Business/Enterprise

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Strategy | chess pieces setup | single piece | competitive move | strategic victory | competition peaks | strategic breakthrough | winning position |
| Team Building | scattered figures | first connection | growing network | unified team | pressure mounts | team rallies | collaborative success |
| Innovation | lightbulb + question | problem identified | solution explored | innovation launched | market resistance | breakthrough moment | market impact |

**Keywords:** strategy, growth, team, innovation, market, leadership, efficiency, ROI, scale, enterprise

### 5. Personal Growth

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Hero's Journey | figure at threshold | leaving comfort | facing trial | transformation | darkest hour | final trial | return empowered |
| Learning | empty vessel | first knowledge | struggle/practice | mastery moment | plateau + doubt | breakthrough | teaching others |
| Transformation | caterpillar + butterfly | cocoon forming | internal change | emergence | struggle within | breaking out | flight + freedom |

**Keywords:** journey, transformation, learning, growth, challenge, overcome, achieve, evolve, discover

### 6. Historical

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Revolution | old vs new contrast | oppression state | spark of change | uprising | forces gather | final battle | new order |
| Discovery | unknown territory | explorer setting out | journey challenges | discovery moment | hostility + setbacks | breakthrough | world changed |
| Legacy | monument silhouette | origin story | building/creating | completion |考验 + challenges | triumph | lasting impact |

**Keywords:** history, revolution, discovery, legacy, founding, era, civilization, monument, heritage

### 7. Scientific

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Research | question + microscope | hypothesis | experimentation | breakthrough | failed theories + setbacks | decisive experiment | verified discovery |
| Discovery | unknown phenomenon | investigation | testing | eureka moment | skepticism + challenges | proof revealed | application |
| Innovation | problem + solution hint | challenge defined | iteration | solution found | resistance + barriers | adoption | world impact |

**Keywords:** research, discovery, experiment, hypothesis, data, breakthrough, innovation, evidence

### 8. Educational

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Learning Path | student + mountain | first step | climbing | summit reached | plateau + doubts | final ascent | teaching others |
| Knowledge | locked book + key | key found | unlocking | reading/absorbing | confusion + complexity | synthesis | sharing wisdom |
| Skills | raw material + tool | first attempt | practice | mastery | rut + stagnation | breakthrough | creation |

**Keywords:** learning, education, knowledge, skills, teaching, student, mastery, curriculum

### 9. Social/Community

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Connection | isolated figures | first bridge | network forming | community | fragmentation threats | reconnection | unified whole |
| Unity | diverse scattered | common ground found | collaboration | movement | external pressures | solidarity | lasting change |
| Diversity | different shapes | coming together | integration | strength | discrimination + setbacks | acceptance | beautiful mosaic |

**Keywords:** community, connection, unity, diversity, belonging, collaboration, social, together

### 10. Adventure/Quest

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Quest | map + destination | departure | journey perils | goal achieved | lost + discouraged | final trial | return home |
| Exploration | unknown territory | first steps | challenges | discovery | hostile terrain | breakthrough | new world |
| Treasure | X marks spot | clues gathered | obstacles overcome | treasure found | guardian + trap | final battle | wealth shared |

**Keywords:** adventure, quest, exploration, journey, treasure, discovery, hero, challenge

### 11. Health/Wellness

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Healing | broken + whole | injury/illness | treatment | recovery | setback + relapse | breakthrough | full health |
| Balance | tilted scale | imbalance | adjusting | equilibrium | external stressors | finding center | harmony |
| Strength | figure + weight | weakness | training | growth | plateau + injury | breakthrough | powerful |

**Keywords:** health, wellness, healing, balance, strength, recovery, vitality, care

### 12. Creative/Artistic

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Inspiration | blank + spark | muse arrives | creative flow | masterpiece | creative block | breakthrough | audience moved |
| Expression | confined + free | first attempt | refinement | breakthrough | criticism + doubt | authentic voice | impact |
| Design | chaos + order | vision | iteration | solution | constraints + limits | elegant solution | beauty |

**Keywords:** creative, artistic, inspiration, design, expression, beauty, craft, vision

### 13. Financial

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Growth | seed + tree | investment | nurturing | harvest | market volatility | diversification | abundance |
| Security | open + vault | vulnerability | protection built | tested | breach attempt | reinforced | secure |
| Building | foundation | structure rising | challenges | completion | cost overruns | funding secured | legacy |

**Keywords:** financial, investment, growth, security, wealth, prosperity, planning, returns

### 14. Leadership

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Vision | fog + lighthouse | clarity emerges | path defined | team aligned | skepticism + resistance | persuasion | destination reached |
| Guidance | lost figures + guide | guide appears | journey together | obstacles overcome | betrayal + loss | renewed trust | new leaders |
| Empowerment | dependent + independent | learning | growing | leading | impostor syndrome | authentic | multiplying |

**Keywords:** leadership, vision, guidance, empowerment, influence, team, direction, inspire

### 15. Abstract/Conceptual

| Topic | Hero SVG | Ch1 SVG | Ch2 SVG | Ch3 SVG | Ch4 SVG | Ch5 SVG | Finale SVG |
|-------|----------|---------|---------|---------|---------|---------|------------|
| Time | hourglass | past | present | future | time distortion | timelessness | eternal |
| Duality | yin-yang split | one side | other side | integration | conflict + tension | synthesis | balance |
| Infinity | finite + infinite | boundary | expansion | limitless | paradox | transcendence | transcendence |

**Keywords:** time, space, infinity, duality, abstract, concept, philosophy, meaning

---

## Composition Rules by Position

### Hero Section
- **Purpose:** Set the stage, show contrast/conflict to come
- **Composition:** Wide scene (1000x1000 viewBox), 2 contrasting elements
- **Complexity:** Medium - enough to intrigue, not overwhelm
- **Opacity:** Lower range (0.04-0.15) for atmospheric effect
- **Elements:** Background landscape + 2 silhouettes showing scale contrast

```svg
<!-- Hero composition template -->
<svg viewBox="0 0 1000 1000">
  <!-- Background layer (hills/landscape) - opacity 0.04-0.08 -->
  <!-- Left element (protagonist) - opacity 0.10-0.15 -->
  <!-- Right element (antagonist/goal) - opacity 0.12-0.18 -->
  <!-- Atmospheric elements (stars/light) - opacity 0.08-0.12 -->
</svg>
```

### Chapter 1
- **Purpose:** Introduce protagonist, establish starting point
- **Composition:** Centered figure (500x500 viewBox), pastoral/simple
- **Complexity:** Low-medium - clear, readable silhouette
- **Opacity:** Medium range (0.15-0.5) for visibility
- **Elements:** Main figure + supporting context (environment, tools)

```svg
<!-- Chapter 1 composition template -->
<svg viewBox="0 0 500 500">
  <!-- Background/context - opacity 0.05-0.15 -->
  <!-- Supporting elements - opacity 0.15-0.30 -->
  <!-- Main figure - opacity 0.5-0.8 -->
</svg>
```

### Chapter 2
- **Purpose:** Introduce conflict, show obstacle/challenge
- **Composition:** Imposing element (500x500 viewBox), fills frame
- **Complexity:** Medium-high - detailed, menacing
- **Opacity:** Higher range (0.3-0.6) for impact
- **Elements:** Antagonist/obstacle dominant, shadow effects

```svg
<!-- Chapter 2 composition template -->
<svg viewBox="0 0 500 500">
  <!-- Ground shadow - opacity 0.08-0.15 -->
  <!-- Main imposing figure - opacity 0.4-0.6 -->
  <!-- Weapons/threat elements - opacity 0.3-0.5 -->
  <!-- Armor/detail elements - opacity 0.25-0.45 -->
</svg>
```

### Chapter 3
- **Purpose:** Resolution, triumph, victory moment
- **Composition:** Dynamic action (500x500 viewBox), radiating energy
- **Complexity:** Medium - clear victory symbolism
- **Opacity:** Full range (0.1-0.8) for drama
- **Elements:** Victor figure + fallen obstacle + radiate effects

```svg
<!-- Chapter 3 composition template -->
<svg viewBox="0 0 500 500">
  <!-- Radiating light burst - opacity 0.06-0.10 -->
  <!-- Fallen/defeated element - opacity 0.15-0.25 -->
  <!-- Triumphant figure - opacity 0.6-0.8 -->
  <!-- Victory trajectory/motion - opacity 0.2-0.4 -->
  <!-- Expanding rings - opacity 0.04-0.08 -->
</svg>
```

### Chapter 4
- **Purpose:** Deepening conflict, escalating stakes (optional chapter)
- **Composition:** Crowded scene (500x500 viewBox), multiplying threats
- **Complexity:** High - multiple elements, tension-building
- **Opacity:** Higher range (0.35-0.6) for intensity
- **Elements:** Multiple obstacles, antagonists massing, narrowing path
- **Background:** Always dark (follows light→dark→light→dark pattern)

```svg
<!-- Chapter 4 composition template -->
<svg viewBox="0 0 500 500">
  <!-- Dark atmosphere - opacity 0.3-0.5 -->
  <!-- Multiple threat elements - opacity 0.4-0.6 -->
  <!-- Crowded antagonists/obstacles - opacity 0.35-0.55 -->
  <!-- Narrowing path/constriction - opacity 0.2-0.4 -->
</svg>
```

### Chapter 5
- **Purpose:** Final climax, decisive confrontation (optional chapter)
- **Composition:** Dynamic action (500x500 viewBox), turning point
- **Complexity:** High - maximum drama, action moment
- **Opacity:** Full range (0.1-0.8) for maximum contrast
- **Elements:** Protagonist in action vs final obstacle, impact moment
- **Background:** Always light (follows light→dark→light→dark→light pattern)

```svg
<!-- Chapter 5 composition template -->
<svg viewBox="0 0 500 500">
  <!-- Divine/heroic light rays - opacity 0.15-0.3 -->
  <!-- Protagonist action figure - opacity 0.6-0.8 -->
  <!-- Final obstacle/recoiling antagonist - opacity 0.4-0.6 -->
  <!-- Impact burst/decisive moment - opacity 0.5-0.7 -->
</svg>
```

### Finale Section
- **Purpose:** Symbolic summary, lasting impression
- **Composition:** Centered symbol (400x400 viewBox), iconic
- **Complexity:** Medium - recognizable at glance
- **Opacity:** Balanced range (0.1-0.5) for elegance
- **Elements:** Crown/trophy + radiate + key symbol from story

```svg
<!-- Finale composition template -->
<svg viewBox="0 0 400 400">
  <!-- Outer rings/rays - opacity 0.08-0.15 -->
  <!-- Light rays - opacity 0.08-0.12 -->
  <!-- Central symbol (crown/trophy) - opacity 0.4-0.6 -->
  <!-- Story callback element - opacity 0.2-0.35 -->
  <!-- Subtle atmospheric - opacity 0.06-0.12 -->
</svg>
```

---

## Bézier Path Templates

### Figure Templates

```svg
<!-- figure-small: Humble protagonist (David-scale) -->
<g class="figure-small">
  <!-- Body/robe -->
  <path fill="var(--deep)" opacity="0.7"
    d="M250 220 Q270 225 280 260 Q285 300 280 340 Q270 360 250 365 Q230 360 220 340 Q215 300 220 260 Q230 225 250 220 Z"/>
  <!-- Head -->
  <circle cx="250" cy="195" r="22" fill="var(--deep)" opacity="0.8"/>
  <!-- Arms -->
  <path fill="var(--deep)" opacity="0.6"
    d="M225 240 Q200 250 180 245 Q175 240 180 235 Q200 230 220 235 Z"/>
  <path fill="var(--deep)" opacity="0.6"
    d="M275 240 Q300 235 320 250 Q325 255 320 260 Q300 255 280 250 Z"/>
</g>

<!-- figure-large: Imposing antagonist (Goliath-scale) -->
<g class="figure-large">
  <!-- Massive torso -->
  <path fill="var(--foam)" opacity="0.5"
    d="M150 180 Q160 140 200 120 Q250 100 300 120 Q340 140 350 180 Q360 240 350 300 Q340 340 300 350 Q250 360 200 350 Q160 340 150 300 Q140 240 150 180 Z"/>
  <!-- Helmet -->
  <path fill="var(--foam)" opacity="0.6"
    d="M200 80 Q220 50 250 45 Q280 50 300 80 Q310 110 300 130 Q280 145 250 150 Q220 145 200 130 Q190 110 200 80 Z"/>
  <!-- Legs -->
  <path fill="var(--foam)" opacity="0.4"
    d="M180 320 Q175 370 170 420 Q165 450 185 455 Q205 450 200 420 Q195 380 200 340 Z"/>
  <path fill="var(--foam)" opacity="0.4"
    d="M300 320 Q305 370 310 420 Q315 450 335 455 Q355 450 350 420 Q345 380 340 340 Z"/>
</g>

<!-- figure-triumphant: Victory pose -->
<g class="figure-triumphant">
  <!-- Body -->
  <path fill="var(--deep)" opacity="0.7"
    d="M250 180 Q270 185 278 220 Q282 260 278 300 Q270 320 250 325 Q230 320 222 300 Q218 260 222 220 Q230 185 250 180 Z"/>
  <!-- Head raised -->
  <circle cx="250" cy="158" r="20" fill="var(--deep)" opacity="0.8"/>
  <!-- Arms raised in V -->
  <path fill="var(--deep)" opacity="0.6"
    d="M230 200 Q210 180 195 160 Q190 150 200 148 Q215 155 235 180 Z"/>
  <path fill="var(--deep)" opacity="0.6"
    d="M270 200 Q290 180 305 160 Q310 150 300 148 Q285 155 265 180 Z"/>
</g>
```

### Nature Templates

```svg
<!-- hills: Rolling landscape background -->
<g class="hills">
  <path fill="var(--deep)" opacity="0.08"
    d="M0 380 Q80 340 160 360 Q240 380 320 350 Q400 320 500 360 L500 500 L0 500 Z"/>
  <path fill="var(--deep)" opacity="0.05"
    d="M0 420 Q100 390 200 410 Q300 430 400 400 Q450 385 500 400 L500 500 L0 500 Z"/>
</g>

<!-- sun: Radiating light source -->
<g class="sun">
  <circle cx="400" cy="100" r="40" fill="var(--deep)" opacity="0.06"/>
  <circle cx="400" cy="100" r="25" fill="var(--deep)" opacity="0.04"/>
</g>

<!-- tree: Growth/knowledge symbol -->
<g class="tree">
  <!-- Trunk -->
  <path fill="var(--deep)" opacity="0.5"
    d="M245 350 Q240 300 245 250 Q250 200 255 250 Q260 300 255 350 Z"/>
  <!-- Crown -->
  <path fill="var(--deep)" opacity="0.4"
    d="M200 180 Q220 140 250 130 Q280 140 300 180 Q310 220 290 250 Q250 270 210 250 Q190 220 200 180 Z"/>
</g>

<!-- path: Journey/direction -->
<path class="path" stroke="var(--deep)" stroke-width="3" fill="none" opacity="0.3"
  d="M100 400 Q150 380 200 390 Q300 410 400 380 Q450 360 500 380"/>
```

### Object Templates

```svg
<!-- staff: Shepherd's crook -->
<path class="staff" stroke="var(--deep)" stroke-width="4" fill="none" opacity="0.6"
  d="M320 400 Q325 300 320 200 Q315 150 290 140 Q270 135 260 145"/>

<!-- crown: Victory symbol -->
<g class="crown">
  <!-- Base band -->
  <path fill="var(--foam)" opacity="0.5"
    d="M130 220 Q140 200 160 195 Q200 190 240 195 Q260 200 270 220 Q260 235 240 240 Q200 245 160 240 Q140 235 130 220 Z"/>
  <!-- Points -->
  <path fill="var(--foam)" opacity="0.6" d="M145 200 Q155 170 165 195"/>
  <path fill="var(--foam)" opacity="0.6" d="M175 195 Q185 155 195 190"/>
  <path fill="var(--foam)" opacity="0.6" d="M200 190 Q210 145 220 190"/>
  <path fill="var(--foam)" opacity="0.6" d="M225 195 Q235 160 245 200"/>
  <!-- Jewel -->
  <circle cx="200" cy="215" r="10" fill="var(--foam)" opacity="0.8"/>
</g>

<!-- shield: Protection symbol -->
<g class="shield">
  <ellipse cx="100" cy="250" rx="45" ry="60" fill="var(--foam)" opacity="0.35"/>
  <ellipse cx="100" cy="250" rx="30" ry="40" fill="var(--deep)" opacity="0.15"/>
</g>

<!-- weapon/spear -->
<g class="weapon">
  <path stroke="var(--foam)" stroke-width="6" fill="none" opacity="0.5"
    d="M400 450 L380 250 L370 50"/>
  <path fill="var(--foam)" opacity="0.7"
    d="M370 50 Q360 30 370 10 Q380 30 370 50 Z"/>
</g>
```

### Abstract Templates

```svg
<!-- radiate: Light burst effect -->
<g class="radiate" opacity="0.08">
  <path fill="var(--deep)" d="M250 200 L245 50 L255 50 Z"/>
  <path fill="var(--deep)" d="M250 200 L150 80 L160 70 Z"/>
  <path fill="var(--deep)" d="M250 200 L350 80 L340 70 Z"/>
  <path fill="var(--deep)" d="M250 200 L400 150 L390 160 Z"/>
  <path fill="var(--deep)" d="M250 200 L100 150 L110 160 Z"/>
</g>

<!-- rings: Expanding circles -->
<g class="rings" opacity="0.15">
  <circle cx="200" cy="200" r="60" fill="none" stroke="var(--foam)" stroke-width="1"/>
  <circle cx="200" cy="200" r="100" fill="none" stroke="var(--foam)" stroke-width="1"/>
  <circle cx="200" cy="200" r="140" fill="none" stroke="var(--foam)" stroke-width="1"/>
  <circle cx="200" cy="200" r="180" fill="none" stroke="var(--foam)" stroke-width="1"/>
</g>

<!-- trajectory: Motion arc with dashes -->
<path class="trajectory" stroke="var(--deep)" stroke-width="2" stroke-dasharray="8 4" fill="none" opacity="0.3"
  d="M320 170 Q350 120 380 140 Q410 180 400 250 Q390 320 400 360"/>
```

---

## Animation Class Reference

| Class | Effect | Best For |
|-------|--------|----------|
| `organic-path` | Base class for all SVG elements | All elements |
| `fade-path` | Fade in on scroll | Background, atmosphere |
| `scale-path` | Scale up on scroll | Main figures, focal points |
| `draw-path` | Stroke draw animation (needs stroke) | Paths, trajectories, staffs |

---

## Checklist: Before Generating

- [ ] Each chapter SVG matches topic keywords
- [ ] Hero shows contrast/conflict setup
- [ ] Chapter 1 introduces protagonist simply
- [ ] Chapter 2 shows imposing obstacle
- [ ] Chapter 3 depicts triumph/resolution
- [ ] Finale has symbolic summary
- [ ] All paths use organic Bézier curves
- [ ] Only `var(--deep)` and `var(--foam)` colors
- [ ] Opacity range matches palette mood
- [ ] Animation classes applied appropriately
