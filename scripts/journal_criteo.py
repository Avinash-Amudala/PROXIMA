"""Streaming, observed-data case study of the pooled Criteo treatment comparison.

Uses visit as the single candidate proxy and conversion as the outcome. No
relabeling as watch time/retention; no claim of 50 independent interventions.
"""
from pathlib import Path
import sys, argparse, json, hashlib
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from proxima.evaluation.audit import score_effects,decision_metrics,bootstrap_score


def run(path,out,seed=42,n_partitions=50):
    out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed); pilot_n=100000
    bins=None; total=0;groups=[]
    for index,chunk in enumerate(pd.read_csv(path,usecols=['f0','treatment','visit','conversion'],chunksize=250000)):
        if index==0:
            bins=np.unique(np.quantile(chunk.f0.iloc[:pilot_n],[.25,.5,.75]))
            chunk=chunk.iloc[pilot_n:].copy()
        chunk=chunk.copy();chunk['exp_id']=rng.integers(0,n_partitions,len(chunk))
        chunk['segment']=np.searchsorted(bins,chunk.f0,side='right')
        chunk['n']=1
        groups.append(chunk.groupby(['exp_id','segment','treatment'])[['n','visit','conversion']].sum())
        total+=len(chunk)
    agg=pd.concat(groups).groupby(level=[0,1,2]).sum()
    agg.to_csv(out/'arm_aggregates.csv')
    def effects(frame,metric):
        means=(frame[metric]/frame.n).unstack('treatment')
        return (means[1]-means[0])
    global_agg=agg.groupby(level=[0,2]).sum()
    p=effects(global_agg,'visit');y=effects(global_agg,'conversion')
    sp=effects(agg,'visit').unstack('segment');sy=effects(agg,'conversion').unstack('segment')
    local_ok=(agg.n.unstack('treatment')>=2).all(axis=1).unstack('segment')
    sp,sy=sp.where(local_ok),sy.where(local_ok)
    score=score_effects(p.to_numpy(),y.to_numpy(),sp.to_numpy(),sy.to_numpy())
    ci=bootstrap_score(p.to_numpy(),y.to_numpy(),sp.to_numpy(),sy.to_numpy(),seed=seed)
    metrics=decision_metrics(p.to_numpy()>0,y.to_numpy())
    always=decision_metrics(np.ones(len(y),bool),y.to_numpy())
    never=decision_metrics(np.zeros(len(y),bool),y.to_numpy())
    pd.DataFrame({'proxy_effect':p,'outcome_effect':y}).to_csv(out/'effects.csv')
    sp.to_csv(out/'segment_proxy_effects.csv');sy.to_csv(out/'segment_outcome_effects.csv')
    hasher=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):hasher.update(block)
    result=dict(evidence_type='observed outcomes from a pooled randomized treatment comparison, randomly partitioned',
                source='https://go.criteo.net/criteo-research-uplift-v2.1.csv.gz',sha256=hasher.hexdigest(),
                total_rows=total+pilot_n,pilot_rows=pilot_n,analysis_rows=total,seed=seed,
                partitions=n_partitions,segment_cutpoints=bins.tolist(),n_segments=len(bins)+1,
                score=score,conditional_partition_bootstrap_ci=ci,visit_decisions=metrics,
                always_ship=always,never_ship=never,
                note='Intervals describe resampling partitions, not uncertainty over distinct interventions. Conversion is not an observed long-term retention outcome.')
    def clean(obj):
        if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items()}
        if isinstance(obj,(list,tuple)):return [clean(v) for v in obj]
        if isinstance(obj,float) and not np.isfinite(obj):return None
        return obj
    (out/'summary.json').write_text(json.dumps(clean(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(clean(result),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=Path('Data/criteo-uplift-v2.1.csv.gz'))
    p.add_argument('--output',type=Path,default=Path('paper/journal/results/criteo'))
    a=p.parse_args();run(a.data,a.output)
