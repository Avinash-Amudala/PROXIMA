# Revision audit — September 2026

Base public repository commit: `418a4ef3bdda0ceb14d15b3ac54f0f091b59db36`.

## Corrections

1. `win_rate` previously measured precision among shipped experiments, excluding correct no-ship decisions. It now measures overall agreement; precision is separate.
2. Regret previously subtracted missed benefits and could be negative. It now adds nonnegative losses from harmful launches and missed benefits.
3. Local fragility previously compared segment proxy signs to the overall outcome. It now compares proxy and outcome within the same segment. Population discordance remains a separate diagnostic.
4. `rebuffer_rate` is oriented as lower-is-better. Zero effects mean no ship. Missing arms/cells are excluded; undefined denominators are not zero error.
5. Experiment bootstrap draws previously could collapse duplicate experiment IDs. Draw multiplicity is now preserved with new block identifiers; fixed local random generators support repeatability.
6. Welch degrees of freedom and pooled variance calculations were corrected. Constant or undersized correlation inputs are guarded.
7. The original reproduction entry point referenced unavailable interfaces. The new entry point executes the disclosed journal protocol.
8. Incorrect proxy-selection citation authors were replaced after checking the cited primary source. The elementary score proposition now states the strictly-positive-weight condition for its endpoint characterization.

## Evidence replaced

The manuscript does not reuse earlier claims of 98.4% oracle agreement, an assumed 50% random baseline, universal superiority, or independent advertising/recommendation validation. The KuaiRec workflow generated treatment/outcome values and cannot substantiate observed long-term effects. Criteo's pooled treatment data are an illustration, not an experiment corpus. New results come from executable, held-out simulations and a transparently delimited observed-data analysis.

## Interpretation and limitations

The corrected manuscript reports competitive simpler baselines and the targeted calibration-shift failure. This improves validity but does not guarantee that the contribution is sufficiently novel for a particular journal. No editor, reviewer, or immigration adjudicator has approved this revision. Author review remains necessary for the scientific claims, affiliation, biography, AI disclosure, and funding statement.

Original local paper sources remain in `paper/`, clearly marked as superseded. The original Overleaf `main.tex` was preserved as `original-main-20260928.tex`. Legacy documents remain historical records, not current evidence.
