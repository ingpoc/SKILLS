#!/bin/bash
# Analyze Swift code for potential memory issues

echo "=== Memory Pattern Analysis ==="
echo ""

# Find closures capturing self without [weak self]
echo "1. Closures capturing self (potential retain cycles):"
grep -rn "in.*self\." --include="*.swift" | grep -v "\[weak self\]" | grep -v "\[unowned self\]" | head -10

echo ""
echo "2. @Published properties (check for bloat):"
grep -rn "@Published" --include="*.swift" | wc -l
echo "Total @Published properties found"

echo ""
echo "3. Classes without deinit (can't verify deallocation):"
find . -name "*.swift" -type f -print0 | while IFS= read -r -d '' file; do
    if grep -q "^class " "$file"; then
        if ! grep -q "deinit" "$file"; then
            echo "$file"
        fi
    fi
done | head -5

echo ""
echo "4. Force unwraps (could hide memory issues):"
grep -rn "!" --include="*.swift" | grep -E ":\s*\w+\!" | wc -l
echo "Force-unwrapped optionals found"

echo ""
echo "5. Large image literals or data:"
find . -name "*.swift" -exec grep -l "Data(repeating:\|Data(count:" {} \; | head -5
