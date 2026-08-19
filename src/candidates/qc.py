"""Phase 1 QC characterization of a PASS SNV candidate table.

Characterization only (no filtering). numpy + matplotlib; reads the TSV written by
``extract.write_candidate_tsv``. Each plot function returns the output path.
"""
from __future__ import annotations
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHROM_ORDER = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
STAT_ORDER = [
    "n_candidates",
    "depth_median", "depth_q25", "depth_q75", "depth_iqr", "depth_p05", "depth_p95",
    "vaf_median", "vaf_q25", "vaf_q75", "vaf_iqr", "vaf_p05", "vaf_p95",
    "alt_count_median", "alt_count_q25", "alt_count_q75", "alt_count_iqr", "alt_count_p05", "alt_count_p95",
    "qual_median", "qual_q25", "qual_q75",
    "corr_vaf_depth", "corr_alt_depth", "corr_alt_vaf",
    "vaf_lt_0.05_pct", "vaf_lt_0.10_pct", "vaf_het_like_0.40_0.60_pct", "vaf_hom_like_gt_0.90_pct",
    "depth_lt_10_pct", "depth_gt_3x_median_pct",
    "per_chrom",
]


def load_table(tsv_path: str) -> dict:
    """Load candidate TSV into column arrays."""
    chrom, qual, depth, refc, altc, vaf = [], [], [], [], [], []
    with open(tsv_path) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        idx = {c: i for i, c in enumerate(header)}
        for line in fh:
            c = line.rstrip("\n").split("\t")
            chrom.append(c[idx["chrom"]])
            qual.append(_f(c[idx["qual"]]))
            depth.append(_i(c[idx["depth"]]))
            refc.append(_i(c[idx["ref_count"]]))
            altc.append(_i(c[idx["alt_count"]]))
            vaf.append(_f(c[idx["vaf"]]))
    return dict(chrom=np.array(chrom), qual=np.array(qual, float),
               depth=np.array(depth, float), ref_count=np.array(refc, float),
               alt_count=np.array(altc, float), vaf=np.array(vaf, float))


def _f(x):
    try: return float(x)
    except (ValueError, TypeError): return np.nan


def _i(x):
    try: return int(x)
    except (ValueError, TypeError): return np.nan


def compute_stats(cols: dict) -> dict:
    vaf, depth, chrom = cols["vaf"], cols["depth"], cols["chrom"]
    alt_count, qual = cols["alt_count"], cols["qual"]
    n = len(vaf)
    v = _clean(vaf)
    d = _clean(depth)
    a = _clean(alt_count)
    q = _clean(qual)

    def pct(mask):
        return 100.0 * np.nansum(mask) / n if n else float("nan")

    stats = {
        "n_candidates": n,
        "depth_median": _round_or_nan(_quantile(d, 50), digits=0),
        "depth_q25": _round_or_nan(_quantile(d, 25), digits=0),
        "depth_q75": _round_or_nan(_quantile(d, 75), digits=0),
        "depth_iqr": _round_or_nan(_iqr(d), digits=0),
        "depth_p05": _round_or_nan(_quantile(d, 5), digits=0),
        "depth_p95": _round_or_nan(_quantile(d, 95), digits=0),
        "vaf_median": _round_or_nan(_quantile(v, 50)),
        "vaf_q25": _round_or_nan(_quantile(v, 25)),
        "vaf_q75": _round_or_nan(_quantile(v, 75)),
        "vaf_iqr": _round_or_nan(_iqr(v)),
        "vaf_p05": _round_or_nan(_quantile(v, 5)),
        "vaf_p95": _round_or_nan(_quantile(v, 95)),
        "alt_count_median": _round_or_nan(_quantile(a, 50), digits=0),
        "alt_count_q25": _round_or_nan(_quantile(a, 25), digits=0),
        "alt_count_q75": _round_or_nan(_quantile(a, 75), digits=0),
        "alt_count_iqr": _round_or_nan(_iqr(a), digits=0),
        "alt_count_p05": _round_or_nan(_quantile(a, 5), digits=0),
        "alt_count_p95": _round_or_nan(_quantile(a, 95), digits=0),
        "qual_median": _round_or_nan(_quantile(q, 50)),
        "qual_q25": _round_or_nan(_quantile(q, 25)),
        "qual_q75": _round_or_nan(_quantile(q, 75)),
        "corr_vaf_depth": _round_or_nan(_corr(vaf, depth)),
        "corr_alt_depth": _round_or_nan(_corr(alt_count, depth)),
        "corr_alt_vaf": _round_or_nan(_corr(alt_count, vaf)),
        "vaf_lt_0.05_pct": round(float(pct(vaf < 0.05)), 1),
        "vaf_lt_0.10_pct": round(float(pct(vaf < 0.10)), 1),
        "vaf_het_like_0.40_0.60_pct": round(float(pct((vaf >= 0.40) & (vaf <= 0.60))), 1),
        "vaf_hom_like_gt_0.90_pct": round(float(pct(vaf > 0.90)), 1),
        "depth_lt_10_pct": round(float(pct(depth < 10)), 1),
        "depth_gt_3x_median_pct": round(float(pct(depth > 3 * np.nanmedian(depth))), 1) if len(d) else float("nan"),
    }
    stats["per_chrom"] = {k: int((chrom == k).sum()) for k in CHROM_ORDER}
    return stats


def write_stats(stats: dict, path: str):
    with open(path, "w") as f:
        for k in STAT_ORDER:
            if k not in stats:
                continue
            v = stats[k]
            if k == "per_chrom":
                f.write("per_chrom\t" + " ".join(f"{c.replace('chr','')}={n}" for c, n in v.items()) + "\n")
            else:
                f.write(f"{k}\t{v}\n")


def write_analysis_table(cols: dict, out_path: str):
    """Write a candidate-level Phase 1 analysis table with derived support metrics."""
    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow([
            "chrom", "qual", "depth", "ref_count", "alt_count", "vaf",
            "alt_fraction_from_counts", "depth_minus_allelic_counts",
            "depth_bin", "vaf_bin", "alt_support_bin",
        ])
        for i in range(len(cols["chrom"])):
            depth = cols["depth"][i]
            ref_count = cols["ref_count"][i]
            alt_count = cols["alt_count"][i]
            vaf = cols["vaf"][i]
            writer.writerow([
                cols["chrom"][i],
                _fmt_num(cols["qual"][i]),
                _fmt_num(depth),
                _fmt_num(ref_count),
                _fmt_num(alt_count),
                _fmt_num(vaf),
                _fmt_num(_safe_fraction(alt_count, ref_count, alt_count)),
                _fmt_num(_safe_difference(depth, ref_count, alt_count)),
                _depth_bin(depth),
                _vaf_bin(vaf),
                _alt_support_bin(alt_count),
            ])


def plot_vaf(cols, out):
    v = cols["vaf"][~np.isnan(cols["vaf"])]
    plt.figure(figsize=(5.2, 3.4))
    plt.hist(v, bins=50, color="#2b8cbe", edgecolor="white")
    plt.xlabel("VAF (FORMAT/AF)"); plt.ylabel("candidate SNVs")
    plt.title(f"VAF distribution (PASS SNVs, n={len(v)})")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def plot_depth(cols, out):
    d = cols["depth"][~np.isnan(cols["depth"])]
    dcap = np.minimum(d, np.percentile(d, 99.5))
    plt.figure(figsize=(5.2, 3.4))
    plt.hist(dcap, bins=60, color="#31a354", edgecolor="white")
    plt.xlabel("Depth (FORMAT/DP, capped p99.5)"); plt.ylabel("candidate SNVs")
    plt.title(f"Depth distribution (median={int(np.median(d))}x)")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def plot_alt_support(cols, out):
    a = cols["alt_count"][~np.isnan(cols["alt_count"])]
    acap = np.minimum(a, np.percentile(a, 99.5))
    plt.figure(figsize=(5.2, 3.4))
    plt.hist(acap, bins=60, color="#dd8452", edgecolor="white")
    plt.xlabel("ALT-supporting reads (FORMAT/AD[1], capped p99.5)"); plt.ylabel("candidate SNVs")
    plt.title(f"ALT-support distribution (median={int(np.median(a))} reads)")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def plot_vaf_vs_depth(cols, out):
    d, v = cols["depth"], cols["vaf"]
    m = ~np.isnan(d) & ~np.isnan(v)
    plt.figure(figsize=(5.2, 3.8))
    plt.hexbin(d[m], v[m], gridsize=60, bins="log", cmap="viridis",
               extent=(0, np.percentile(d[m], 99), 0, 1))
    plt.colorbar(label="log10 count"); plt.xlabel("Depth"); plt.ylabel("VAF")
    plt.title("VAF vs depth (PASS SNVs)")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def plot_alt_vs_depth(cols, out):
    d, a = cols["depth"], cols["alt_count"]
    m = ~np.isnan(d) & ~np.isnan(a)
    plt.figure(figsize=(5.2, 3.8))
    plt.hexbin(d[m], a[m], gridsize=60, bins="log", cmap="magma",
               extent=(0, np.percentile(d[m], 99), 0, np.percentile(a[m], 99)))
    plt.colorbar(label="log10 count"); plt.xlabel("Depth"); plt.ylabel("ALT-supporting reads")
    plt.title("ALT support vs depth (PASS SNVs)")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def plot_per_chrom(cols, out):
    chrom = cols["chrom"]
    counts = [int((chrom == k).sum()) for k in CHROM_ORDER]
    plt.figure(figsize=(7.5, 3.4))
    plt.bar(range(len(CHROM_ORDER)), counts, color="#756bb1")
    plt.xticks(range(len(CHROM_ORDER)), [k.replace("chr", "") for k in CHROM_ORDER], fontsize=7)
    plt.xlabel("chromosome"); plt.ylabel("candidate SNVs"); plt.title("Candidate SNVs per chromosome")
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close(); return out


def _clean(arr):
    arr = np.asarray(arr, float)
    return arr[~np.isnan(arr)]


def _quantile(arr, pct):
    arr = _clean(arr)
    if not len(arr):
        return np.nan
    return float(np.percentile(arr, pct))


def _iqr(arr):
    arr = _clean(arr)
    if not len(arr):
        return np.nan
    return float(np.percentile(arr, 75) - np.percentile(arr, 25))


def _corr(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    if np.sum(mask) < 2:
        return np.nan
    return float(np.corrcoef(x[mask], y[mask])[0, 1])


def _round_or_nan(value, digits=3):
    if np.isnan(value):
        return "nan"
    rounded = round(float(value), digits)
    return int(rounded) if digits == 0 else rounded


def _fmt_num(value):
    if isinstance(value, str):
        return value
    if value is None or np.isnan(value):
        return ""
    intval = int(value)
    if float(value) == float(intval):
        return str(intval)
    return f"{float(value):.4f}"


def _safe_fraction(numer, left, right):
    vals = [left, right]
    if any(np.isnan(v) for v in vals):
        return np.nan
    denom = left + right
    if denom == 0 or np.isnan(numer):
        return np.nan
    return numer / denom


def _safe_difference(depth, ref_count, alt_count):
    vals = [depth, ref_count, alt_count]
    if any(np.isnan(v) for v in vals):
        return np.nan
    return depth - (ref_count + alt_count)


def _depth_bin(depth):
    if np.isnan(depth):
        return "missing"
    if depth < 30:
        return "lt30"
    if depth < 60:
        return "30to59"
    if depth < 100:
        return "60to99"
    if depth < 200:
        return "100to199"
    return "ge200"


def _vaf_bin(vaf):
    if np.isnan(vaf):
        return "missing"
    if vaf < 0.10:
        return "lt0.10"
    if vaf < 0.30:
        return "0.10to0.29"
    if vaf < 0.70:
        return "0.30to0.69"
    if vaf < 0.90:
        return "0.70to0.89"
    return "ge0.90"


def _alt_support_bin(alt_count):
    if np.isnan(alt_count):
        return "missing"
    if alt_count < 5:
        return "lt5"
    if alt_count < 10:
        return "5to9"
    if alt_count < 20:
        return "10to19"
    if alt_count < 40:
        return "20to39"
    return "ge40"
