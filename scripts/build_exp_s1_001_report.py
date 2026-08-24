#!/usr/bin/env python3
"""Build the EXP-S1-001 figure report — the falsification, made visible.

Three figures, every value computed from the measured TSVs at build time, so the report cannot
drift from the data and needs no external assets. Nothing is hand-entered.

    python3 scripts/build_exp_s1_001_report.py
    python3 scripts/build_exp_s1_001_report.py -o /tmp/report.html
"""

from __future__ import annotations

import argparse
import html as html_lib
import importlib.util
import math
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("blr", REPO / "scripts" / "build_linkage_report.py")
_blr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_blr)
text, rect, figure, STYLE = _blr.text, _blr.rect, _blr.figure, _blr.STYLE
INK, MUTED, LINE, GREY = _blr.INK, _blr.MUTED, _blr.LINE, _blr.GREY

# Two categorical hues, validated with the dataviz palette checker (light, surface #fffdf8):
# lightness band PASS, chroma floor PASS, CVD separation PASS (dE 8.2 protan, 21.2 tritan),
# normal-vision floor PASS (17.7), contrast PASS. The project's original #1f5c4e fails the
# chroma floor, so it is not reused here.
GERM, GERM_SOFT = "#007a5e", "#d8ebe5"
SOMA, SOMA_SOFT = "#a06400", "#f7ebc7"

EXP = REPO / "research/surveys/long-read-tumor-only-mrd/exp-s1-001"
FEATURES = EXP / "results/features_chr1.tsv"
LABELS = EXP / "results/labels_chr1.tsv"
DEFAULT_OUT = REPO / "outputs/accepted/reports/2026-08-24-exp-s1-001.html"

MIN_HAP_READS = 10                     # pre-registered, 08 section 4
EDGES = [0, .15, .30, .45, .60, .75, .85, .95, 1.01]   # the bins 03_score.py reports
OP = 0.90                              # pre-registered operating point


# --------------------------------------------------------------------------- data
def _read_tsv(path):
    with path.open() as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            yield dict(zip(header, line.rstrip("\n").split("\t")))


def load():
    """Join features to labels and apply the pre-registered inclusion rule.

    Returns (retained, excluded, totals). `retained` is what the primary comparison scored;
    `excluded` carries the reason, which is the second half of the result.
    """
    labels = {int(r["pos"]): r for r in _read_tsv(LABELS)}
    retained, excluded = [], []
    n_features = n_labelled_in_hc = 0
    for feat in _read_tsv(FEATURES):
        n_features += 1
        lab = labels.get(int(feat["pos"]))
        if lab is None:
            continue
        if lab["in_hc"] != "1" or lab["label"] not in ("germline", "somatic"):
            continue
        n_labelled_in_hc += 1
        n1, n2 = int(feat["n_hp1"]), int(feat["n_hp2"])
        row = dict(label=lab["label"], vaf=float(feat["vaf"]), n_hp1=n1, n_hp2=n2,
                   hapvaf=float(feat["hapvaf"]) if feat["hapvaf"] != "nan" else float("nan"))
        if n1 >= MIN_HAP_READS and n2 >= MIN_HAP_READS and not math.isnan(row["hapvaf"]):
            retained.append(row)
        else:
            row["min_hap"] = min(n1, n2)
            excluded.append(row)
    return retained, excluded, dict(features=n_features, labelled_in_hc=n_labelled_in_hc)


def auc(scores, positive):
    """Rank-based AUC with mid-ranks for ties — the same estimator 03_score.py used."""
    pairs = sorted(zip(scores, positive))
    ranks, i = [0.0] * len(pairs), 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2.0 + 1.0
        i = j + 1
    n1 = sum(p for _, p in pairs)
    n0 = len(pairs) - n1
    s1 = sum(r for r, (_, p) in zip(ranks, pairs) if p)
    return (s1 - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def roc_points(scores, positive):
    """(FPR, TPR) walked down the score order. Positive class = germline."""
    order = sorted(zip(scores, positive), key=lambda t: -t[0])
    n1 = sum(p for _, p in order)
    n0 = len(order) - n1
    pts, tp, fp, i = [(0.0, 0.0)], 0, 0, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and order[j + 1][0] == order[i][0]:
            j += 1
        for k in range(i, j + 1):
            tp += order[k][1]
            fp += 1 - order[k][1]
        pts.append((fp / n0, tp / n1))
        i = j + 1
    return pts


def binned(rows, key):
    """Share of each class falling in each bin, as a percentage of that class."""
    out = {}
    for cls in ("germline", "somatic"):
        sel = [r for r in rows if r["label"] == cls]
        counts = [sum(1 for r in sel if lo <= r[key] < hi) for lo, hi in zip(EDGES[:-1], EDGES[1:])]
        out[cls] = dict(counts=counts, n=len(sel),
                        pct=[100.0 * c / len(sel) for c in counts])
    return out


# --------------------------------------------------------------------------- layout audit
_TEXT_RE = re.compile(
    r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="(\d+)"[^>]*text-anchor="(\w+)"([^>]*)>([^<]*)</text>')
_ROT_RE = re.compile(r'rotate\(-90')


def audit(svg: str, viewbox: str, name: str):
    """Assert every label sits inside the viewBox and no two labels overlap.

    Checking anchor points alone misses overflowing labels, so each label's box is reconstructed
    from its font size and string length (0.55em mean advance for this sans stack).
    """
    _, _, vw, vh = (float(v) for v in viewbox.split())
    boxes = []
    for x, y, size, anchor, attrs, content in _TEXT_RE.findall(svg):
        x, y, size = float(x), float(y), float(size)
        w = 0.55 * size * len(html_lib.unescape(content))
        if _ROT_RE.search(attrs):
            # Rotated -90 about its own anchor: the run is vertical, so width and height swap.
            y0 = {"start": y, "middle": y - w / 2, "end": y - w}[anchor]
            boxes.append((x - size * 0.8, y0, x + size * 0.25, y0 + w, content))
            continue
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        boxes.append((x0, y - size * 0.8, x0 + w, y + size * 0.25, content))
    problems = []
    for x0, y0, x1, y1, content in boxes:
        if x0 < -0.5 or y0 < -0.5 or x1 > vw + 0.5 or y1 > vh + 0.5:
            problems.append(f"{name}: '{content}' outside viewBox ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
    for a in range(len(boxes)):
        for b in range(a + 1, len(boxes)):
            ax0, ay0, ax1, ay1, ac = boxes[a]
            bx0, by0, bx1, by1, bc = boxes[b]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                problems.append(f"{name}: '{ac}' overlaps '{bc}'")
    if problems:
        raise SystemExit("layout audit failed:\n  " + "\n  ".join(problems))
    return len(boxes)


# --------------------------------------------------------------------------- figures
def fig_distributions(retained):
    """The mechanism made visible: where each class sits under each statistic."""
    W, PANEL_H, GAP = 760, 208, 54
    left, right, top = 46, 14, 30
    plot_w = W - left - right
    slot = plot_w / len(EDGES[:-1])
    parts = []

    for panel, (key, title) in enumerate((
            ("vaf", "Whole-locus allele fraction — the baseline"),
            ("hapvaf", "Allele fraction within one haplotype — the tested statistic"))):
        oy = panel * (PANEL_H + GAP)
        data = binned(retained, key)
        top_pct = max(max(data["germline"]["pct"]), max(data["somatic"]["pct"]))
        scale = (PANEL_H - top - 30) / (top_pct * 1.12)
        base = oy + PANEL_H - 30
        parts.append(text(0, oy + 12, title, size=12, fill=INK, weight="600"))
        # recessive grid
        for g in range(0, int(top_pct * 1.12) + 1, 20):
            y = base - g * scale
            parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" '
                         f'stroke="{LINE}" stroke-width="1"/>')
            parts.append(text(left - 6, y + 3.5, f"{g}%", size=9, anchor="end"))
        parts.append(f'<line x1="{left}" y1="{base}" x2="{W - right}" y2="{base}" '
                     f'stroke="{GREY}" stroke-width="1"/>')
        for i, (lo, hi) in enumerate(zip(EDGES[:-1], EDGES[1:])):
            x = left + i * slot
            bw = (slot - 12) / 2 - 1          # 2px surface gap between adjacent fills
            for k, (cls, hue) in enumerate((("germline", GERM), ("somatic", SOMA))):
                pct = data[cls]["pct"][i]
                h = pct * scale
                parts.append(rect(x + 6 + k * (bw + 2), base - h, bw, h, hue, rx=4))
            parts.append(text(x + slot / 2, base + 14, f"{lo:.2f}–{min(hi, 1.0):.2f}",
                              size=9, anchor="middle"))
        if panel == 1:      # direct labels only where the story is, not on every bar
            for cls, hue in (("germline", GERM), ("somatic", SOMA)):
                pct = data[cls]["pct"][-1]
                x = left + 7 * slot + slot / 2
                dy = -6 if cls == "germline" else -20
                parts.append(text(x, base - pct * scale + dy, f"{pct:.1f}%",
                                  size=11, fill=hue, anchor="middle", weight="600"))

    ng = sum(1 for r in retained if r["label"] == "germline")
    ns = len(retained) - ng
    ly = 2 * (PANEL_H + GAP) - 18
    for k, (cls, hue, n) in enumerate((("germline", GERM, ng), ("somatic", SOMA, ns))):
        x = left + k * 200
        parts.append(rect(x, ly - 9, 11, 11, hue, rx=3))
        parts.append(text(x + 17, ly, f"{cls} (n={n:,})", size=11, fill=MUTED))
    h = 2 * (PANEL_H + GAP)
    vb = f"0 0 {W} {h}"
    return "".join(parts), vb


def fig_roc(retained):
    """The primary metric, drawn. One axis, two curves, chance as a reference."""
    W, H, S = 760, 400, 330
    ox, oy = 60, 24
    parts, y = [], [1 if r["label"] == "germline" else 0 for r in retained]
    parts.append(f'<line x1="{ox}" y1="{oy + S}" x2="{ox + S}" y2="{oy}" stroke="{GREY}" '
                 f'stroke-width="1" stroke-dasharray="4 4"/>')
    for g in (0, 0.25, 0.5, 0.75, 1.0):
        parts.append(f'<line x1="{ox}" y1="{oy + S - g * S:.1f}" x2="{ox + S}" '
                     f'y2="{oy + S - g * S:.1f}" stroke="{LINE}" stroke-width="1"/>')
        parts.append(text(ox - 8, oy + S - g * S + 3.5, f"{g:.2f}", size=9, anchor="end"))
        parts.append(text(ox + g * S, oy + S + 15, f"{g:.2f}", size=9, anchor="middle"))
    aucs = {}
    for key, hue, name in (("vaf", SOMA, "locus VAF"),
                           ("hapvaf", GERM, "within one haplotype")):
        scores = [r[key] for r in retained]
        aucs[key] = auc(scores, y)
        pts = roc_points(scores, y)
        d = " ".join(f"{'M' if i == 0 else 'L'}{ox + fx * S:.1f},{oy + S - ty * S:.1f}"
                     for i, (fx, ty) in enumerate(pts))
        parts.append(f'<path d="{d}" fill="none" stroke="{hue}" stroke-width="2" '
                     f'stroke-linejoin="round"/>')
    parts.append(text(ox + S / 2, oy + S + 34, "false positive rate", size=11, anchor="middle"))
    parts.append(f'<text x="20" y="{oy + S / 2}" font-size="11" fill="{MUTED}" '
                 f'text-anchor="middle" transform="rotate(-90 20 {oy + S / 2})" '
                 f'font-family="var(--sans)">true positive rate</text>')
    lx = ox + S + 34
    parts.append(text(lx, oy + 14, "positive class = germline", size=11, fill=INK, weight="600"))
    for k, (key, hue, name) in enumerate((("hapvaf", GERM, "within one haplotype"),
                                          ("vaf", SOMA, "locus VAF"))):
        ly = oy + 44 + k * 46
        parts.append(rect(lx, ly - 9, 11, 11, hue, rx=3))
        parts.append(text(lx + 17, ly, name, size=11, fill=MUTED))
        parts.append(text(lx + 17, ly + 17, f"AUC {aucs[key]:.4f}", size=13, fill=INK, weight="600"))
    parts.append(text(lx, oy + 152, f"ΔAUC {aucs['hapvaf'] - aucs['vaf']:+.4f}",
                      size=13, fill=INK, weight="600"))
    parts.append(text(lx, oy + 170, "H0 was ΔAUC ≤ 0.02,", size=10))
    parts.append(text(lx, oy + 184, "fixed before the run.", size=10))
    parts.append(text(lx, oy + 202, "H0 not rejected.", size=10, fill=INK, weight="600"))
    parts.append(text(lx, oy + 226, "chance line dashed", size=9))
    return "".join(parts), f"0 0 {W} {H}", aucs


def fig_funnel(retained, excluded, totals):
    """Why the comparison never saw the regions the statistic was aimed at."""
    W, H = 760, 236
    left, bar_h = 0, 26
    zero_hap = sum(1 for r in excluded if r["min_hap"] == 0)
    thin_hap = len(excluded) - zero_hap
    rows = [
        ("candidates with features on chr1", totals["features"], GREY),
        ("labelled and inside the SEQC2 high-confidence region", totals["labelled_in_hc"], GREY),
        ("scored — ≥10 reads on BOTH haplotypes", len(retained), GERM),
        ("excluded — 1–9 reads on the thinner haplotype", thin_hap, SOMA),
        ("excluded — ZERO reads on one haplotype", zero_hap, SOMA),
    ]
    top = max(n for _, n, _ in rows)
    scale = 420 / top
    parts = []
    for i, (label, n, hue) in enumerate(rows):
        y = 16 + i * (bar_h + 18)
        parts.append(rect(left, y, n * scale, bar_h, hue, rx=4))
        parts.append(text(left + n * scale + 10, y + bar_h / 2 + 4,
                          f"{n:,}   ({100 * n / totals['features']:.1f}%)",
                          size=11, fill=INK, weight="600"))
        parts.append(text(left + 2, y - 5, label, size=10))
    return "".join(parts), f"0 0 {W} {H}", dict(zero=zero_hap, thin=thin_hap)


# --------------------------------------------------------------------------- build
def build(out: Path) -> Path:
    retained, excluded, totals = load()
    ng = sum(1 for r in retained if r["label"] == "germline")
    ns = len(retained) - ng

    svg1, vb1 = fig_distributions(retained)
    svg2, vb2, aucs = fig_roc(retained)
    svg3, vb3, funnel = fig_funnel(retained, excluded, totals)
    for svg, vb, name in ((svg1, vb1, "fig1"), (svg2, vb2, "fig2"), (svg3, vb3, "fig3")):
        audit(svg, vb, name)

    d = aucs["hapvaf"] - aucs["vaf"]
    hb = binned(retained, "hapvaf")
    vb_ = binned(retained, "vaf")
    g_top = hb["germline"]["pct"][-1]
    s_top = hb["somatic"]["pct"][-1]
    op_g = sum(1 for r in retained if r["label"] == "germline" and r["hapvaf"] >= OP)
    op_s = sum(1 for r in retained if r["label"] == "somatic" and r["hapvaf"] >= OP)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EXP-S1-001 — a falsification, in three figures</title>
<style>{STYLE}</style></head><body><div class="wrap">

<header>
  <p class="kicker">ONT MRD · research report · 2026-08-24</p>
  <h1>A statistic that should have separated two classes, and did not</h1>
  <p class="lead">EXP-S1-001 asked whether allele fraction computed <em>within a single
  haplotype</em> separates inherited from tumor-acquired variants in a long-read tumor-only
  candidate set better than whole-locus allele fraction does. On chr1 of the pure HCC1395 tumor it
  does not, and the pre-registered failure criterion — fixed in <code>08</code> §10–§11 before the
  run — was met. The three figures below are the whole result.</p>
</header>

<p><strong>The criterion, stated before the numbers.</strong> H0 was ΔAUC ≤ 0.02 against
whole-locus VAF on the identical retained candidate set. Inclusion was fixed in advance: inside a
SEQC2 high-confidence region, carrying a germline or somatic label, and at least
{MIN_HAP_READS} reads assigned to each of the two haplotypes. The single reported operating point
was fixed at {OP:.2f} from the mechanism, not tuned on the data. Features were written to disk
before any label file existed.</p>

{figure(1, "Where each class sits under each statistic",
        f"Share of each class per bin, as a percentage of that class — germline n={ng:,}, "
        f"somatic n={ns:,}, so the two panels are comparable despite unequal class sizes. "
        f"The predicted direction is present: {g_top:.1f}% of germline candidates land in the "
        f"top bin under the haplotype-conditioned statistic. It is not discriminating, because "
        f"{s_top:.1f}% of somatic candidates land there too. The baseline panel shows what is "
        f"lost — under whole-locus VAF the two classes peak in different bins.",
        svg1, vb1)}

{figure(2, "The primary comparison",
        f"AUC {aucs['vaf']:.4f} for whole-locus VAF against {aucs['hapvaf']:.4f} for the "
        f"haplotype-conditioned statistic, ΔAUC {d:+.4f}. Conditioning on the ALT-carrying "
        f"haplotype does not add discrimination; it removes some. At the pre-fixed operating "
        f"point it strips {op_g}/{ng} germline candidates ({100 * op_g / ng:.1f}%) while "
        f"discarding {op_s}/{ns} somatic ones ({100 * op_s / ns:.1f}%).",
        svg2, vb2)}

{figure(3, "The candidates the comparison never saw",
        f"The statistic needs two haplotypes to compare, so the inclusion rule removes the "
        f"positions that have lost one. Of {totals['labelled_in_hc']:,} labelled in-region "
        f"candidates, {funnel['zero'] + funnel['thin']:,} never reach the comparison and "
        f"{funnel['zero']:,} have zero reads on one haplotype. Those are the hemizygous and "
        f"loss-of-heterozygosity regions — where germline contamination is worst. The method is "
        f"defined where the problem is mild and undefined where it is severe.",
        svg3, vb3)}

<h2>What this does and does not establish</h2>
<ul>
  <li><strong>Established.</strong> On this material the statistic is not a germline
  discriminator. HCC1395 is a pure tumor line, so a clonal somatic variant occupies one haplotype
  exactly as an inherited heterozygote does, and both saturate at the same ceiling.</li>
  <li><strong>Established, and unwelcome.</strong> The baseline is stronger than assumed — plain
  locus VAF carries AUC {aucs['vaf']:.2f} here. Any future proposal has to beat that, not 0.5.</li>
  <li><strong>Not established.</strong> That haplotype information is useless for tumor-only
  calling in general, or at lower tumor purity. This material cannot test the low-purity case:
  at 0.01% tumor fraction there is no tumor read population at a locus to assign a haplotype
  to.</li>
  <li><strong>Not established.</strong> That the germline contamination in the candidate set
  cannot be removed by some other within-sample statistic. Only that this one does not remove
  it.</li>
</ul>

<footer>
  Generated from measured files by <code>scripts/build_exp_s1_001_report.py</code>; every value
  above is computed at build time from <code>features_chr1.tsv</code> and
  <code>labels_chr1.tsv</code>. Sources: EXP-S1-001, FIND-0004, EV-0019, LOG-2026-08-24.
  Germline labels are ≥2 ALT-supporting reads in the matched normal, an evaluation-only resource
  read at labelling and nowhere else; somatic labels are SEQC2 high-confidence sSNV. One
  chromosome of one sample. Observations are what the artifacts showed; the readings above them
  are the researcher's interpretation.
</footer>

</div></body></html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    path = build(args.output.resolve())
    print(f"wrote {path.relative_to(REPO) if REPO in path.parents else path} "
          f"({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
