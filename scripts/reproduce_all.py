#!/usr/bin/env python3
"""
Reproduce All Paper Results for PROXIMA

This script regenerates all figures and tables from the PROXIMA paper.
Run with: python scripts/reproduce_all.py

Expected outputs:
- outputs/paper_figures/figure1_proxy_reliability.png
- outputs/paper_figures/figure2_decision_simulation.png
- outputs/paper_figures/summary_table.csv

Author: Avinash Amudala
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

import argparse
import json
from datetime import datetime

# PROXIMA imports
from proxima.generator.simulate import generate_synthetic_experiments
from proxima.models.baseline import ProxyScorer
from proxima.evaluation.decision_sim import DecisionSimulator
from proxima.visualization.plots import (
    plot_proxy_reliability,
    plot_decision_simulation,
)


def main():
    parser = argparse.ArgumentParser(description="Reproduce PROXIMA paper results")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--n_users", type=int, default=250000, help="Number of users to simulate")
    parser.add_argument("--n_experiments", type=int, default=50, help="Number of experiments")
    parser.add_argument("--output_dir", type=str, default="outputs/paper_figures", help="Output directory")
    args = parser.parse_args()

    print("=" * 60)
    print("PROXIMA Paper Reproduction Script")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Seed: {args.seed}")
    print("=" * 60)

    # Create output directory
    output_dir = ROOT_DIR / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate synthetic data
    print("\n[1/4] Generating synthetic experiment data...")
    experiments = generate_synthetic_experiments(
        n_users=args.n_users,
        n_experiments=args.n_experiments,
        seed=args.seed,
    )
    print(f"  Generated {len(experiments)} experiments with {args.n_users} users each")

    # Step 2: Score proxies
    print("\n[2/4] Computing proxy reliability scores...")
    scorer = ProxyScorer()
    proxy_scores = scorer.score_all(experiments)
    
    print("\n  Proxy Reliability Scores:")
    print("  " + "-" * 50)
    for metric, scores in proxy_scores.items():
        print(f"  {metric:20s} | Reliability: {scores['reliability']:.3f} | "
              f"Corr: {scores['correlation']:.3f} | DA: {scores['directional_accuracy']:.3f}")

    # Step 3: Run decision simulation
    print("\n[3/4] Running decision simulation...")
    simulator = DecisionSimulator()
    decision_results = simulator.simulate_all(experiments, proxy_scores)
    
    print("\n  Decision Simulation Results:")
    print("  " + "-" * 50)
    for metric, results in decision_results.items():
        print(f"  {metric:20s} | Win Rate: {results['win_rate']:.3f} | "
              f"FPR: {results['fpr']:.3f} | FNR: {results['fnr']:.3f}")

    # Step 4: Generate figures
    print("\n[4/4] Generating paper figures...")
    
    # Figure 1: Proxy reliability
    fig1_path = output_dir / "figure1_proxy_reliability.png"
    plot_proxy_reliability(proxy_scores, save_path=str(fig1_path))
    print(f"  Saved: {fig1_path}")
    
    # Figure 2: Decision simulation
    fig2_path = output_dir / "figure2_decision_simulation.png"
    plot_decision_simulation(decision_results, save_path=str(fig2_path))
    print(f"  Saved: {fig2_path}")
    
    # Summary table
    summary_path = output_dir / "summary_table.csv"
    _save_summary_table(proxy_scores, decision_results, summary_path)
    print(f"  Saved: {summary_path}")

    # Save reproduction metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "seed": args.seed,
        "n_users": args.n_users,
        "n_experiments": args.n_experiments,
        "python_version": sys.version,
    }
    metadata_path = output_dir / "reproduction_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: {metadata_path}")

    print("\n" + "=" * 60)
    print("Reproduction complete!")
    print(f"All outputs saved to: {output_dir}")
    print("=" * 60)


def _save_summary_table(proxy_scores: dict, decision_results: dict, path: Path):
    """Save summary table as CSV."""
    import csv
    
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "reliability", "correlation", "directional_accuracy", 
                         "fragility_rate", "win_rate", "fpr", "fnr", "regret"])
        
        for metric in proxy_scores:
            ps = proxy_scores[metric]
            dr = decision_results.get(metric, {})
            writer.writerow([
                metric,
                f"{ps.get('reliability', 0):.4f}",
                f"{ps.get('correlation', 0):.4f}",
                f"{ps.get('directional_accuracy', 0):.4f}",
                f"{ps.get('fragility_rate', 0):.4f}",
                f"{dr.get('win_rate', 0):.4f}",
                f"{dr.get('fpr', 0):.4f}",
                f"{dr.get('fnr', 0):.4f}",
                f"{dr.get('regret', 0):.4f}",
            ])


if __name__ == "__main__":
    main()

