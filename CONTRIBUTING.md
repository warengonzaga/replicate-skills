# Contributing

Read [AGENTS.md](AGENTS.md) for the project rules. Start from `dev` on a
focused feature or fix branch, and explain the problem before changing behavior.
Use Clean Commit messages, such as `🔧 update: preserve installed skills on conflicts`.
Feature PRs target `dev` and squash on approval. Promote stable `dev` to `main`
with a reviewed merge commit. Never send a feature PR directly to `main`.

| Type | Emoji | Purpose |
| --- | --- | --- |
| new | 📦 | New capabilities |
| update | 🔧 | Improvements and fixes |
| remove | 🗑️ | Removing code or features |
| security | 🔒 | Security hardening |
| setup | ⚙️ | Configuration and tooling |
| chore | ☕ | Housekeeping |
| test | 🧪 | Tests and test fixes |
| docs | 📖 | Documentation |
| release | 🚀 | Release preparation |

Format: `<emoji> <type>: <description>` or `<emoji> <type> (<scope>): <description>`.
Use lowercase types and present tense; start descriptions in lowercase.
PR squash titles must use the same convention for release version detection.

## Local checks

Python 3.8 or newer is sufficient; there are no pip dependencies.

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

For an installer change, exercise both runtimes with temporary destinations.
For a skill change, review its input/output contract, path handling, evidence
rules, and relevant scenarios in [docs/evaluation.md](docs/evaluation.md).
Record manual agent checks separately from automated checks.

## Pull requests

State the behavior before and after the change, checks actually run, and remaining
limitations. Preserve upstream copyright notices. Keep upstream imports separate
from downstream changes and update the source history below when refreshing the base.
Use draft PRs until all applicable checks are complete. The owner approves merges
and releases. No GitHub branch protection is configured by these files; configure
required checks in repository settings if desired.

## Release workflow

Only release.yml is enabled. After an approved dev-to-main promotion, it runs
local validation commands in GitHub Actions, plans a version, synchronizes both
plugin manifest versions, and creates the changelog, tag, and GitHub Release.
The Release Build Flow action is pinned to a commit. Skills ship as source;
there is no npm package or container publication. A manual run is permitted only
on main. A release is not considered verified until its workflow and tag are
read back successfully. Branch protection is not installed by these files.

## Adaptation and attribution

Credit the original Claude Code Replica skills and the OpenAI adaptation in
README.md. Record source commits and whether material was imported, adapted, or
used as reference in the source history below. MIT permits direct adaptation; retain all
applicable license notices after refactoring. Review reused components and revise
them for concrete clarity, correctness, or maintainability improvements. Explain
the change and cover behavior with regression tests rather than making cosmetic
edits to imply independent authorship.

## Source history

Replicate Skills combines the original Claude Code Replica workflow with the
OpenAI adaptation's packaging approach, then revises and improves the shared pack
for Codex and Claude Code. Both projects are credited in [README.md](README.md).

### Claude Code implementation foundation

Repository: https://github.com/Jakeschincariol/replica-skill

Author: Jake Schincariol

Imported commit: `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`

Import date: 2026-10-07

License: MIT. The original copyright notice is preserved in LICENSE.

The separate import commit records the eleven skills, templates, six Python
helpers, regression tests, plugin metadata, and ignore rules before our revision.
Keep that historical baseline for provenance; the delivered tree is the reviewed,
refactored adaptation maintained by Waren Gonzaga and contributors.

### OpenAI adaptation reference

Repository: https://github.com/Jayesh01323/replica-skill-openai

Publisher: Jayesh01323

Reviewed commit: `a574630bb884ac295536a49ea942cb17c2f17881`

License: MIT, preserving the original Jake Schincariol notice.

The OpenAI plugin layout informed our packaging review. No files or code were
imported separately from this repository. Both manifests point to one canonical
skills/ tree instead of keeping multiple copies of the same instructions.

### Downstream revisions

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

### Updating from either source

Review source changes in a separate checkout, including the license and affected
instructions. Apply relevant changes on a feature branch with a rationale and
regression coverage. Record the source SHA and whether changes were imported,
adapted, or reviewed as reference. Preserve source notices even for rewritten code.
Do not overwrite our skill tree with an unreviewed source snapshot.
