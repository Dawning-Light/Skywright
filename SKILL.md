---
name: game-gdd
description: Use when a game project's `design/` directory holds any pillar, mechanic, economy, or comp-analysis data and the owner wants a current GDD — renders `design/gdd.md` fresh on every invocation from whatever structured data currently exists, overwriting any prior render (and any hand-edit made directly to it) rather than merging. Not for eliciting the underlying pillar, mechanic, economy, or comp-analysis data itself (see `game-pillars`, `game-mechanics`, `game-comp-analysis`) and not for critiquing what renders (see `game-critique`).
---

# Game GDD

Renders the core Game Design Document as a **view** onto structured data that
already exists elsewhere in the project, never as a document authored or
hand-maintained in its own right. This is the fourth of five independent
Orrery skills for game design (`game-pillars`, `game-comp-analysis`,
`game-mechanics`, `game-gdd`, `game-critique`). It defines no record shape of
its own — every field it reads is defined once, by the skill that writes it,
and this file names that skill rather than restating the field.

## Standalone invocation

Run this skill against any game project, regardless of how much or how little
of the structured data below currently exists. Nothing here waits on a
complete set of inputs, and nothing here refuses to run because a pillar,
mechanic, or comp-analysis file is missing — a project with only a concept
statement and nothing else still gets a GDD, and so does a project with
nothing at all. The suggested order across the five skills —
`game-pillars` → `game-comp-analysis` → `game-mechanics` → `game-gdd` →
`game-critique` — is a recommendation, not a requirement this skill enforces.

## What this skill produces

One file, `design/gdd.md`, inside the *consuming* game project — never inside
this skill's own repository. `design/gdd.md` is the **core** GDD only: the
ninth of nine supporting-document types the spec's research surveyed, and the
only one this pass renders. The other eight are named, with the reason each
is absent, under "The eight absent supporting documents" below.

## The five inputs — read, never restated

Each rendered section below maps to exactly one of these shapes. This skill
reads each at the path and field names its defining skill fixes, and does not
redefine, rename, or add a field to any of them:

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

## Rendering is total, local, and addressable

Three properties the template below is built to guarantee, because
`game-critique` (landing after this skill) relies on all three:

- **Total.** Every render starts from nothing and is built up only from what
  the five inputs above currently hold. No content survives from a prior
  render that isn't derivable from current data. Concretely: a hand-edit made
  directly to `design/gdd.md` — a paragraph added, a section reworded, a
  section deleted — does not survive the next render. This skill overwrites
  the whole file every time it runs; it never opens the existing
  `design/gdd.md` to preserve, diff against, or merge with what's already
  there. `design/gdd.md` is rendered fresh on every invocation, in full, from
  the structured data alone.
- **Local.** The template maps each record to exactly one section, and each
  section's content is derived only from that record's own fields — never
  from another record's fields, and never from the previous render. Editing
  one field of one pillar, mechanic, node, connection, or family and
  re-rendering changes exactly the section that field maps to, and nothing
  else in the file. A family section is the one section derived from two
  records rather than one — the family record and the declarations written
  over it — but both already live in `design/economy.md` beside it, never in
  another family's record or in the previous render, so the same guarantee
  holds. Section *order* follows a fixed, content-independent rule (slug or
  frontmatter-list order, below), so reordering never happens as a side
  effect of editing a field's value.
- **Addressable.** Every rendered section names the record it came from — a
  file path for a concept statement, pillar, or mechanic entry; a node,
  family, or connection identifier for the economy graph. A reader, or a
  `game-critique` note, can always get from a section back to the exact
  record that must change to affect it.

## The template — the one and only definition of how `design/gdd.md` renders

A fixed section-per-record template, in this order:

1. **`## Concept`** — one section, from `design/concept.md`. Body is that
   file's own prose, unchanged. Addressed by the path `design/concept.md`.
   Absent when the file does not exist: the section still appears, with body
   text stating plainly that no concept statement has been recorded yet and
   pointing at `game-pillars`.

2. **`## Design Pillars`** — one subsection per pillar record, one section
   per approved pillar found under `design/pillars/`. Only pillars with
   `status: approved` render as pillars proper here; a `status: candidate`
   pillar (written by `game-comp-analysis`) is **not** rendered as a pillar
   in this section — rendering an unapproved candidate as if it were settled
   design would make the GDD lie about approval state. Instead, if one or
   more candidates exist, this section closes with one line stating the
   count and pointing at `game-pillars` as where the owner reviews and
   approves them; if none exist, that line is omitted. Approved pillars are
   ordered alphabetically by slug (not by file mtime or elicitation order),
   so section order never shifts as a side effect of editing a pillar's
   content. Each subsection is headed by the pillar's `title` and addressed
   by its path, `design/pillars/<slug>.md`, and its body is that file's own
   prose. Absent when no approved pillar exists yet: the section still
   appears, stating that plainly and pointing at `game-pillars`.

3. **`## Mechanics`** — one section per mechanic entry found under
   `design/mechanics/`, ordered alphabetically by slug. A mechanic's `parent`
   and `children` fields render as given, inside its own section, rather than
   being used to compute a tree order for the section list — this keeps a
   mechanic's position in the document stable under edits to its own
   taxonomy fields, the same locality guarantee the pillar ordering rule
   gives above. Each subsection is headed by the mechanic's `title` and
   addressed by its path, `design/mechanics/<slug>.md`; its body carries that
   entry's `## Description`, `## Strong example`, and `## Weak example`
   headings, unchanged. Absent when no mechanic entry exists yet: the section
   still appears, stating that plainly and pointing at `game-mechanics`.

4. **`## Economy`** — from `design/economy.md`, split into three parts, one
   section per node, one section per family, and one section per connection
   that is not a declaration over a family, so an individual node, family, or
   connection is addressable on its own rather than folded into one
   undifferentiated dump:
   - One section per node, in the order `nodes` lists them in the file's
     frontmatter (a content-independent order, for the same locality reason
     as above). Each is addressed by its `id`, and states its `type` and, if
     present, its `value_progression`; a node with no `value_progression`
     states that plainly rather than omitting the field silently.
   - One section per family, in the order `families` lists them in the
     file's frontmatter, addressed by `@<name>`. It names the family, its
     `type`, and enumerates the member ids it expands to — the same ids the
     node sections above already render in full, so both the family and its
     members stay visible rather than one collapsing into the other. Beneath
     it, the declarations written over the family are listed, each addressed
     by its own `id` and stating how many edges it expands to and whether it
     is `one-of-family`. A `one-of-family` declaration is never presented as
     N simultaneous edges — the count and the flag are stated on the
     declaration itself, never unrolled into one line per expanded member.
     Each declaration states its `resource` where the record carries one, on
     the same terms the connection section below does. Each expanded
     connection stays addressable by the derived id `game-mechanics`
     defines; this section references that rule rather than restating it.
   - One section per connection that is not a declaration over a family, in
     the order `connections` lists them (a content-independent order, the
     same as node order above, and a different property from addressing:
     reordering the list changes order, never identity). Each is addressed
     by its `id`. Each states its `subtype` if present, or that none is
     recorded if absent, on the same terms the node section above states an
     absent `value_progression`. Each states its `rate` if present, or that
     none is recorded if absent. Each states its `resource` where the record
     carries one.

   Absent when `design/economy.md` does not exist: the whole `## Economy`
   section still appears, stating that plainly and pointing at
   `game-mechanics`.

   Invalid when a connection in `design/economy.md` has no `id`, or when the
   file carries block-style edges or slash-joined headings: this skill
   writes nothing, so it proposes no upgrade of its own. It reports it as
   invalid rather than rendering it on a best-effort basis — a partial
   render of an invalid file is indistinguishable from a render of a valid
   one to the reader holding it — naming which of these behaviours the file
   fails, and pointing to `game-mechanics`, where the upgrade is proposed and
   confirmed with the owner.

5. **`## Competitive Differentiation`** — one section, from
   `design/comp-analysis.md`. Body is that file's own differentiation
   statement and per-competitor records, unchanged. Addressed by the path
   `design/comp-analysis.md`. Absent when the file does not exist: the
   section still appears, stating that plainly and pointing at
   `game-comp-analysis`.

6. **`## Supporting Documents Not Rendered`** — fixed content, not derived
   from any project data; see the next section for what it states.

No section in this list is ever dropped for lack of data — a project missing
one or more of the five inputs still renders a complete `design/gdd.md`, with
each missing part shown as an explicitly absent section carrying that
statement and a pointer to the skill that would populate it, never invented
content and never a silently missing heading.

## The eight absent supporting documents

The spec's own research surveyed nine supporting-document types a GDD
practice commonly names. `design/gdd.md` renders the core GDD — the ninth —
and no other. The `## Supporting Documents Not Rendered` section states all
eight of the rest, and why each is absent, rather than leaving a reader to
wonder whether they were forgotten:

- **Concept Document** and **Marketing & Business Plan** — out of scope for
  this skillset, not merely undone in v1: the Concept Document is already
  served by `game-pillars`'s own concept statement, and the Marketing &
  Business Plan is a business concern outside this skillset's design-quality
  scope.
- **Technical Design Document**, **Art Bible**, **Story/Narrative Bible**,
  **Level Design Document**, **Sound Design Document**, and **Test Plan** —
  absent for a grounding reason: the schema this skillset builds (pillars,
  mechanic entries, the economy graph) carries none of the technical,
  visual, narrative, audio, or QA data any of these six would need to render
  from, and rendering one without that data would mean inventing content
  rather than deriving it. Each is a documented future extension, not a
  silent omission — a later pass would need its own research to determine
  what schema each requires, exactly as this spec already documents for
  Elo/Monte Carlo/MCTS balancing in `game-mechanics`.

This is the spec's own accounting, not one invented here — see
`docs/traverse/specs/2026-09-06-game-design-skillset.md`'s `## Out of scope`
section for the source statement this section restates in the rendered file.

## Rendering procedure

1. Read `design/concept.md`. Render section 1 from it, or its absent form.
2. Read every file under `design/pillars/`. Split by `status`; render section
   2 from the `approved` ones, alphabetically by slug, plus the candidate
   count line if any `candidate` files exist; or the absent form if none
   exist at all.
3. Read every file under `design/mechanics/`. Render section 3 from them,
   alphabetically by slug, or the absent form if none exist.
4. Read `design/economy.md`. Render section 4's node subsections in
   frontmatter `nodes` order, family subsections in frontmatter `families`
   order, and connection subsections (excluding declarations over a family,
   rendered under their family instead) in frontmatter `connections` order,
   or the absent form if the file doesn't exist.
5. Read `design/comp-analysis.md`. Render section 5 from it, or its absent
   form.
6. Append section 6, the fixed eight-absent-supporting-documents statement
   above — this section's content never varies with project data.
7. Assemble sections 1–6, in that order, into one document and write it to
   `design/gdd.md`, replacing whatever content was there before. This is the
   only write this skill makes; it never reads the existing `design/gdd.md`
   before overwriting it, because there is nothing in a prior render that
   this step needs — everything section 1–6 renders comes from the five
   inputs, read fresh, every time.

## Writing the file

Write `design/gdd.md` inside the game project you were invoked against —
never into this skill's own repository. If `design/` does not yet exist in
the consuming project, create it; a project with no structured data at all is
a legal starting state, and step 7 above still produces a `design/gdd.md`
made entirely of absent-section statements.
