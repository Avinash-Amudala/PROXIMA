# Verification record

- Python 3.13.7, package versions pinned in requirements-journal.txt.
- 65 tests passed, including known-answer scientific regressions and JSON API behavior. One upstream Starlette/httpx deprecation warning remains.
- A separate complete rerun reproduced all nine CSV result files byte for byte. See reproduction-verification.json.
- pdfLaTeX completed twice with no errors, unresolved citations or unresolved cross-references. All seven pages were rendered and visually inspected. Template-origin header/footer box notices remain; no clipped body text or overlapping equations were observed.
- Generated tables and figure read the stored results. No numeric performance values were invented or manually inserted into outputs.
- Source and result manifests bind the current calculations to their artifacts. Raw Criteo data were not committed.

These checks verify execution, reproducibility and presentation, not editorial acceptance or external validity. Author scientific review remains to be completed before journal submission.
