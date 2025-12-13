# Tufte Slide Review Checklist

Use this checklist to quickly evaluate and improve any slide before finalizing.

## Pre-Design Questions

- [ ] What is the ONE insight this slide must communicate?
- [ ] Is a slide the best format? (Consider: handout, table, prose)
- [ ] What data supports this insight?

## Chartjunk Elimination

### Remove Completely

- [ ] 3D effects on charts
- [ ] Decorative clip art or images
- [ ] Background images/textures
- [ ] Drop shadows
- [ ] Bevels and embossing
- [ ] Reflection effects
- [ ] Animation (unless demonstrating motion)

### Minimize or Simplify

- [ ] Gradient fills → solid colors
- [ ] Heavy gridlines → light or none
- [ ] Thick borders → thin or none
- [ ] Multiple fonts → one or two
- [ ] Excessive colors → limited palette

## Data-Ink Audit

For each element, ask: "Does removing this lose information?"

- [ ] Every line carries data or is essential structure
- [ ] No redundant legends (use direct labels)
- [ ] No redundant axes (range-frame sufficient)
- [ ] Labels are concise but clear
- [ ] Color encodes data, not decoration

## Graphical Integrity Check

### Lie Factor Scan

- [ ] Visual proportions match data proportions
- [ ] Baselines are appropriate (zero when needed)
- [ ] Scale is consistent across compared items
- [ ] No 2D/3D representation of 1D data

### Context Check

- [ ] Full relevant data range shown
- [ ] Source cited
- [ ] Time period clear
- [ ] Units labeled
- [ ] Sample size noted (if applicable)

## Chart-Specific Checks

### Bar Charts

- [ ] 2D only (no 3D)
- [ ] Baseline at zero
- [ ] Direct labels (not legend)
- [ ] Horizontal if labels are long
- [ ] Sorted by value or logical order

### Line Charts

- [ ] Direct labels at line ends
- [ ] Minimal point markers
- [ ] Consistent scale if comparing
- [ ] Time flows left-to-right

### Pie Charts (Avoid If Possible)

- [ ] Is bar chart better? (Usually yes)
- [ ] Maximum 4 slices
- [ ] 2D only
- [ ] Direct labels with percentages
- [ ] Starts at 12 o'clock

### Tables

- [ ] Minimal rules (horizontal only)
- [ ] Left-align text, right-align numbers
- [ ] No cell backgrounds
- [ ] Logical column order
- [ ] Clear headers

## Text Content Check

### Bullet Points (Minimize)

- [ ] Is prose or diagram better?
- [ ] Maximum 4-5 bullets per slide
- [ ] No nested bullets (flatten hierarchy)
- [ ] Each bullet is complete thought

### Labels and Titles

- [ ] Title states the insight, not the topic
- [ ] Labels are direct and specific
- [ ] No abbreviations audience won't know
- [ ] Numbers have context

## Final Review

### The Newspaper Test

Could this graphic appear in a quality newspaper?

- [ ] Stands alone without explanation
- [ ] Insight is immediately apparent
- [ ] No chartjunk
- [ ] Professional typography

### The Squint Test

Squint at the slide from a distance:

- [ ] Main message still visible
- [ ] Visual hierarchy is clear
- [ ] No competing elements
- [ ] Data is the focus

### The Necessity Test

- [ ] This slide is necessary (can't be cut)
- [ ] Every element is necessary (can't be removed)
- [ ] Information density is appropriate

## Quick Fixes Reference

| Problem | Quick Fix |
|---------|-----------|
| Cluttered chart | Remove gridlines, use direct labels |
| Boring data | Add context, comparison, trend |
| Wall of text | Convert to diagram or table |
| Confusing legend | Label directly on chart |
| Distorted proportions | Check Lie Factor, fix scales |
| Too many colors | Limit to 3-4 colors max |
| Unclear point | Rewrite title as insight statement |

## Slide Type Decision Tree

```
Is there data to show?
├─ Yes → Use chart or table
│   └─ Is comparison the goal?
│       ├─ Yes → Small multiples or grouped chart
│       └─ No → Single focused chart
└─ No → Is there a process or relationship?
    ├─ Yes → Use diagram
    └─ No → Is detailed explanation needed?
        ├─ Yes → Consider handout instead
        └─ No → Minimal text slide or skip
```
