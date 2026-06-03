#!/usr/bin/env python3
"""
mark-tested.py

Purpose: Mark feature as browser tested (Python version - handles file permissions better)
Updates testing-list.json with test result and evidence

Usage: python3 mark-tested.py <feature-id> [passed|failed|skipped] [--evidence "item1" "item2"]
Example: python3 mark-tested.py SDK-BUYER-CART-004 passed --evidence "Renders" "No errors"

Status values: pending, in_progress, passed, failed, skipped
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

def main():
    parser = argparse.ArgumentParser(description='Mark feature as browser tested')
    parser.add_argument('feature_id', help='Feature ID to mark as tested')
    parser.add_argument('status', nargs='?', default='passed',
                       choices=['pending', 'in_progress', 'passed', 'failed', 'skipped'],
                       help='Test status (default: passed)')
    parser.add_argument('--evidence', nargs='*', default=[],
                       help='Test evidence items to add')

    args = parser.parse_args()

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
        if feature['id'] == args.feature_id:
            feature_found = True

            # Update feature
            timestamp = datetime.now().isoformat()
            feature['browser_test_status'] = args.status
            feature['last_tested'] = timestamp
            feature['attempts'] = feature.get('attempts', 0) + 1

            # Add evidence if provided
            if args.evidence:
                existing_evidence = feature.get('test_evidence', [])
                for evidence_item in args.evidence:
                    if evidence_item not in existing_evidence:
                        existing_evidence.append(evidence_item)
                feature['test_evidence'] = existing_evidence

            break

    if not feature_found:
        print(f"Error: Feature '{args.feature_id}' not found in testing-list.json", file=sys.stderr)
        sys.exit(1)

    # Recalculate summary
    timestamp = datetime.now().isoformat()
    data['updated'] = timestamp
    data['summary'] = {
        'total': len(data['features']),
        'tested': sum(1 for f in data['features'] if f['browser_test_status'] == 'passed'),
        'pending': sum(1 for f in data['features'] if f['browser_test_status'] == 'pending'),
        'failed': sum(1 for f in data['features'] if f['browser_test_status'] == 'failed'),
        'skipped': sum(1 for f in data['features'] if f['browser_test_status'] == 'skipped')
    }

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

    # Output summary
    status_str = feature['browser_test_status']
    print(f"✅ Updated {args.feature_id} browser test status to: {status_str}")
    print(f"Summary: Tested: {data['summary']['tested']} | Pending: {data['summary']['pending']} | Failed: {data['summary']['failed']}")

    sys.exit(0)

if __name__ == '__main__':
    main()
