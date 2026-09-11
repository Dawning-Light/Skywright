---
name: game-gdd
description: Use when a game project's `design/` directory holds pillar, mechanic, economy, comp-analysis, or technical-decision data and the owner wants a current GDD — runs a script that renders `design/gdd.md` and a styled `design/gdd.html` fresh from whatever data exists, overwriting any prior render or hand-edit rather than merging. Not for eliciting that underlying data (see `game-pillars`, `game-mechanics`, `game-comp-analysis`, `game-tech`) or critiquing the render (see `game-critique`).
---

# Game GDD

Renders the core Game Design Document as a **view** onto structured data that
already exists elsewhere in the project, never as a document authored or
hand-maintained in its own right. This is the fifth of six independent
Orrery skills for game design (`game-pillars`, `game-comp-analysis`,
`game-mechanics`, `game-tech`, `game-gdd`, `game-critique`). It defines no record shape of
its own — every field it reads is defined once, by the skill that writes it,
and this file names that skill rather than restating the field.

## Standalone invocation

Run this skill against any game project, regardless of how much or how little
of the structured data below currently exists. Nothing here waits on a
complete set of inputs, and nothing here refuses to run because a pillar,
mechanic, or comp-analysis file is missing — a project with only a concept
statement and nothing else still gets a GDD, and so does a project with
nothing at all. The suggested order across the six skills —
`game-pillars` → `game-comp-analysis` → `game-mechanics` → `game-tech` →
`game-gdd` → `game-critique` — is a recommendation, not a requirement this
skill enforces.

## What this skill produces

Three files, all inside the *consuming* game project's `design/` directory —
never inside this skill's own repository:

- **`design/gdd.md`** — the machine-readable form: the core GDD as
  markdown, the form other skills and agents (`game-critique`) parse.
  Overwritten in full on every render.
- **`design/gdd.html`** — the human-readable form: the same render,
  section for section, as an HTML document with a table of contents that
  tracks the reader's position (the one piece of script in the file, inline
  and self-contained; the document reads fine without it). Overwritten in
  full on every render. It links to `gdd.css` beside it rather than
  inlining any style.
- **`design/gdd.css`** — the stylesheet `gdd.html` uses. Seeded once, on the
  first render, by copying this skill's `templates/default.css`; after that
  it belongs to the owner. A re-render never touches an existing `gdd.css`,
  so a style-only change needs no re-render at all, and only an explicit
  `--reset-css` overwrites it with the default again.

`design/gdd.md` is the **core** GDD only: the ninth of nine
supporting-document types the spec's research surveyed, and the only one
rendered as a document of its own. One of the other eight, the Technical
Design Document, folds into this file as its `## Technical Design` section;
the remaining seven are named, with the reason each is absent, under "The
seven absent supporting documents" below.

## The six inputs — read, never restated

Each rendered section maps to exactly one of these shapes. The render script
reads each at the path and field names its defining skill fixes, and does
not redefine, rename, or add a field to any of them:

- **The concept statement**, `design/concept.md` — shape defined by
  `game-pillars`.
- **The pillar record**, `design/pillars/<slug>.md` — shape defined by
  `game-pillars`, including its `status` field (`approved` or `candidate`).
- **The mechanic entry**, `design/mechanics/<slug>.md` — shape defined by
  `game-mechanics`.
- **The economy graph**, `design/economy.md`, read as its `nodes`,
  `connections` and `families` — shape defined by `game-mechanics`, including
  `value_progression`, `id`, `subtype`, `resource`, the `families` block, the
  `@` sigil, and `applies: one-of-family`.
- **The differentiation statement**, `design/comp-analysis.md` — shape
  defined by `game-comp-analysis`.
- **The technical decision record**, `design/tech/<slug>.md` — shape
  defined by `game-tech`, including its `status` field (`open`, `accepted`,
  `superseded`), its `scope` field (`contained`, `cross-cutting`), its
  `category`, `drivers`, and `superseded_by` fields, and which body headings
  its status and scope require.

## Rendering is total, local, and addressable

Three properties the render is built to guarantee, because `game-critique`
(landing after this skill) relies on all three:

- **Total.** Every render starts from nothing and is built up only from what
  the six inputs above currently hold. No content survives from a prior
  render that isn't derivable from current data. Concretely: a hand-edit made
  directly to `design/gdd.md` or `design/gdd.html` — a paragraph added, a
  section reworded, a section deleted — does not survive the next render.
  The script overwrites both files every time it runs; it never opens the
  existing render to preserve, diff against, or merge with what's already
  there. Both are rendered fresh on every invocation, in full, from the
  structured data alone. (`design/gdd.css` is the one deliberate exception:
  it is a style, not content, and it is the owner's to keep.)
- **Local.** Each record maps to exactly one section, and each section's
  content is derived only from that record's own fields — never from another
  record's fields, and never from the previous render. Editing one field of
  one pillar, mechanic, node, connection, or family and re-rendering changes
  exactly the section that field maps to, and nothing else in the file. A
  family section is the one section derived from two records rather than one
  — the family record and the declarations written over it — but both
  already live in `design/economy.md` beside it, never in another family's
  record or in the previous render, so the same guarantee holds. Section
  *order* follows a fixed, content-independent rule — alphabetical by slug
  for pillars, mechanics, and technical decision records; frontmatter-list
  order for economy nodes, families, and connections — so reordering never
  happens as a side effect of editing a field's value.
- **Addressable.** Every rendered section names the record it came from — a
  file path for a concept statement, pillar, mechanic entry, or technical
  decision record; a node, family, or connection identifier for the economy
  graph. In `gdd.md` that is the italic `Source:` caption under each heading;
  in `gdd.html` it is the same caption, visible, plus a `data-source`
  attribute on the section. A reader, or a `game-critique` note, can always
  get from a section back to the exact record that must change to affect it.

## Rendering is scripted

The whole render — markdown and HTML both — is one deterministic
transformation of the six inputs, and it is performed by a script rather
than by hand. `scripts/render_gdd.py` is the one and only definition of how
`design/gdd.md` and `design/gdd.html` render: which sections exist, in what
order, what each states, and what an absent or invalid input produces. Do not
re-derive that template in prose here or reproduce it by hand; the script is
what runs.

**Invocation.** Write `<skill>` for the directory this file sits in. Run
from the consuming project's own working directory — the one whose `design/`
directory holds the structured data — and do not `cd` to `<skill>` first,
because the script reads and writes `design/` relative to the directory it
is run from:

```
python3 <skill>/scripts/render_gdd.py [--reset-css]
```

Stdlib-only Python 3; no packages to install.

**On exit 0**, the script has written `design/gdd.md` and `design/gdd.html`,
and has seeded `design/gdd.css` if it did not already exist (creating
`design/` itself if needed — a project with no structured data at all is a
legal starting state, and still gets a complete render made entirely of
absent-section statements). With `--reset-css` it also overwrites
`design/gdd.css` with the default template, discarding any hand-edits — the
only destructive path the script has, and one it takes only when asked.
Relay the outcome to the owner and name the three paths.

**On non-zero exit**, the script has written **nothing** — none of the three
files, not even the CSS seed — and has printed one message to stderr naming
which record fails which rule and which upstream skill fixes it. The
conditions that produce this are the ones the upstream skills define as
invalid: an economy connection with no `id`, block-style edges, slash-joined
headings, or a reference that resolves to nothing in `design/economy.md`
(fixed with `game-mechanics`); a technical decision record whose `status` or
`scope` lies outside its closed set, or that is missing a body heading its
status and scope require (fixed with `game-tech`). This skill writes nothing
into any of the six inputs, so it proposes no repair of its own, and it does
not render an invalid file on a best-effort basis — a partial render of an
invalid file is indistinguishable from a render of a valid one to the reader
holding it. **Relay stderr to the owner verbatim.** Do not re-derive,
reformat, or soften the message, and do not attempt a render of your own
in its place.

**Determinism.** Given the same six inputs, the script produces
byte-identical output every time — no timestamps, no dependence on
filesystem iteration order. Two renders that differ mean the inputs differ.

**Styling.** `design/gdd.html` carries no style of its own; every visual
choice lives in `design/gdd.css`, which the owner edits directly. Each
section and record in the HTML carries a class for its kind (`.pillar`,
`.mechanic`, `.economy-node`, `.economy-family`, `.economy-connection`,
`.tech-record`) and each non-record state a render can show has one too
(`.absent`, `.open-note`, `.candidate-note`, `.superseded-note`), so a theme
has real hooks for every category. `templates/default.css` documents the
full structure at the top of the file. Changing the look of the rendered
GDD means editing `design/gdd.css`; nothing about the script changes for a
style change, and no re-render is needed to see one.

**Tests.** `scripts/tests/run_tests.sh` renders fixture projects under
`scripts/tests/fixtures/` and diffs the result against checked-in expected
output. Run it after any change to the script or to the record shapes it
reads; `UPDATE=1` regenerates the expected files once a change to the
render is intended.

## The seven absent supporting documents

The spec's own research surveyed nine supporting-document types a GDD
practice commonly names. `design/gdd.md` renders the core GDD — the ninth —
as a document of its own, and folds one more into it. The
`## Supporting Documents Not Rendered` section states all seven of the rest,
and why each is absent, rather than leaving a reader to wonder whether they
were forgotten:

- **Technical Design Document** — not absent, and not a separate document:
  at solo and small-team scale technical design folds into the GDD, so it
  renders as the `## Technical Design` section, from the technical
  decision records `game-tech` writes, rather than as a standalone
  `design/tdd.md`. The section states this in one sentence so a reader
  looking for a TDD knows where it went.
- **Concept Document** and **Marketing & Business Plan** — out of scope for
  this skillset, not merely undone in v1: the Concept Document is already
  served by `game-pillars`'s own concept statement, and the Marketing &
  Business Plan is a business concern outside this skillset's design-quality
  scope.
- **Art Bible**, **Story/Narrative Bible**, **Level Design Document**,
  **Sound Design Document**, and **Test Plan** — absent for a grounding
  reason: the schema this skillset builds (pillars, mechanic entries, the
  economy graph, technical decision records) carries none of the visual,
  narrative, audio, or QA data any of these five would need to render from,
  and rendering one without that data would mean inventing content rather
  than deriving it. Each is a documented future extension, not a silent
  omission — a later pass would need its own research to determine what
  schema each requires, exactly as this spec already documents for
  Elo/Monte Carlo/MCTS balancing in `game-mechanics`.

This is the spec's own accounting, not one invented here — see
`docs/traverse/specs/2026-09-06-game-design-skillset.md`'s `## Out of scope`
section for the source statement, and
`docs/superpowers/specs/2026-09-11-game-tech-design.md` for the change that
moved the Technical Design Document off the absent list. The section's
fixed text lives in the script, beside every other section's rendering.
