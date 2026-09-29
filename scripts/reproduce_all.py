"""Reproduce the current journal benchmark and optional Criteo case study.

This intentionally does not reproduce superseded preprint numbers. See
paper/journal/README.md for evidence provenance and exact commands.
"""
import argparse
from pathlib import Path
from journal_benchmark import run as simulation
from journal_criteo import run as criteo

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=int,default=20260928)
    p.add_argument('--repetitions',type=int,default=100)
    p.add_argument('--criteo',type=Path)
    p.add_argument('--output-dir',type=Path,default=Path('paper/journal/results'))
    a=p.parse_args()
    simulation(a.output_dir/'simulation',repetitions=a.repetitions,seed=a.seed)
    if a.criteo: criteo(a.criteo,a.output_dir/'criteo')
