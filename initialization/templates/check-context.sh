#!/bin/bash
# Check context usage level
# Output: none|remove_raw|summarize|full|emergency

# This would typically read from Claude's context API
# For now, use heuristic based on conversation length

USAGE=${1:-0.75}  # Pass usage as argument or default

if (( $(echo "$USAGE > 0.95" | bc -l) )); then
    echo "emergency"
elif (( $(echo "$USAGE > 0.90" | bc -l) )); then
    echo "full"
elif (( $(echo "$USAGE > 0.85" | bc -l) )); then
    echo "summarize"
elif (( $(echo "$USAGE > 0.80" | bc -l) )); then
    echo "remove_raw"
else
    echo "none"
fi
