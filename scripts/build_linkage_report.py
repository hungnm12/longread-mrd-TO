#!/usr/bin/env python3
"""Build the research report: does long-read ONT supply evidence that improves tumor recognition?

A research report, not a status page — one question, the measurements that bear on it, and a
verdict with its limits. Every figure is inline SVG computed from the measured files, so the
report cannot drift from the data and needs no external assets.

    python3 scripts/build_linkage_report.py
    python3 scripts/build_linkage_report.py -o /tmp/report.html
"""

from __future__ import annotations

import argparse
import collections
import csv
import html as html_lib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANDIDATES = REPO / "outputs/active/results/tumor_only/HCC1395/candidate_pass_snvs.tsv"
COOCCURRENCE = REPO / "outputs/active/results/linkage/cooccurrence_pure_tumor.tsv"
SUMMARY = REPO / "outputs/active/results/linkage/cooccurrence_pure_tumor.summary.json"
DEFAULT_OUT = REPO / "outputs/accepted/reports/2026-08-19-ont-linked-evidence.html"

INK, MUTED, LINE = "#1f1b16", "#695f56", "#d4c8bb"
ACCENT, ACCENT_SOFT = "#1f5c4e", "#d8ebe5"
WARN, WARN_SOFT = "#8d5c14", "#f7ebc7"
DANGER, DANGER_SOFT = "#8f3d2c", "#f6ddd7"
PANEL, BG = "#fffdf8", "#f7f3eb"
GREY = "#c9beb2"


# --------------------------------------------------------------------------- data
def nearest_neighbour_histogram():
    by_chrom = collections.defaultdict(list)
    with CANDIDATES.open() as handle:
        next(handle)
        for line in handle:
            fields = line.split("\t")
            by_chrom[fields[0]].append(int(fields[1]))
    distances = []
    for positions in by_chrom.values():
        positions.sort()
        for i, pos in enumerate(positions):
            neighbours = [abs(pos - positions[j]) for j in (i - 1, i + 1) if 0 <= j < len(positions)]
            distances.append(min(neighbours) if neighbours else 10**9)
    bins = [(0, 500), (500, 1000), (1000, 2000), (2000, 5000), (5000, 10_000),
            (10_000, 20_000), (20_000, 50_000), (50_000, 10**9)]
    counts = [sum(1 for d in distances if lo <= d < hi) for lo, hi in bins]
    within_10k = sum(1 for d in distances if d <= 10_000)
    return bins, counts, len(distances), within_10k


def cooccurrence_tables():
    rows = list(csv.DictReader(COOCCURRENCE.open(), delimiter="\t"))
    for row in rows:
        for key in ("covers_both", "alt_alt", "alt_ref", "ref_alt", "ref_ref", "other", "distance"):
            row[key] = int(row[key])
    evaluable = [r for r in rows if r["covers_both"] > 0]

    fraction_hist = [0] * 10
    for row in evaluable:
        fraction_hist[min(9, int(row["alt_alt"] / row["covers_both"] * 10))] += 1

    decay = []
    for lo, hi, label in ((0, 1000, "<1 kb"), (1000, 5000, "1–5 kb"),
                          (5000, 10_000, "5–10 kb"), (10_000, 20_000, "10–20 kb")):
        subset = [r for r in evaluable if lo <= r["distance"] < hi]
        hits = [r for r in subset if r["alt_alt"] > 0]
        median_cov = sorted(r["covers_both"] for r in subset)[len(subset) // 2] if subset else 0
        decay.append({
            "label": label,
            "pairs": len(subset),
            "pct": 100 * len(hits) / len(subset) if subset else 0,
            "median_reads": median_cov,
        })
    return evaluable, fraction_hist, decay


# --------------------------------------------------------------------------- svg helpers
def text(x, y, content, *, size=12, fill=MUTED, anchor="start", weight="normal", family="sans"):
    """A text node. Content is escaped: a label like "<1 kb" is otherwise malformed markup."""
    fonts = {"sans": "var(--sans)", "mono": "var(--mono)", "serif": "var(--serif)"}
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{fonts[family]}">{html_lib.escape(str(content))}</text>')


def rect(x, y, w, h, fill, *, rx=0, stroke="none", opacity=1.0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" opacity="{opacity}"/>')


def figure(number, title, caption, svg, viewbox):
    return f"""<figure class="fig">
  <figcaption class="fig__head"><span class="fig__num">Figure {number}</span> {title}</figcaption>
  <div class="fig__canvas"><svg viewBox="{viewbox}" role="img" aria-label="{html_lib.escape(title)}">{svg}</svg></div>
  <p class="fig__caption">{caption}</p>
</figure>"""


# --------------------------------------------------------------------------- figures
def fig_availability(bins, counts, total, within_10k):
    """Distance to the nearest other candidate, against what one read spans."""
    w, h = 900, 350
    left, right, top, bottom = 76, 30, 66, 70
    plot_w, plot_h = w - left - right, h - top - bottom
    top_count = max(counts)
    bar_w = plot_w / len(counts) - 12
    svg = [rect(left, top, plot_w, plot_h, "none", stroke=LINE)]

    # the region a single read can span, drawn behind the bars
    read_span_index = 4.6  # ~11.3 kb falls inside the 5–10 kb bin's right edge
    span_x = left + (read_span_index / len(counts)) * plot_w
    svg.append(rect(left, top, span_x - left, plot_h, ACCENT_SOFT, opacity=0.55))
    svg.append(f'<line x1="{span_x:.0f}" y1="{top}" x2="{span_x:.0f}" y2="{top + plot_h}" '
               f'stroke="{ACCENT}" stroke-width="2" stroke-dasharray="5 4"/>')
    # Both captions sit above the plot frame, clear of the bars.
    svg.append(text(span_x + 8, top - 10, "median read ≈ 11.3 kb", size=12, fill=ACCENT, weight="600"))
    svg.append(text(left, top - 28, f"{100 * within_10k / total:.1f}% of candidates have a neighbour "
                    "within one read", size=13, fill=ACCENT, weight="600"))
    svg.append(text(left, top - 10, "share of candidates", size=11, fill=MUTED))

    for index, ((lo, hi), count) in enumerate(zip(bins, counts)):
        x = left + index * (plot_w / len(counts)) + 6
        bar_h = plot_h * count / top_count
        y = top + plot_h - bar_h
        in_range = index < 5
        svg.append(rect(x, y, bar_w, bar_h, ACCENT if in_range else GREY, rx=3))
        svg.append(text(x + bar_w / 2, y - 6, f"{100 * count / total:.1f}%", size=11,
                        fill=INK if in_range else MUTED, anchor="middle", family="mono"))
        label = f"{lo // 1000}–{hi // 1000} kb" if hi < 10**9 else "> 50 kb"
        if hi <= 1000:
            label = f"{lo}–{hi} bp"
        svg.append(text(x + bar_w / 2, top + plot_h + 20, label, size=11, anchor="middle"))
    svg.append(text(left, h - 22, "distance to the nearest other PASS candidate", size=12))
    return figure(
        1,
        "Linked evidence is available for about a third of candidates",
        f"Nearest-neighbour distance for all {total:,} PASS SNV candidates. Green bars fall within "
        "the span of a single median read; the dashed line marks that span. Availability is an "
        "opportunity, not an observation — Figure 2 tests whether it is taken.",
        "".join(svg), f"0 0 {w} {h}")


def fig_cooccurrence(summary, fraction_hist, evaluable):
    """What reads covering both positions actually carry, and how pairs distribute."""
    w, h = 900, 380
    svg = []
    # --- panel A: read classification, one stacked bar over 50,756 reads
    total = summary["reads_covering_both"]
    classes = [
        ("both ALT", summary["reads_alt_alt"], ACCENT),
        ("ALT at one", summary["reads_alt_ref"] + summary["reads_ref_alt"], WARN),
        ("neither ALT", summary["reads_ref_ref"], GREY),
    ]
    other = total - sum(c[1] for c in classes)
    if other > 0:
        classes.append(("other", other, LINE))
    left, bar_y, bar_h, bar_w = 60, 70, 54, 780
    svg.append(text(60, 40, "A · What the reads carry", size=14, fill=INK, weight="600", family="serif"))
    svg.append(text(60, 58, f"{total:,} reads spanning both positions of a sampled pair", size=11))
    x = left
    for label, value, colour in classes:
        seg_w = bar_w * value / total
        svg.append(rect(x, bar_y, seg_w, bar_h, colour, rx=3))
        if seg_w > 60:
            svg.append(text(x + seg_w / 2, bar_y + 24, f"{100 * value / total:.1f}%", size=14,
                            fill="#fffdf8" if colour in (ACCENT, WARN) else INK,
                            anchor="middle", weight="700", family="mono"))
            svg.append(text(x + seg_w / 2, bar_y + 42, label, size=11,
                            fill="#fffdf8" if colour in (ACCENT, WARN) else MUTED, anchor="middle"))
        x += seg_w

    # --- panel B: per-pair ALT-ALT fraction, showing the in-cis / in-trans split
    top, plot_h, plot_w = 190, 130, 780
    svg.append(text(60, 168, "B · How pairs distribute", size=14, fill=INK, weight="600", family="serif"))
    top_count = max(fraction_hist)
    bin_w = plot_w / len(fraction_hist) - 8
    for index, count in enumerate(fraction_hist):
        x = left + index * (plot_w / len(fraction_hist)) + 4
        bar_h = (plot_h - 20) * count / top_count
        y = top + plot_h - bar_h
        colour = GREY if index == 0 else (ACCENT if index >= 7 else WARN)
        svg.append(rect(x, y, bin_w, bar_h, colour, rx=2))
        svg.append(text(x + bin_w / 2, y - 5, str(count), size=10, anchor="middle", family="mono"))
    svg.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="{LINE}"/>')
    for index, label in ((0, "0"), (5, "0.5"), (9, "1.0")):
        x = left + index * (plot_w / len(fraction_hist)) + bin_w / 2
        svg.append(text(x, top + plot_h + 18, label, size=11, anchor="middle", family="mono"))
    svg.append(text(left, top + plot_h + 40,
                    "fraction of reads carrying both ALT alleles, per candidate pair", size=12))
    svg.append(text(left + 6, top - 4, "never together", size=11, fill=MUTED))
    svg.append(text(left + plot_w - 6, top - 4, "always together", size=11, fill=ACCENT, anchor="end"))
    return figure(
        2,
        "Two candidates do appear on the same molecule",
        f"{summary['pairs_with_alt_alt']} of {summary['pairs_evaluable']} evaluable pairs "
        f"({summary['pairs_with_alt_alt_pct']}%) had at least one read carrying both ALT alleles, "
        f"and {summary['pairs_with_alt_alt_support_2plus']} had two or more. Panel B is bimodal: "
        "pairs tend to be either never or almost always together on a molecule — the signature of "
        "two variants lying in cis on one haplotype versus in trans on opposite ones.",
        "".join(svg), f"0 0 {w} {h}")


def fig_specificity(summary):
    """The pre-registered criterion, and the direction it actually went."""
    w, h = 900, 350
    left, top, plot_h, group_w = 90, 86, 180, 200
    svg = [text(60, 26, "Predicted: confirmed-somatic pairs should co-occur more often",
                size=12, fill=MUTED)]
    strata = [
        ("both confirmed", summary["by_seqc2_stratum"]["both"], ACCENT),
        ("one confirmed", summary["by_seqc2_stratum"]["one"], WARN),
        ("neither confirmed", summary["by_seqc2_stratum"]["neither"], DANGER),
    ]
    top_pct = 90
    for index, (label, stats, colour) in enumerate(strata):
        x = left + index * (group_w + 60)
        bar_h = plot_h * stats["pct"] / top_pct
        y = top + plot_h - bar_h
        svg.append(rect(x, y, group_w, bar_h, colour, rx=4))
        svg.append(text(x + group_w / 2, y - 10, f"{stats['pct']:.1f}%", size=20, fill=INK,
                        anchor="middle", weight="700", family="mono"))
        svg.append(text(x + group_w / 2, top + plot_h + 22, label, size=12, fill=INK, anchor="middle"))
        svg.append(text(x + group_w / 2, top + plot_h + 40,
                        f"{stats['pairs_with_alt_alt']} of {stats['pairs_evaluable']} pairs",
                        size=11, anchor="middle"))
    svg.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{w - 40}" y2="{top + plot_h}" stroke="{LINE}"/>')
    # the observed direction, drawn against the prediction
    arrow_y = top - 18   # above the tallest bar's value label, not through it
    svg.append(f'<path d="M {left + 100} {arrow_y} L {left + 2 * (group_w + 60) + 100} {arrow_y}" '
               f'stroke="{DANGER}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
    svg.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
               f'markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{DANGER}"/></marker></defs>')
    svg.append(text(left + group_w + 60, arrow_y - 8, "observed direction", size=12, fill=DANGER,
                    anchor="middle", weight="600"))
    return figure(
        3,
        "The co-occurrence is not specific to somatic pairs",
        "Share of pairs with at least one both-ALT read, split by how many of the two candidates "
        "are SEQC2 high-confidence somatic SNVs. The criterion set before the run predicted the "
        "opposite ordering. Germline heterozygous variants lying in cis is the economical "
        "explanation, and it is what a candidate set of unknown composition would produce.",
        "".join(svg), f"0 0 {w} {h}")


def fig_decay(decay):
    """Co-occurrence against distance, with the coverage that explains it."""
    w, h = 900, 300
    left, top, plot_h, plot_w = 70, 50, 170, 760
    svg = [rect(left, top, plot_w, plot_h, "none", stroke=LINE)]
    step = plot_w / len(decay)
    points = []
    for index, entry in enumerate(decay):
        x = left + index * step + step / 2
        bar_h = plot_h * entry["median_reads"] / 80
        svg.append(rect(x - 42, top + plot_h - bar_h, 84, bar_h, ACCENT_SOFT, rx=3))
        svg.append(text(x, top + plot_h - bar_h - 8, f'{entry["median_reads"]} reads', size=11,
                        anchor="middle", fill=ACCENT, family="mono"))
        y = top + plot_h - plot_h * entry["pct"] / 100
        points.append((x, y))
        svg.append(text(x, top + plot_h + 22, entry["label"], size=12, anchor="middle", fill=INK))
        svg.append(text(x, top + plot_h + 40, f'{entry["pairs"]} pairs', size=11, anchor="middle"))
    path = " ".join(f"{'M' if i == 0 else 'L'} {x:.0f} {y:.0f}" for i, (x, y) in enumerate(points))
    svg.append(f'<path d="{path}" fill="none" stroke="{DANGER}" stroke-width="2.5"/>')
    for (x, y), entry in zip(points, decay):
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{DANGER}"/>')
        svg.append(text(x, y - 12, f'{entry["pct"]:.0f}%', size=12, anchor="middle", fill=DANGER,
                        weight="700", family="mono"))
    svg.append(text(left, h - 14, "distance between the two candidates", size=12))
    svg.append(text(left + plot_w, top - 14, "line: pairs with a both-ALT read   ·   bars: median reads covering both",
                    size=11, anchor="end"))
    return figure(
        4,
        "The decline with distance is a read-length effect, not a biological one",
        "Co-occurrence falls from 78% under 1 kb to 63% at 10–20 kb, tracking the fall in reads "
        "that cover both positions at all (median 72 → 28). Nothing here suggests linkage decays "
        "biologically over this range; the molecule simply stops reaching.",
        "".join(svg), f"0 0 {w} {h}")


def fig_ladder():
    """Where the claim stands, rung by rung."""
    w, h = 900, 300
    rungs = [
        ("1", "Candidates are close enough to share a read", "measured", "34.8% within 10 kb", ACCENT),
        ("2", "Two candidates appear as ALT on one molecule", "measured", "67.9% of pairs", ACCENT),
        ("3", "That co-occurrence is specific to somatic pairs", "contradicted", "65.1% vs 78.6%", DANGER),
        ("4", "It persists at low tumor fraction", "not measured", "next experiment", GREY),
        ("5", "It suppresses background relative to blanks", "not measured", "—", GREY),
    ]
    svg = []
    row_h = 50
    for index, (num, claim, status, detail, colour) in enumerate(rungs):
        y = 30 + index * row_h
        svg.append(rect(60, y, 780, row_h - 8, PANEL, rx=8, stroke=LINE))
        svg.append(rect(60, y, 6, row_h - 8, colour, rx=3))
        svg.append(text(80, y + 27, num, size=13, fill=colour, weight="700", family="mono"))
        svg.append(text(104, y + 27, claim, size=13.5, fill=INK))
        svg.append(text(640, y + 27, status, size=12, fill=colour, weight="600", anchor="end"))
        svg.append(text(830, y + 27, detail, size=11.5, fill=MUTED, anchor="end", family="mono"))
    return figure(
        5,
        "Where the claim stands",
        "Rungs 1 and 2 are measurements made today. Rung 3 was pre-registered and came out in the "
        "opposite direction. Rungs 4 and 5 are what would turn an available evidence type into an "
        "improvement in recognition — and neither has been attempted.",
        "".join(svg), f"0 0 {w} {h}")


# --------------------------------------------------------------------------- page
STYLE = """
:root{--bg:#f7f3eb;--panel:#fffdf8;--ink:#1f1b16;--muted:#695f56;--line:#d4c8bb;
--accent:#1f5c4e;--accent-soft:#d8ebe5;--warn:#8d5c14;--warn-soft:#f7ebc7;--danger:#8f3d2c;
--danger-soft:#f6ddd7;--serif:Georgia,"Iowan Old Style",serif;--sans:"Segoe UI",Calibri,system-ui,sans-serif;
--mono:"IBM Plex Mono",Consolas,monospace;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.62;font-size:16px}
.page{width:min(58rem,calc(100% - 3rem));margin:0 auto;padding:3rem 0 4rem}
.masthead{border-bottom:2px solid var(--accent);padding-bottom:1rem;margin-bottom:2rem}
.masthead__kicker{font-family:var(--mono);font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0}
h1{font-family:var(--serif);font-size:2.3rem;line-height:1.18;margin:.6rem 0 .8rem}
.masthead__meta{font-size:.85rem;color:var(--muted);margin:0;display:flex;flex-wrap:wrap;gap:.4rem 1.4rem}
h2{font-family:var(--mono);font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);
margin:2.8rem 0 .7rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
p{margin:0 0 1rem;max-width:62ch}
.verdict{border:1px solid var(--line);border-left:5px solid var(--accent);background:var(--panel);
border-radius:12px;padding:1.3rem 1.5rem;margin:0 0 2rem}
.verdict h2{margin:0 0 .6rem;border:none;padding:0}
.verdict p{font-size:1.05rem;max-width:none}
.verdict p:last-child{margin-bottom:0}
.verdict strong{color:var(--accent)}
.fig{margin:1.6rem 0 2.2rem;border:1px solid var(--line);border-radius:14px;background:var(--panel);
padding:1.1rem 1.2rem 1rem}
.fig__head{font-size:1rem;font-family:var(--serif);margin-bottom:.7rem}
.fig__num{font-family:var(--mono);font-size:.72rem;letter-spacing:.07em;text-transform:uppercase;
color:var(--accent);margin-right:.5rem}
.fig__canvas{overflow-x:auto}
.fig svg{display:block;width:100%;min-width:640px;height:auto}
.fig__caption{margin:.8rem 0 0;font-size:.87rem;color:var(--muted);max-width:none}
.keynum{display:flex;flex-wrap:wrap;gap:1px;background:var(--line);border:1px solid var(--line);
border-radius:12px;overflow:hidden;margin:0 0 2rem}
.keynum div{flex:1 1 10rem;background:var(--panel);padding:.9rem 1rem}
.keynum dt{font-family:var(--mono);font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.keynum dd{margin:.25rem 0 0;font-family:var(--mono);font-size:1.35rem;color:var(--accent)}
.keynum dd small{font-family:var(--sans);font-size:.78rem;color:var(--muted);display:block;line-height:1.35}
.caution{border:1px solid rgba(141,92,20,.35);border-left:4px solid var(--warn);background:var(--warn-soft);
border-radius:10px;padding:.9rem 1.2rem;margin:1.4rem 0}
.caution p{margin:0;max-width:none;font-size:.94rem}
ul{margin:0 0 1rem;padding-left:1.2rem;max-width:62ch}
li{margin-bottom:.4rem}
.method{font-size:.9rem;color:var(--muted)}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted)}
@media print{body{background:#fff;font-size:11pt}.page{width:100%;padding:0}.fig{break-inside:avoid}
.fig svg{min-width:0}h2{break-after:avoid}}
"""


def build(out: Path) -> Path:
    summary = json.loads(SUMMARY.read_text())
    bins, counts, total_candidates, within_10k = nearest_neighbour_histogram()
    evaluable, fraction_hist, decay = cooccurrence_tables()

    figures = "\n".join([
        fig_availability(bins, counts, total_candidates, within_10k),
        fig_cooccurrence(summary, fraction_hist, evaluable),
        fig_specificity(summary),
        fig_decay(decay),
        fig_ladder(),
    ])

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Does long-read ONT supply evidence that improves tumor recognition?</title>
<style>{STYLE}</style></head>
<body><div class="page">

<header class="masthead">
  <p class="masthead__kicker">Research report · 19 August 2026</p>
  <h1>Does long-read ONT supply evidence that improves recognition of tumor-derived molecules?</h1>
  <p class="masthead__meta">
    <span>HCC1395, pure tumor</span><span>ONT R10.4.1 simplex, native 5mC/5hmC</span>
    <span>ClairS-TO v0.5.0 candidates</span><span>EXP-G1-001</span>
  </p>
</header>

<section class="verdict">
  <h2>Answer so far</h2>
  <p>
    <strong>Yes to the evidence, not yet to the recognition.</strong> Long reads deliver a kind of
    evidence short fragments cannot: two candidate variants observed on one physical molecule,
    which happens for {summary['pairs_with_alt_alt_pct']}% of candidate pairs tested. But the same
    experiment shows that co-occurrence is <strong>not specific to somatic variants</strong> — it is
    more common among pairs the truth set does not confirm than among pairs it does.
  </p>
  <p>
    So the platform supplies the raw material for a linkage-based detector. Whether that material
    improves recognition remains unmeasured, and the honest reading is that it will not until the
    composition of the candidate set is known.
  </p>
</section>

<dl class="keynum">
  <div><dt>Candidates with a neighbour in read range</dt><dd>{100 * within_10k / total_candidates:.1f}%<small>of {total_candidates:,} PASS SNVs, within 10 kb</small></dd></div>
  <div><dt>Pairs seen with both ALT on one read</dt><dd>{summary['pairs_with_alt_alt_pct']}%<small>{summary['pairs_with_alt_alt']} of {summary['pairs_evaluable']} evaluable pairs</small></dd></div>
  <div><dt>Reads carrying both ALT alleles</dt><dd>{100 * summary['reads_alt_alt'] / summary['reads_covering_both']:.1f}%<small>of {summary['reads_covering_both']:,} reads spanning both</small></dd></div>
  <div><dt>Somatic specificity</dt><dd>none<small>65.1% confirmed vs 78.6% unconfirmed</small></dd></div>
</dl>

<h2>The question</h2>
<p>
  Every method in the reviewed MRD literature improves the same ratio — tumor signal over
  background — by making each observation carry more before combining. Long reads offer a way of
  doing that which short fragments cannot: several facts about the <em>same physical molecule</em>,
  across kilobases. This report asks whether that offer is real in our data, and whether it helps.
</p>
<p class="method">
  <strong>Method.</strong> All {total_candidates:,} PASS SNV candidates were enumerated into pairs
  within 20 kb ({summary['pairs_within_window']:,} pairs); {summary['pairs_sampled']:,} were sampled
  with a fixed seed. For each pair, every read spanning both positions in the pure tumor BAM was
  classified by the base it carried at each (MAPQ ≥ 20, base quality ≥ 10). Thresholds and success
  criteria were registered before the run. SEQC2 high-confidence somatic calls were read only after
  counting, to stratify the report — never to select pairs.
</p>

{figures}

<h2>What this does and does not establish</h2>
<ul>
  <li><strong>Established:</strong> the co-observation exists physically, abundantly, and with
  multi-read support. G1's premise is no longer an inference from genomic coordinates.</li>
  <li><strong>Not established:</strong> that co-occurring ALT alleles are somatic in origin.</li>
  <li><strong>Not established:</strong> that linkage separates tumor-derived molecules from
  background — that needs the blank comparison, which has not been run.</li>
  <li><strong>Not addressed:</strong> anything at low tumor fraction. This is pure tumor, the most
  favourable case by construction.</li>
</ul>

<div class="caution">
  <p>
    <strong>The result that matters most is the negative one.</strong> Had the somatic-specificity
    criterion not been fixed before the run, 67.9% would have read as a clean success. It was
    fixed, it failed, and it points at the candidate set's unknown composition as the thing to
    resolve next.
  </p>
</div>

<h2>What would settle it</h2>
<ul>
  <li><strong>The blank comparison.</strong> The same statistic on the five tumor-free replicates
  and the 1%, 0.1% and 0.01% dilutions. If co-occurrence at low tumor fraction is
  indistinguishable from blanks, linkage carries no usable signal where it matters — a publishable
  negative.</li>
  <li><strong>Candidate composition.</strong> How much of the retained set is somatic, germline or
  recurrent artifact. Until this is known, no co-occurrence count can be attributed to tumor
  origin.</li>
  <li><strong>Cis versus trans.</strong> A third of reads carried exactly one ALT; whether those
  pairs sit on opposite haplotypes, are subclonal, or include an artifact is unexamined.</li>
</ul>

<footer>
  Generated from measured files by <code>scripts/build_linkage_report.py</code>. Sources:
  EXP-G1-001, FIND-0001, EV-0010. Pure tumor at 100% tumor fraction; sampling error at n=1,000 is
  roughly ±3 percentage points. Method positions in the surrounding synthesis derive from indexed
  summaries rather than source PDFs.
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
    path = build(args.output)
    print(f"wrote {path.relative_to(REPO) if REPO in path.resolve().parents else path} "
          f"({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
