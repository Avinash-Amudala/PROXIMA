"""Scientific regression tests with known answers, separate from performance claims."""
import numpy as np
import pandas as pd
import pytest
from proxima.evaluation.audit import score_effects, decision_metrics, bootstrap_score
from proxima.evaluation.decision_sim import simulate_shipping_decisions
from proxima.models.baseline import score_proxies, compute_diff_in_means_effect
from proxima.evaluation.statistical_tests import compute_proxy_reliability_confidence


def frame(effects):
    rows=[]
    for e,(y,p) in enumerate(effects):
        for treatment in [0,1]:
            for _ in range(3):
                rows.append(dict(exp_id=e,treatment=treatment,long_retained=treatment*y,
                                 proxy=treatment*p,region='A',device='B',tenure='C'))
    return pd.DataFrame(rows)


def test_agreement_is_not_precision_and_regret_is_nonnegative():
    df=frame([(1,-1),(1,-1),(-1,-1),(-1,1)])
    r=simulate_shipping_decisions(df,'proxy')
    assert r.win_rate == .25
    assert r.precision == 0
    assert r.false_positive_rate == .5
    assert r.false_negative_rate == 1
    assert r.avg_regret == .75
    assert r.correct_no_ships == 1


def test_oracle_always_agrees_even_when_no_experiment_should_ship():
    df=frame([(-1,-1),(-2,-2),(0,0)])
    r=simulate_shipping_decisions(df,'long_retained')
    assert r.win_rate == 1 and r.avg_regret == 0
    assert np.isnan(r.precision) and np.isnan(r.false_negative_rate)


def test_negative_orientation_is_applied_before_decisions():
    df=frame([(1,-1),(-1,1)]).rename(columns={'proxy':'rebuffer_rate'})
    r=simulate_shipping_decisions(df,'rebuffer_rate')
    assert r.win_rate == 1 and r.avg_regret == 0


def test_local_truth_not_global_truth_determines_fragility():
    p=np.array([.3,-.3]); y=p.copy()
    local=np.array([[-1,2],[1,-2.]])
    r=score_effects(p,y,local,local)
    assert r['fragility_rate']==0 and r['reliability']==pytest.approx(1)
    flipped=score_effects(p,y,-local,local)
    assert flipped['fragility_rate']==1


def test_missing_local_effect_is_not_a_sign_flip():
    r=score_effects([1,-1],[1,-1],[1,np.nan], [1,-1])
    assert r['fragility_rate']==0


def test_zero_effect_uses_no_ship_rule_consistently():
    r=score_effects([-1,1],[0,1],[-1,1],[0,1])
    assert r['directional_accuracy']==1 and r['fragility_rate']==0


def test_invalid_weights_rejected():
    for w in [(-1,1,1),(.5,.5,.5),(np.nan,0,1)]:
        with pytest.raises(ValueError): score_effects([1],[1],[1],[1],weights=w)


def test_undefined_correlation_is_explicit():
    r=score_effects([1,1],[1,1],[1,1],[1,1])
    assert not r['correlation_defined'] and r['correlation_component']==.5


def test_missing_treatment_arm_is_excluded():
    df=frame([(1,1),(-1,-1),(1,1)])
    df=df[~((df.exp_id==2)&(df.treatment==0))]
    details,_=score_proxies(df,proxy_metrics=['proxy'])
    assert details.iloc[0].n_experiments_scored==2
    assert details.iloc[0].reliability==pytest.approx(1)


def test_scores_and_objects_have_identical_sorted_order():
    df=frame([(1,1),(-1,-1),(2,2)])
    df['bad']=-df.proxy
    details,objects=score_proxies(df,proxy_metrics=['bad','proxy'])
    assert list(details.metric)==[s.metric for s in objects]==['proxy','bad']


def test_bootstrap_retains_multiplicity_and_is_seeded():
    p=np.array([-.4,-.1,.2,.7]);y=np.array([-.2,.2,.1,.8])
    result=bootstrap_score(p,y,p[:,None],y[:,None],seed=17,n_bootstrap=80)
    rng=np.random.default_rng(17);values=[]
    for _ in range(80):
        ids=rng.integers(0,4,4)
        values.append(score_effects(p[ids],y[ids],p[ids],y[ids])['reliability'])
    assert result==pytest.approx(np.quantile(values,[.025,.975]))
    assert result==bootstrap_score(p,y,p[:,None],y[:,None],seed=17,n_bootstrap=80)


def test_row_bootstrap_matches_effect_bootstrap():
    pairs=[(-.2,-.4),(.2,-.1),(.1,.2),(.8,.7)]
    df=frame(pairs)
    score,ci=compute_proxy_reliability_confidence(df,'proxy',n_bootstrap=40,seed=17)
    y,p=np.array(pairs).T
    assert ci==pytest.approx(bootstrap_score(p,y,p[:,None],y[:,None],seed=17,n_bootstrap=40))


def test_decision_metrics_consistent_with_dataframe_api():
    pairs=[(-1,1),(1,-1),(-1,-1),(2,1)]
    r=simulate_shipping_decisions(frame(pairs),'proxy')
    y,p=np.array(pairs).T;m=decision_metrics(p>0,y)
    assert r.win_rate==m['agreement'] and r.avg_regret==m['regret']
    assert r.false_positive_rate==m['fpr']


def test_decisions_use_pairwise_complete_observations():
    df=frame([(1,1),(-1,-1)])
    outlier=df.iloc[[0]].copy()
    outlier['proxy']=1000
    outlier['long_retained']=np.nan
    r=simulate_shipping_decisions(pd.concat([df,outlier]),'proxy')
    assert r.win_rate==1 and r.avg_regret==0


def test_api_undefined_rates_are_json_null(monkeypatch):
    from fastapi.testclient import TestClient
    from proxima.api import main
    from proxima.models.baseline import EARLY_METRICS
    df=frame([(1,1),(2,2),(3,3)])
    for metric in EARLY_METRICS:
        df[metric]=df.proxy*(-1 if metric=='rebuffer_rate' else 1)
    monkeypatch.setattr(main,'current_data',df)
    client=TestClient(main.app)
    response=client.get('/api/decision-simulation')
    assert response.status_code==200
    for result in response.json():
        assert result['false_positive_rate'] is None
        assert result['win_rate']==1
        assert result['precision']==1
        assert result['n_experiments']==3
    response=client.get('/api/proxy-scores')
    assert response.status_code==200
    assert all(r['correlation_defined'] and r['n_segment_cells']==3 for r in response.json())


def test_degenerate_correlation_is_undefined_not_certain_zero():
    from proxima.evaluation.statistical_tests import compute_correlation_significance
    r=compute_correlation_significance(np.ones(5),np.arange(5))
    assert np.isnan(r.test_statistic) and np.isnan(r.confidence_interval_95).all()


def test_paired_superiority_respects_orientation_zero_and_ties():
    from proxima.evaluation.statistical_tests import test_proxy_superiority
    df=frame([(0,-1),(1,1),(-1,-1)])
    df['rebuffer_rate']=-df.proxy
    r=test_proxy_superiority(df,'proxy','rebuffer_rate')
    assert r['proxy1_accuracy']==r['proxy2_accuracy']==1
    assert r['winner'] is None and r['p_value']==1
