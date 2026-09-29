"""Reproducible, explicitly synthetic held-out experiment benchmark.

No result from this generator is described as an observed platform experiment.
Candidate order, weights, scenarios and seeds are fixed, not selected by outcomes.
"""
from pathlib import Path
import sys, json, argparse, hashlib, platform, subprocess
import numpy as np
import pandas as pd
from scipy.stats import t
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from proxima.evaluation.audit import score_effects, decision_metrics

CANDIDATES = ['faithful', 'offset', 'local_reversal', 'unrelated']
WEIGHTS = {'PROXIMA':(.6,.2,.2), 'Correlation':(1.,0.,0.),
           'Decision only':(0.,1.,0.), 'Local only':(0.,0.,1.),
           'Equal weights':(1/3,1/3,1/3), 'No local component':(.75,.25,0.)}
SCENARIOS = {'balanced':(.04,.08,False), 'heterogeneous':(.04,.20,False),
             'noisy':(.12,.08,False), 'shifted':(.04,.08,True)}

def corpus(rng, n, noise, heterogeneity, drift=False):
    global_truth = rng.normal(0,.12,n)
    deviations = rng.normal(0,heterogeneity,(n,5))
    deviations -= deviations.mean(axis=1,keepdims=True)
    truth = global_truth[:,None]+deviations
    faithful = truth + rng.normal(0,.06,(n,5)) + (.20 if drift else 0.)
    candidate_truth = np.stack([faithful,truth+.12,global_truth[:,None]-deviations,
                                rng.normal(0,.20,(n,5))])
    shared = rng.normal(0,noise,(n,5))
    outcome = truth + shared
    proxy = candidate_truth + .3*shared[None,:,:] + np.sqrt(.91)*rng.normal(0,noise,candidate_truth.shape)
    return truth, outcome, proxy


def evaluate(proxy,truth):
    pglobal=proxy.mean(axis=1); yglobal=truth.mean(axis=1)
    metrics=decision_metrics(pglobal>0,yglobal)
    metrics['local_error']=float(np.mean((proxy>0)!=(truth>0)))
    return metrics


def run(out, repetitions=100, n_train=60, n_test=60, seed=20260928):
    out.mkdir(parents=True,exist_ok=True)
    records=[]; selections=[]; all_scores=[]
    for scenario_index,(scenario,(noise,het,shift)) in enumerate(SCENARIOS.items()):
        for rep in range(repetitions):
            rng=np.random.default_rng(np.random.SeedSequence([seed,scenario_index,rep]))
            _, train_y, train_p = corpus(rng,n_train,noise,het)
            truth,test_y,test_p = corpus(rng,n_test,noise,het,shift)
            scores=[score_effects(p.mean(1),train_y.mean(1),p,train_y) for p in train_p]
            component=np.array([[s['correlation_component'],s['directional_accuracy'],1-s['fragility_rate']] for s in scores])
            for j,s in enumerate(scores):
                all_scores.append(dict(scenario=scenario,replicate=rep,proxy=CANDIDATES[j],**s))
            for method,w in WEIGHTS.items():
                j=int(np.argmax(component@np.asarray(w)))
                m=evaluate(test_p[j],truth)
                selections.append(dict(scenario=scenario,replicate=rep,method=method,selected=CANDIDATES[j]))
                records.append(dict(scenario=scenario,replicate=rep,method=method,**m))
            candidate_metrics=[evaluate(p,truth) for p in test_p]
            for j,m in enumerate(candidate_metrics):
                records.append(dict(scenario=scenario,replicate=rep,method='Fixed '+CANDIDATES[j],**m))
            # Exact expectation under uniform proxy selection, not random coin-flip decisions.
            records.append(dict(scenario=scenario,replicate=rep,method='Uniform proxy',
                                **{k:float(np.mean([m[k] for m in candidate_metrics])) for k in ['agreement','regret','local_error']}))
            for method,decision in [('Always ship',True),('Never ship',False)]:
                m=decision_metrics(np.full(n_test,decision),truth.mean(1))
                m['local_error']=float(np.mean(np.full(truth.shape,decision)!=(truth>0)))
                records.append(dict(scenario=scenario,replicate=rep,method=method,**m))
    records=pd.DataFrame(records)
    records.to_csv(out/'replicates.csv',index=False,float_format='%.12g')
    pd.DataFrame(selections).to_csv(out/'selections.csv',index=False)
    pd.DataFrame(all_scores).to_csv(out/'training_scores.csv',index=False,float_format='%.12g')
    summary=[]
    for (scenario,method),g in records.groupby(['scenario','method'],sort=False):
        for metric in ['agreement','regret','local_error']:
            values=g[metric].to_numpy();mean=float(values.mean())
            se=float(values.std(ddof=1)/np.sqrt(len(values)))
            half=float(t.ppf(.975,len(values)-1)*se)
            summary.append(dict(scenario=scenario,method=method,metric=metric,mean=mean,mcse=se,ci_low=mean-half,ci_high=mean+half))
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False,float_format='%.12g')
    # Paired Monte Carlo comparisons preserve the common train/test corpus.
    paired=[]
    for scenario,g in records.groupby('scenario'):
        for metric in ['agreement','regret','local_error']:
            table=g.pivot(index='replicate',columns='method',values=metric)
            for comparator in ['Correlation','Decision only','Local only','Equal weights','No local component']:
                d=table.PROXIMA-table[comparator];se=float(d.std(ddof=1)/np.sqrt(len(d)))
                paired.append(dict(scenario=scenario,metric=metric,comparator=comparator,difference=float(d.mean()),mcse=se,ci_low=float(d.mean()-t.ppf(.975,len(d)-1)*se),ci_high=float(d.mean()+t.ppf(.975,len(d)-1)*se)))
    pd.DataFrame(paired).to_csv(out/'paired_comparisons.csv',index=False,float_format='%.12g')
    metadata=dict(seed=seed,repetitions=repetitions,n_train=n_train,n_test=n_test,segments=5,
                  scenario_parameters=SCENARIOS,weights=WEIGHTS,candidate_order=CANDIDATES,
                  python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
                  evidence_type='fully synthetic Gaussian effect-estimate simulation',
                  tie_break='first candidate in declared order',
                  uncertainty='95% t intervals over independent Monte Carlo replicate means; exploratory, no familywise correction',
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(pd.DataFrame(summary).query("metric == 'agreement' and method in ['PROXIMA','Correlation','Decision only']").to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('paper/journal/results/simulation'))
    p.add_argument('--repetitions',type=int,default=100);p.add_argument('--seed',type=int,default=20260928)
    a=p.parse_args()
    if a.repetitions < 2: p.error('at least two repetitions required')
    run(a.output,repetitions=a.repetitions,seed=a.seed)
