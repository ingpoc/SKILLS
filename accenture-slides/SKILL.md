---
name: accenture-slides
description: Create premium Accenture-branded PowerPoint presentations following Tufte data visualization principles and Dieter Rams design philosophy. Use when creating slides, presentations, or decks for Accenture corporate settings that require (1) Accenture brand identity (purple A100FF chevron logo clean layouts) (2) Minimal data-focused design (Tufte less but better) (3) Executive-ready aesthetics for boardroom presentations client pitches or internal reports
---

# Accenture Slides Skill

Create premium Accenture-branded presentations combining authentic corporate branding with Tufte's data visualization principles and Dieter Rams' "less, but better" design philosophy.

## Core Design Philosophy

### Tufte Principles
- Maximize data-ink ratio: Remove all non-essential visual elements
- One message per slide: Each slide communicates a single clear point
- Direct labeling: Minimal legends emphasis through typography not decoration
- High information density with generous whitespace: Let data breathe
- Show data variation not design variation: Consistency over creativity

### Dieter Rams Principles  
- Less but better: Only essential elements remain
- Honest design: No exaggeration just key facts
- Understandable: Instant comprehension minimal cognitive load
- As little design as possible: Pure function over form

## Accenture Brand System

### Colors
```javascript
const colors = {
  purple: "A100FF",        // Accenture signature purple
  black: "000000",
  darkGray: "3B3B3B",
  mediumGray: "808080",
  lightGray: "CCCCCC",
  white: "FFFFFF",
  backgroundGray: "F7F7F7"
};
```

### Typography
- Font: Arial
- Title slides: 44-48pt bold
- Section headers: 28pt bold
- Subheaders: 20pt bold  
- Body text: 16pt regular
- Supporting text: 14pt medium gray

### Logo Usage
- File: assets/accenture_logo.png (transparent chevron)
- Title slide: Top-left larger (1.2 x 0.8 inches)
- Content slides: Top-right smaller (0.8 x 0.53 inches)

### Signature Elements
- Purple underline: 2-3pt line under every slide title
- Purple accent: Used sparingly for large numbers key metrics
- Minimal footer: "Accenture" in 9pt medium gray bottom-left

## Implementation Pattern

### Setup
```javascript
const pptxgen = require("pptxgenjs");
const fs = require("fs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Author Name';
pres.company = 'Accenture';

// Load logo as base64
const logoPath = 'path/to/assets/accenture_logo.png';
// Convert to base64 with proper format
```

### Branding Helper
```javascript
function addBranding(slide) {
  slide.addImage({
    data: logoBase64,
    x: 9.0, y: 0.25, w: 0.8, h: 0.53
  });
  
  slide.addText("Accenture", {
    x: 0.4, y: 5.4, w: 2, h: 0.15,
    fontSize: 9, color: colors.mediumGray,
    fontFace: "Arial", align: "left"
  });
}
```

### Title Slide
```javascript
let slide1 = pres.addSlide();
slide1.background = { color: colors.white };

slide1.addImage({
  data: logoBase64,
  x: 0.4, y: 0.4, w: 1.2, h: 0.8
});

slide1.addText("Title", {
  x: 0.4, y: 2.3, w: 9, h: 0.7,
  fontSize: 44, bold: true, color: colors.black,
  fontFace: "Arial", align: "left"
});

slide1.addShape(pres.shapes.LINE, {
  x: 0.4, y: 3.15, w: 3.5, h: 0,
  line: { color: colors.purple, width: 4 }
});
```

### Content Slide
```javascript
let slide = pres.addSlide();
slide.background = { color: colors.white };
addBranding(slide);

slide.addText("Title", {
  x: 0.4, y: 0.4, w: 9.2, h: 0.4,
  fontSize: 28, bold: true, color: colors.black
});

slide.addShape(pres.shapes.LINE, {
  x: 0.4, y: 0.88, w: 2.0, h: 0,
  line: { color: colors.purple, width: 3 }
});
```

### Data Display
```javascript
// Large metric
slide.addText("227%", {
  x: 0.4, y: 1.8, w: 2.9, h: 0.7,
  fontSize: 60, bold: true, color: colors.purple
});

slide.addText("Label", {
  x: 0.4, y: 2.6, w: 2.9, h: 0.25,
  fontSize: 14, color: colors.mediumGray
});
```

### Table Pattern
```javascript
const data = [
  [
    { text: "Row", options: { fontSize: 16, bold: true } },
    { text: "Value", options: { fontSize: 16, color: colors.mediumGray } }
  ]
];

slide.addTable(data, {
  x: 0.4, y: 1.5, w: 9.2,
  border: { pt: 0 },
  align: "left"
});
```

## Quality Checklist

- Logo is transparent
- Purple underline under every title
- Margins: 0.4" all sides
- Left-aligned text
- Arial font
- No decorative elements
- Purple used sparingly
- Single horizontal lines only
- Generous whitespace
- Save to /mnt/user-data/outputs/

## Content Guidelines

Never use bullet points unless:
- User explicitly requests list
- Response is multifaceted requiring lists

Default to natural prose and generous whitespace.

Maximum 5 elements per slide.

Alternate white and grey backgrounds for visual rhythm.

## Forbidden Elements

Never include:
- 3D effects
- Gradients  
- Decorative borders
- Heavy gridlines
- Excessive bolding
- Multiple colors
- Dense text blocks

## Common Patterns

Problem Slide: Large number (64pt purple) + 2-3 supporting facts

Comparison Slide: Borderless table bold new approach column

Multi-Metric Slide: 3 metrics with aligned baselines equal spacing

Process Slide: 3-4 principles with bold names and brief explanations

## Assets

Logo: assets/accenture_logo.png (transparent purple chevron)
