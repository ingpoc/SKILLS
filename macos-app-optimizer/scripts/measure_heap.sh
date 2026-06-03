#!/bin/bash
# Estimate heap allocation patterns in Swift code

echo "=== Heap Allocation Estimation ==="
echo ""

# Count class instances (heap allocated)
echo "1. Heap-allocated types (classes):"
find . -name "*.swift" -exec grep -h "^class " {} \; | wc -l
echo "Classes defined"

echo ""
echo "2. Value types (stack preferred):"
find . -name "*.swift" -exec grep -h "^struct " {} \; | wc -l
echo "Structs defined"

echo ""
echo "3. Large data allocations (>1KB):"
grep -rn "Data(count:\|Data(repeating:\|Array(repeating:" --include="*.swift" | while read line; do
    # Extract the count/repeating value to estimate size
    if [[ $line =~ (Data\(count:\s*[0-9]+|Array\(repeating:\s*count:\s*[0-9]+) ]]; then
        echo "$line"
    fi
done | head -10

echo ""
echo "4. Array copy potential (CoW):"
grep -rn "\.append\|\.insert\|\.remove" --include="*.swift" | wc -l
echo "Mutation operations (may trigger CoW copies)"

echo ""
echo "5. Potential boxed values:"
grep -rn "\[Any\]\|AnyObject" --include="*.swift" | head -5
echo "Any type usage causes boxing"

echo ""
echo "6. Escaping closures (heap capture):"
grep -rn "@escaping" --include="*.swift" | wc -l
echo "Escaping closures found"
