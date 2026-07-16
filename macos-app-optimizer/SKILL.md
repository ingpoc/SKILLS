---
name: macos-app-optimizer
description: "Audit native macOS, AppKit, and SwiftUI applications for memory ownership, ARC cycles, rendering cost, heap growth, and profiling evidence. Use when the operator asks to diagnose or optimize a macOS application's runtime performance. Do not use for generic code quality or non-Apple web performance."
---

# macOS App Optimizer

Analyze macOS applications for performance and memory optimization opportunities.

## Core Principle: RAM Optimization

Memory optimization is the primary focus. Every analysis should identify:

- Memory leaks (retain cycles, unbalanced alloc/free)
- Unnecessary object retention
- Inefficient data structures
- Cached data that should be purged
- Large objects that could be lazy-loaded

## Workflow

### 1. Analyze Codebase Structure

```bash
# Identify main components
find . -name "*.swift" -type f | head -20
# Check for common patterns
grep -r "@Published\|@State\|@ObservedObject" --include="*.swift"
# Find potential retain cycles
grep -r "closure\|weak\|unowned" --include="*.swift"
```

### 2. Check Context7 for Apple Best Practices

Use Context7 to query relevant Apple documentation:

| Use Case | Context7 Query |
|----------|----------------|
| SwiftUI performance | `/swiftlang/swift` "SwiftUI performance view redraw" |
| Memory management | `/swiftlang/swift` "ARC memory management retain cycles" |
| Async operations | `/swiftlang/swift` "async await memory management" |
| SwiftData optimization | Search for SwiftData-specific docs |
| Foundation patterns | `/apple/foundation` "memory efficient collections" |

### 3. Analyze Common Memory Issues

| Issue | Pattern to Find | Fix |
|-------|-----------------|-----|
| Retain cycles | Closures capturing `self` | Use `[weak self]` |
| @Published bloat | Too many published properties | Consolidate or use computed |
| Large images | Image literals, large assets | Lazy load, downsample |
| Memory leaks | Classes without deinit | Add `deinit` to verify |
| Cached data | Static caches without purge | LRU cache, memory pressure handlers |

### 4. Check Instruments-Ready Patterns

Ensure code is instrumentable:

```swift
// Good - trackable
class ViewModel: ObservableObject {
    deinit { print("ViewModel deallocated") }
}

// Bad - can't track lifecycle
class ViewModel {
    // No deinit
}
```

### 5. Specific Optimizations by Component

#### SwiftUI Views

- Use `@State` for local view state only
- Prefer `let` over `var` for view body
- Extract expensive computations to separate functions
- Use `LazyVStack`/`LazyHStack` for long lists

#### ViewModels

- Use `@Observable` instead of `ObservableObject` (Swift 5.9+)
- Minimize `@Published` properties
- Avoid storing large data directly (use IDs, fetch separately)

#### Networking

- Cancel tasks on deinit
- Stream large responses instead of buffering
- Use `URLSession.shared` (singleton)

#### Persistence

- Use SwiftData with proper faulting
- Avoid loading entire datasets into memory
- Consider Core Data for complex queries

### 6. Memory Pressure Handling

```swift
// Listen for memory warnings
NotificationCenter.default.addObserver(
    forName: NSApplication.didReceiveMemoryWarningNotification,
    object: nil,
    queue: .main
) { _ in
    // Purge caches, clear non-essential data
}
```

### 7. Output Format

Provide optimization report in this table:

| Priority | Issue | Location | RAM Impact | Fix |
|----------|-------|----------|------------|-----|
| HIGH | Retain cycle in closure | ViewModel.swift:42 | ~5MB/minute | Use `[weak self]` |
| MEDIUM | Unnecessary image caching | ImageLoader.swift:15 | ~50MB | Downsample images |
| LOW | Redundant @Published | SettingsView.swift:8 | ~1KB | Remove `@Published` |

## Quick Reference: Context7 Library IDs

| Library | ID | Use For |
|---------|-----|---------|
| Swift Language | `/swiftlang/swift` | Language patterns, ARC, async |
| Foundation | `/apple/foundation` | Collections, URL, file I/O |
| SwiftUI | Check Apple docs | View optimization |
| SwiftData | Check Apple docs | Persistence patterns |

## Scripts

| Script | Purpose |
|--------|---------|
| scripts/analyze_memory.sh | Find potential memory issues |
| scripts/check_retain_cycles.sh | Detect closure capture patterns |
| scripts/measure_heap.sh | Estimate heap allocation |
