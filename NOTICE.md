# Attribution

Replicate Skills combines the Claude Code Replica workflow and the OpenAI
adaptation's packaging approach into a revised pack for Codex and Claude Code,
with additional improvements and enhancements.

## Original Replica Skills

Author: Jake Schincariol

Repository: https://github.com/Jakeschincariol/replica-skill

Source commit: `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`

License: MIT, copyright (c) 2026 Jake Schincariol.

The original workflow, templates, Python helper foundations, and regression tests
form our licensed implementation base. The original notice is preserved in LICENSE.

## OpenAI Replica adaptation

Publisher: Jayesh01323

Repository: https://github.com/Jayesh01323/replica-skill-openai

Reviewed commit: `a574630bb884ac295536a49ea942cb17c2f17881`

License: MIT; its LICENSE retains the original Jake Schincariol copyright notice.

This adaptation informed the OpenAI plugin layout and packaging review. It was
reviewed as a reference; no separate code import from that repository occurred.
Our unified skills tree and native manifests were implemented and validated here.

## Replicate Skills changes

Maintainer: Waren Gonzaga and contributors

Repository: https://github.com/warengonzaga/replicate-skills

Our changes revise the skill instructions, refactor the six helpers, add explicit
input/error contracts, and supply portable installation, native plugin metadata,
and the contribution and release workflow. See UPSTREAM.md for provenance and
revision details. MIT allows direct adaptation; attribution and required copyright
notices remain part of the distribution after refactoring.
