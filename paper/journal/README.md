# Current journal artifact

The canonical manuscript is `main.tex`, formatted using the official IEEE Access LaTeX template released May 13, 2026. `main.pdf` is the corresponding rendered manuscript. This is an author-review draft for submission, not an acceptance guarantee. The earlier repository papers and arXiv v1 are superseded for numerical claims.

## Reproduction

Use the root README commands and the pinned `requirements-journal.txt`. The full default simulation runs 100 repetitions in each of four settings with 60 training and 60 test experiments and five segments. Outputs are under `results/simulation`; each repetition and method is retained. The master seed is 20260928. Criteo uses seed 42.

To regenerate all results into an independent directory:

```sh
python scripts/reproduce_all.py --criteo Data/criteo-uplift-v2.1.csv.gz --output-dir /tmp/proxima-results
```

To regenerate manuscript tables/figures from recorded outputs, run `python scripts/build_journal_assets.py`. The generated tables must not be edited manually. Two pdfLaTeX passes build `main.pdf`. The original class and font assets are bundled unchanged. The class emits box warnings from its header/footer machinery; inspect the PDF rather than treating these as scientific errors.

## Dataset provenance

Source page: https://ailab.criteo.com/criteo-uplift-prediction-dataset/

Data: https://go.criteo.net/criteo-research-uplift-v2.1.csv.gz

SHA-256: `2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc`

License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0, as stated by the provider. Consult the source terms before downloading or reusing the dataset. Raw rows are excluded from Git. Criteo-derived aggregates retain the source attribution and applicable dataset terms; the project's MIT license does not override them.

There are 13,979,592 rows. The first 100,000 establish quartile boundaries of f0 and are excluded. The remaining 13,879,592 observations retain the original treatment labels and are randomly assigned to 50 analysis partitions. Visit is the only proxy; conversion is the outcome. Neither is renamed retention. The public pooled data do not expose the intervention identifiers needed to evaluate generalization across independent interventions.

The case-study bootstrap resamples these partitions and is conditional on that construction. It is not uncertainty over a population of product experiments. The all-positive reference class makes a false-positive rate undefined. Always-ship agreement is 1.0, like the visit proxy. No inference about long-horizon prediction follows from this result.

## Artifact map

- `results/simulation/`: all repetition-level outputs, component scores, selections, summaries, paired comparisons, metadata.
- `results/criteo/`: observed arm aggregates, effect estimates, segment estimates, summary and source checksum.
- `generated/`: tables and scientific figure derived from those files.
- `results-manifest.json`: SHA-256 output inventory.
- `REVISION_AUDIT.md`: corrections and scope changes.
- `SUBMISSION_CHECKLIST.md`: remaining author/submission actions.
- `cover-letter.md`: a draft for author review; not sent.

The study is exploratory. Monte Carlo intervals quantify variation across the specified simulated corpora, not real-world generalization. The default weights are heuristic. External validation on a genuine multi-intervention, long-horizon corpus remains a substantive research opportunity.
