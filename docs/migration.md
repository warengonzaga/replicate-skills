# Helper interface migration

The current tools introduce explicit contracts before the first release.
Skill invocation names and project artifact root `replica/` stay stable. Internal
helper names, templates, input schemas, and report fields change.

Back up existing artifacts before converting them. There is no automatic converter
that can turn old completion claims into verified evidence.

| Retired helper | Replacement | Input change |
| --- | --- | --- |
| `parity.py` | `acceptance_gate.py` | CSV scores become a versioned criteria ledger with required flags, states, and evidence |
| `imgdiff.py` | `frame_compare.py` | Comparable opaque screenshots keep their dimensions; optional rectangular masks are explicit |
| `contrast.py` | `palette_audit.py` | Tokens and inferred pairs become named foreground/background pairs with declared roles |
| `reviews.py` | `feedback_triage.py` | Reviews and regex themes become dated respondent records and caller-defined literal topics |
| `sweep.py` | `identity_audit.py` | Brand criteria become literal terms and explicit include/exclude file patterns |
| `listing.py` | `copy_check.py` | Store defaults become source-referenced field limits and counting rules |

## Acceptance ledger

Copy the structure in `skills/replica-recon/scope.example.json`. Give each criterion
a unique ID and boolean `required`. Its state is `pass`, `fail`, `blocked`, or
`unknown`. Evidence entries contain `kind` (`test` or `observation`) and a nonempty
`ref` to reproducible results. Add descriptive fields for actors and expected outcomes
as needed; the gate validates the acceptance fields and permits descriptive metadata.

A required `pass` without evidence is unverified. A ledger with no required criteria
cannot establish readiness. Optional failures remain visible but do not override
required outcomes. The gate does not inspect referenced files or execute tests.

## Images

PPM P3/P6 with maxval 255 works without dependencies. For PNG or JPEG, install
Pillow into your chosen Python environment. Flatten transparent captures onto an
explicit background and capture both states at the same dimensions.

Masks are `[x, y, width, height]` rectangles; overlapping masks are counted once.
All coordinates must fit the frame. Excluding every pixel is an error. The result
contains changed pixel percentage, channel deltas, bounding box, thresholds, and
mask counts. The PPM heatmap highlights changed pixels; masked and unchanged pixels
are black. This output is diagnostic and does not establish perceptual equivalence.

## Feedback, identity, and copy

Feedback records require unique respondent IDs, dates, source references, and text.
Provide `--as-of` explicitly. Future dates and duplicate IDs are rejected. Literal
substring matches can include negation or accidental matches; review grouped,
unmatched, and ambiguous records before using them in a hypothesis.

Identity selection patterns use Python fnmatch on relative paths; a leading `**/`
also matches root files. Select explicit shipped surfaces and exclude legal notices
when their attribution is expected. The audit skips symlinks, dependencies, root
agent configuration, and non-UTF-8 or binary files. Zero scanned files is a failed
gate. It never automatically edits a finding or echoes source lines.

Copy fields specify `required`, positive integer `max_length`, `count`, and a
nonempty constraint `source`. Modes are `codepoints`, `utf16`, and `utf8`; none
counts grapheme clusters. Use dated primary channel rules rather than the examples'
internal constraints. Passing lengths do not verify claims or store eligibility.

## Installation update

Use the installer with `--replace` to back up selected existing skill folders and
replace them. Generated application artifacts are not touched. Start a new client
session after updating and verify the selected replacement helpers are available.
Plugin caches may need a client-specific refresh; an enabled plugin does not prove
its cache contains the latest source tree.
