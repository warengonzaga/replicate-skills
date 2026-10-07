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
limitations. Preserve upstream copyright notices. Record any future third-party reuse
and update the source history below when changing implementation provenance.
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

## Authorship and inspiration

Credit both inspiration projects in README.md. Implement from explicit requirements
rather than transplanting their instructions, templates, tools, or tests. Do not
claim a clean-room process: the sources were reviewed during the earlier prototype.
Any future third-party reuse must retain the applicable license and copyright
notices. Renaming or refactoring imported code does not establish independent authorship.

## Source history

On 2026-10-07, the prototype imported Jake Schincariol's MIT-licensed Replica
Skills at `77c9436fb3d18c3d58169efb8caf4fe906b0dc51` from
https://github.com/Jakeschincariol/replica-skill. The import commit `40312a4`
on the archived `feature/portable-improved-skills` branch contains the original
copyright and license. Intermediate adaptations retained it.

The OpenAI adaptation at `a574630bb884ac295536a49ea942cb17c2f17881` from
https://github.com/Jayesh01323/replica-skill-openai was reviewed for packaging;
no separate files were imported from that repository.

The owner subsequently requested replacing the imported implementation. The current
skill instructions, templates, six tools, and tool tests were newly written with
new contracts. The imported helper and template filenames were retired. Plugin
metadata was authored for this project against the clients' packaging conventions;
the original imported manifests and ignore rules were replaced as well.

The current LICENSE applies to the replacement tree. It names Waren Gonzaga.
Historical snapshots on `feature/portable-improved-skills` containing imported material
retain their historical notices; the current license does not change the licensing
of those snapshots. That prototype branch is preserved. The replacement branch
`feature/replicate-skills` starts at dev and records the final implementation in one
commit without the prototype commits in its ancestry. Feature work is squash-merged into dev under Clean Flow, so release
snapshots contain the reviewed current tree rather than intermediate source states.

### Replacement design

- Required acceptance is an explicit gate with evidence; it is not a weighted score.
- Visual comparison preserves dimensions, validates masks, and emits a heatmap.
- Contrast inputs name actual pairs and semantic roles; no inferred token matching.
- Feedback uses caller-defined literal terms, explicit dates, and respondent IDs.
- Identity audits select shipped surfaces and report skipped files without rewriting.
- Copy limits are supplied with source references and explicit Unicode counting modes.
- Skill templates connect source observations, criterion IDs, checks, and handoffs.

See [docs/migration.md](docs/migration.md) for the intentional interface changes.
No live model-driven scenario result should be inferred from unit tests or discovery.
