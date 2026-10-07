# Source provenance and adaptation

Replicate Skills combines the original Claude Code Replica workflow with the
OpenAI adaptation's packaging approach, then revises and improves the shared pack
for Codex and Claude Code. Both projects are credited in [NOTICE.md](NOTICE.md).

## Claude Code implementation foundation

Repository: https://github.com/Jakeschincariol/replica-skill

Author: Jake Schincariol

Imported commit: `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`

Import date: 2026-10-07

License: MIT. The original copyright notice is preserved in LICENSE.

The separate import commit records the eleven skills, templates, six Python
helpers, regression tests, plugin metadata, and ignore rules before our revision.
Keep that historical baseline for provenance; the delivered tree is the reviewed,
refactored adaptation maintained by Waren Gonzaga and contributors.

## OpenAI adaptation reference

Repository: https://github.com/Jayesh01323/replica-skill-openai

Publisher: Jayesh01323

Reviewed commit: `a574630bb884ac295536a49ea942cb17c2f17881`

License: MIT, preserving the original Jake Schincariol notice.

The OpenAI plugin layout informed our packaging review. No files or code were
imported separately from this repository. Both manifests point to one canonical
skills/ tree instead of keeping multiple copies of the same instructions.

## Downstream revisions

- Revise all eleven skills with runtime-neutral instructions, evidence contracts,
  project-aware defaults, portable helper paths, and completion criteria.
- Provide native plugin manifests and an installer that preserves licenses,
  attribution, user changes, and backups.
- Refactor parity CSV normalization and visual-report validation; compose reports
  without mutating the caller's feature results. Add the must-have release gate.
- Separate contrast input loading from calculations; reject malformed pairs rather
  than reporting a pass after silently skipping them.
- Validate listing schemas before linting and count repeated keywords in one pass.
- Validate review schemas and theme IDs, enforce reproducible dates, and report
  output errors consistently instead of using the current date or a traceback.
- Validate image comparison options and cover reading, comparing, and writing with
  one CLI error boundary.
- Separate brand criteria loading from scanning, reject malformed configuration
  and missing scan roots, and skip agent examples unless explicitly included.
- Establish contribution guidance, regression coverage, and release-only automation.

Existing skill names, artifact formats, scoring algorithms, and CLI behavior for
valid inputs are retained. Invalid inputs that previously crashed or falsely
passed now produce a clear error. Reviewed licensed portions may remain in the
adaptation; attribution describes their lineage even after code is revised.

## Updating from either source

Review source changes in a separate checkout, including the license and affected
instructions. Apply relevant changes on a feature branch with a rationale and
regression coverage. Record the source SHA and whether changes were imported,
adapted, or reviewed as reference. Preserve source notices even for rewritten code.
Do not overwrite our skill tree with an unreviewed source snapshot.
