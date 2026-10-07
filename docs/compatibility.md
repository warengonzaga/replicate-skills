# Runtime compatibility

One canonical set of SKILL.md files is shared by both runtimes. No proprietary
runtime APIs are used by the helpers. Discovery locations and invocation differ.

| Capability | Codex | Claude Code |
| --- | --- | --- |
| Project skill location | `.agents/skills/` | `.claude/skills/` |
| User skill location | `~/.agents/skills/` | `~/.claude/skills/` |
| Explicit invocation | `$replica-recon` | `/replica-recon` for copied skills |
| Plugin invocation | `$replicate-skills:replica-recon` | `/replicate-skills:replica-recon` |
| Python helpers | Python 3.8+, standard library | Python 3.8+, standard library |
| Browser workflows | Requires an available browser or supplied evidence | Same |

Sources checked on 2026-10-07:
- https://developers.openai.com/codex/skills/
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/plugins-reference

## Verification boundary

Installer tests exercise both runtime destinations, helper preservation, conflicts,
backups, and failure rollback. Structural checks validate skill metadata and plugin
packaging. Helper regression tests verify deterministic local behavior.

Observed on 2026-10-07:
- Codex CLI 0.159.0-alpha.3: local marketplace registration and plugin installation
  passed; `plugin/read` exposes eleven enabled namespaced skills.
- Codex app-server `skills/list`: all eleven copied project skills discovered and
  enabled in a separate disposable project.
- Claude Code 2.1.292: native manifest validation and local marketplace/plugin
  installation passed; plugin list reports version 0.1.0 enabled, with all eleven
  canonical SKILL.md files present in the installed cache. The validator warns
  that root CLAUDE.md is not plugin context; that file is for repository contributors.
- Python 3.12.14: all 88 helper/installer regression tests and structural validation
  passed, including malformed input and output-error cases.
- Both runtime installers copy LICENSE and README.md into all eleven skills.

Trigger selection and end-to-end agent behavior remain manual checks in
[the evaluation scenarios](evaluation.md). No model-driven app build, live browser
workflow, Python 3.8 execution, or production release has been run.

## Helper invocation

After loading a skill, resolve its actual directory. Set `SKILL_DIR` to that
absolute path and run its helpers from the user's project root, quoting the path.
For sibling helpers used by deployment, set `SKILLS_ROOT` to its parent directory.
Do not assume a particular home directory or change HOME. Missing helpers are a
blocked check, not permission to fabricate a result.

## Combined source approaches

The Claude Code workflow foundation comes from Jakeschincariol/replica-skill.
The OpenAI packaging approach was informed by Jayesh01323/replica-skill-openai.
Both are credited in [README.md](../README.md). Exact commits and the distinction
between the implementation import and packaging reference are recorded in
[CONTRIBUTING.md](../CONTRIBUTING.md#source-history). Both native manifests load the same revised skill
folders, and all six helpers have documented refactors and regression coverage.
