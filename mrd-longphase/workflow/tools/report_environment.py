#!/usr/bin/env python3
"""Report the analysis environment: tool versions, Python packages, and data reachability.

Run this before any experiment and paste the output into the run's manifest. It answers
"why did this run behave differently from the last one" faster than anything else.

Absent tools are reported as absent rather than omitted — a missing `longphase` is exactly
the kind of fact that explains a downstream result, and a report that silently drops it
hides the explanation.

  python workflow/tools/report_environment.py
  python workflow/tools/report_environment.py --json
  python workflow/tools/report_environment.py --check-data config/datasets/hcc1395_dilution.yaml
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.provenance import collect_tool_versions  # noqa: E402

#: Tools whose absence blocks a specific phase, and which phase.
BLOCKING = {
    "longphase": "phasing / haplotagging (H1)",
    "samtools": "all BAM operations",
}


def check_data(dataset_path: str) -> list:
    """Confirm every path in a dataset config is readable, without opening the files."""
    import yaml

    with open(dataset_path) as fh:
        dataset = yaml.safe_load(fh) or {}

    entries = []
    for role, source in (dataset.get("sources") or {}).items():
        entries.append((f"source:{role}", source.get("bam")))
    for sample in dataset.get("samples") or []:
        entries.append((f"sample:{sample.get('sample_id')}", sample.get("bam")))
    if dataset.get("reference"):
        entries.append(("reference", dataset["reference"]))

    results = []
    for label, path in entries:
        if not path:
            continue
        exists = os.path.exists(path)
        entry = {"label": label, "path": path, "exists": exists}
        if exists:
            entry["readable"] = os.access(path, os.R_OK)
            entry["size_gb"] = round(os.path.getsize(path) / 1e9, 1)
            # Writable source data is a governance problem, not a convenience.
            entry["writable_warning"] = os.access(path, os.W_OK)
        results.append(entry)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--check-data", help="dataset YAML whose paths should be checked")
    args = parser.parse_args(argv)

    versions = collect_tool_versions()
    report = {"tool_versions": versions}
    if args.check_data:
        report["data"] = check_data(args.check_data)

    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    print("Environment report")
    print("=" * 68)
    for name in sorted(versions):
        value = versions[name]
        marker = "  " if value != "absent" else "! "
        print(f"{marker}{name:14s} {value}")

    missing_blocking = [tool for tool, phase in BLOCKING.items() if versions.get(tool) == "absent"]
    if missing_blocking:
        print("\nBlocking absences:")
        for tool in missing_blocking:
            print(f"  ! {tool} — required for {BLOCKING[tool]}")

    if args.check_data:
        print("\nData reachability")
        print("=" * 68)
        for entry in report["data"]:
            status = "ok " if entry["exists"] else "MISSING"
            size = f"{entry.get('size_gb', '?')} GB" if entry["exists"] else ""
            print(f"  {status} {entry['label']:36s} {size:>10s}  {entry['path']}")
            if entry.get("writable_warning"):
                print("       ! this path is writable by the current user; treat as read-only anyway")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
