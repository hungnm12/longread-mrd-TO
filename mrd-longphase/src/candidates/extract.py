"""Extract a tumor-only PASS SNV candidate table from a ClairS-TO VCF.

Reusable library code (no CLI side effects). ClairS-TO tumor-only FORMAT is
``GT:GQ:DP:AF:AD:AU:CU:GU:TU`` — we read the derived per-variant fields:

- ``depth``      = FORMAT/DP  (read depth in the tumor BAM)
- ``ref_count``  = FORMAT/AD[0], ``alt_count`` = FORMAT/AD[1]
- ``vaf``        = FORMAT/AF   (ClairS-TO estimated tumor allele fraction;
                                note AD[0]+AD[1] need not equal DP)
- ``qual``       = VCF QUAL    (model confidence)

Nothing is invented: a field missing in the record is written as empty.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterator, Optional
import pysam

CANDIDATE_FIELDS = [
    "chrom", "pos", "ref", "alt", "filter", "qual",
    "depth", "ref_count", "alt_count", "vaf",
]


@dataclass
class Candidate:
    chrom: str
    pos: int
    ref: str
    alt: str
    filter: str
    qual: Optional[float]
    depth: Optional[int]
    ref_count: Optional[int]
    alt_count: Optional[int]
    vaf: Optional[float]


def _fmt(sample, key):
    return sample[key] if key in sample else None


def iter_pass_snvs(vcf_path: str) -> Iterator[Candidate]:
    """Yield PASS single-base SNV candidates from a ClairS-TO VCF."""
    vf = pysam.VariantFile(vcf_path)
    for rec in vf:
        if rec.alts is None or len(rec.alts) != 1:
            continue
        ref, alt = rec.ref, rec.alts[0]
        if len(ref) != 1 or len(alt) != 1:
            continue  # SNV only
        if "PASS" not in set(rec.filter.keys()):
            continue
        smp = rec.samples[0] if len(rec.samples) else {}
        ad = _fmt(smp, "AD")
        ref_c = ad[0] if ad and len(ad) >= 1 else None
        alt_c = ad[1] if ad and len(ad) >= 2 else None
        af = _fmt(smp, "AF")
        af = af[0] if isinstance(af, tuple) else af
        yield Candidate(
            chrom=rec.chrom, pos=rec.pos, ref=ref, alt=alt,
            filter=";".join(rec.filter.keys()) or "PASS",
            qual=round(rec.qual, 4) if rec.qual is not None else None,
            depth=_fmt(smp, "DP"), ref_count=ref_c, alt_count=alt_c,
            vaf=round(af, 4) if af is not None else None,
        )


def write_candidate_tsv(vcf_path: str, out_tsv: str) -> int:
    """Write the PASS SNV candidate table; return the row count."""
    n = 0
    with open(out_tsv, "w") as fh:
        fh.write("\t".join(CANDIDATE_FIELDS) + "\n")
        for c in iter_pass_snvs(vcf_path):
            d = asdict(c)
            fh.write("\t".join("" if d[k] is None else str(d[k]) for k in CANDIDATE_FIELDS) + "\n")
            n += 1
    return n


def summarize_counts(vcf_path: str) -> dict:
    """Total calls, PASS calls, PASS SNVs, PASS indels — for the summary table."""
    total = pass_calls = pass_snv = pass_indel = 0
    vf = pysam.VariantFile(vcf_path)
    for rec in vf:
        total += 1
        if "PASS" not in set(rec.filter.keys()):
            continue
        pass_calls += 1
        alt = rec.alts[0] if rec.alts else ""
        if len(rec.ref) == 1 and len(alt) == 1:
            pass_snv += 1
        else:
            pass_indel += 1
    return {
        "total_calls": total,
        "pass_calls": pass_calls,
        "pass_snvs": pass_snv,
        "pass_indels": pass_indel,
    }
