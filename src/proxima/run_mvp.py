"""
Main MVP Runner for PROXIMA

Generates synthetic data, trains models, scores proxies, and produces visualizations.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from proxima.generator.simulate import generate_synthetic_experiments
from proxima.models.baseline import (
    train_long_term_model,
    score_proxies,
    find_top_fragility_segments,
    EARLY_METRICS
)
from proxima.evaluation.decision_sim import compare_decision_strategies
from proxima.visualization.plots import (
    plot_reliability_comparison,
    plot_all_proxy_correlations,
    plot_fragility_heatmap,
    plot_decision_simulation_results
)


def main(
    n_users: int = 250_000,
    n_experiments: int = 50,
    seed: int = 7,
    output_dir: str = "outputs"
):
    """
    Run the complete PROXIMA MVP pipeline.
    
    Args:
        n_users: Number of user observations to generate
        n_experiments: Number of experiments to simulate
        seed: Random seed for reproducibility
        output_dir: Directory to save outputs
    """
    print("=" * 80)
    print("PROXIMA: Proxy Metric Intelligence for Online Experiments")
    print("=" * 80)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    figures_path = output_path / "figures"
    figures_path.mkdir(exist_ok=True)
    
    # 1. Generate synthetic data
    print(f"\n[1/6] Generating synthetic experiment data...")
    print(f"  - Users: {n_users:,}")
    print(f"  - Experiments: {n_experiments}")
    print(f"  - Seed: {seed}")
    
    df = generate_synthetic_experiments(n_users=n_users, n_experiments=n_experiments, seed=seed)
    
    # Save data
    data_path = output_path / "synthetic_data.csv"
    df.to_csv(data_path, index=False)
    print(f"  ✓ Data saved to {data_path}")
    print(f"  - Shape: {df.shape}")
    print(f"  - Failure cohort size: {df['failure_cohort'].sum():,} ({df['failure_cohort'].mean():.1%})")
    
    # 2. Train long-term model
    print(f"\n[2/6] Training long-term outcome model...")
    model, auc = train_long_term_model(df)
    print(f"  ✓ Model trained")
    print(f"  - ROC-AUC: {auc:.4f}")
    
    # 3. Score proxies
    print(f"\n[3/6] Scoring proxy metrics...")
    details, proxy_scores = score_proxies(df)
    print(f"  ✓ Proxy scoring complete")
    print("\n" + "=" * 80)
    print("PROXY RELIABILITY RANKING")
    print("=" * 80)
    print(details.to_string(index=False))
    print("=" * 80)
    
    # Save proxy scores
    scores_path = output_path / "proxy_scores.csv"
    details.to_csv(scores_path, index=False)
    print(f"\n  ✓ Scores saved to {scores_path}")
    
    # 4. Find fragile segments
    print(f"\n[4/6] Detecting fragile segments...")
    top_metric = details.iloc[0]["metric"]
    frag = find_top_fragility_segments(df, top_metric, min_count=400)
    print(f"\n  Most fragile segments for '{top_metric}':")
    print(frag.head(10).to_string(index=False))
    
    frag_path = output_path / f"fragility_{top_metric}.csv"
    frag.to_csv(frag_path, index=False)
    print(f"\n  ✓ Fragility analysis saved to {frag_path}")
    
    # 5. Decision simulation
    print(f"\n[5/6] Running decision simulation...")
    decision_results = compare_decision_strategies(df, EARLY_METRICS)
    print("\n" + "=" * 80)
    print("DECISION SIMULATION RESULTS")
    print("=" * 80)
    print(decision_results.to_string(index=False))
    print("=" * 80)
    
    decision_path = output_path / "decision_simulation.csv"
    decision_results.to_csv(decision_path, index=False)
    print(f"\n  ✓ Decision results saved to {decision_path}")
    
    # 6. Generate visualizations
    print(f"\n[6/6] Generating visualizations...")
    
    # Reliability comparison
    plot_reliability_comparison(details, save_path=figures_path / "reliability_comparison.png", show=False)
    print(f"  ✓ Reliability comparison plot saved")
    
    # All proxy correlations
    plot_all_proxy_correlations(df, EARLY_METRICS, save_path=figures_path / "proxy_correlations.png", show=False)
    print(f"  ✓ Proxy correlation plots saved")
    
    # Fragility heatmap
    plot_fragility_heatmap(df, top_metric, segment_cols=["region", "device"], 
                          save_path=figures_path / f"fragility_heatmap_{top_metric}.png", show=False)
    print(f"  ✓ Fragility heatmap saved")
    
    # Decision simulation results
    plot_decision_simulation_results(decision_results, 
                                    save_path=figures_path / "decision_simulation.png", show=False)
    print(f"  ✓ Decision simulation plots saved")
    
    print("\n" + "=" * 80)
    print("PROXIMA MVP COMPLETE!")
    print("=" * 80)
    print(f"\nAll outputs saved to: {output_path.absolute()}")
    print(f"Figures saved to: {figures_path.absolute()}")
    print("\nKey findings:")
    print(f"  - Best proxy: {details.iloc[0]['metric']} (reliability: {details.iloc[0]['reliability']:.3f})")
    print(f"  - Worst proxy: {details.iloc[-1]['metric']} (reliability: {details.iloc[-1]['reliability']:.3f})")
    print(f"  - Best decision win rate: {decision_results.iloc[0]['win_rate']:.1%} ({decision_results.iloc[0]['proxy_metric']})")
    print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PROXIMA MVP pipeline")
    parser.add_argument("--n-users", type=int, default=250_000, help="Number of users to generate")
    parser.add_argument("--n-experiments", type=int, default=50, help="Number of experiments")
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Output directory")
    
    args = parser.parse_args()
    main(args.n_users, args.n_experiments, args.seed, args.output_dir)

