#!/usr/bin/env python3
"""
BM-0001-methyl-gate-mrd — derived artifacts and the preregistered criteria S1-S4.

Reads results/per_sample_metrics.tsv, ablation_results.tsv, blank_selfcheck.tsv.
Applies protocol v1.0 §20 and §21 literally. Makes no interpretation.
"""
import csv, os, sys, argparse
from collections import defaultdict

LEVEL_ORDER = ['TF0', 'TF1e-2', 'TF1e-3', 'TF1e-4']
LABEL = {'TF0': '0%', 'TF1e-2': '1%', 'TF1e-3': '0.1%', 'TF1e-4': '0.01%'}
PRIMARY = 'TF1e-3'
ARMS = ['B0', 'B1', 'C1', 'C2']


def rd(p):
    with open(p) as f:
        return list(csv.DictReader(f, delimiter='\t'))


def w(p, rows, cols=None):
    if not rows:
        open(p, 'w').write('')
        return
    cols = cols or list(rows[0].keys())
    with open(p, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main(outdir):
    ps = rd(f'{outdir}/per_sample_metrics.tsv')
    ab = rd(f'{outdir}/ablation_results.tsv')
    bs = rd(f'{outdir}/blank_selfcheck.tsv')
    inds = sorted({r['individual'] for r in ps})

    # ---------- dilution_metrics ----------
    dil = []
    g = defaultdict(list)
    for r in ps:
        g[(r['individual'], r['level'], r['arm'], r['variance_construction'])].append(r)
    for k in sorted(g, key=lambda k: (k[0], LEVEL_ORDER.index(k[1]), ARMS.index(k[2]), k[3])):
        rows = sorted(g[k], key=lambda r: int(r['replicate']))
        ind, lv, arm, vc = k
        verd = [r['verdict'] for r in rows]
        dil.append(dict(
            benchmark_id='BM-0001-methyl-gate-mrd', individual=ind, level=lv,
            level_label=LABEL[lv], arm=arm, variance_construction=vc,
            n_replicates=len(rows),
            truth_label=rows[0]['truth_label'],
            G=';'.join(r['G'] for r in rows),
            z=';'.join(r['z'] for r in rows),
            z_lo=';'.join(r['z_lo'] for r in rows),
            z_hi=';'.join(r['z_hi'] for r in rows),
            verdicts=';'.join(verd),
            level_detected_replicate_rule=('yes' if (lv != 'TF0' and verd and all(v == 'detected' for v in verd)) else 'no'),
            retention=';'.join(r['retention'] for r in rows),
            alt_unscorable=';'.join(r['alt_unscorable'] for r in rows),
            n_gate_pass=';'.join(r['n_gate_pass'] for r in rows),
            depth_mean=';'.join(r['depth_mean'] for r in rows),
            premise_flag=rows[0]['premise_flag']))
    w(f'{outdir}/dilution_metrics.tsv', dil)

    det = {(d['individual'], d['arm'], d['variance_construction'], d['level']):
           d['level_detected_replicate_rule'] for d in dil}

    # ---------- aggregate_metrics ----------
    agg = []
    for ind in inds:
        for arm in ARMS:
            for vc in ('V1', 'V2'):
                a = [r for r in ab if r['individual'] == ind and r['arm'] == arm
                     and r['variance_construction'] == vc]
                a = a[0] if a else {}
                agg.append(dict(
                    benchmark_id='BM-0001-methyl-gate-mrd', individual=ind, arm=arm,
                    variance_construction=vc, metric='zlo_min@0.1% (PRIMARY)',
                    value=a.get('zlo_min', 'NA'),
                    delta_vs_B0=a.get('delta_vs_B0', 'NA'),
                    delta_vs_C1=a.get('delta_vs_C1', 'NA'),
                    delta_vs_C2=a.get('delta_vs_C2', 'NA'),
                    retention_blank=a.get('retention_blank', 'NA'),
                    retention_0p1=a.get('retention_level', 'NA'),
                    retention_ratio=a.get('retention_ratio', 'NA'),
                    levels_detected=a.get('levels_detected_replicate_rule', 'NA'),
                    n_positive=9, n_negative=5))
    w(f'{outdir}/aggregate_metrics.tsv', agg)

    # ---------- error_analysis ----------
    err = []
    for r in ps:
        t = int(r['truth_label']); p = int(r['prediction'])
        err.append(dict(
            observation_id=f"{r['individual']}.{r['level']}.rep{r['replicate']}",
            individual=r['individual'], sample_id=f"{r['level']}.rep{r['replicate']}",
            level=r['level'], level_label=r['level_label'], arm=r['arm'],
            variance_construction=r['variance_construction'],
            truth_label=t, prediction=p, verdict=r['verdict'], score=r['z'],
            error_type=('TP' if t and p else 'FN' if t and not p else 'FP' if p else 'TN')))
    w(f'{outdir}/error_analysis.tsv', err)

    # ---------- criteria ----------
    crit = []

    def zl(ind, arm, vc):
        for r in ab:
            if r['individual'] == ind and r['arm'] == arm and r['variance_construction'] == vc:
                return num(r['zlo_min']), r['zlo_min']
        return None, 'MISSING'

    for ind in inds:
        for vc in ('V1', 'V2'):
            b1, b1s = zl(ind, 'B1', vc)
            for other in ('B0', 'C1', 'C2'):
                o, os_ = zl(ind, other, vc)
                if b1 is None or o is None:
                    out, delta = 'UNDEFINED', 'UNDEFINED'
                else:
                    out, delta = ('HELD' if b1 > o else 'FAILED'), round(b1 - o, 4)
                crit.append(dict(criterion='S1', leg=f'B1 > {other}', individual=ind,
                                 variance_construction=vc, level=PRIMARY,
                                 b1_value=b1s, comparator_value=os_, delta=delta, outcome=out))
            # S2
            reg = []
            for lv in ['TF1e-2', 'TF1e-3', 'TF1e-4']:
                d0 = det.get((ind, 'B0', vc, lv), 'no'); d1 = det.get((ind, 'B1', vc, lv), 'no')
                if d0 == 'yes' and d1 != 'yes':
                    reg.append(LABEL[lv])
            crit.append(dict(criterion='S2', leg='no level lost B0->B1', individual=ind,
                             variance_construction=vc, level='all',
                             b1_value=';'.join(f"{LABEL[l]}:{det.get((ind,'B1',vc,l),'no')}" for l in ['TF1e-2','TF1e-3','TF1e-4']),
                             comparator_value=';'.join(f"{LABEL[l]}:{det.get((ind,'B0',vc,l),'no')}" for l in ['TF1e-2','TF1e-3','TF1e-4']),
                             delta=';'.join(reg) if reg else 'none lost',
                             outcome='FAILED' if reg else 'HELD'))
            # S3
            hits = [r for r in bs if r['individual'] == ind and r['arm'] == 'B1'
                    and r['variance_construction'] == vc and r['detected'] == '1']
            n_bl = len({r['held_out'] for r in bs if r['individual'] == ind and r['arm'] == 'B1'
                        and r['variance_construction'] == vc})
            crit.append(dict(criterion='S3', leg='B1 detects no blank', individual=ind,
                             variance_construction=vc, level='TF0',
                             b1_value=f'{len(hits)} of {n_bl} leave-one-out blanks detected',
                             comparator_value='threshold z>=3', delta=len(hits),
                             outcome='FAILED' if hits else 'HELD'))
            # S4
            row = [r for r in ab if r['individual'] == ind and r['arm'] == 'B1'
                   and r['variance_construction'] == vc]
            c1r = [r for r in ab if r['individual'] == ind and r['arm'] == 'C1'
                   and r['variance_construction'] == vc]
            rb, rl = (num(row[0]['retention_blank']), num(row[0]['retention_level'])) if row else (None, None)
            c1ratio = num(c1r[0]['retention_ratio']) if c1r else None
            if rb is None or rl is None:
                out = 'UNDEFINED'
            else:
                out = 'HELD' if rl > rb else 'FAILED'
            crit.append(dict(criterion='S4', leg='B1 retention differential (0.1% > blank)',
                             individual=ind, variance_construction=vc, level=PRIMARY,
                             b1_value=f'blank={rb} level={rl} ratio={row[0]["retention_ratio"] if row else "NA"}',
                             comparator_value=f'C1 ratio={c1ratio} (expected ~1 by construction)',
                             delta=round(rl - rb, 6) if (rb is not None and rl is not None) else 'NA',
                             outcome=out))
    w(f'{outdir}/criteria_evaluation.tsv', crit)

    # ---------- registered outcome ----------
    def all_out(c):
        return [r['outcome'] for r in crit if r['criterion'] == c]
    s1 = all_out('S1'); s2 = all_out('S2'); s3 = all_out('S3'); s4 = all_out('S4')
    s1_ok = all(o == 'HELD' for o in s1) and s1
    s2_ok = all(o == 'HELD' for o in s2) and s2
    s3_ok = all(o == 'HELD' for o in s3) and s3
    s4_ok = all(o == 'HELD' for o in s4) and s4

    per_ind_vc = defaultdict(list)
    for r in crit:
        if r['criterion'] == 'S1':
            per_ind_vc[(r['individual'], r['variance_construction'])].append(r['outcome'])
    s1_by = {k: all(o == 'HELD' for o in v) for k, v in per_ind_vc.items()}
    inds_holding = {i for (i, vc), ok in s1_by.items() if ok}
    vcs_holding = {vc for (i, vc), ok in s1_by.items() if ok}

    if s1_ok and s2_ok and s3_ok and s4_ok:
        verdict = 'H1 SUPPORTED'
    elif s1_ok and not s4_ok:
        verdict = 'MECHANISM UNSUPPORTED'
    elif not s3_ok:
        verdict = 'B1 INADMISSIBLE (S3 failed)'
    elif not s2_ok:
        verdict = 'B1 INADMISSIBLE (S2 failed)'
    elif len(inds_holding) == 1 and len(inds) > 1:
        verdict = 'NOT REPLICATED'
    elif len(vcs_holding) == 1:
        verdict = 'SD-MODEL DEPENDENT'
    else:
        verdict = 'H1 NOT SUPPORTED'

    with open(f'{outdir}/registered_outcome.txt', 'w') as f:
        f.write('# BM-0001-methyl-gate-mrd — registered outcome under protocol v1.0 §20/§21\n')
        f.write('# Mechanical application of the preregistered rules. No interpretation.\n\n')
        for c, ok in (('S1', s1_ok), ('S2', s2_ok), ('S3', s3_ok), ('S4', s4_ok)):
            f.write(f'{c}: {"HELD" if ok else "FAILED"}\n')
        f.write(f'\nS1 holds for individuals: {sorted(inds_holding) or "none"}\n')
        f.write(f'S1 holds for constructions: {sorted(vcs_holding) or "none"}\n')
        f.write(f'\nREGISTERED_OUTCOME: {verdict}\n')
    print(open(f'{outdir}/registered_outcome.txt').read())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--outdir', default='results')
    main(ap.parse_args().outdir)
