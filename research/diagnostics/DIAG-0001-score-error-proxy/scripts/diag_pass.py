#!/usr/bin/env python3
"""
DIAG-0001 — recompute BM-0001's score_b1 and record methylation-blind error proxies
in the same pass.

Constants are FROZEN from EXEC-001's run_sample.py and must not be changed here.
Inputs are CRAM (EV-0052); everything else follows the locked protocol exactly, so the
reproduction check against EXEC-001's recorded values is meaningful.
"""
import pysam, os, sys, json, argparse

# ---- frozen constants, identical to execution/scripts/run_sample.py ----
ML       = 128
MIN_COV  = 10
CONF_LO  = 0.1
CONF_HI  = 0.9
MIN_CPG  = 5
PCT      = 95
GLO, GHI = 1, 2
MIN_BQ   = 20
MIN_MQ   = 20


def ref_calls(rd):
    mb = rd.modified_bases or {}
    if not mb:
        return []
    q2r = {q: r for q, r in rd.get_aligned_pairs(matches_only=True)}
    return [(q2r[qp], 1 if p >= ML else 0)
            for v in mb.values() for qp, p in v if q2r.get(qp) is not None]


def read_meta(rd):
    """Error proxies. None of these touches methylation state."""
    aln = rd.query_alignment_length or 0
    try:
        nm = rd.get_tag('NM')
    except KeyError:
        nm = -1
    mb = rd.modified_bases or {}
    probs = [p for v in mb.values() for _, p in v]
    return dict(nm=int(nm), aln_len=int(aln), mapq=int(rd.mapping_quality),
                read_len=int(rd.query_length or 0),
                mean_ml=(sum(probs) / len(probs)) if probs else -1.0,
                n_modcalls=len(probs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cram', required=True)
    ap.add_argument('--ref', required=True)
    ap.add_argument('--cands', required=True)
    ap.add_argument('--sample', required=True)
    ap.add_argument('--outdir', required=True)
    a = ap.parse_args()

    cands = []
    with open(a.cands) as fh:
        hdr = fh.readline().rstrip('\n').split('\t')
        ci = {k: i for i, k in enumerate(hdr)}
        for ln in fh:
            f = ln.rstrip('\n').split('\t')
            cands.append((f[ci['chrom']], int(f[ci['pos']]), f[ci['alt']].upper()))

    bam = pysam.AlignmentFile(a.cram, 'rc', reference_filename=a.ref)
    calls_of, meta_of = {}, {}
    at = []
    for i, (chrom, pos, alt_b) in enumerate(cands):
        dep, alts = 0, []
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
                if rd.query_name not in calls_of:
                    calls_of[rd.query_name] = ref_calls(rd)
                    meta_of[rd.query_name] = read_meta(rd)
                if rd.query_sequence[pr.query_position].upper() == alt_b:
                    alts.append(rd.query_name)
        at.append((dep, alts))
        if i % 500 == 0:
            sys.stderr.write(f'  {a.sample} cand {i}/{len(cands)}\n'); sys.stderr.flush()
    bam.close()

    # ---- consensus, identical to run_sample.py ----
    m, n = {}, {}
    for cl in calls_of.values():
        for r, me in cl:
            n[r] = n.get(r, 0) + 1
            m[r] = m.get(r, 0) + me
    cons = {r: m[r] / n[r] for r in n if n[r] >= MIN_COV}
    conf = {r: b for r, b in cons.items() if b < CONF_LO or b > CONF_HI}

    score_b1, score_c2, disc = {}, {}, {}
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
            disc[name] = d

    scorable = sorted(score_b1)
    n_scorable = len(scorable)
    if n_scorable == 0:
        cut = 1.0; keep_b1 = set()
    else:
        bg = sorted(score_b1.values())
        cut = bg[int(PCT / 100 * (len(bg) - 1))]
        keep_b1 = {nm for nm in scorable if score_b1[nm] > cut}

    # ---- ALT reads at GATE-PASSING candidates ----
    gated_alt = set()
    for dep, alts in at:
        if GLO <= len(alts) <= GHI:
            gated_alt.update(alts)

    os.makedirs(a.outdir, exist_ok=True)
    rp = os.path.join(a.outdir, f'reads_{a.sample}.tsv')
    with open(rp, 'w') as out:
        out.write('read\tscore_b1\tn_conf\tn_disc\tnm\taln_len\tnm_rate\tmapq\tread_len\t'
                  'mean_ml\tn_modcalls\tkept_b1\tgated_alt\n')
        for nm_ in scorable:
            md = meta_of[nm_]
            rate = (md['nm'] / md['aln_len']) if (md['nm'] >= 0 and md['aln_len'] > 0) else -1.0
            out.write(f"{nm_}\t{score_b1[nm_]:.6f}\t{score_c2[nm_]}\t{disc[nm_]}\t{md['nm']}\t"
                      f"{md['aln_len']}\t{rate:.6f}\t{md['mapq']}\t{md['read_len']}\t"
                      f"{md['mean_ml']:.3f}\t{md['n_modcalls']}\t"
                      f"{int(nm_ in keep_b1)}\t{int(nm_ in gated_alt)}\n")

    summary = dict(sample=a.sample, cram=a.cram, n_candidates=len(cands),
                   n_reads_touched=len(calls_of),
                   n_consensus_positions=len(cons), n_confident_positions=len(conf),
                   n_scorable_reads=n_scorable, K_B1=len(keep_b1), cut=cut,
                   n_gated_alt_scorable=sum(1 for x in scorable if x in gated_alt),
                   reads_table=rp)
    sp = os.path.join(a.outdir, f'summary_{a.sample}.json')
    json.dump(summary, open(sp, 'w'), indent=1)
    sys.stderr.write(f'DONE {a.sample} -> {sp}\n')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
