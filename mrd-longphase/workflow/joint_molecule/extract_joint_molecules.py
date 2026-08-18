#!/usr/bin/env python3
"""Extract joint-molecule evidence (allele + haplotype + native methylation) per region.

Thin CLI over ``src.joint_evidence``. Region-scoped, resumable, deterministic. The BAM is
never loaded whole — only ``fetch``/``pileup`` over the requested intervals.

Example (a single small region, the way this should first be run):

  python workflow/joint_molecule/extract_joint_molecules.py \\
      --bam       /bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-2_25x/TF1e-2_25x.rep1.bam \\
      --candidates results/tumor_only/HCC1395/candidate_pass_snvs.tsv \\
      --config    config/experiments/h1_feasibility.yaml \\
      --sample-id HCC1395_TF1e-2_25x_rep1 --dilution 1e-2 \\
      --region    chr1:1000000-2000000 \\
      --outdir    results/joint_evidence/HCC1395_TF1e-2_25x_rep1

Evaluation-only labels are opt-in via ``--label-tumor-bam``/``--label-normal-bam``. They
are written to the table for scoring and are never consulted by any filter.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pysam  # noqa: E402
import yaml  # noqa: E402

from src.io.regions import Region, merge_overlapping, parse_region, partition_contig, read_region_bed  # noqa: E402
from src.joint_evidence import (  # noqa: E402
    ExtractionConfig,
    JointEvidenceStore,
    describe_inputs,
    extract_region,
    input_manifest_id,
    iter_candidates_from_tsv,
)
from src.joint_evidence.labels import label_region  # noqa: E402
from src.provenance import collect_tool_versions, format_tool_versions, run_manifest  # noqa: E402

LOGGER = logging.getLogger("extract_joint_molecules")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bam", required=True, help="mixture/tumor BAM to extract from (read-only)")
    p.add_argument("--candidates", required=True, help="candidate_pass_snvs.tsv from src.candidates")
    p.add_argument("--config", required=True, help="experiment YAML holding extraction.* thresholds")
    p.add_argument("--sample-id", required=True)
    p.add_argument("--dilution", required=True, help="nominal mixing ratio, e.g. 1e-2 / 0 / pure")
    p.add_argument("--outdir", required=True)

    regions = p.add_argument_group("region selection (choose one)")
    regions.add_argument("--region", action="append", default=[], help="chrom:start-end, repeatable")
    regions.add_argument("--region-bed", help="BED of regions")
    regions.add_argument("--contig", help="whole contig, partitioned by --chunk-size")
    p.add_argument("--chunk-size", type=int, default=1_000_000, help="partition size for --contig")

    labels = p.add_argument_group("evaluation-only labelling")
    labels.add_argument("--label-tumor-bam", help="tumor source BAM for per-read labels")
    labels.add_argument("--label-normal-bam", help="normal source BAM for per-read labels")

    p.add_argument("--force", action="store_true", help="re-extract regions already marked complete")
    p.add_argument("--log-level", default="INFO")
    return p.parse_args(argv)


def resolve_regions(args, bam) -> list:
    """Build the region list, merging overlaps so no read is counted twice."""
    regions = [parse_region(spec) for spec in args.region]
    if args.region_bed:
        regions.extend(read_region_bed(args.region_bed))
    if args.contig:
        lengths = dict(zip(bam.references, bam.lengths))
        if args.contig not in lengths:
            raise SystemExit(f"contig {args.contig!r} not in BAM header")
        regions.extend(partition_contig(args.contig, lengths[args.contig], args.chunk_size))
    if not regions:
        raise SystemExit("no regions selected; pass --region, --region-bed or --contig")
    return merge_overlapping(regions)


def load_extraction_config(path: str) -> tuple:
    """Load the ``extraction:`` block. Missing thresholds raise rather than default."""
    with open(path) as fh:
        raw = yaml.safe_load(fh) or {}
    block = raw.get("extraction")
    if block is None:
        raise SystemExit(f"{path}: no 'extraction:' block")
    return ExtractionConfig.from_dict(block), raw


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )

    config, raw_config = load_extraction_config(args.config)
    candidates = list(iter_candidates_from_tsv(args.candidates))
    LOGGER.info("loaded %d candidate loci", len(candidates))

    if (args.label_tumor_bam is None) != (args.label_normal_bam is None):
        raise SystemExit("--label-tumor-bam and --label-normal-bam must be given together")

    bam = pysam.AlignmentFile(args.bam, "rb")
    regions = resolve_regions(args, bam)
    LOGGER.info("%d region(s) after merging", len(regions))

    inputs = {"bam": args.bam, "candidates": args.candidates, "config": args.config}
    if args.label_tumor_bam:
        inputs["label_tumor_bam"] = args.label_tumor_bam
        inputs["label_normal_bam"] = args.label_normal_bam

    manifest_id = input_manifest_id(inputs, raw_config.get("extraction"))
    versions = collect_tool_versions()
    version_string = format_tool_versions(versions)

    store = JointEvidenceStore(args.outdir)
    store.ensure_dirs()
    store.write_manifest(
        run_manifest(
            experiment_id=raw_config.get("id", args.sample_id),
            inputs=describe_inputs(inputs),
            config=raw_config,
            extra={
                "input_manifest_id": manifest_id,
                "sample_id": args.sample_id,
                "dilution": args.dilution,
                "regions": [r.id for r in regions],
            },
        )
    )

    tumor_src = pysam.AlignmentFile(args.label_tumor_bam, "rb") if args.label_tumor_bam else None
    normal_src = pysam.AlignmentFile(args.label_normal_bam, "rb") if args.label_normal_bam else None

    total_records = total_usable = skipped = 0
    for region in regions:
        if store.is_complete(region.id) and not args.force:
            LOGGER.info("region %s already complete, skipping", region.id)
            skipped += 1
            continue

        started = time.time()
        labels = label_region(tumor_src, normal_src, region) if tumor_src else None
        records = extract_region(
            bam,
            region,
            candidates,
            config,
            sample_id=args.sample_id,
            dilution=args.dilution,
            tool_versions=version_string,
            input_manifest_id=manifest_id,
            source_labels=labels,
        )
        written = store.write_partition(region.id, records)
        usable = sum(1 for r in records if r.usable)
        total_records += written
        total_usable += usable
        LOGGER.info(
            "region %s: %d records, %d usable, %.1fs",
            region.id, written, usable, time.time() - started,
        )

    bam.close()
    for handle in (tumor_src, normal_src):
        if handle is not None:
            handle.close()

    LOGGER.info(
        "done: %d records, %d usable, %d region(s) skipped -> %s",
        total_records, total_usable, skipped, args.outdir,
    )
    print(f"[extract_joint_molecules] {total_records} records, {total_usable} usable -> {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
