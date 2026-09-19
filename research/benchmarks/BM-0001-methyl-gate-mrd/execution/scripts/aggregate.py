#!/usr/bin/env python3
"""
BM-0001-methyl-gate-mrd — aggregation, metrics, criteria.

Executes locked protocol v1.0. Interval machinery is IMPORTED from mrdz (protocol §15
normative implementation); it is not reimplemented here.
"""
import json, os, sys, math, hashlib, argparse
import numpy as np

sys.path.insert(0, '/big8_disk/hung114/ONT_MRD/mrd/tools/mrdz')
from mrdz.score import blank_spread, z_interval, interval_verdict   # protocol §15

GLO, GHI = 1, 2
CALL = 3.0
N_DRAWS = 200
LEVELS = ['TF0', 'TF1e-2', 'TF1e-3', 'TF1e-4']
TF = {'TF0': 0.0, 'TF1e-2': 0.01, 'TF1e-3': 0.001, 'TF1e-4': 0.0001}
LABEL = {'TF0': '0%', 'TF1e-2': '1%', 'TF1e-3': '0.1%', 'TF1e-4': '0.01%'}
PRIMARY_LEVEL = 'TF1e-3'          # protocol §15, fixed from the prior record


def prep(js):
    """Gate on the UNFILTERED alt count (protocol §10 normative), then vectorise."""
    dep, alt, unsc, k1, k2, i1, i2 = [], [], [], [], [], [], []
    for r in js['rows']:
        if r['depth'] <= 0 or not (GLO <= r['alt_total'] <= GHI):
            continue
        dep.append(r['depth']); alt.append(r['alt_total'])
        unsc.append(r['alt_unscorable']); k1.append(r['kept_B1']); k2.append(r['kept_C2'])
        s = r['alt_scorable_idx']
        i1.append(s[0] if len(s) > 0 else -1)
        i2.append(s[1] if len(s) > 1 else -1)
    return dict(dep=np.array(dep, float), alt=np.array(alt, float),
                unsc=np.array(unsc, float), k1=np.array(k1, float),
                k2=np.array(k2, float), i1=np.array(i1, int), i2=np.array(i2, int),
                n_gate=len(dep), n_scorable=js['n_scorable_reads'], K=js['K_B1'],
                meta=js)


def stat(dep, a):
    """G and the plug-in binomial sample sd, protocol §9."""
    if len(dep) == 0:
        return 0.0, 0.0
    p = a / dep
    return float(a.sum()), float(math.sqrt(float((dep * p * (1 - p)).sum())))


def arm_counts(g, arm, mask=None):
    if arm == 'B0':
        return g['alt']
    if arm == 'B1':
        return g['k1']
    if arm == 'C2':
        return g['k2']
    if arm == 'C1':
        a = np.zeros(g['n_gate'])
        if g['n_gate']:
            m1 = (g['i1'] >= 0); m2 = (g['i2'] >= 0)
            a[m1] += mask[g['i1'][m1]]
            a[m2] += mask[g['i2'][m2]]
        return a
    raise ValueError(arm)


def retention(g, a, arm=None):
    """kept / scorable ALT, over gate-passing candidates (protocol §16).

    For B0 the numerator `a` is every ALT read, including the unscorable ones, so the literal
    §16 ratio exceeds 1. B0 applies no filter, so the comparable quantity is its kept-among-
    scorable rate, which is 1.0 by definition. Reported as `retention_scorable_only`; the
    literal §16 value is reported unchanged beside it.
    """
    scor = float((g['alt'] - g['unsc']).sum())
    lit = (float(a.sum()) / scor if scor > 0 else float('nan'))
    so = 1.0 if arm == 'B0' else lit
    return lit, scor, so


def main(indir, outdir, tag, individuals):
    S = {}
    for ind in individuals:
        for lv in LEVELS:
            for rep in (1, 2, 3, 4, 5):
                p = os.path.join(indir, f'{tag}{ind}_{lv}_rep{rep}.json')
                if os.path.exists(p):
                    S[(ind, lv, rep)] = prep(json.load(open(p)))

    per_sample, ablation, c1_draws, blank_self, missing, cis = [], [], [], [], [], []

    for ind in individuals:
        keys = sorted([k for k in S if k[0] == ind], key=lambda k: (LEVELS.index(k[1]), k[2]))
        if not keys:
            continue
        blank_keys = [(ind, 'TF0', r) for r in (1, 2, 3) if (ind, 'TF0', r) in S]
        blank5_keys = [(ind, 'TF0', r) for r in (1, 2, 3, 4, 5) if (ind, 'TF0', r) in S]

        # ---------- C1: 200 draws, one draw spans all of this individual's samples ----------
        c1 = {k: {'G': [], 'sd': [], 'ret': []} for k in keys}
        for j in range(N_DRAWS):
            seed = int(hashlib.sha256(f'20260831|C1|{ind}|{j}'.encode()).hexdigest()[:12], 16)
            rng = np.random.default_rng(seed)
            for k in keys:                       # fixed sample order within a draw
                g = S[k]
                n, K = g['n_scorable'], g['K']
                mask = (rng.permutation(n) < K).astype(float) if n > 0 else np.zeros(0)
                a = arm_counts(g, 'C1', mask)
                G, sd = stat(g['dep'], a)
                r, _sc, so = retention(g, a, 'C1')
                c1[k]['G'].append(G); c1[k]['sd'].append(sd); c1[k]['ret'].append(so)

        # ---------- deterministic arms ----------
        base = {}
        for k in keys:
            g = S[k]
            for arm in ('B0', 'B1', 'C2'):
                a = arm_counts(g, arm)
                G, sd = stat(g['dep'], a)
                r, scor, so = retention(g, a, arm)
                base[(k, arm)] = dict(G=G, sd=sd, ret=r, scor=scor, ret_so=so)

        # ---------- per-sample metrics ----------
        def blanks_of(arm, draw=None):
            if arm == 'C1':
                return [c1[bk]['G'][draw] for bk in blank_keys]
            return [base[(bk, arm)]['G'] for bk in blank_keys]

        for k in keys:
            ind_, lv, rep = k
            g = S[k]
            for arm in ('B0', 'B1', 'C1', 'C2'):
                if arm == 'C1':
                    G = float(np.median(c1[k]['G'])); sd = float(np.median(c1[k]['sd']))
                    ret = float(np.nanmedian(c1[k]['ret'])); scor = base[(k, 'B0')]['scor']; ret_so = ret
                    bl = [float(np.median(c1[bk]['G'])) for bk in blank_keys]
                else:
                    d = base[(k, arm)]; G, sd, ret, scor, ret_so = d['G'], d['sd'], d['ret'], d['scor'], d['ret_so']
                    bl = blanks_of(arm)
                bm, bsd, nb = blank_spread(bl)
                for vc, ssd in (('V1', sd), ('V2', math.sqrt(bm) if bm > 0 else 0.0)):
                    z, lo, hi, n = z_interval(G, bl, ssd)
                    verd, _ = interval_verdict(z, lo, hi, CALL)
                    per_sample.append(dict(
                        benchmark_id='BM-0001-methyl-gate-mrd', individual=ind_, level=lv,
                        level_label=LABEL[lv], replicate=rep, arm=arm, variance_construction=vc,
                        n_candidates=g['meta']['n_candidates'], n_gate_pass=g['n_gate'],
                        depth_mean=round(float(g['dep'].mean()) if g['n_gate'] else 0.0, 3),
                        alt_total=float(g['alt'].sum()), alt_scorable=scor,
                        alt_unscorable=float(g['unsc'].sum()), alt_kept=G,
                        retention=round(ret, 6) if ret == ret else 'NA',
                        retention_scorable_only=round(ret_so, 6) if ret_so == ret_so else 'NA',
                        G=G, sample_sd=round(ssd, 4), blank_mean=round(bm, 4),
                        blank_sd=round(bsd, 4) if bsd == bsd else 'NA', n_blanks=nb,
                        z=round(z, 4) if z == z else 'NA',
                        z_lo=round(lo, 4) if lo == lo else 'NA',
                        z_hi=round(hi, 4) if hi == hi else 'NA',
                        verdict=verd, prediction=1 if verd == 'detected' else 0,
                        truth_label=0 if lv == 'TF0' else 1,
                        premise_flag='oracle_free_premise_weakest_here' if lv == 'TF1e-2' else '-',
                        n_consensus_positions=g['meta']['n_consensus_positions'],
                        n_confident_positions=g['meta']['n_confident_positions'],
                        n_scorable_reads=g['n_scorable'], cut=round(g['meta']['cut'], 6)))
                    cis.append(dict(individual=ind_, arm=arm, level=lv, replicate=rep,
                                    variance_construction=vc, metric='z', estimate=round(z, 4) if z == z else 'NA',
                                    ci_lower=round(lo, 4) if lo == lo else 'NA',
                                    ci_upper=round(hi, 4) if hi == hi else 'NA',
                                    method='mrdz.score.z_interval, Student-t 95% on the blank mean',
                                    n_resamples=nb))
                if lv != 'TF0':
                    missing.append(dict(feature='per_read_methylation_score', arm=arm,
                                        individual=ind_, sample=f'{lv}.rep{rep}',
                                        missing_count=float(g['unsc'].sum()),
                                        missing_fraction=round(float(g['unsc'].sum()) / max(float(g['alt'].sum()), 1), 6),
                                        action='unscorable ALT reads dropped (protocol §10 step 7)'))

        # ---------- S3: leave-one-out over five blanks ----------
        for arm in ('B0', 'B1', 'C1', 'C2'):
            for i, bk in enumerate(blank5_keys):
                others = [x for x in blank5_keys if x != bk]
                if arm == 'C1':
                    G = float(np.median(c1[bk]['G'])) if bk in c1 else float('nan')
                    sd = float(np.median(c1[bk]['sd'])) if bk in c1 else float('nan')
                    ref = [float(np.median(c1[o]['G'])) for o in others if o in c1]
                else:
                    G = base[(bk, arm)]['G']; sd = base[(bk, arm)]['sd']
                    ref = [base[(o, arm)]['G'] for o in others]
                if len(ref) < 2 or G != G:
                    continue
                bm, _bs, _n = blank_spread(ref)
                for vc, ssd in (('V1', sd), ('V2', math.sqrt(bm) if bm > 0 else 0.0)):
                    z, lo, hi, n = z_interval(G, ref, ssd)
                    verd, _ = interval_verdict(z, lo, hi, CALL)
                    blank_self.append(dict(individual=ind_, arm=arm, held_out=f'TF0.rep{bk[2]}',
                                           variance_construction=vc, G=G,
                                           ref_mean=round(bm, 4), n_ref=len(ref),
                                           z=round(z, 4) if z == z else 'NA',
                                           z_lo=round(lo, 4) if lo == lo else 'NA',
                                           z_hi=round(hi, 4) if hi == hi else 'NA',
                                           verdict=verd,
                                           detected=1 if verd == 'detected' else 0))

        # ---------- C1 per-draw zlo_min at the primary level ----------
        pk = [k for k in keys if k[1] == PRIMARY_LEVEL]
        for j in range(N_DRAWS):
            bl = [c1[bk]['G'][j] for bk in blank_keys]
            bm, _bs, _n = blank_spread(bl)
            for vc in ('V1', 'V2'):
                los = []
                for k in pk:
                    ssd = c1[k]['sd'][j] if vc == 'V1' else (math.sqrt(bm) if bm > 0 else 0.0)
                    z, lo, hi, n = z_interval(c1[k]['G'][j], bl, ssd)
                    los.append(lo)
                zlo = min(los) if los and not any(x != x for x in los) else float('nan')
                c1_draws.append(dict(individual=ind_, draw=j, variance_construction=vc,
                                     zlo_min=round(zlo, 4) if zlo == zlo else 'NA',
                                     blank_mean=round(bm, 4)))

        # ---------- ablation / criteria ----------
        def zlo_min_of(arm, lv, vc):
            ks = [k for k in keys if k[1] == lv]
            if not ks:
                return float('nan')
            if arm == 'C1':
                vals = [d['zlo_min'] for d in c1_draws
                        if d['individual'] == ind_ and d['variance_construction'] == vc]
                vals = [v for v in vals if v != 'NA']
                return float(np.median(vals)) if vals else float('nan')
            bl = blanks_of(arm)
            bm, _b, _n = blank_spread(bl)
            los = []
            for k in ks:
                d = base[(k, arm)]
                ssd = d['sd'] if vc == 'V1' else (math.sqrt(bm) if bm > 0 else 0.0)
                z, lo, hi, n = z_interval(d['G'], bl, ssd)
                los.append(lo)
            return min(los) if los and not any(x != x for x in los) else float('nan')

        def ret_of(arm, lv):
            ks = [k for k in keys if k[1] == lv]
            if arm == 'C1':
                vs = [float(np.nanmedian(c1[k]['ret'])) for k in ks if k in c1]
            else:
                vs = [base[(k, arm)]['ret_so'] for k in ks]
            vs = [v for v in vs if v == v]
            return float(np.mean(vs)) if vs else float('nan')

        def levels_detected(arm, vc):
            out = []
            for lv in ['TF1e-2', 'TF1e-3', 'TF1e-4']:
                ks = [k for k in keys if k[1] == lv]
                if not ks:
                    continue
                bl = ([float(np.median(c1[bk]['G'])) for bk in blank_keys] if arm == 'C1'
                      else blanks_of(arm))
                bm, _b, _n = blank_spread(bl)
                ok = True
                for k in ks:
                    if arm == 'C1':
                        G = float(np.median(c1[k]['G'])); sd = float(np.median(c1[k]['sd']))
                    else:
                        G = base[(k, arm)]['G']; sd = base[(k, arm)]['sd']
                    ssd = sd if vc == 'V1' else (math.sqrt(bm) if bm > 0 else 0.0)
                    z, lo, hi, n = z_interval(G, bl, ssd)
                    v, _ = interval_verdict(z, lo, hi, CALL)
                    if v != 'detected':
                        ok = False
                if ok:
                    out.append(LABEL[lv])
            return ';'.join(out) if out else 'none'

        for vc in ('V1', 'V2'):
            zb0 = zlo_min_of('B0', PRIMARY_LEVEL, vc)
            for arm in ('B0', 'B1', 'C1', 'C2'):
                zl = zlo_min_of(arm, PRIMARY_LEVEL, vc)
                rb, rl = ret_of(arm, 'TF0'), ret_of(arm, PRIMARY_LEVEL)
                p05 = p95 = 'NA'
                rr05 = rr95 = 'NA'
                if arm == 'C1':
                    bl_r = [np.nanmedian([c1[k]['ret'][j] for k in keys if k[1] == 'TF0' and k in c1])
                            for j in range(N_DRAWS)]
                    lv_r = [np.nanmedian([c1[k]['ret'][j] for k in keys if k[1] == PRIMARY_LEVEL and k in c1])
                            for j in range(N_DRAWS)]
                    rr = [l / b for l, b in zip(lv_r, bl_r) if b and b == b and l == l and b > 0]
                    if rr:
                        rr05, rr95 = round(float(np.percentile(rr, 5)), 4), round(float(np.percentile(rr, 95)), 4)
                    vals = [d['zlo_min'] for d in c1_draws
                            if d['individual'] == ind_ and d['variance_construction'] == vc
                            and d['zlo_min'] != 'NA']
                    if vals:
                        p05, p95 = round(float(np.percentile(vals, 5)), 4), round(float(np.percentile(vals, 95)), 4)
                ablation.append(dict(
                    benchmark_id='BM-0001-methyl-gate-mrd', individual=ind_,
                    level=PRIMARY_LEVEL, level_label=LABEL[PRIMARY_LEVEL], arm=arm,
                    variance_construction=vc,
                    zlo_min=round(zl, 4) if zl == zl else 'UNDEFINED',
                    zlo_min_p05=p05, zlo_min_p95=p95,
                    delta_vs_B0=round(zl - zb0, 4) if (zl == zl and zb0 == zb0) else 'UNDEFINED',
                    delta_vs_C1='PENDING', delta_vs_C2='PENDING',
                    retention_blank=round(rb, 6) if rb == rb else 'NA',
                    retention_level=round(rl, 6) if rl == rl else 'NA',
                    retention_ratio=round(rl / rb, 4) if (rb == rb and rl == rl and rb > 0) else 'NA',
                    retention_ratio_p05=rr05, retention_ratio_p95=rr95,
                    levels_detected_replicate_rule=levels_detected(arm, vc),
                    criterion='-', criterion_outcome='-'))

    # fill deltas vs C1 / C2
    idx = {(r['individual'], r['variance_construction'], r['arm']): r for r in ablation}
    for r in ablation:
        for other in ('C1', 'C2'):
            o = idx.get((r['individual'], r['variance_construction'], other))
            if o and r['zlo_min'] != 'UNDEFINED' and o['zlo_min'] != 'UNDEFINED':
                r['delta_vs_' + other] = round(r['zlo_min'] - o['zlo_min'], 4)
            else:
                r['delta_vs_' + other] = 'UNDEFINED'

    def w(path, rows):
        if not rows:
            open(path, 'w').write('')
            return
        cols = list(rows[0].keys())
        with open(path, 'w') as f:
            f.write('\t'.join(cols) + '\n')
            for r in rows:
                f.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')

    os.makedirs(outdir, exist_ok=True)
    w(f'{outdir}/per_sample_metrics.tsv', per_sample)
    w(f'{outdir}/ablation_results.tsv', ablation)
    w(f'{outdir}/c1_draws.tsv', c1_draws)
    w(f'{outdir}/blank_selfcheck.tsv', blank_self)
    w(f'{outdir}/missingness_report.tsv', missing)
    w(f'{outdir}/confidence_intervals.tsv', cis)
    print(f'wrote {len(per_sample)} per-sample rows, {len(ablation)} ablation rows to {outdir}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--indir', default='execution/raw')
    ap.add_argument('--outdir', default='results')
    ap.add_argument('--tag', default='')
    ap.add_argument('--individuals', default='HCC1395,COLO829')
    a = ap.parse_args()
    main(a.indir, a.outdir, a.tag, a.individuals.split(','))
