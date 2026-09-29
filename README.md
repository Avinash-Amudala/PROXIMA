# PROXIMA: proxy decision auditing

PROXIMA reports effect correlation, overall decision agreement, and within-segment proxy disagreement. Its optional weighted score is descriptive: it is not a calibrated probability of reliability or protection against distribution shift.

**Current research artifact:** [journal manuscript and reproduction instructions](paper/journal/README.md). This September 2026 revision supersedes the numerical claims in the earlier preprint and legacy documents. It is a submission preparation, not an accepted or published journal article.

## What the evaluation establishes

- Four disclosed synthetic settings, 100 independent repetitions each, with separate training and test experiment corpora.
- Component ablations, fixed candidates, uniform proxy selection, and always/never-ship baselines.
- A Criteo observed-data illustration using visit and conversion, with original randomized assignments. Its 50 random partitions do not represent 50 independent interventions; all favor treatment, and always shipping matches perfect agreement.
- Explicit failure under a targeted calibration shift. The default composite trades some global accuracy for lower local error relative to decision-only selection; a simpler comparator can outperform it.

The old KuaiRec workflow generates outcomes using user covariates. It is **semi-synthetic demonstration code**, not evidence of observed randomized long-term effects. Legacy manuscripts, result summaries, patent drafts, and application demos are retained for provenance and are not the current scientific evidence. See [revision audit](paper/journal/REVISION_AUDIT.md).

## Reproduce the current study

Python 3.13 is the verified environment. Run from the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-journal.txt
python -m pip install --no-deps -e .
python -m pytest
python scripts/reproduce_all.py
python scripts/build_journal_assets.py
```

For the observed-data illustration, download the original dataset under its provider's terms and pass its local path:

```sh
python scripts/reproduce_all.py --criteo Data/criteo-uplift-v2.1.csv.gz
python scripts/build_journal_assets.py
cd paper/journal
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The source, checksum, row counts, license, and full protocol are in [the artifact guide](paper/journal/README.md). Raw data are not redistributed. Recorded aggregate results allow table generation without the raw dataset.

## Implementation

- `src/proxima/evaluation/audit.py`: effect-level score, decision metrics, and experiment-block bootstrap.
- `src/proxima/models/baseline.py`: participant-level differences in means and local diagnostics.
- `scripts/journal_benchmark.py`: independent synthetic training/test corpora.
- `scripts/journal_criteo.py`: streaming observed-data illustration.
- `tests/test_journal_regressions.py`: known-answer regression checks.

The API and dashboard are demonstrations. Their generated data do not establish external validity. `win_rate` now means agreement across all eligible decisions; `precision` is separate. Undefined rates remain undefined rather than becoming zero. The old score's population-discordance calculation is now reported separately from local proxy error. These semantic corrections can change results from old notebooks and scripts.

## Author and licensing

Avinash Amudala · Rochester Institute of Technology · aa9429@g.rit.edu · [ORCID 0009-0000-7226-6156](https://orcid.org/0009-0000-7226-6156)

Project code is MIT-licensed; third-party datasets and the IEEE template retain their own terms. See [third-party notice](paper/journal/THIRD_PARTY_NOTICES.md). Earlier preprint: [arXiv:2604.14352](https://arxiv.org/abs/2604.14352).
