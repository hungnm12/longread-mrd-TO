"""Genomic regions — the unit of partitioning, resumability, and leakage-safe splitting.

A ``Region`` is a half-open interval in 0-based coordinates (BED convention). Candidate
positions arriving from VCFs are 1-based; conversion happens at the boundary, once, in
``src.joint_evidence.candidates``.

``region_id`` is the single source of truth for partition naming. It is used as
* the output filename stem (``chr1_1000000_2000000.tsv.gz``),
* the resumability marker name,
* the ``region_id`` column in every joint-molecule record,
* the grouping key that Phase 5 splits on so that reads from one region never cross a
  train/test boundary.

Because all four uses share one function, a region can never be named inconsistently
between the data and the split.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List


@dataclass(frozen=True, order=True)
class Region:
    """A half-open, 0-based genomic interval."""

    chrom: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"region start must be >= 0, got {self.start}")
        if self.end <= self.start:
            raise ValueError(f"region end must exceed start, got {self.start}-{self.end}")

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def id(self) -> str:
        return region_id(self.chrom, self.start, self.end)

    def __str__(self) -> str:  # samtools-style, 1-based inclusive
        return f"{self.chrom}:{self.start + 1}-{self.end}"


def region_id(chrom: str, start: int, end: int) -> str:
    """Stable partition identifier. Filename-safe, sortable within a contig."""
    return f"{chrom}_{start}_{end}"


def parse_region(spec: str) -> Region:
    """Parse ``chr1:1000-2000`` (1-based inclusive) or ``chr1`` into a Region.

    A bare contig name is not resolvable to an end coordinate here — callers that allow
    it must supply contig lengths and use :func:`partition_contig` instead.
    """
    spec = spec.strip()
    if ":" not in spec:
        raise ValueError(
            f"region {spec!r} has no coordinates; use partition_contig() for whole contigs"
        )
    chrom, _, coords = spec.partition(":")
    start_s, _, end_s = coords.partition("-")
    if not end_s:
        raise ValueError(f"region {spec!r} must be chrom:start-end")
    start = int(start_s.replace(",", ""))
    end = int(end_s.replace(",", ""))
    if start < 1:
        raise ValueError(f"1-based region start must be >= 1, got {start}")
    return Region(chrom, start - 1, end)


def read_region_bed(path: str) -> List[Region]:
    """Read regions from a BED file (0-based half-open). Blank and ``#``/``track`` lines skipped."""
    regions: List[Region] = []
    with open(path) as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith(("#", "track", "browser")):
                continue
            parts = line.split("\t") if "\t" in line else line.split()
            if len(parts) < 3:
                raise ValueError(f"{path}:{line_no}: expected at least 3 BED columns")
            regions.append(Region(parts[0], int(parts[1]), int(parts[2])))
    return regions


def partition_contig(chrom: str, length: int, chunk: int) -> Iterator[Region]:
    """Split a contig into fixed-size regions.

    The final chunk is short rather than padded, so region bounds never exceed the contig
    and ``region_id`` stays reproducible for a given (contig length, chunk size).
    """
    if chunk <= 0:
        raise ValueError(f"chunk size must be positive, got {chunk}")
    for start in range(0, length, chunk):
        yield Region(chrom, start, min(start + chunk, length))


def merge_overlapping(regions: List[Region]) -> List[Region]:
    """Sort and merge overlapping/adjacent regions.

    Needed because overlapping partitions would emit a read twice at the same candidate,
    silently double-counting the funnel.
    """
    if not regions:
        return []
    ordered = sorted(regions)
    merged = [ordered[0]]
    for region in ordered[1:]:
        last = merged[-1]
        if region.chrom == last.chrom and region.start <= last.end:
            merged[-1] = Region(last.chrom, last.start, max(last.end, region.end))
        else:
            merged.append(region)
    return merged
