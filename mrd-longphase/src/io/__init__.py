"""Region and alignment input helpers.

Side-effect free. Nothing here opens a file at import time, and nothing here knows
about the joint-molecule schema — that lives in ``src.joint_evidence``.
"""
from .regions import Region, parse_region, read_region_bed, partition_contig, region_id

__all__ = ["Region", "parse_region", "read_region_bed", "partition_contig", "region_id"]
