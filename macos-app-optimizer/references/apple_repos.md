# Apple Repositories for macOS Optimization

## Context7 Library Mappings

| Repository | Context7 ID | Use For |
|------------|-------------|---------|
| Swift Language | `/swiftlang/swift` | ARC, memory management, async/await, concurrency |
| Foundation | `/apple/foundation` | Collections, URL, file I/O, caching patterns |
| Swift Algorithms | `/apple/swift-algorithms` | Efficient algorithms, sequence operations |
| Swift Collections | `/apple/swift-collections` | High-performance data structures |
| Swift System | `/apple/swift-system` | Low-level system calls, file descriptors |
| Swift NIO | `/apple/swift-nio` | High-performance networking, event loops |

## Core Swift Repos (Language & Tooling)

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-format | 1.5k | Code style consistency |
| swift-syntax | 2.6k | Code generation, analysis |
| swift-log | 1.1k | Structured logging |
| swift-argument-parser | 2.3k | CLI argument parsing |
| swift-docc | 1.1k | Documentation generation |
| swift-crypto | 1.4k | Cryptographic operations |
| swift-numerics | 1.1k | Math, complex numbers |
| swift-markdown | 300 | Markdown parsing |
| swift-protobuf | 4.9k | Protocol buffers, serialization |
| swift-atomics | 1.2k | Low-level concurrency, memory |
| swift-metrics | 748 | Performance monitoring |
| swift-http-types | 1k | HTTP type safety |

## Networking & Servers

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-nio | 7.7k | High-performance networking |
| swift-nio-http2 | 491 | HTTP/2 support |
| swift-nio-ssl | 422 | TLS, secure networking |
| swift-nio-ssh | 474 | SSH implementation |
| swift-nio-transport-services | 329 | Apple platform extensions |
| swift-http-structured-headers | 192 | HTTP header efficiency |
| swift-service-context | 190 | Async context propagation |
| swift-async-dns-resolver | 146 | Async DNS networking |

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-nio | 7.7k | High-performance networking |
| swift-nio-http2 | 491 | HTTP/2 support |
| swift-nio-ssl | 422 | TLS, secure networking |
| swift-nio-ssh | 474 | SSH implementation |
| swift-nio-transport-services | 329 | Apple platform extensions |

## Data & Persistence

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-collections | 4.3k | High-performance collections |
| swift-collections-benchmark | 365 | Collection performance testing |
| swift-async-algorithms | 2.5k | Async sequence operations |
| swift-algorithms | 5.5k | Efficient algorithms |

## Development Tools

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-llbuild | 815 | Build system |
| swift-package-manager | 9.5k | Dependency management |
| swift-format | 1.5k | Code formatting |
| swift-binary-parsing | 359 | Binary efficiency |
| swift-xcode-playground-support | 307 | Playground development |
| swift-http-structured-headers | 192 | HTTP header efficiency |
| swift-service-context | 190 | Async context propagation |
| swift-profile-recorder | 190 | Performance profiling |
| swift-llbuild2 | 303 | Build system API |
| pkl-swift | 190 | Config language |
| swift-async-dns-resolver | 146 | Async DNS networking |

## Sample Code & Patterns

| Repo | Stars | Use Case |
|------|--------|----------|
| sample-food-truck | 1.8k | SwiftUI patterns (WWDC22) |
| sample-cloudkit-sharing | 329 | CloudKit integration |
| swift-3-api-guidelines-review | 453 | API design best practices |
| sample-cloudkit-coredatasync | 198 | CloudKit + Core Data patterns |
| sample-cloudkit-privatedb-sync | 192 | CloudKit sync patterns |
| sample-cloudkit-privatedb | 153 | CloudKit patterns |

## Sample Code & Patterns

| Repo | Stars | Use Case |
|------|--------|----------|
| sample-food-truck | 1.8k | SwiftUI patterns (WWDC22) |
| sample-cloudkit-sharing | 329 | CloudKit integration |
| swift-3-api-guidelines-review | 453 | API design best practices |

## Machine Learning (Apple Silicon Optimized)

| Repo | Stars | Use Case |
|------|--------|----------|
| ml-stable-diffusion | 18k | Core ML on Apple Silicon |
| coremltools | 5.1k | Model conversion, editing |
| turicreate | 9.1k | ML framework |

## Apple Intelligence (On-Device AI)

| Repo | Stars | Use Case |
|------|--------|----------|
| swift-transform | Internal | ML model execution (Apple private) |
| coremltools | 5.1k | Model conversion, optimization |
| coreml | Built-in | Core ML framework (macOS) |

## Containers & Infrastructure

| Repo | Stars | Use Case |
|------|--------|----------|
| container | 24k | Linux containers on Mac |
| containerization | 8.3k | Container packaging |

## Context7 Query Templates by Use Case

### Memory & Performance

```
/swiftlang/swift: "ARC retain cycle memory management"
/swiftlang/swift: "weak unowned closure capture"
/swiftlang/swift: "@Observable vs @Published memory"
/swiftlang/swift: "async await memory leaks"
/swiftlang/swift: "Copy-on-Write collections performance"
/apple/foundation: "NSCache memory pressure purge"
/apple/foundation: "URLSession memory efficient streaming"
/swiftlang/swift: "Swift Concurrency memory management"
/swiftlang/swift: "actor isolation race safety"
```

### Networking

```
/swiftlang/swift-nio: "HTTP2 efficient streaming"
/swiftlang/swift-nio: "TLS memory efficient connections"
/apple/foundation: "URLSession async await best practices"
/swiftlang/swift-nio: "Channel memory buffer pool"
```

### Data Structures

```
/apple/swift-collections: "Deque performance vs Array"
/apple/swift-algorithms: "lazy sequence memory efficiency"
/apple/swift-numerics: "value types stack allocation"
```

### SwiftUI & Views

```
/swiftlang/swift: "SwiftUI view redraw optimization"
/swiftlang/swift: "@State vs @Observable memory"
/apple/foundation: "SwiftUI lazy loading performance"
```

### Persistence

```
Search: "SwiftData faulting lazy loading"
Search: "Core Data memory best practices"
Search: "NSBatchFetchRequest memory efficiency"
Search: "NSManagedObject memory lifecycle"
```

### Instruments & Debugging

```
/swiftlang/swift: "deinit memory leak debugging"
/apple/foundation: "Instruments memory profiling"
/swiftlang/swift: "swift-backtrace memory analysis"
/swift-metrics: "performance metrics collection"
```
