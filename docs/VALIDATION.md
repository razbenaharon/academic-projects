# Validation and Known Limitations

Publication preparation: 2026-10-02. This is a collection of separate coursework environments,
not a claim that every project runs on a fresh laptop.

## Completed checks

- Thirteen deterministic local regression cases pass (`python -m pytest tests -q`).
  They cover Minkowski KNN against scikit-learn without vote ties, deterministic tie
  handling, perceptron convergence/termination, manual MLP gradients against autograd,
  CNN/VAE forward shapes, exact vector deletion/reinsertion and influence simulation/imports.
- Python files and ordinary Python notebook cells receive AST syntax checks. Notebook
  magic cells are treated separately; Databricks SQL/magic cells are not parsed as Python.
- Rush Hour and bit-operation C sources pass GCC C11 syntax checks. Rush Hour emits
  warnings for unused parameters/variables; gameplay was not exhaustively tested.
- README relative links are checked, and restored demo CSVs are explicitly allowlisted.
- Imported notebook outputs, attachments and personal metadata are removed. Embedded
  submission images are omitted rather than trusted to a text-only identifier scan.
- PDF report pages were rendered and visually reviewed; presentation XML and document
  metadata were inspected. Demo video frames were sampled, not reviewed frame by frame.
- All 167 audited personal source files outside archives retain their original SHA-256 hashes
  in OneDrive. No source originals were modified.
- After history cleanup, 28 reachable commits and 345 unique blobs across `main` and
  the reorganization branch were independently checked against privately identified
  identifiers and credential literals: no matches remained. Historical notebooks were
  checked for outputs/attachments, and historical filenames for identifier patterns.

Run `python scripts/check_publication.py` after staging changes. It inspects tracked text,
notebook structure, PDF text and PPTX XML and reports paths/reasons without revealing matches.
Install PyMuPDF for its PDF checks. It does not perform OCR or prove that arbitrary media
contain no sensitive information; imported outputs are removed and retained media reviewed.

## Public-copy repairs

- KNN: absolute Minkowski differences, valid neighbor boundaries and documented ties.
- Perceptron: bounded epochs with exposed convergence state.
- Manual MLP: use the instance activation instead of an accidental global variable;
  extract reusable code and verify gradients independently.
- Cat CNN: restore the missing `nn` import in the standalone class and use zero notebook
  loader workers on Windows.
- VAE: align generation defaults with training, validate checkpoint latent size, load only
  weights and preserve a two-dimensional latent batch during generation.
- Influence experiments: import the existing pipeline module and check referenced symbols.
- MatchPoint scraping: use notebook `%pip` syntax for the installation cell.
- FoodFlow: credentials and deployment configuration come from the local environment.

These repairs can change behavior from the historical submission. Original experiment
results were not rerun or silently relabeled as results from the repaired code.

## Remaining limits

- Spark/Databricks jobs and Spark NLP classification were not executed locally.
- GraphSAGE requires the course harness/data and torch-geometric, unavailable here.
- Query expansion is missing `hw3_utils`; no replacement was invented.
- Flower weights/data are excluded; the original checkpoint was not loaded.
- Java was not compiled because a JDK was unavailable. xv6 lacks its exact base revision.
- Stocks Django contains app/templates/SQL, not a complete configured Django project.
- Full deep-learning training, adversarial/contrastive comparisons and entity-matching CV
  were not rerun. Written historical results require careful split/leakage review.
- The original manual MLP chooses a learning rate using test accuracy; those test results
  are not an untouched final holdout. Keep that limitation visible.
- Credentials that appeared in history must be revoked/replaced by their owner. Cleanup
  of branch history does not remove hosting caches, old PR refs or other people's copies.
