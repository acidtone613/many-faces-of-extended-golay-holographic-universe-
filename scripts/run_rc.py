#!/usr/bin/env python3
"""
24D-DMF Research Cycle Runner

Usage:
  python scripts/run_rc.py                  # Interactive menu
  python scripts/run_rc.py --list           # List all RCs
  python scripts/run_rc.py --search 170     # Search by RC number
  python scripts/run_rc.py --run RC-170b    # Run a specific RC
  python scripts/run_rc.py --run 170b       # Shorthand
"""

import sys
import os
import argparse
import glob
import subprocess
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIRS = sorted(ROOT.glob("*/scripts/")) + sorted(ROOT.glob("*/*/scripts/"))
DOMAIN_NAMES = {
    "clocks": "Clocks",
    "dark": "Dark",
    "holography": "Holography",
    "manifolds": "Manifolds",
    "physics/constants": "Physics/Constants",
    "physics/gauge": "Physics/Gauge",
    "physics/masses": "Physics/Masses",
    "physics/mixings": "Physics/Mixings",
    "quantum": "Quantum",
    "catalogue": "Catalogue",
    "uncertain": "Uncertain",
}


def discover_rcs():
    rcs = {}
    for scripts_dir in SCRIPTS_DIRS:
        domain = str(scripts_dir.parent.relative_to(ROOT)).replace("\\", "/")
        py_files = sorted(scripts_dir.glob("*.py"))
        if not py_files:
            continue
        entries = []
        for f in py_files:
            match = re.search(r"(RC-\d+[a-zA-Z]*(?:_\d+[a-zA-Z]*)*)", f.stem, re.IGNORECASE)
            rc_id = match.group(1).upper() if match else f.stem.replace("_", " ")
            entries.append((rc_id, str(f)))
        rcs[domain] = entries
    return rcs


def list_rcs(rcs):
    print(f"\n{'='*60}")
    print(f"  24D-DMF v8.4.6 — Available Research Cycles")
    print(f"{'='*60}")
    total = 0
    for domain in sorted(rcs.keys()):
        label = DOMAIN_NAMES.get(domain, domain)
        entries = rcs[domain]
        print(f"\n  {label} ({len(entries)}):")
        for rc_id, path in entries:
            print(f"    {rc_id:12s}  {path}")
        total += len(entries)
    print(f"\n  Total: {total} scripts across {len(rcs)} domains")
    print()


def search_rcs(rcs, query):
    query = query.upper().replace("RC-", "").replace("RC", "")
    results = []
    for domain, entries in rcs.items():
        for rc_id, path in entries:
            rc_num = rc_id.replace("RC-", "").upper()
            if query in rc_num:
                results.append((domain, rc_id, path))
    if results:
        print(f"\n  Found {len(results)} match(es) for '{query}':")
        for domain, rc_id, path in results:
            label = DOMAIN_NAMES.get(domain, domain)
            print(f"    [{label}] {rc_id:12s}  {path}")
        print()
    else:
        print(f"  No results for '{query}'\n")
    return results


def run_script(path):
    abs_path = Path(path).resolve()
    if not abs_path.exists():
        print(f"  Error: {path} not found")
        return
    print(f"\n  Running: {abs_path.name}")
    print(f"  {'='*56}")
    result = subprocess.run([sys.executable, str(abs_path)], cwd=ROOT)
    print(f"\n  {'='*56}")
    print(f"  Exit code: {result.returncode}")
    if result.returncode != 0:
        print(f"  (script may have errors printed above)")


def find_rc(rci_d, entry):
    rc_id, path = entry
    return rc_id


def interactive_menu(rcs):
    flat = []
    for domain in sorted(rcs.keys()):
        for entry in rcs[domain]:
            flat.append((domain, entry))

    while True:
        print(f"\n{'='*60}")
        print(f"  24D-DMF v8.4.6 — Interactive Runner")
        print(f"{'='*60}")
        print(f"  0)  Quit")
        print(f"  L)  List all RCs")
        print(f"  S)  Search by RC number")

        domain_indices = {}
        current = 1
        for domain in sorted(rcs.keys()):
            label = DOMAIN_NAMES.get(domain, domain)
            count = len(rcs[domain])
            domain_indices[current] = (domain, None)
            print(f"  {current})  [{label}] ({count} scripts)")
            current += 1

        choice = input(f"\n  Select ({'|'.join(str(k) for k in domain_indices)}|0|L|S): ").strip()

        if choice == "0":
            print("  Goodbye.")
            break
        elif choice.upper() == "L":
            list_rcs(rcs)
            continue
        elif choice.upper() == "S":
            query = input("  Search: ").strip()
            if query:
                results = search_rcs(rcs, query)
                if results and len(results) == 1:
                    _, rc_id, path = results[0]
                    run_script(path)
            continue

        try:
            idx = int(choice)
        except ValueError:
            print("  Invalid choice")
            continue

        if idx not in domain_indices:
            print("  Invalid choice")
            continue

        domain, _ = domain_indices[idx]
        domain_entries = rcs[domain]

        while True:
            label = DOMAIN_NAMES.get(domain, domain)
            print(f"\n  [{label}] — Select RC:")
            print(f"  0)  Back")
            for i, (rc_id, path) in enumerate(domain_entries, 1):
                print(f"  {i:2d})  {rc_id:12s}  {Path(path).name}")
            print(f"  S)  Search")

            sub = input(f"\n  Select (1-{len(domain_entries)}|0|S): ").strip()

            if sub == "0":
                break
            elif sub.upper() == "S":
                query = input("  Search: ").strip()
                if query:
                    results = search_rcs(rcs, query)
                    if results and len(results) == 1:
                        _, _, path = results[0]
                        run_script(path)
                continue

            try:
                sidx = int(sub)
            except ValueError:
                print("  Invalid choice")
                continue

            if sidx < 1 or sidx > len(domain_entries):
                print("  Invalid choice")
                continue

            rc_id, path = domain_entries[sidx - 1]
            run_script(path)


def main():
    parser = argparse.ArgumentParser(description="24D-DMF Research Cycle Runner")
    parser.add_argument("--list", action="store_true", help="List all available RCs")
    parser.add_argument("--search", type=str, help="Search RCs by number")
    parser.add_argument("--run", type=str, help="Run a specific RC (e.g. RC-170b or 170b)")
    args = parser.parse_args()

    rcs = discover_rcs()

    if args.list:
        list_rcs(rcs)
    elif args.search:
        search_rcs(rcs, args.search)
    elif args.run:
        query = args.run.upper().replace("RC-", "").replace("RC", "")
        results = search_rcs(rcs, query)
        if len(results) == 1:
            _, _, path = results[0]
            run_script(path)
        elif len(results) > 1:
            print(f"  Multiple matches for '{query}':")
            for domain, rc_id, path in results:
                print(f"    {rc_id:12s}  {path}")
            choice = input("  Enter RC ID to run (or 0 to cancel): ").strip().upper()
            if choice != "0":
                for domain, rc_id, path in results:
                    if choice in rc_id:
                        run_script(path)
                        break
        else:
            print(f"  No script found for '{args.run}'")
    else:
        interactive_menu(rcs)


if __name__ == "__main__":
    main()
