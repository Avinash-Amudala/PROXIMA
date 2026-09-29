"""Auditable effect-level scores and decisions used by the journal experiments.

All metrics must be oriented so positive means beneficial. Scores are descriptive,
not calibrated probabilities. Zero effects map to no-ship. Undefined denominators
are NaN, never evidence of zero error. Segment arrays may be E x S or flattened.
"""
from __future__ import annotations
import numpy as np


def score_effects(proxy, outcome, local_proxy, local_outcome, *, direction=1,
                  weights=(0.6, 0.2, 0.2)):
    w = np.asarray(weights, dtype=float)
    if w.shape != (3,) or not np.isfinite(w).all() or (w < 0).any() or not np.isclose(w.sum(), 1):
        raise ValueError("Three finite nonnegative weights must sum to one")
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or +1")
    p, y = np.asarray(proxy, float), np.asarray(outcome, float)
    sp, sy = np.asarray(local_proxy, float), np.asarray(local_outcome, float)
    if p.shape != y.shape or sp.shape != sy.shape:
        raise ValueError("Paired effects must have matching shapes")
    ok = np.isfinite(p) & np.isfinite(y)
    p, y = direction * p[ok], y[ok]
    if not len(p):
        raise ValueError("No finite paired experiment effects")
    defined = len(p) >= 2 and np.std(p) > 1e-12 and np.std(y) > 1e-12
    corr = float(np.clip(np.corrcoef(p, y)[0, 1], -1, 1)) if defined else 0.0
    # Neutral imputation is explicit, not an estimated zero correlation.
    c = (corr + 1) / 2
    da = float(np.mean((p > 0) == (y > 0)))
    sok = np.isfinite(sp) & np.isfinite(sy)
    fr = float(np.mean((direction * sp[sok] > 0) != (sy[sok] > 0))) if sok.any() else float('nan')
    reliability = w[0]*c + w[1]*da + w[2]*(1-fr) if np.isfinite(fr) else float('nan')
    return dict(reliability=float(reliability), effect_corr=corr, correlation_defined=bool(defined),
                correlation_component=c, directional_accuracy=da, fragility_rate=fr)


def decision_metrics(decision, outcome, threshold=0.0):
    decision, outcome = np.asarray(decision, bool), np.asarray(outcome, float)
    if decision.shape != outcome.shape or not outcome.size or not np.isfinite(outcome).all():
        raise ValueError("Decisions and finite outcomes must have the same nonempty shape")
    true = outcome > threshold
    tp, fp = int((decision & true).sum()), int((decision & ~true).sum())
    fn, tn = int((~decision & true).sum()), int((~decision & ~true).sum())
    ratio = lambda n, d: n/d if d else float('nan')
    return dict(agreement=float(np.mean(decision == true)), precision=ratio(tp,tp+fp),
                fpr=ratio(fp,fp+tn), fnr=ratio(fn,tp+fn),
                regret=float(np.mean(np.abs(outcome-threshold)*(decision != true))),
                tp=tp,fp=fp,fn=fn,tn=tn,n=int(outcome.size))


def bootstrap_score(proxy, outcome, local_proxy, local_outcome, *, seed=42,
                    n_bootstrap=1000, alpha=0.05, weights=(0.6,0.2,0.2)):
    """Experiment-block percentile interval; repeated draws retain multiplicity.

    The first dimension indexes experiments in every array. Within-experiment
    segment dependence is preserved. This is conditional on the measured effects;
    it does not correct measurement error or distribution shift.
    """
    p,y,sp,sy = map(lambda x: np.asarray(x,float), (proxy,outcome,local_proxy,local_outcome))
    if p.ndim != 1 or y.shape != p.shape or sp.shape != sy.shape or sp.shape[0] != len(p) or len(p) < 2:
        raise ValueError("Need at least two experiments and aligned segment arrays")
    if not 0 < alpha < 1 or n_bootstrap < 2:
        raise ValueError("Invalid bootstrap count or alpha")
    rng = np.random.default_rng(seed)
    values=[]
    for _ in range(n_bootstrap):
        idx=rng.integers(0,len(p),len(p))
        values.append(score_effects(p[idx],y[idx],sp[idx],sy[idx],weights=weights)['reliability'])
    values=np.asarray(values)
    if not np.isfinite(values).all():
        raise ValueError("Bootstrap produced undefined scores; inspect segment availability")
    return tuple(map(float,np.quantile(values,[alpha/2,1-alpha/2])))
