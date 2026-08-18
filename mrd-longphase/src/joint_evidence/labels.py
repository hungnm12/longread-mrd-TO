"""Per-read source labels — **EVALUATION ONLY**.

.. warning::

   Nothing in this module may be imported from ``src.models`` or from any feature-building
   code path. It exists to score results, never to produce them. See
   ``docs/research/05_claim_boundaries.md`` §2, and the assertions in
   ``tests/unit/test_leakage.py``.

How the labels are recoverable
------------------------------
The HCC1395 dilution BAMs carry no ``@RG`` lines, so source is not directly annotated. But
their ``@PG`` chain records how they were built::

    tumor : samtools view -s <seed>.<frac>   ← HCC1395.bam
    normal: samtools view -s <seed>.<frac>   ← HCC1395BL.bam
            samtools merge -o TF<level>_25x.rep1.bam <tumor> <normal>

Both subsampling and merging preserve read names. Membership of a read name in the tumor
source BAM versus the normal source BAM therefore recovers its origin.

Verified at ``chr1:1,000,000-1,002,000`` on ``TF1e-2_25x``: 28/28 reads assigned, 0
unassigned, 0 name collisions between the two sources (``docs/repo_audit.md`` §14.4).

Cost model
----------
Labelling is **region-scoped**: for each region, the same interval is fetched from the two
source BAMs and their read-name sets compared. Two indexed range queries per region, not a
scan of 440 GB. Sets are built per region and discarded, so memory stays bounded by
regional depth rather than by genome size.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, Set

from ..io.regions import Region

LOGGER = logging.getLogger(__name__)

LABEL_TUMOR = "tumor"
LABEL_NORMAL = "normal"
LABEL_UNASSIGNED = "unassigned"
LABEL_AMBIGUOUS = "ambiguous"


def read_names_in_region(bam, region: Region, primary_only: bool = True) -> Set[str]:
    """Collect read names overlapping a region.

    Secondary and supplementary alignments are excluded by default: they share a name with
    their primary and would inflate the set without adding a distinct molecule.
    """
    names: Set[str] = set()
    for read in bam.fetch(region.chrom, region.start, region.end):
        if primary_only and (read.is_secondary or read.is_supplementary):
            continue
        names.add(read.query_name)
    return names


def label_region(
    tumor_source_bam,
    normal_source_bam,
    region: Region,
) -> Dict[str, str]:
    """Map read name → source label for one region.

    A name found in both sources is labelled ``ambiguous`` rather than silently assigned.
    The pilot check found no collisions, but a collision at scale must be visible as a data
    problem, not resolved by an arbitrary precedence rule.
    """
    tumor_names = read_names_in_region(tumor_source_bam, region)
    normal_names = read_names_in_region(normal_source_bam, region)

    collisions = tumor_names & normal_names
    if collisions:
        LOGGER.warning(
            "region %s: %d read names present in both source BAMs; labelled %s",
            region.id,
            len(collisions),
            LABEL_AMBIGUOUS,
        )

    labels: Dict[str, str] = {}
    for name in tumor_names:
        labels[name] = LABEL_AMBIGUOUS if name in collisions else LABEL_TUMOR
    for name in normal_names:
        if name not in collisions:
            labels[name] = LABEL_NORMAL
    return labels


def labelling_stats(labels: Dict[str, str], observed_read_ids: Optional[Set[str]] = None) -> Dict:
    """Summarize label coverage for a region — reported by the funnel, never by a model.

    ``observed_read_ids`` is the set of reads actually seen in the mixture BAM. Reads in it
    that carry no label are ``unassigned``, and that count is the honest measure of whether
    the labelling mechanism holds up at scale.
    """
    counts = {LABEL_TUMOR: 0, LABEL_NORMAL: 0, LABEL_AMBIGUOUS: 0}
    for label in labels.values():
        if label in counts:
            counts[label] += 1

    stats: Dict[str, object] = dict(counts)
    if observed_read_ids is not None:
        unassigned = {rid for rid in observed_read_ids if rid not in labels}
        stats[LABEL_UNASSIGNED] = len(unassigned)
        stats["observed_reads"] = len(observed_read_ids)
        stats["assignment_rate"] = (
            (len(observed_read_ids) - len(unassigned)) / len(observed_read_ids)
            if observed_read_ids
            else float("nan")
        )
    return stats
