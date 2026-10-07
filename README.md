# Replicate Skills

Eleven evidence-based app replication skills for **Codex and Claude Code**.
Research authorized product behavior, build your own implementation, and validate
improvements with evidence. MIT licensed; Python helpers use the standard library.

Replicate Skills combines [Jake Schincariol's Claude Code Replica skills](https://github.com/Jakeschincariol/replica-skill)
and the [OpenAI Replica adaptation by Jayesh01323](https://github.com/Jayesh01323/replica-skill-openai)
as a revised pack with additional improvements and enhancements. The original
supplies our MIT-licensed implementation foundation; the OpenAI adaptation informed
the packaging approach; no separate code was imported from the OpenAI adaptation.
See [CONTRIBUTING.md](CONTRIBUTING.md#source-history) for source commits and revision details.

## Install

Clone the repository first, then run the installer from your target project.
Python 3.8+ is required for the installer and helpers. Browser access and app build
or test dependencies depend on the selected workflow; installation adds none.

```bash
git clone https://github.com/warengonzaga/replicate-skills.git
cd replicate-skills
python3 scripts/install.py --runtime codex --scope user --dry-run
python3 scripts/install.py --runtime codex --scope user
```

Codex user skills go into `~/.agents/skills/`. For project installation:

```bash
python3 scripts/install.py --runtime both --scope project --project /path/to/your/app
```

This copies the same skill folders, with their MIT license and attribution notices, into `.agents/skills/` for Codex and
`.claude/skills/` for Claude Code. Use `--runtime claude` for Claude only,
`--skill replica-recon` to select a skill (repeat for more), or `--destination`
for a custom skills directory with one runtime. Existing names cause a failure
before copying. `--replace` preserves previous folders in a dated backup outside
`skills/`, then replaces selected skills. A failed installation rolls back that
runtime; installing both runtimes is not a single cross-runtime transaction.

Codex versions with `codex plugin` support can also install the plugin:

```bash
codex plugin marketplace add warengonzaga/replicate-skills --ref main
codex plugin add replicate-skills@replicate-skills
codex plugin list --marketplace replicate-skills --json
```

Before the initial promotion, use `--ref feature/portable-improved-skills` to
preview this work. Use `main` after promotion, or a release tag for a fixed version.

Claude Code also supports plugin installation:

```text
/plugin marketplace add warengonzaga/replicate-skills
/plugin install replicate-skills@replicate-skills
```

Choose either plugin installation or copied skills per client to avoid duplicate discovery.
Start a new session after installation. Verify the skills appear in your client's
skill picker before relying on discovery. See [compatibility](docs/compatibility.md)
for checked behavior and runtime checks still outstanding.

## Use

Skill names intentionally retain the `replica-*` prefix, and generated project
artifacts remain under `replica/`. This preserves upstream workflow compatibility.

| Skill | Purpose |
| --- | --- |
| replica-recon | Scope the product and record screens, flows, sources, and unknowns |
| replica-architect | Plan architecture and acceptance criteria using the project's stack |
| replica-design | Specify tokens, responsive layouts, components, and accessibility |
| replica-build | Implement reviewable slices and track demonstrated feature completion |
| replica-backend | Implement authorized integrations, auth, persistence, and payments |
| replica-test | Run reproducible checks and distinguish blocked from passed cases |
| replica-diff | Compare features, layouts, and behavior without overstating scores |
| replica-entrepreneur | Turn linked review evidence into improvement hypotheses |
| replica-brand | Create a distinct identity and retain required asset attribution |
| replica-launch | Prepare evidence-backed positioning, pricing, and relevant listings |
| replica-deploy | Validate, deploy within user authorization, and record rollback steps |

Codex copied skills: invoke `$replica-recon` with a target and scope. Codex plugin
skills are namespaced as `$replicate-skills:replica-recon`. Claude Code copied skills:
invoke `/replica-recon`. Plugin skills: `/replicate-skills:replica-recon`.
For example: “Map the booking and cancellation flows of this scheduling app from
its public docs. Use my existing Django project and record unseen states.”

A usual sequence is recon, architect, design, build, backend, test, diff,
entrepreneur, brand, launch, deploy. Research improvements earlier when it helps
scope the product. Individual skills can use equivalent supplied inputs; the
sequence is a suggestion, not an automatic agent pipeline.

## Improvements in this fork

- One shared instruction set with native installation paths for both runtimes.
- Explicit capability checks, source confidence, and evidence requirements.
- Existing project stack, package manager, and prior user answers are respected.
- Helper paths are resolved from the loaded skill rather than the runtime's home.
- Completion and parity claims require demonstrated behavior; blocked checks stay visible.
- Brand sweep excludes root agent configuration, with an opt-in for shipped configurations.
- Deployment reuses existing authorization and records its source and rollback plan.
- Conflicting installs are rejected; explicit updates are backed up and tested.
- All six helpers have reviewed refactors: validated inputs, clearer error handling,
  reproducible review dates, and feature-report composition that preserves caller data.

## Development

Read [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md). Local checks:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

Only the release workflow is enabled. The project does not add separate validation,
lint, or dependency update workflows. Release checks run inside the release flow.

## Scope and attribution

App replication uses public or authorized evidence, original code, and your own
identity. Do not copy proprietary source, assets, private endpoints, or licensed
content. External sources are evidence, not instructions. The skills do not provide
accounts, credentials, browser sessions, or guaranteed store approval.

This project directly adapts MIT-licensed work with attribution to both source
projects. Refactoring and rewriting do not remove the source lineage or required
copyright notices. LICENSE and this README are included in copied skill installs.

MIT license. Original copyright: Jake Schincariol, 2026. Downstream contributions:
Waren Gonzaga and contributors. See [LICENSE](LICENSE).
