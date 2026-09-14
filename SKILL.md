---
name: game-authoring
description: Use when about to write or revise a game design record — a concept statement, pillar, mechanic entry, economy graph, differentiation statement, or technical decision record.
---

# Game Authoring

The rule set every design-writing skill in the game-design skillset loads
before it writes. This skill defines no record shape and produces no file of
its own: `game-pillars`, `game-comp-analysis`, `game-mechanics`, and
`game-tech` each invoke it before writing or revising a record they own, and
the seven rules below govern what they write. `game-gdd` (renders only) and
`game-critique` (reads only, and its critique notes are not a shape these
rules govern) do not invoke it.

This is the one and only place these rules are defined. A calling skill
names this file; it does not restate the rules.

## The seven rules

1. **Current-state prose only.** A record states what the design is, never
   what it used to be or how it changed. No history or transition wording —
   "now", "no longer", "used to", "originally", "before X existed", "this
   migration", "replacing..." — in a record body, unless the design itself is
   about change over time (a mechanic whose own state changes during play).
   History belongs in git and, where deliberately kept, in `design/ideas.md`
   or a superseded record — never in the live one.

2. **Rewrite the affected unit, don't splice.** When a decision changes,
   rewrite each affected paragraph and example so it reads as though the
   current design had always been the design, rather than appending a clause
   to what is already there.

3. **No orphan content — ask first.** Everything written lands under an
   existing heading in the shape being authored. Content with no natural
   heading stops the write: put it to the owner as a choice between extending
   the shape with a new heading, or leaving the content out. Never write it
   without a heading, and never infer the extension and write it
   unconfirmed — the same propose-and-confirm posture `game-mechanics` takes
   toward a detected family and `game-tech` toward a proposed decision.

4. **Cite, don't restate.** When a record refers to a fact owned by another
   record — a count, a value, a name, a relationship — it cites that record
   with a typed wikilink (below) and says nothing further about the fact
   itself. The owning record is the only place the fact is stated. Nothing is
   duplicated, so nothing needs to be found and re-synced after a change: if
   the owning record changes, every citation still reads correctly by
   construction, and if a citation's target is renamed or removed,
   `game-gdd`'s render refuses to render until it is fixed. That refusal is
   what surfaces a break, in place of a tree-wide manual search.

5. **A citation must resolve to what it claims.** Citing `[[tech:X]]` as the
   source of a rule requires `X` to actually state that rule. `game-gdd`'s
   render checks only that a reference resolves to a real record; it cannot
   check that the record supports the claim. That check is this skill's, at
   write time.

6. **Open questions are stated, not hedged.** Unsettled content goes under
   the shape's `## Open Questions` heading (below), stated plainly. A settled
   statement that becomes uncertain is rewritten there, and anything
   elsewhere in the record still asserting the old certainty is rewritten
   too — not left standing beside a caveat that contradicts it.

7. **Be concise.** Explain clearly and simply, in as few words as the content
   needs. Prefer the plain statement over the padded one.

## Typed wikilinks

A closed set of eight reference forms, usable in any record body these
skills write:

| Form | Resolves to |
| --- | --- |
| `[[pillar:<slug>]]` | `design/pillars/<slug>.md`, with `status: approved` |
| `[[mechanic:<slug>]]` | `design/mechanics/<slug>.md` |
| `[[node:<id>]]` | a node `id` in `design/economy.md` |
| `[[family:<name>]]` | a family `name` in `design/economy.md` (bare, no `@`) |
| `[[connection:<id>]]` | a connection `id` in `design/economy.md` (bare, no `#`) |
| `[[tech:<slug>]]` | `design/tech/<slug>.md`, with `status: open` or `accepted` |
| `[[concept]]` | `design/concept.md` |
| `[[comp-analysis]]` | `design/comp-analysis.md` |

The last two carry no identifier: one concept statement and one
differentiation statement exist per project. The type prefix is what makes a
reference unambiguous — a pillar slug and a mechanic slug can never collide
under one reference — and it is what lets a citation reach every record kind.
An untyped `[[slug]]` is not a reference form; `game-gdd` refuses to render
it. A candidate pillar and a superseded technical decision record have no
section of their own in the render, so neither can be cited: a citation
names something the reader can be taken to.

`game-gdd`'s render resolves every reference to a real anchor in `gdd.html`
and carries the same reference through to `gdd.md`. A reference that does
not resolve — an unknown type, an identifier that names nothing, or a
malformed `[[...]]` — is a hard render failure: nothing is written, and
stderr names the file, the reference, and what it fails to resolve to. Text
inside a code span or a fenced code block is never read as a reference.

## `## Open Questions`

The pillar record, concept statement, mechanic entry, and differentiation
statement each accept an optional `## Open Questions` heading; each owning
skill places it within its own shape. It holds unsettled content, stated
plainly, per rule 6. A record with the heading empty, or with the heading
omitted where nothing is open, is valid — the heading exists to hold content
when there is any, not to be always populated.

The economy graph does not gain the heading: its per-node and per-family
prose notes are rationale, a different purpose from an open question. The
technical decision record already has `## Assumptions to verify`, its own
version of the same idea, scoped to unverified engine assumptions.

## `updated`

Every record shape's frontmatter carries `updated`:

```yaml
updated: 2026-09-11T20:42Z
```

`YYYY-MM-DDTHH:MMZ`, UTC, 24-hour clock. Set it to the actual current date
and time — check the clock, do not guess — on every write to the record, not
only on a status change. For the economy graph, the one `updated` sits at
file level beside `nodes`, `connections`, and `families`, and moves on every
rewrite of the file. `game-gdd` renders the value beside each section's
`Source:` caption — raw in `gdd.md`, converted to the reader's local time in
`gdd.html`.

## Quick check before writing

- Does any sentence describe a change rather than the design? Rewrite it
  (rules 1, 2).
- Does every paragraph sit under a heading the shape defines? If not, stop
  and ask (rule 3).
- Does any sentence state a fact another record owns? Replace the statement
  with a typed wikilink (rule 4), and confirm the target says what the
  citation claims (rule 5).
- Is anything uncertain? Say so under `## Open Questions`, and remove the
  certainty it replaces (rule 6).
- Is `updated` the current UTC time?
