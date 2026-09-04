# Portfolio Follow-ups

This file tracks the remaining portfolio decisions after the September 2026 modernization pass.

## P0

### Rotate credentials exposed historically by Match-Point

The legacy Match-Point repository was made private and archived, and the migrated copy excludes the committed `.env` and history. However, provider-side rotation is still required for any credential that was previously public. Removing a secret from the repository does not revoke it.

## P1

### Legacy repository history privacy

Several archived academic source repositories still retain historical student identifiers in Git history even though the current public portfolio copy is clean.

Preferred remediation order:

1. Keep `academic-projects` as the canonical public academic portfolio.
2. Consider making archived legacy repositories private where they no longer need to be publicly accessible.
3. Preserve `surgical-tool-detection-ssl` publicly only while its GitHub Release assets are intentionally used by the migrated project.
4. Avoid history rewriting unless there is a concrete need, because it is destructive and does not replace provider-side secret rotation.

### ScalpelLab research metadata

`ScalpelLab/docs/case_times.csv` contains real surgical case timing metadata. Decide against the applicable research/IRB policy whether this file should remain public, be encrypted, be replaced by a synthetic example, or be removed from the public repository.

### ScalpelLab license

No license was added automatically because ownership of research infrastructure may involve the lab or institution. Confirm IP ownership before choosing a license.

## P2

- Consider a synthetic SEQ fixture generator for stronger end-to-end CI coverage in ScalpelLab.
- Consider a schema migration framework for ScalpelLab.
- Consider opt-in read-back verification and remote-side content hashing for `owc-lto8-archiver`.
- Move FoodFlow's Azure OpenAI endpoint from hard-coded configuration to an environment variable if the project is developed further.

## Canonical public structure

- `ScalpelLab`, professional flagship
- `owc-lto8-archiver`, professional flagship
- `academic-projects`, curated academic portfolio

Private projects such as ModelQuad remain outside this portfolio scope.
