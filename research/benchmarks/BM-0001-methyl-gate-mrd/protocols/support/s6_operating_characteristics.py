#!/usr/bin/env python3
"""Operating characteristics for v1.1 S6, computed BEFORE EXEC-002.

Protocol: protocols/v1.1_draft.md §15.5.9. This script is part of that protocol and is
checksummed with it. Its SEED and every constant are fixed here.

WHAT CHANGED AT DESIGN ITERATION 8 (panel findings MAJ-L2-03, SV-01, SV-04, SV-05, and the
minor finding on the region filter). The iteration-7 version simulated a DIFFERENT rule from the
one the protocol installs, under a blank model the protocol's own §15.5.10 refutes:

  1. DECISION RULE. It scored `D > 1.645 * sd`, a symmetric-normal proxy. §15.5.8 (a) decides on
     the EMPIRICAL 5th percentile of a 2000-resample paired candidate bootstrap of a MIN-over-
     replicates functional. This version runs an inner bootstrap inside every simulation
     replicate and applies the empirical-percentile rule.
  2. n_tau. §15.5.8 (a) RE-DERIVES n_tau from each resample's own scorable_ALT. This version does.
  3. REGION FILTER. §20.4 pools over DISCRIMINATING targets only. §15.5.11's DEGENERATE_HIGH rule
     is applied here exactly as it will be at evaluation, including the B0_scorable anchor.
  4. BLANK CORRELATION. MODEL-I keeps the iteration-7 assumption of three independent blanks.
     MODEL-C sets the effective blank count to 1 (EV-0045: the three TF0 replicates share ~90% of
     their normal reads on HCC1395 and ~45% on COLO829). MODEL-C's figures are the design's
     STATED size and power.
  5. SD INFLATION. Every table is produced at f = 1 and at f = 11.7 (EV-0036's measured
     between-library understatement), so the design has stated operating characteristics under
     its own admitted variance model.
  6. FAMILY-WISE REFUTATION (RESULT 4). §15.5.8 (d)'s rule is now CENTRED — the reference is the
     bootstrap distribution of (D* - D_obs)/null_sd*, not of D*/null_sd — so it has a size and a
     power at all. Both are reported.
  7. RESULT 5. §20.4 installs a conjunction over 4 legs x 2 axes x 2 constructions, and S7 doubles
     it. This script simulates leg (i) on AXIS-L only, so it reports an UPPER BOUND on
     P(S6 HOLDS) rather than pretending the leg-(i) figure is the criterion's.

STATED APPROXIMATIONS OF THIS ADVANCE CALCULATION, which EXEC-002 does not make because it runs
the real bootstrap on the real data:
  A1  The outer realisation draws one latent uniform per scorable blank ALT read per arm and
      thresholds it at q = tau / ratio, so every target is a re-reading of THE SAME reads. That is
      the real dependence structure across targets.
  A2  The inner candidate bootstrap is approximated in COUNT space: scorable_ALT at the level and
      in each blank are resampled as Poisson about their observed values (the bootstrap of a sum
      over gate-passing candidates of 1-2 ALT reads has variance of that order), and the kept
      blank count at each target is drawn about B* * p_hat with ONE standard-normal random effect
      per (blank replicate, resample) shared across targets, so that the bootstrap is JOINT across
      targets as §15.5.8 (d) requires. A per-read resample would be exact and is not affordable at
      this NSIM x B_inner; the approximation preserves the two structures that matter — the joint
      re-reading across targets, and the re-derivation of n_tau inside the resample.
  A3  sample_sd under V1 is sqrt(G). EXEC-001 measures sample_sd/sqrt(G) at 0.97 +- 0.02.
  A4  The two arms' blank draws are independent of each other. EXEC-001 shows their kept blank
      sets largely disjoint at the operating point (B1 keeps 2/0/4 where C2 keeps 0/1/0 on
      COLO829), so this is close and errs toward a WIDER null.
  A5  T95 here is the exact quantile; mrdz/score.py uses a truncated table (4.303 at n = 3). The
      difference is immaterial and is stated in §15.5.9 so a fourth-decimal disagreement between
      this table and EXEC-002's re-run is not reported as a finding.
"""
import numpy as np

T95 = 4.302652729696142
NSIM = 2500            # outer realisations of the experiment
BINNER = 300           # inner bootstrap resamples (the protocol's B = 2000 at evaluation)
SEED = 20260919
UNDEF_CEILING = 0.20   # §15.5.8 (a): >20% undefined resamples -> INADMISSIBLE
DEG_Z = 0.50           # §15.5.11 DEGENERATE_HIGH (i)
DEG_FRAC = 0.80        # §15.5.11 DEGENERATE_HIGH (ii)
TAUS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]

IND = {
    'HCC1395': dict(L=[45, 35, 45], B=[25, 22, 20], ratio=1.6741),
    'COLO829': dict(L=[51, 55, 63], B=[33, 20, 30], ratio=2.9127),
}


def _lo(G, b, vc, f):
    """lo = (G - mb)/sd - f*T95*sdb/sqrt(3)/sd, with mrdz's arithmetic. b is (..., 3)."""
    mb = b.mean(axis=-1)
    sdb = b.std(axis=-1, ddof=1)
    out = np.full(b.shape[:-1] + (3,), np.nan)
    for r in range(3):
        Gr = G[..., r] if np.ndim(G) == np.ndim(b) - 1 + 1 else G[r]
        sd = np.sqrt(np.maximum(Gr, 0.0)) if vc == 'V1' else np.sqrt(np.maximum(mb, 0.0))
        with np.errstate(divide='ignore', invalid='ignore'):
            v = (Gr - mb) / sd - f * T95 * sdb / np.sqrt(3.0) / sd
        out[..., r] = np.where(sd > 0, v, np.nan)
    return out


def _Z(G, b, vc, f):
    L = _lo(G, b, vc, f)
    bad = np.isnan(L).any(axis=-1)
    return np.where(bad, np.nan, np.nanmin(L, axis=-1))


def outer(ind, d, ratio_B1, ratio_comp, model, rng):
    """One set of NSIM realisations. Returns per-tau observed quantities, dependence preserved."""
    nB = d['B']
    U = {}
    for arm in ('B1', 'comp'):
        if model == 'I':
            U[arm] = [rng.random((NSIM, nB[j])) for j in range(3)]
        else:                                   # MODEL-C: effective blank count 1
            base = rng.random((NSIM, max(nB)))
            U[arm] = [base[:, :nB[j]] for j in range(3)]
    res = {}
    for tau in TAUS:
        G = np.array([int(round(tau * x)) for x in d['L']], float)
        cell = {}
        for arm, ratio in (('B1', ratio_B1), ('comp', ratio_comp)):
            q = min(tau / ratio, 1.0)
            b = np.stack([(U[arm][j] < q).sum(axis=1) for j in range(3)], axis=1).astype(float)
            cell[arm] = b
        res[tau] = (G, cell)
    return res


def inner(d, G, b_obs, ratio_arm_b, vc, f, rng, shared):
    """Joint inner bootstrap in count space (approximation A2). Returns D* pieces per arm."""
    Lstar = shared['Lstar']                                  # (NSIM, BINNER, 3)
    Bstar = shared['Bstar']                                  # (NSIM, BINNER, 3)
    e = shared['e']                                          # (NSIM, BINNER, 3) shared across taus
    n_tau = np.rint(shared['tau'] * Lstar)                   # re-derived per resample
    p = np.clip(b_obs[:, None, :] / np.array(d['B'], float)[None, None, :], 0.0, 1.0)
    mean = Bstar * p
    sd = np.sqrt(np.maximum(Bstar * p * (1 - p), 0.0))
    bstar = np.clip(np.rint(mean + sd * e), 0.0, Bstar)
    return _Z(n_tau, bstar, vc, f), n_tau


def run_cell(ind, d, ratio_B1, ratio_comp, model, vc, f, seed):
    rng = np.random.default_rng(seed)
    obs = outer(ind, d, ratio_B1, ratio_comp, model, rng)

    # --- B0_scorable anchor: every scorable ALT read kept, in level and in blanks ---
    b0_b = np.tile(np.array(d['B'], float), (NSIM, 1))
    Z_b0 = _Z(np.array(d['L'], float), b0_b, vc, f)

    # --- one joint inner-bootstrap structure, reused at every target (§15.5.8 d) ---
    Lstar = rng.poisson(np.array(d['L'], float)[None, None, :], (NSIM, BINNER, 3)).astype(float)
    Bstar = rng.poisson(np.array(d['B'], float)[None, None, :], (NSIM, BINNER, 3)).astype(float)
    e = rng.standard_normal((NSIM, BINNER, 3))

    per_tau = {}
    for tau in TAUS:
        G, cell = obs[tau]
        shared = dict(Lstar=Lstar, Bstar=Bstar, e=e, tau=tau)
        Zs, Ds = {}, {}
        for arm in ('B1', 'comp'):
            Zs[arm] = _Z(G, cell[arm], vc, f)
            Ds[arm], n_tau_star = inner(d, G, cell[arm], None, vc, f, rng, shared)
        D_obs = Zs['B1'] - Zs['comp']
        D_star = Ds['B1'] - Ds['comp']                       # (NSIM, BINNER)
        undef = np.isnan(D_star)
        frac_undef = undef.mean(axis=1)
        with np.errstate(invalid='ignore'):
            null_sd_star = np.nanstd(D_star, axis=1, ddof=1)
        delta_lo = np.nanpercentile(np.where(undef, np.nan, D_star), 5, axis=1)
        delta_hi = np.nanpercentile(np.where(undef, np.nan, D_star), 95, axis=1)

        # --- §15.5.6 count floor and §15.5.11 region filter, as installed ---
        floor = ((cell['B1'] >= 1).all(axis=1) & (cell['B1'].sum(axis=1) >= 5) &
                 (cell['comp'] >= 1).all(axis=1) & (cell['comp'].sum(axis=1) >= 5) &
                 ~np.isnan(Zs['B1']) & ~np.isnan(Zs['comp']) & (G.min() >= 5) &
                 (frac_undef <= UNDEF_CEILING) & (null_sd_star > 0))
        near_anchor = (np.maximum(np.abs(Zs['B1'] - Z_b0), np.abs(Zs['comp'] - Z_b0)) < DEG_Z)
        high_keep = all(int(round(tau * x)) >= DEG_FRAC * x for x in d['L'])
        discriminating = floor & ~near_anchor & (not high_keep)

        per_tau[tau] = dict(D_obs=D_obs, D_star=D_star, undef=undef,
                            null_sd_star=null_sd_star,
                            null_sd_obs=np.nanstd(np.where(undef, np.nan, D_star), axis=1, ddof=1),
                            delta_lo=delta_lo, delta_hi=delta_hi, ok=discriminating,
                            n_tau=G)
    return per_tau


def summarise(tag, ind, d, model, f, ratio_comp_factor, seed):
    out = {}
    for vc in ('V1', 'V2'):
        pt = run_cell(ind, d, d['ratio'], d['ratio'] / ratio_comp_factor, model, vc, f, seed)
        out[vc] = pt
    return out


def main():
    rs = np.random.SeedSequence(SEED)
    child = iter(rs.spawn(64))

    print('=== RESULT 1 — per-target size and power, leg (i), AXIS-L, THE RULE AS INSTALLED ===')
    print('(empirical 5th-percentile bootstrap rule; region filter applied; '
          'n_tau re-derived per resample)')
    hdr = (f'{"ind":8s} {"mdl":3s} {"f":5s} {"vc":3s} {"tau":5s} {"n_tau":13s} {"sim_sd_D":8s} '
           f'{"P(discrim)":10s} {"P(hold)H0":9s} {"P(hold)1.5x":11s} {"P(hold)2x":9s}')
    print(hdr)
    store = {}
    for ind, d in IND.items():
        for model in ('I', 'C'):
            for f in (1.0, 11.7):
                h0 = summarise('H0', ind, d, model, f, 1.0, int(next(child).generate_state(1)[0]))
                h15 = summarise('H15', ind, d, model, f, 1.5, int(next(child).generate_state(1)[0]))
                h20 = summarise('H20', ind, d, model, f, 2.0, int(next(child).generate_state(1)[0]))
                store[(ind, model, f)] = (h0, h15, h20)
                for vc in ('V1', 'V2'):
                    for tau in TAUS:
                        a, b, c = h0[vc][tau], h15[vc][tau], h20[vc][tau]
                        ok = a['ok']
                        sd = np.nanmedian(a['null_sd_star'][ok]) if ok.sum() > 50 else np.nan
                        def ph(x):
                            m = x['ok']
                            return (x['delta_lo'][m] > 0).mean() if m.sum() > 50 else np.nan
                        print(f'{ind:8s} {model:3s} {f:5.1f} {vc:3s} {tau:5.2f} '
                              f'{str(list(a["n_tau"].astype(int))):13s} '
                              f'{sd:8.3f} {ok.mean():10.3f} {ph(a):9.3f} {ph(b):11.3f} '
                              f'{ph(c):9.3f}')

    print('\n=== RESULT 2 — the all-target intersection (S6-STRICT), leg (i), AXIS-L ===')
    print(f'{"ind":8s} {"mdl":3s} {"f":5s} {"alt":6s} {"P(>=3 discrim)":15s} '
          f'{"P(HOLDS everywhere)":20s} {"P(some target FAILS)":20s}')
    for (ind, model, f), (h0, h15, h20) in store.items():
        for lbl, h in (('H0', h0), ('1.5x', h15), ('2x', h20)):
            allhold = np.ones(NSIM, bool); anyfail = np.zeros(NSIM, bool); nev = np.zeros(NSIM, int)
            for vc in ('V1', 'V2'):
                for tau in TAUS:
                    x = h[vc][tau]; ok = x['ok']
                    allhold &= (~ok) | (x['delta_lo'] > 0)
                    anyfail |= ok & (x['delta_hi'] < 0)
                    nev += ok.astype(int)
            enough = nev >= 3
            if enough.sum() < 50:
                continue
            print(f'{ind:8s} {model:3s} {f:5.1f} {lbl:6s} {enough.mean():15.3f} '
                  f'{allhold[enough].mean():20.3f} {anyfail[enough].mean():20.3f}')

    print('\n=== RESULT 3 — the POOLED rule §20.4 installs, leg (i), AXIS-L, per cell ===')
    print('(5th percentile of the joint-bootstrap mean over DISCRIMINATING targets of '
          'D*/null_sd*)')
    print(f'{"ind":8s} {"mdl":3s} {"f":5s} {"vc":3s} {"P(hold)H0":9s} {"P(hold)1.5x":11s} '
          f'{"P(hold)2x":9s} {"P(fail)H0":9s}')
    pooled = {}
    for (ind, model, f), (h0, h15, h20) in store.items():
        for vc in ('V1', 'V2'):
            row = {}
            for lbl, h in (('H0', h0), ('1.5x', h15), ('2x', h20)):
                A = []; OK = []
                for tau in TAUS:
                    x = h[vc][tau]
                    with np.errstate(invalid='ignore', divide='ignore'):
                        s = np.where(x['ok'][:, None], x['D_star'] / x['null_sd_star'][:, None],
                                     np.nan)
                    A.append(s); OK.append(x['ok'])
                S = np.nanmean(np.stack(A, axis=2), axis=2)          # (NSIM, BINNER)
                nev = np.stack(OK, axis=1).sum(axis=1)
                lo = np.nanpercentile(S, 5, axis=1)
                hi = np.nanpercentile(S, 95, axis=1)
                m = (nev >= 3) & ~np.isnan(lo)
                row[lbl] = ((lo[m] > 0).mean() if m.sum() > 50 else np.nan,
                            (hi[m] < 0).mean() if m.sum() > 50 else np.nan,
                            m)
            pooled[(ind, model, f, vc)] = row
            print(f'{ind:8s} {model:3s} {f:5.1f} {vc:3s} {row["H0"][0]:9.3f} '
                  f'{row["1.5x"][0]:11.3f} {row["2x"][0]:9.3f} {row["H0"][1]:9.3f}')

    print('\n=== RESULT 4 - the CENTRED family-wise refutation rule of section 15.5.8 (d) ===')
    print('(size under exact equivalence; power when the COMPARATOR is 1.5x / 2x B1)')
    print(f'{"ind":8s} {"mdl":3s} {"f":5s} {"vc":3s} {"size":8s} {"pow 1.5x":9s} {"pow 2x":9s}')

    def fw(h, vc):
        Wmin = None; Mobs = None; nev = np.zeros(NSIM, int)
        for tau in TAUS:
            x = h[vc][tau]
            with np.errstate(invalid='ignore', divide='ignore'):
                W = (x['D_star'] - x['D_obs'][:, None]) / x['null_sd_star'][:, None]
                Mo = x['D_obs'] / x['null_sd_obs']
            W = np.where(x['ok'][:, None], W, np.nan)
            Mo = np.where(x['ok'], Mo, np.nan)
            Wmin = W if Wmin is None else np.fmin(Wmin, W)
            Mobs = Mo if Mobs is None else np.fmin(Mobs, Mo)
            nev += x['ok'].astype(int)
        q05 = np.nanpercentile(Wmin, 5, axis=1)
        m = (nev >= 3) & ~np.isnan(q05) & ~np.isnan(Mobs)
        return (Mobs[m] < q05[m]).mean() if m.sum() > 50 else np.nan

    for (ind, model, f), (h0, h15, h20) in store.items():
        dd = IND[ind]
        r15 = summarise('R15', ind, dd, model, f, 1.0 / 1.5, int(next(child).generate_state(1)[0]))
        r20 = summarise('R20', ind, dd, model, f, 1.0 / 2.0, int(next(child).generate_state(1)[0]))
        for vc in ('V1', 'V2'):
            print(f'{ind:8s} {model:3s} {f:5.1f} {vc:3s} {fw(h0, vc):8.3f} '
                  f'{fw(r15, vc):9.3f} {fw(r20, vc):9.3f}')

    print('\n=== RESULT 5 — UPPER BOUND on the criterion §20.4 actually installs ===')
    print('S6 as installed requires 4 legs x 2 axes x 2 constructions per individual, and S7')
    print('doubles it. This script simulates leg (i) on AXIS-L only. What it can bound:')
    print(f'{"ind":8s} {"mdl":3s} {"f":5s} {"UB P(S6|ind) H0":16s} {"UB 1.5x":9s} {"UB 2x":9s}')
    ub = {}
    for (ind, model, f) in list(store.keys()):
        row = {}
        for lbl in ('H0', '1.5x', '2x'):
            v1 = pooled[(ind, model, f, 'V1')][lbl][0]
            v2 = pooled[(ind, model, f, 'V2')][lbl][0]
            row[lbl] = min(v1, v2)          # an upper bound on the conjunction over constructions
        ub[(ind, model, f)] = row
        print(f'{ind:8s} {model:3s} {f:5.1f} {row["H0"]:16.3f} {row["1.5x"]:9.3f} '
              f'{row["2x"]:9.3f}')
    print('\nUPPER BOUND on P(S6 HOLDS on BOTH individuals) = product of the per-individual')
    print('upper bounds (leg (i), AXIS-L, pooled, both constructions):')
    for model in ('I', 'C'):
        for f in (1.0, 11.7):
            for lbl in ('H0', '1.5x', '2x'):
                a = ub[('HCC1395', model, f)][lbl]; b = ub[('COLO829', model, f)][lbl]
                print(f'  MODEL-{model} f={f:4.1f} {lbl:5s}  <= {a * b:.4f}')
    print('\nP(L-I) = 0 EXACTLY, independently of every figure above: §21 F11 freezes EXEC-001\'s')
    print('retention_ratio values, on which HCC1395 has point(B1) 1.6741 < point(C2) 1.6839, so')
    print('§16.2\'s dominance rule cannot return HOLDS for S5 leg (b) on that individual. See')
    print('§20.6 clause 0b. THE POWER OF S6 AS INSTALLED IS UNKNOWN AND STRICTLY LOWER THAN THE')
    print('LEG-(i) FIGURES ABOVE.')


if __name__ == '__main__':
    main()
