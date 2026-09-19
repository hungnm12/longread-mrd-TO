#!/usr/bin/env python3
"""
BM-0001-methyl-gate-mrd — one BAM pass, producing every arm's raw material.

Executes locked protocol v1.0 (sha256 9c615da4af068a5330bb512942810c9f2229aa2348554cddcfc130021e200b8c).
This script implements methodology; it does not choose it. Every constant below is quoted from
the locked protocol section named beside it.

Emits one JSON per sample. Arms B0, B1, C2 are resolved here; C1's 200 draws are resolved in
the aggregation step from `alt_scorable_idx`, because a C1 draw is defined (protocol §10) as a
complete re-run across all of an individual's samples under one draw index.
"""
import pysam, os, sys, json, hashlib, argparse

# ---- locked constants, protocol §10 (B1) and §9 (gate / quality) ----
ML       = 128          # §10 B1: modification-probability threshold
MIN_COV  = 10           # §10 B1: minimum observations for a consensus position
CONF_LO  = 0.1          # §10 B1: CONF_BAND
CONF_HI  = 0.9
MIN_CPG  = 5            # §10 B1: minimum confident positions for a read to be scorable
PCT      = 95           # §10 B1: percentile rule
GLO, GHI = 1, 2         # §9  gate, evaluated on the UNFILTERED alt count (§10 normative)
MIN_BQ   = 20           # §9
MIN_MQ   = 20           # §9

FILES_OPENED = []


def ref_calls(rd):
    mb = rd.modified_bases or {}
    if not mb:
        return []
    q2r = {q: r for q, r in rd.get_aligned_pairs(matches_only=True)}
    return [(q2r[qp], 1 if p >= ML else 0)
            for v in mb.values() for qp, p in v if q2r.get(qp) is not None]


def analyse(bam_path, cands):
    FILES_OPENED.append(bam_path)
    bam = pysam.AlignmentFile(bam_path, 'rb')
    calls_of = {}          # read name -> [(refpos, meth)]
    at = []                # per candidate: (depth, [alt read names])
    n_dup = 0
    seen_dupflag = set()
    for i, (chrom, pos, alt_b) in enumerate(cands):
        dep = 0
        alts = []
        for col in bam.pileup(chrom, pos - 1, pos, truncate=True,
                              min_base_quality=MIN_BQ, min_mapping_quality=MIN_MQ,
                              stepper='samtools'):
            if col.reference_pos != pos - 1:
                continue
            for pr in col.pileups:
                if pr.is_del or pr.is_refskip or pr.query_position is None:
                    continue
                rd = pr.alignment
                dep += 1
                if rd.is_duplicate and rd.query_name not in seen_dupflag:
                    seen_dupflag.add(rd.query_name); n_dup += 1
                if rd.query_name not in calls_of:
                    calls_of[rd.query_name] = ref_calls(rd)
                if rd.query_sequence[pr.query_position].upper() == alt_b:
                    alts.append(rd.query_name)
        at.append((dep, alts))
        if i % 500 == 0:
            sys.stderr.write(f'  {os.path.basename(bam_path)} cand {i}/{len(cands)}\n')
            sys.stderr.flush()
    bam.close()

    # ---- consensus from exactly the reads touched above (protocol §10 B1 step 3) ----
    m, n = {}, {}
    for cl in calls_of.values():
        for r, me in cl:
            n[r] = n.get(r, 0) + 1
            m[r] = m.get(r, 0) + me
    cons = {r: m[r] / n[r] for r in n if n[r] >= MIN_COV}
    conf = {r: b for r, b in cons.items() if b < CONF_LO or b > CONF_HI}

    # ---- per-read scores (B1) and confident-position counts (C2) ----
    score_b1 = {}
    score_c2 = {}
    for name, cl in calls_of.items():
        d = t = 0
        for r, me in cl:
            b = conf.get(r)
            if b is None:
                continue
            t += 1
            d += (me != (1 if b >= 0.5 else 0))
        if t >= MIN_CPG:
            score_b1[name] = d / t
            score_c2[name] = t

    scorable = sorted(score_b1)                     # deterministic index space
    idx_of = {nm: j for j, nm in enumerate(scorable)}
    n_scorable = len(scorable)

    # ---- cut, protocol §10 B1 step 6 and the empty-set case ----
    if n_scorable == 0:
        cut = 1.0
        keep_b1 = set()
        keep_c2 = set()
        k_c2 = 0
    else:
        bg = sorted(score_b1.values())
        cut = bg[int(PCT / 100 * (len(bg) - 1))]
        keep_b1 = {nm for nm in scorable if score_b1[nm] > cut}
        # C2 top-k, protocol §10 C2: k depends only on n_scorable
        k_c2 = max(0, n_scorable - 1 - int(PCT / 100 * (n_scorable - 1)))
        seed = int(hashlib.sha256(('20260831|' + os.path.basename(bam_path)).encode()
                                  ).hexdigest()[:12], 16)
        import random as _r
        rng = _r.Random(seed)
        order = list(scorable)
        rng.shuffle(order)                          # seeded tie-break, protocol §10 C2
        order.sort(key=lambda nm: -score_c2[nm])    # stable: ties keep the shuffled order
        keep_c2 = set(order[:k_c2])

    rows = []
    for dep, alts in at:
        sc_idx = [idx_of[nm] for nm in alts if nm in idx_of]
        rows.append({
            'depth': dep,
            'alt_total': len(alts),
            'alt_unscorable': sum(1 for nm in alts if nm not in idx_of),
            'alt_scorable_idx': sc_idx,
            'kept_B1': sum(1 for nm in alts if nm in keep_b1),
            'kept_C2': sum(1 for nm in alts if nm in keep_c2),
        })

    return {
        'bam': bam_path,
        'n_candidates': len(cands),
        'n_reads_touched': len(calls_of),
        'n_consensus_positions': len(cons),
        'n_confident_positions': len(conf),
        'n_scorable_reads': n_scorable,
        'K_B1': len(keep_b1),
        'k_C2': k_c2,
        'cut': cut,
        'n_duplicate_flagged_reads': n_dup,
        'rows': rows,
    }


def load_cands(path, chrom_filter=None):
    FILES_OPENED.append(path)
    out = []
    with open(path) as f:
        f.readline()
        for line in f:
            q = line.rstrip('\n').split('\t')
            if len(q) >= 7:
                if chrom_filter and q[1] != chrom_filter:
                    continue
                out.append((q[1], int(q[2]), q[4]))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--bam', required=True)
    ap.add_argument('--candidates', required=True)
    ap.add_argument('--chrom-filter', default=None)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    cands = load_cands(a.candidates, a.chrom_filter)
    res = analyse(a.bam, cands)
    res['candidates_file'] = a.candidates
    res['chrom_filter'] = a.chrom_filter
    res['files_opened'] = FILES_OPENED
    with open(a.out, 'w') as fh:
        json.dump(res, fh)
    sys.stderr.write(f'DONE {a.bam} -> {a.out}\n')
