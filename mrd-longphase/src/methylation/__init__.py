"""Native methylation evidence from ONT MM/ML tags.

5mC and 5hmC are kept separate throughout — never summed into one "methylation" number.
See ``docs/research/05_claim_boundaries.md``.
"""
from .mod_bases import (
    CpGEvidence,
    MOD_5HMC,
    MOD_5MC,
    read_cpg_evidence,
    summarize_calls,
)

__all__ = [
    "CpGEvidence",
    "MOD_5MC",
    "MOD_5HMC",
    "read_cpg_evidence",
    "summarize_calls",
]
