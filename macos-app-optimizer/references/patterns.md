# Common Memory Optimization Patterns

## 1. Avoid Retain Cycles

### BAD

```swift
class ViewModel {
    var closure: (() -> Void)?

    func setup() {
        closure = {
            self.doSomething()  // Retain cycle
        }
    }
}
```

### GOOD

```swift
class ViewModel {
    var closure: (() -> Void)?

    func setup() {
        closure = { [weak self] in
            self?.doSomething()
        }
    }
}
```

## 2. Use Value Types Where Possible

### BAD

```swift
class Point {  // Heap allocated
    var x: Double
    var y: Double
}
```

### GOOD

```swift
struct Point {  // Stack allocated
    var x: Double
    var y: Double
}
```

## 3. Lazy Load Large Resources

### BAD

```swift
class ImageLoader {
    let images = loadAllImages()  // Loads immediately
}
```

### GOOD

```swift
class ImageLoader {
    lazy var images = loadAllImages()  // Loads on access
}
```

## 4. Purge on Memory Warning

```swift
final class CacheManager {
    private var cache: [String: Data] = [:]

    init() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleMemoryWarning),
            name: NSApplication.didReceiveMemoryWarningNotification,
            object: nil
        )
    }

    @objc private func handleMemoryWarning() {
        cache.removeAll()
    }
}
```

## 5. Cancel Async Work on Deinit

```swift
final class DataLoader {
    private var task: Task<Void, Never>?

    func load() {
        task = Task {
            // Async work
        }
    }

    deinit {
        task?.cancel()
    }
}
```

## 6. Use NSCache Instead of Dictionary

### BAD

```swift
private var imageCache: [String: NSImage] = [:]  // Never purged
```

### GOOD

```swift
private let imageCache = NSCache<NSString, NSImage>()
imageCache.countLimit = 100
```

## 7. Stream Large Data

### BAD

```swift
let data = try Data(contentsOf: url)  // Loads entire file
```

### GOOD

```swift
let handles = try FileHandle(forReadingFrom: url)
// Read in chunks
```

## 8. @Observable > ObservableObject

```swift
// Swift 5.9+ - Less overhead
@Observable
class ViewModel {
    var items: [Item] = []
}
```

## 9. Use deinit for Debugging

```swift
class MyViewModel {
    deinit {
        print("✅ MyViewModel deallocated")
    }
}
```

## 10. Avoid Force Unwraps in Long-Lived Objects

```swift
// Bad: Can hide nil that should be freed
@IBOutlet var label: UILabel!

// Good: Optional, properly managed
@IBOutlet var label: UILabel?
```
