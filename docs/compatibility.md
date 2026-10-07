# Client compatibility

The pack has one canonical `skills/` directory and no client-specific helper imports.
Both native plugin descriptors point to that tree. Copied installation includes
complete individual skill folders with the project LICENSE and README.

| Mode | Codex | Claude Code |
| --- | --- | --- |
| Project skill copies | `.agents/skills/` | `.claude/skills/` |
| User skill copies | `~/.agents/skills/` | `~/.claude/skills/` |
| Native plugin | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |
| Marketplace | `.agents/plugins/marketplace.json` | `.claude-plugin/marketplace.json` |

Copied invocations use `$replica-recon` in Codex and `/replica-recon` in Claude Code.
Native plugins add the `replicate-skills:` namespace. Available marketplace and
plugin commands depend on the installed client version.

## What has been checked

Replacement checks on 2026-10-07:

| Check | Observed result |
| --- | --- |
| Python 3.12 automated suite | 94 tests passed, including optional Pillow PNG checks |
| Both copied installations | Eleven complete skills each, including LICENSE and README, in paths containing spaces |
| Codex 0.159.0-alpha.3 native validator | Passed |
| Codex app-server `plugin/read` | Eleven enabled replacement skills from the current source tree |
| Codex app-server `skills/list` | Eleven enabled replacement skills from a disposable copied installation |
| Claude Code 2.1.292 plugin and marketplace validators | Passed; contributor CLAUDE.md root-context warning is expected |
| Python 3.8 grammar | All 17 Python files parsed; not execution on Python 3.8 |

Pillow 12.3.0 was present for optional PNG decoding tests. The contributor CLAUDE.md
is intentionally repository guidance; plugin users load the skills themselves.
Client discovery must be checked separately after an update; cached plugins may
retain old content. An enabled or discoverable skill is not proof that the client
followed it correctly. Model-driven evaluation remains pending.

## Local runtime requirements

Python 3.8+ is the source compatibility target. The helpers have no mandatory Python
packages. PPM comparison uses the standard library; PNG/JPEG support optionally
requires Pillow. Pillow's runtime version support depends on the selected package
version. Browser, build, test, provider, and deployment capabilities come from the
user's actual project and client tools, not this pack.

Python 3.8 execution, live agent workflows, browser interactions, provider calls,
and release publication remain unverified unless explicitly recorded as run.
Use [evaluation scenarios](evaluation.md) for those instruction checks.
