#!/usr/bin/env python3
"""
mark-in-progress.py

Purpose: Mark feature as in_progress for testing
Updates testing-list.json with in_progress status

Usage: python3 mark-in-progress.py <feature-id>
Example: python3 mark-in-progress.py SDK-BUYER-CART-004

Status: Sets browser_test_status to 'in_progress'
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <feature-id>", file=sys.stderr)
        print("Example: python3 mark-in-progress.py SDK-BUYER-CART-004", file=sys.stderr)
        sys.exit(1)

    feature_id = sys.argv[1]

    # Path to testing list
    testing_file = Path('.claude/progress/testing-list.json')

    if not testing_file.exists():
        print(f"Error: testing-list.json not found at {testing_file}", file=sys.stderr)
        print("Run 'initialize-testing-list.sh' first", file=sys.stderr)
        sys.exit(1)

    try:
        # Read current testing list
        with open(testing_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {testing_file}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {testing_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Find feature
    feature_found = False
    for feature in data['features']:
        if feature['id'] == feature_id:
            feature_found = True
            feature['browser_test_status'] = 'in_progress'
            feature['attempts'] = feature.get('attempts', 0) + 1
            break

    if not feature_found:
        print(f"Error: Feature '{feature_id}' not found in testing-list.json", file=sys.stderr)
        sys.exit(1)

    # Update timestamp
    timestamp = datetime.now().isoformat()
    data['updated'] = timestamp

    # Write to temp file first
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name

        # Copy temp to actual file (more reliable than mv in sandboxed environments)
        shutil.copy2(tmp_path, testing_file)
        Path(tmp_path).unlink()

    except Exception as e:
        print(f"Error writing to {testing_file}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Marked {feature_id} as in_progress")

    sys.exit(0)

if __name__ == '__main__':
    main()
