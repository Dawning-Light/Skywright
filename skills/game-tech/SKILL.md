---
name: game-tech
description: Use when a game project's design needs a technical decision made and recorded — networking, simulation, persistence, engine. Not for writing code or engine config.
---

# Game Tech

Proposes, from a game project's existing design data, the technical decisions
that data calls for, and records each decision the owner makes as its own
file inside that project's `design/tech/` directory. This is the fourth of
six independent skills for game design (`game-pillars`,
`game-comp-analysis`, `game-mechanics`, `game-tech`, `game-gdd`,
`game-critique`). It defines exactly one record shape, the **technical
decision record**, and every other skill that reads one (`game-gdd`,
`game-critique`) names this file rather than restating the fields. Every
field it reads from another skill's record is defined once, by the skill
that writes it, and this file names that skill rather than restating the
field.

The stance is elicitation, not generation — the same stance `game-pillars`
and `game-mechanics` take. This skill reads the design data, matches it
against a catalog of decision categories, and puts proposals to the owner
with the record and the phrase behind each one. It writes a decision only
after the owner has confirmed the decision is needed and has stated it.

## Standalone invocation

Run this skill against any game project, regardless of how much or how
little design data currently exists. It is the one skill in the set whose
job is reading the other skills' data, and it requires none of it: on a
project with no design data it proposes nothing on the strength of data, but
the owner can still walk the catalog or name a decision directly. The
suggested order across the six skills — `game-pillars` →
`game-comp-analysis` → `game-mechanics` → `game-tech` → `game-gdd` →
`game-critique`, looping back to `game-mechanics` after a critique pass — is
a recommendation, not a requirement this skill enforces.

## What this skill produces

One file shape, inside the *consuming* game project — never inside this
skill's own repository:

- **The technical decision record**, one file per decision, at
  `design/tech/<slug>.md`.

It never writes into another skill's records. A trigger found in a concept
statement, pillar, mechanic entry, economy graph, or comp-analysis file is
quoted from that file, never edited into it.

## Consumes — read, never restated

Each is read at the path and field names its defining skill fixes:

- **The concept statement**, `design/concept.md` — shape defined by
  `game-pillars`.
- **The pillar record**, `design/pillars/<slug>.md` — shape defined by
  `game-pillars`. Only records with `status: approved` are read for
  triggers; a `candidate` pillar is unsettled and triggers nothing.
- **The mechanic entry**, `design/mechanics/<slug>.md` — shape defined by
  `game-mechanics`.
- **The economy graph**, `design/economy.md` — shape defined by
  `game-mechanics`, including the sigil rule (`#<connection-id>`,
  `@<family>`, bare node id) that a `drivers` entry of the form
  `economy:<ref>` follows. When the file is invalid under `game-mechanics`'
  rules (a connection with no `id`, block-style edges, slash-joined
  headings), leave it out of trigger reading, tell the owner once with a
  pointer to `game-mechanics`, and continue with the rest. Never rewrite
  another skill's file.
- **The differentiation statement**, `design/comp-analysis.md` — shape
  defined by `game-comp-analysis`.
- **Every existing technical decision record**, `design/tech/<slug>.md` —
  this skill's own shape, below.

## The technical decision record — the one and only definition

ADR/MADR-derived, in the frontmatter-plus-markdown shape the skillset already
uses: a YAML frontmatter block between `---` lines, then a markdown body.

### Frontmatter

| Field | Rule |
| --- | --- |
| `name` | The slug. Matches the filename without `.md`. |
| `title` | The decision stated as one sentence. For an `open` record, the question to be decided, stated as one sentence. |
| `status` | Exactly one of `open`, `accepted`, `superseded`. **This set is closed.** `open` means the owner has confirmed the decision is needed but has not made it. A catalog proposal the owner declines is never written at all, so there is no `rejected` status. |
| `category` | A category id from the decision catalog (`references/decision-catalog.md`), or `other`. |
| `scope` | Exactly one of `contained`, `cross-cutting`. **This set is closed.** This is the blast-radius classification, and it decides which body sections are required (below). |
| `drivers` | A list, possibly empty, of what forces this decision. Each entry takes one of three forms. A path to a concept, pillar, mechanic, or comp-analysis record (`design/concept.md`, `design/pillars/<slug>.md`, `design/mechanics/<slug>.md`, `design/comp-analysis.md`). Or `economy:<ref>`, where `<ref>` follows `game-mechanics`' sigil rule: a bare node id, `#<connection-id>`, or `@<family>`. Or a path to another technical decision record, `design/tech/<slug>.md`. A driver that resolves to nothing is invalid. A decision forced only by owner constraints (skills, budget, an existing codebase) has an empty `drivers` list, and its `## Context` states the constraint. |
| `superseded_by` | Present only when `status: superseded`: the `name` of the replacing record. |
| `source` | Always `game-tech`. |
| `updated` | The UTC time of the last write to this file, `YYYY-MM-DDTHH:MMZ` (the form `game-authoring` defines). Moves on every edit — a status change, a new driver, a typo. Check the real clock rather than guessing it. |

### Body

One heading per section, so a reader and a renderer see the same structure:

| Heading | Required when |
| --- | --- |
| `## Context` | Always. States the forces behind the decision. Unlike `game-mechanics`' schema, design-intent forces such as feel and pacing belong here: a technical decision is often driven by exactly the emergent property the mechanics schema excludes. GGPO's "as responsive as offline" is the model case. |
| `## Decision` | `accepted` or `superseded`. Absent while `open`. |
| `## Options considered` | Always when `cross-cutting`; optional when `contained`. Each option comes with its trade-offs. For an `open` record, the options known so far. |
| `## Consequences` | `accepted` or `superseded`; optional while `open`. States what the decision commits to *and what it forecloses*. |
| `## Assumptions to verify` | Optional. Things taken on faith until code exists. |

### Rules

- **Supersede, never reverse in place.** An accepted decision's
  `## Decision` is never edited to say something different. A changed
  decision is a new record. The old record's `status` becomes `superseded`,
  and its `superseded_by` names the new one. Every other edit — a typo, an
  added driver, a new assumption, a refined consequence — is made in place,
  and `updated` moves on every one of them. Superseded records are kept,
  never deleted: they are the project's record of decisions that turned out
  wrong, the source a future agent-facing digest would draw its
  "past mistakes to avoid" from.
- **Unverified assumptions do not block `accepted`.** On a project with no
  code yet, every engine assumption is unverified, so a rule that held a
  record at `open` until its assumptions were checked would leave nothing
  ever accepted. Assumptions are written under `## Assumptions to verify`
  and rendered visibly by `game-gdd` instead.

### Illustrative record — shape, not a decision anyone has made

```markdown
---
name: party-networking
title: Multiplayer parties run on a dedicated authoritative server; clients predict only their own movement.
status: accepted
category: networking-topology
scope: cross-cutting
drivers:
  - design/concept.md
  - design/mechanics/party.md
  - design/mechanics/trading.md
source: game-tech
updated: 2026-09-11T20:42Z
---

## Context
The concept commits to small-form multiplayer through a dedicated server,
where a party mixes two guilds' characters. <...forces, including feel...>

## Decision
<...the owner's stated decision...>

## Options considered
- P2P rollback: <trade-offs>
- Listen server: <trade-offs>
- Dedicated authoritative server: <trade-offs>

## Consequences
Commits to hosting a server. Rules out offline-only builds having party
play. <...>

## Assumptions to verify
- <...>
```

The angle-bracketed spans stand for owner-supplied content.

## The decision catalog

`references/decision-catalog.md` is the only place decision categories are
defined; this file references it and does not restate it. Each category
section there states the question the category settles, the design-data
signals that trigger it, the related categories it tends to force, its
typical options with their trade-offs and pairings, and the named sources
the owner can be pointed to while eliciting. A category is added by adding a
section there; nothing in this file changes, because the procedure below is
written against "each category in the catalog" rather than against any
category by name.

Two categories carry a **sequencing gate**, stated in their own catalog
sections: `engine` is proposed only once every *triggered*
`platform-targets`, `simulation-model`, and `networking-topology` decision
has a record, and `engine-architecture` only after an `engine` record is
`accepted`. One category, `build-and-tooling`, has no design-data trigger at
all and is reached only by a full walk or by the owner naming it.

## Procedure

Before writing or revising any file this skill produces, invoke
`game-authoring` if it has not already run earlier in this conversation. Its
rules govern every body written below; in particular, a body that refers to
a fact another record owns cites it with one of the typed wikilinks
`game-authoring` defines (`[[mechanic:<slug>]]`, `[[node:<id>]]`,
`[[pillar:<slug>]]`, and the rest) rather than restating it, while `drivers`
keep their own path and `economy:<ref>` forms above.

1. **Read what exists**, per Consumes above: `design/concept.md`; every
   `design/pillars/*.md` with `status: approved`; every
   `design/mechanics/*.md`; `design/economy.md` (or, if invalid, skip it and
   say so once); `design/comp-analysis.md`; and every existing
   `design/tech/*.md`.
2. **Open records first.** List every `open` record before proposing
   anything new, and offer to settle each now. An `open` record settled in
   this step is edited in place: `## Decision` and `## Consequences` are
   added, `status` becomes `accepted`, and `updated` moves to now.
3. **Match triggers.** Walk the catalog. Every category that some record
   triggers becomes a proposal carrying the record's address and a
   **verbatim quote** of the triggering phrase. A category no record
   triggers is never proposed as though the data called for it; it is
   reachable only through a full walk or by the owner naming it. A category
   already covered by a live (`open` or `accepted`) record is not proposed
   again, with one exception: a trigger found in a record that is *not*
   among that live record's `drivers` is raised as a re-examination —
   "this may affect `<slug>`; re-examine it?" — which is how a technical
   decision gets flagged when the design moves under it. `engine` and
   `engine-architecture` obey their sequencing gates.
4. **Present, then confirm.** Put the whole proposal list to the owner at
   once: category, citation, and suggested scope for each. The owner
   confirms, declines, or adds a decision (a named catalog category, or
   `other`). Declined proposals write nothing. The owner may instead ask for
   a full walk of every category. **A decline is not sticky.** It means "not
   now", and the same trigger proposes the category again on the next
   invocation. To settle a triggered category for good, the owner records
   the decision that makes it moot — for example, `networking-topology`
   accepted as single-player only. For the `engine` sequencing gate alone, a
   triggered category declined in the current invocation counts as settled
   for that invocation.
5. **Elicit each confirmed decision.** Build `## Context` from its drivers.
   Lay out the catalog's typical options and trade-offs and name its
   sources. This skill may recommend an option. It **never writes a
   `## Decision` the owner did not state or explicitly confirm** — the
   facilitator's rule, and the same propose-and-confirm stance
   `game-mechanics` takes toward a family. A decision the owner makes now is
   written `accepted`; one they defer is written `open`.
6. **Classify scope by blast radius.** Ask: "Do this decision's consequences
   reach another decision, or more than one mechanic?" Yes gives
   `cross-cutting` and no gives `contained`. **Unsure gives
   `cross-cutting`** — uncertainty routes to the heavier path, the one that
   requires `## Options considered`.
7. **Write each record as it is settled**, one file per decision, never
   batched at the end. A decision settled early in the conversation and
   never revisited should already be a file by the time the conversation
   ends.
8. **Supersede rather than reverse.** When the owner changes an accepted
   decision, write the new record and mark the old one `superseded` per the
   Rules above. Never edit an accepted `## Decision` to say something
   different.

## Out of this skill's job

Code, scaffolding, and engine project config (`project.godot`,
`Packages/manifest.json`, `.uproject`) are not this skill's output and are
never read as a substitute for its records: an engine config file holds
values with no rationale, so it cannot stand in for a decision record. When
the owner already has an engine, that fact is recorded as an `accepted`
`engine` record whose `## Context` says so, without re-arguing the choice —
see the catalog's `engine` section.

Technical critique — a technical persona, cross-decision conflict review, a
certification checklist — is not built here. A technical decision record
reaches `game-critique` only through the `## Technical Design` section
`game-gdd` renders from it.

## Writing the files

Write each `design/tech/<slug>.md` inside the game project you were invoked
against — never into this skill's own repository. If `design/` or
`design/tech/` does not yet exist in the consuming project, create it; a
project with no technical decisions and no other design data at all is a
legal starting state, and the owner can still name a decision directly.
