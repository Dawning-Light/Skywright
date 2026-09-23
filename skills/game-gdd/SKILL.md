---
name: game-gdd
description: Use when a game project's design data needs upkeep rather than authoring — rendering the GDD, checking or looking up references, other maintenance. Not for eliciting design data (see `game-pillars`, `game-mechanics`) or critiquing it (see `game-critique`).
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
  tracks the reader's position and each record's `updated` time shown in
  the reader's local time (the one piece of script in the file, inline and
  self-contained; the document reads fine without it, with the raw UTC
  `updated` value showing instead). Overwritten in full on every render.
  It links to `gdd.css` beside it rather than inlining any style.
- **`design/gdd.css`** — the stylesheet `gdd.html` uses. Seeded once, on the
  first render, by copying this skill's `templates/default.css`; after that
  it belongs to the owner. A re-render never touches an existing `gdd.css`,
  so a style-only change needs no re-render at all, and only an explicit
  `--reset-css` overwrites it with the default again.
- **`design/gdd-fonts/`** — the font files the default stylesheet loads
  (Inter, with its OFL licence), copied from this skill's `templates/fonts/`
  so `gdd.html` needs no network to look right. Same rule as `gdd.css`: a
  file is written only when it is missing, and overwritten only by
  `--reset-css`.

`design/gdd.md` is the **core** GDD only: the ninth of nine
supporting-document types the spec's research surveyed, and the only one
rendered as a document of its own. One of the other eight, the Technical
Design Document, folds into this file as its `## Technical Design` section;
the remaining seven are named, with the reason each is absent, under "The
seven absent supporting documents" below.

## Scripts

Two so far, both stdlib-only Python 3, both run from the consuming project's
own working directory:

- **`scripts/render_gdd.py`** — renders `design/gdd.md` and `design/gdd.html`.
  See "Rendering is scripted" below.
- **`scripts/find_references.py`** — lists every reference to one record. See
  "Finding references" below.

Both read design records through `scripts/economy_frontmatter.py`, a module
rather than a script: the one frontmatter parser, plus `design/economy.md`'s
validator and canonical serializer. `game-mechanics`' `economy-tool` imports
it too, so the economy graph that tool writes is read back by the same code
this skill renders it with.

A future maintenance script gets named here, one line each, rather than in
this skill's trigger description above.

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

Two things cut across all six, both defined once by `game-authoring` and
read here at its definition: the `updated` frontmatter field every shape
carries (`YYYY-MM-DDTHH:MMZ`, UTC), and the eight typed wikilink forms a
body may use to cite another record — `[[pillar:<slug>]]`,
`[[mechanic:<slug>]]`, `[[node:<id>]]`, `[[family:<name>]]`,
`[[connection:<id>]]`, `[[tech:<slug>]]`, `[[concept]]`, `[[comp-analysis]]`.

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
  *order* follows a fixed rule — alphabetical by slug for pillars and
  technical decision records; frontmatter-list order for economy nodes,
  families, and connections; for mechanics, the container tree: root
  mechanics alphabetical by slug, each one's contained mechanics alphabetical
  beneath it, as deep as the tree goes (in `gdd.html` a contained card is
  indented under its container and the table of contents nests the same way).
  A mechanic's container is its `parent`, or its `part_of` where `parent` is
  `none` — so the fields whose values move a section are those two and
  nothing else reorders as a side effect of editing a value.
- **Addressable.** Every rendered section names the record it came from — a
  file path for a concept statement, pillar, mechanic entry, or technical
  decision record; a node, family, or connection identifier for the economy
  graph. In `gdd.md` that is the italic `Source:` caption under each heading;
  in `gdd.html` it is the same caption, visible, plus a `data-source`
  attribute on the section. A reader, or a `game-critique` note, can always
  get from a section back to the exact record that must change to affect it.
  The record's `updated` value sits beside the same caption when the record
  carries one — raw UTC in `gdd.md`; in `gdd.html` a `<time>` element the
  inline script converts to local time, plus a `data-updated` attribute on
  the same element that carries `data-source`. The economy graph's one
  file-level `updated` is shown once, on its section caption.
- **Linked.** A typed wikilink in any record body resolves to the anchor of
  the section it names, so a citation in the data is a working link in
  `gdd.html`; `gdd.md` carries the same reference text through unchanged.
  Only a rendered section can be cited: a candidate pillar or a superseded
  technical decision record, which get a note rather than a section, is an
  unresolved reference.
  Text inside a code span or a fenced code block is never read as a
  reference.
- **Linked both ways.** Every section `gdd.html` renders ends with the
  reverse of the bullet above: a collapsed `Citations` disclosure,
  badge-counted, naming every rendered body that cites it as one
  comma-joined line. Each name is the citing record's own identifier —
  never its `.md` path, which the HTML has no use for — linked to the
  citing record's own section (a candidate pillar or superseded technical
  decision cites like any other body but has no section of its own to link
  to, so it shows unlinked). A section nothing cites gets no disclosure at
  all — it is never shown reading "Citations 0". The badge counts
  occurrences, not distinct citing records, so a body that cites the same
  target twice still counts twice even though the line itself only names
  that citer once. Built from the same reference resolution as the bullet
  above, so it needs its own render
  pass only after every reference in the document is already known to
  resolve.

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
and has seeded `design/gdd.css` and any missing `design/gdd-fonts/` file
(creating `design/` itself if needed — a project with no structured data at
all is a legal starting state, and still gets a complete render made
entirely of absent-section statements). With `--reset-css` it also
overwrites `design/gdd.css` and `design/gdd-fonts/` with the default
template, discarding any hand-edits — the only destructive path the script
has, and one it takes only when asked. Relay the outcome to the owner and
name the three file paths.

**On non-zero exit**, the script has written **nothing** — none of the three
files, not even the CSS or font seed — and has printed one message to stderr naming
which record fails which rule and which upstream skill fixes it. The
conditions that produce this are the ones the upstream skills define as
invalid: an economy connection with no `id`, a node id, connection id, or
family name declared twice, block-style edges, slash-joined headings, or a
reference that resolves to nothing in `design/economy.md` (fixed with
`game-mechanics`); a technical decision record whose `status` or
`scope` lies outside its closed set, or that is missing a body heading its
status and scope require (fixed with `game-tech`); a typed wikilink in any
record body that is malformed — an unknown type, a missing identifier, or
an untyped `[[slug]]` — or that resolves to no record, and an `updated`
value outside the `YYYY-MM-DDTHH:MMZ` form (both defined by
`game-authoring`, fixed with whichever skill writes the failing file).
This skill writes nothing
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
`.tech-record`), each non-record state a render can show has one too
(`.absent`, `.open-note`, `.candidate-note`, `.superseded-note`), and so do
the `updated` time (`.updated`), an `## Open Questions` heading inside a
record body (`.open-questions`), and the reverse-citations disclosure a
cited section ends with (`.citations`, a plain `<details>` — no script
involved), so a theme has real hooks for every category.
`templates/default.css` documents the full structure at the top of the
file. Changing the look of the rendered
GDD means editing `design/gdd.css`; nothing about the script changes for a
style change, and no re-render is needed to see one.

**Tests.** `scripts/tests/run_tests.sh` renders fixture projects under
`scripts/tests/fixtures/` and diffs the result against checked-in expected
output. Run it after any change to the script or to the record shapes it
reads; `UPDATE=1` regenerates the expected files once a change to the
render is intended. `scripts/tests/test_economy_frontmatter.py` tests the
shared module directly — its frontmatter span, the economy validator, and
the serializer's byte-for-byte round trip — run with
`python3 -m unittest scripts/tests/test_economy_frontmatter.py`.

## Finding references

Before renaming or removing a pillar, mechanic, tech decision, or economy
node/family/connection, `scripts/find_references.py` lists every place that
currently cites it — the same reverse lookup `gdd.html`'s own per-section
`Citations` disclosure shows inline, as a CLI query against one target
instead of every target at once. Both sit on top of `render_gdd.py`'s
`iter_wikilink_hits`, the one implementation of "find every wikilink hit in
a text"; `find_references.py` defines no scanning of its own.

**Invocation.** Same working-directory rule as `render_gdd.py`:

```
python3 <skill>/scripts/find_references.py <target>
```

`<target>` is either a typed reference exactly as it appears inside
`[[...]]` (`pillar:zero-grind`, `tech:netcode`, `concept`) or the record's
own file path (`design/pillars/zero-grind.md`). A `node`, `family`, or
`connection` lives inside `design/economy.md` rather than as a file of its
own, so only the typed form works for those three.

**Output.** One line per hit — `design/mechanics/combat.md:14: [[pillar:zero-grind]] (in "## Core Loop")`
— or `No references to [[pillar:zero-grind]].` when there are none, which is
itself the useful answer: nothing cites it, so it's safe to change or
remove. A reference inside a code span or fenced block is never counted,
same as `render_gdd.py`'s own render.

**Exit codes.** 0 whether or not any references were found. Non-zero only
when `<target>` itself is malformed — an unknown type, a missing
identifier, or a path that isn't a recognized record shape — with the
reason on stderr. It does not check that `<target>` resolves to a real
record; that check is `render_gdd.py`'s, at render time.

**Tests.** `scripts/tests/test_find_references.py`, run with
`python3 -m unittest scripts/tests/test_find_references.py`.

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
