#!/bin/bash
# Check for potential retain cycles in Swift code

echo "=== Retain Cycle Detection ==="
echo ""

# Pattern 1: Closures in classes capturing self
echo "1. Closures in classes that might capture self strongly:"
grep -rn "class.*{" --include="*.swift" -A 20 | grep -E "(var|let).*=.*\{.*self\." | head -10

echo ""
echo "2. Property observers calling closures (common leak source):"
grep -rn "didSet\|willSet" --include="*.swift" | grep -E "\{.*self\." | head -5

echo ""
echo "3. Combine subscribers without .store(in:):"
grep -rn "\.sink\|\.subscribe" --include="*.swift" | grep -v "\.store\|\.assign(to:" | head -5

echo ""
echo "4. Timer references that aren't invalidated:"
grep -rn "Timer\." --include="*.swift" | grep -v "invalidate\|\.invalidate()" | head -5

echo ""
echo "5. NotificationCenter observers without removal:"
grep -rn "NotificationCenter\.default\.addObserver" --include="*.swift" | head -5
echo "Check for matching .removeObserver calls"
