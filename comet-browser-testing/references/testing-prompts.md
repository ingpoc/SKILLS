# Testing Prompts Reference

Validated prompt templates for Comet browser testing. These prompts avoid false positives by asking for specific evidence.

## Prompt Design Principles

| Principle | Example |
|-----------|---------|
| Ask for evidence | "List any console errors" vs "Does it work?" |
| Be specific | "Describe 3-5 visible elements" vs "Is content visible?" |
| Request details | "What happens when you click?" vs "Can you click?" |
| Specify format | "Report: yes/no with details" vs "Report status" |

## Core Testing Patterns

### 1. Initial Load Check

**Use when:** First time visiting a page, checking basic functionality.

```
Navigate to {URL} and report:
1. Does the page fully load? (yes/no)
2. Any console errors? (list them)
3. What specific elements are visible? (describe 3-5 elements)
4. Is there a loading state that doesn't resolve? (describe)
5. What is the page title? (exact text)
```

**What to look for in response:**

- Specific element names (not just "content is visible")
- Exact console error messages
- Loading spinner details
- Page title text

### 2. Styling Verification

**Use when:** Checking theme application, layout integrity, visual consistency.

```
Navigate to {URL} and check styling:
1. Are there any obvious layout breaks? (describe specifically)
2. Do colors/theme appear consistent? (yes/no - describe which elements)
3. Are there any unstyled elements? (describe - raw HTML visible?)
4. Is text readable against backgrounds? (yes/no - which text/background)
5. Any obvious visual bugs? (broken images, misaligned elements)
```

**What to look for in response:**

- Specific elements affected
- Color descriptions (not just "looks good")
- Raw HTML/text without CSS applied
- Contrast issues called out

### 3. Functionality Test

**Use when:** Testing specific interactions, buttons, forms.

```
Navigate to {URL} and test {button/element}:
1. Can you see {button/element}? (yes/no - describe appearance)
2. Click the {button/element} - what happens? (describe exact behavior)
3. Any console errors on click? (list them)
4. Does the action complete? (describe result - URL change, modal, etc.)
5. Is there a loading state? (describe)
```

**What to look for in response:**

- Button appearance description
- Exact behavior after click
- Console error messages
- Visual feedback (loading spinner, etc.)

### 4. Multi-Page Navigation

**Use when:** Testing routing, navigation menus, page transitions.

```
Navigate to {URL} and test navigation:
1. Click on {navigation item/link}
2. Does the URL change? (yes/no - what is the new URL?)
3. Does the new page load? (yes/no - describe what you see)
4. Any console errors during navigation? (list them)
5. Is there a page transition animation? (describe)
6. Can you click browser back button? (what happens?)
```

**What to look for in response:**

- Exact URL before/after
- Page content descriptions
- Navigation errors
- Back button behavior

### 5. Visual Completeness

**Use when:** Checking for missing content, broken assets, layout issues.

```
Navigate to {URL} and verify completeness:
1. Are all expected sections visible? (describe which sections)
2. Any broken images or icons? (describe - alt text, placeholder boxes)
3. Is content truncated or hidden? (describe - text cut off, overflow)
4. Any obvious visual bugs? (misaligned, overlapping, missing spacing)
5. Does scrolling work? (describe behavior)
```

**What to look for in response:**

- Section names/headers
- Image descriptions (broken icons, alt text)
- Truncation details
- Scroll behavior

### 6. Feature Behavior

**Use when:** Testing specific feature with expected behavior.

```
Navigate to {URL} and test {feature}:
1. What specific action did you take? (describe step by step)
2. What was the expected behavior? (describe what should happen)
3. What actually happened? (describe exactly what you observed)
4. Any console errors during test? (list full error messages)
5. Is there visual feedback? (describe - toast, modal, redirect, etc.)
```

**What to look for in response:**

- Step-by-step action description
- Expected vs actual comparison
- Full error messages
- Visual feedback details

## Feature-Specific Templates

### Authentication/Authorization

```
Test authentication on {URL}:
1. Is there a login button/form visible? (yes/no - describe its appearance)
2. Click the login button - what happens? (describe redirect, modal, etc.)
3. Any auth-related console errors? (list full error messages)
4. Does the page indicate authenticated state? (describe - user menu, logout button)
5. Can you access protected content? (describe what happens)
```

### Form Submission

```
Test form on {URL}:
1. What form fields are visible? (list them)
2. Fill in the form with: {test data for each field}
3. Click submit - what happens? (describe - loading state, redirect, error)
4. Any validation errors? (list exact error messages)
5. Does submission complete? (describe result - success message, redirect)
6. Any console errors? (list full error messages)
```

### Data Display

```
Test data display on {URL}:
1. Is data visible on the page? (describe what data - cards, table, list)
2. Does data appear complete? (yes/no - describe any missing fields)
3. Any loading states or skeletons? (describe)
4. Any console errors related to data fetching? (list full error messages)
5. Can you interact with data items? (describe - click, hover, actions)
```

### User Interactions

```
Test {interaction type} on {URL}:
1. What element did you interact with? (describe - button, link, card)
2. What was the expected result? (describe - modal opens, details expand)
3. What actually happened? (describe exactly - nothing, wrong thing, error)
4. Any console errors during interaction? (list full error messages)
5. Is there visual feedback? (describe - hover state, active state, animation)
```

## Anti-Patterns (What NOT to do)

| Bad Prompt | Why It Fails | Better Alternative |
|------------|--------------|-------------------|
| "Does it work?" | Too vague, false positive | "What specific errors appear?" |
| "Is the page loading?" | Yes/No insufficient | "Describe any loading spinners visible" |
| "Test the app" | No guidance on what to test | "Test the login button specifically" |
| "Check for issues" | Doesn't specify issue type | "Check for console errors and broken layout" |
| "Navigate and verify" | Verify what exactly? | "Navigate and check if X button appears" |

## Response Validation Checklist

When reviewing Comet's response, verify:

- [ ] Specific element names mentioned (not "content", "items")
- [ ] Exact error messages quoted (not "errors occurred")
- [ ] Visual descriptions provided (colors, layout, appearance)
- [ ] Step-by-step actions described
- [ ] Console output captured if errors present
- [ ] Screenshots taken for visual evidence

## Custom Prompt Builder

Mix and match these components:

| Component | Options |
|-----------|---------|
| Action | Navigate to, Click on, Fill in, Scroll to |
| Target | {URL}, {button}, {form}, {element} |
| Verification | Describe, List, Specify exact |
| Evidence | Console errors, Visual state, URL change, Loading state |
| Format | yes/no with details, describe specifically, list them |

Example: "Navigate to {URL}, click {button}, and describe: what appears, any console errors (list them), and URL change (exact new URL)."
