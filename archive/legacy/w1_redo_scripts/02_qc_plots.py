#!/usr/bin/env python3
"""Basic QC characterization of the tumor-only PASS SNV candidate set.
Reads candidate_pass_snvs.tsv, writes QC plots + a stats summary. No filtering here
(characterization only). numpy + matplotlib only (no pandas)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..")
TSV = os.path.join(OUT, "candidate_pass_snvs.tsv")

# load
chrom = []
pos, qual, depth, refc, altc, vaf = [], [], [], [], [], []
with open(TSV) as fh:
    next(fh)
    for line in fh:
        c = line.rstrip("\n").split("\t")
        chrom.append(c[0])
        qual.append(float(c[5])); depth.append(int(c[6]))
        refc.append(int(c[7])); altc.append(int(c[8]))
        try: vaf.append(float(c[9]))
        except ValueError: vaf.append(np.nan)
chrom = np.array(chrom); qual = np.array(qual); depth = np.array(depth)
refc = np.array(refc); altc = np.array(altc); vaf = np.array(vaf)
N = len(vaf)

# ---- plots ----
plt.figure(figsize=(5.2, 3.4))
plt.hist(vaf[~np.isnan(vaf)], bins=50, color="#2b8cbe", edgecolor="white")
plt.xlabel("VAF (FORMAT/AF)"); plt.ylabel("candidate SNVs"); plt.title(f"VAF distribution (PASS SNVs, n={N})")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "vaf_distribution.png"), dpi=130); plt.close()

dcap = np.minimum(depth, np.percentile(depth, 99.5))
plt.figure(figsize=(5.2, 3.4))
plt.hist(dcap, bins=60, color="#31a354", edgecolor="white")
plt.xlabel("Depth (FORMAT/DP, capped at p99.5)"); plt.ylabel("candidate SNVs"); plt.title(f"Depth distribution (median={int(np.median(depth))}x)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "depth_distribution.png"), dpi=130); plt.close()

plt.figure(figsize=(5.2, 3.8))
plt.hexbin(depth, vaf, gridsize=60, bins="log", cmap="viridis",
           extent=(0, np.percentile(depth, 99), 0, 1))
plt.colorbar(label="log10 count"); plt.xlabel("Depth"); plt.ylabel("VAF")
plt.title("VAF vs depth (PASS SNVs)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "vaf_vs_depth.png"), dpi=130); plt.close()

order = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
counts = {k: int((chrom == k).sum()) for k in order}
plt.figure(figsize=(7.5, 3.4))
plt.bar(range(len(order)), [counts[k] for k in order], color="#756bb1")
plt.xticks(range(len(order)), [k.replace("chr", "") for k in order], fontsize=7)
plt.xlabel("chromosome"); plt.ylabel("candidate SNVs"); plt.title("Candidate SNVs per chromosome")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "variants_per_chromosome.png"), dpi=130); plt.close()

# ---- stats for notes ----
def frac(mask): return 100.0 * mask.sum() / N
v = vaf[~np.isnan(vaf)]
stats = []
stats.append(f"n_candidates\t{N}")
stats.append(f"VAF median\t{np.median(v):.3f}")
stats.append(f"VAF q25/q75\t{np.percentile(v,25):.3f} / {np.percentile(v,75):.3f}")
stats.append(f"VAF<0.05 (%)\t{frac(vaf<0.05):.1f}")
stats.append(f"VAF<0.10 (%)\t{frac(vaf<0.10):.1f}")
stats.append(f"VAF 0.40-0.60 (~het-like) (%)\t{frac((vaf>=0.40)&(vaf<=0.60)):.1f}")
stats.append(f"VAF>0.90 (~hom-like) (%)\t{frac(vaf>0.90):.1f}")
stats.append(f"depth median\t{np.median(depth):.0f}")
stats.append(f"depth q25/q75\t{np.percentile(depth,25):.0f} / {np.percentile(depth,75):.0f}")
stats.append(f"depth<10 (%)\t{frac(depth<10):.1f}")
stats.append(f"depth>3x median (%)\t{frac(depth>3*np.median(depth)):.1f}")
stats.append("per_chrom\t" + " ".join(f"{k.replace('chr','')}={counts[k]}" for k in order))
with open(os.path.join(OUT, "qc_stats.txt"), "w") as f:
    f.write("\n".join(stats) + "\n")
print("\n".join(stats))
print("\nplots: vaf_distribution.png depth_distribution.png vaf_vs_depth.png variants_per_chromosome.png")
