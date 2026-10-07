# Upstream provenance

Source: https://github.com/Jakeschincariol/replica-skill

Imported commit: `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`

Import date: 2026-10-07

License: MIT. The original copyright notice is preserved in LICENSE.

Replicate Skills is an independently maintained derivative by Waren Gonzaga.
The initial import commit contains the eleven skill folders, templates, helpers,
tests, plugin metadata, and ignore rules. Our following commits add portable
installation, a canonical skills/ layout, runtime-neutral instructions, evidence contracts, and a contribution
workflow. The parity CLI also gains an explicit must-have release gate, with
regression coverage; existing invocation behavior remains available. Existing skill names and artifact formats are retained.

## Updating from upstream

Fetch upstream into a separate checkout. Compare the recorded commit with the
new version, review the license and changed instructions, and apply changes on
an update branch. Keep helper regression tests and downstream portability rules.
Record the new SHA and summarize conflicts resolved in the PR. Do not replace
all skill folders blindly; doing so would discard downstream improvements.
