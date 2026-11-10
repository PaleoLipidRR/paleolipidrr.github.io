# TEXAS publication day

Until the TEXAS paper is published, /projects/ shows a TEXAS card (from `_data/upcoming_projects.yml`) whose only link is the ESSOAr preprint. The full project page, its figures and the S-curve explorer are kept out of this public repository; restore them from the saved `texas-full-local` branch (git bundle).

1. Restore from the bundle: `_projects/texas.md`, `_includes/texas_scurve_explorer.liquid`, `_data/texas_params.yml`, and the figures into `assets/img/projects/texas/`.
   The bundle was written for the pre-v1 theme. The site now runs on al-folio v1 (no jQuery, no Bootstrap or MDB JavaScript, and a Content-Security-Policy meta tag on every page), so rebuild locally and test the S-curve explorer in a browser with the console open before publishing.
2. `_projects/texas.md`: delete `published: false` (and the comment above it); set `status: published`, fill in `doi:` (and `pdf:` if open access).
3. `_data/upcoming_projects.yml`: delete the `texas` entry.
4. `_bibliography/papers.bib`: paste in `texas.bib` (this folder); add `doi`, `url`, `volume`, `pages`, `altmetric`, `dimensions={true}`; drop `note = {Under review}`. Remove the ESSOAr TEXAS entry from `preprints.bib`.
5. `_includes/research_program_diagram.liquid`: change the TEXAS box from "under review" to the journal.
6. `_news/`: add an announcement linking to /projects/texas/.
7. Build, then check /projects/, /projects/texas/, and the TEXAS links on the PNAS and GRL pages (they turn into links automatically).
