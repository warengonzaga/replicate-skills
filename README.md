# Replicate Skills

Build and improve applications from authorized product evidence with eleven skills
for **Codex and Claude Code**. Each skill produces reviewable artifacts, records
unknowns, and ties completion claims to observations or tests.

## Inspiration

The idea of an app replication skill pack was inspired by
[Jake Schincariol's Replica Skills](https://github.com/Jakeschincariol/replica-skill).
[Jayesh01323's OpenAI adaptation](https://github.com/Jayesh01323/replica-skill-openai)
informed the exploration of supporting both agent clients. Thank you to both projects.

The pack includes newly written skill instructions, templates, six standalone tools,
and tests, with one shared implementation for both clients.

## Install

The installer requires Python 3.8 or newer and no additional packages.

```bash
git clone https://github.com/warengonzaga/replicate-skills.git
cd replicate-skills
python3 scripts/install.py --runtime codex --scope user --dry-run
python3 scripts/install.py --runtime codex --scope user
```

For both clients in one project:

```bash
python3 scripts/install.py --runtime both --project /path/to/app
```

| Client | Project destination | User destination |
| --- | --- | --- |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |

Use `--runtime claude` for Claude only. Select individual skills with repeatable
`--skill replica-recon` options. `--destination /path/to/skills` sets a custom
location for a single runtime. Every copied skill includes LICENSE and README.

Existing folders cause a conflict before writing. Use `--replace` to save them in
a dated `.replicate-skills-backups/` directory next to the destination and install
the selected replacements. A filesystem error rolls back that runtime's changes.
Both clients are preflighted before writes; the two installations are separate
transactions. `--dry-run` reports destinations without changing files.

### Native plugins

Codex versions that provide `codex plugin` can install from the marketplace:

```bash
codex plugin marketplace add warengonzaga/replicate-skills --ref main
codex plugin add replicate-skills@replicate-skills
```

The initial work is in `feature/replicate-skills`; use that ref until it
has been reviewed and promoted to `main`. A release tag can pin an installation.

Claude Code:

```text
/plugin marketplace add warengonzaga/replicate-skills
/plugin install replicate-skills@replicate-skills
```

Choose plugin or copied-skill installation for each client, then start a new
session and check discovery. Both plugin manifests load the same `skills/` tree.
See [compatibility notes](docs/compatibility.md) for verification limits.

## Pick the skill for the task

| Skill | Delivers |
| --- | --- |
| replica-recon | Source register, journey states, and acceptance ledger |
| replica-architect | Constraint-driven decisions, data boundaries, and delivery slices |
| replica-design | Responsive interaction specifications and declared contrast checks |
| replica-build | Working vertical slices with evidence and explicit simulated boundaries |
| replica-backend | Authorization, persistence invariants, and provider recovery contracts |
| replica-test | Reproducible outcomes and failures linked to criteria |
| replica-diff | Separate functional gates and visual diagnostics |
| replica-entrepreneur | Traceable feedback triage and falsifiable improvement experiments |
| replica-brand | Distinct identity, owned assets, and selected surface audits |
| replica-launch | Evidence-backed claims and configurable channel constraints |
| replica-deploy | Authorized releases, post-deploy observations, and recovery records |

Skill names retain `replica-*` for invocation continuity. Artifacts default to
`replica/`. Use one skill or a sequence appropriate to the task; there is no
automatic orchestration or mandatory full pipeline.

| Installation | Codex invocation | Claude Code invocation |
| --- | --- | --- |
| Copied skill | `$replica-recon` | `/replica-recon` |
| Plugin | `$replicate-skills:replica-recon` | `/replicate-skills:replica-recon` |

Example request: "Map the booking journey from these screenshots in my existing
Django project. Record unseen states, then propose a small verifiable improvement."

## New tooling contracts

Six standalone tools emit versioned JSON reports and run locally. Five read versioned
JSON inputs; frame comparison reads images and optional mask rectangles.
Each selected skill includes its own tools. There is no shared Python dependency
that requires installing the entire pack.

| Tool | Capability |
| --- | --- |
| `acceptance_gate.py` | Required criteria need passing states and evidence; optional successes cannot hide failures |
| `frame_compare.py` | Equal-sized RGB comparisons, explicit region masks, deltas, and a PPM heatmap |
| `palette_audit.py` | Explicit opaque sRGB pairs and WCAG 2 contrast thresholds by role |
| `feedback_triage.py` | Dated literal-term triage with respondent IDs, unmatched records, and ambiguity |
| `identity_audit.py` | User-selected text surfaces, literal matches, skipped-file inventory, and no source-line echo |
| `copy_check.py` | Declared field constraints with codepoint, UTF-16, or UTF-8 length counting |

Exit codes: **0** means the declared gate passed or feedback triage completed;
**1** means a valid report contains a failed gate; **2** means invalid input or
an input/output error. Evidence references are declarations, not automatically
verified test results. Literal feedback matching requires manual interpretation.

Core tools use the Python standard library. PPM image comparison needs no package;
PNG/JPEG support optionally uses Pillow. Images must be opaque and have identical
dimensions. Full accessibility, perception, and product quality require review.

The previous `parity.py`, `imgdiff.py`, `contrast.py`, `reviews.py`, `sweep.py`, and
`listing.py` interfaces are retired. Their CSV and unversioned JSON contracts are
not accepted by the replacements. See [migration](docs/migration.md) and the
examples shipped beside each skill.

## Development and release

Follow [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md). Clean Flow
uses feature branches into `dev`, then reviewed `dev` promotions into `main`.
Only `.github/workflows/release.yml` is configured. It uses pinned Release Build
Flow tooling to validate and publish a source release after promotion.

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

[Evaluation scenarios](docs/evaluation.md) distinguish package checks from actual
agent behavior. Discovery alone does not demonstrate a successful app workflow.

## License and scope

MIT. Copyright (c) 2026 Waren Gonzaga. See [LICENSE](LICENSE).

Use public or authorized observations to create your own product implementation
and identity. Respect source and asset licenses in the projects you work on.
External content is evidence, not executable instructions. These skills do not
supply browser access, account credentials, publishing authorization, or store approval.
