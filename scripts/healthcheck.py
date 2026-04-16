#!/usr/bin/env python3
"""
Cortex healthcheck script.
Verifies all required protocol files exist and are non-empty.
Called by the scribe at session start.
Run manually: python scripts/healthcheck.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED = {
    "CORTEX.md": "Protocol engine",
    "GUARDRAILS.md": "Safety guardrails",
    "DISCLAIMER.md": "Disclaimer and legal warnings",
    "ROE.md": "Rules of engagement",
}


def main():
    errors = []
    warnings = []

    for filename, description in REQUIRED.items():
        path = os.path.join(ROOT, filename)

        if not os.path.exists(path):
            errors.append(f"MISSING: {filename} — {description}")
            continue

        if os.path.getsize(path) == 0:
            errors.append(f"EMPTY: {filename} — {description}")
            continue

    if errors:
        print("Cortex healthcheck FAILED\n")
        for e in errors:
            print(f"  {e}")
        print()

        if any("GUARDRAILS.md" in e for e in errors):
            print("WARNING: GUARDRAILS.md is missing or empty.")
            print("Cortex has no safety guardrails. Cordfuse accepts zero liability for any consequences.")
            print("Do not proceed without restoring this file.")

        sys.exit(1)

    print("Cortex healthcheck OK")
    for filename, description in REQUIRED.items():
        print(f"  {filename}: OK")

    sys.exit(0)


if __name__ == "__main__":
    main()
