---
name: game-comp-analysis
description: Use when a game project needs to know how its concept differs from competitors in its genre. Not for approving a pillar (see `game-pillars`) or a one-off fact lookup (see `research`).
---

# Game Competitive Analysis

Turns competitive analysis into a repeatable procedure: identify competitors,
research each one, and map the findings into a differentiation statement and a
set of candidate design pillars. This is one of six independent Orrery
skills for game design (`game-pillars`, `game-comp-analysis`,
`game-mechanics`, `game-tech`, `game-gdd`, `game-critique`). `game-pillars` is the sole
definition of the pillar record shape and the `design/pillars/<slug>.md`
path; this file names that skill rather than restating its fields, and adds
only the two values described under Candidate pillar records below.

## A main-session skill — never dispatch this as a subagent

Invoke this skill directly, in conversation with the owner, in the main
session. It must never be dispatched as a subagent by another agent, skill,
or orchestration run.

The reason is `research`'s own no-nesting rule. `research`'s
`SKILL.md:81-82` states: "One level of delegation. The main session dispatches
research subagents; those subagents are leaves and must not dispatch
subagents of their own." This skill's whole job is to invoke `research`'s own
flow **in the main session** and let it dispatch its usual 3-5 subagents at
`thorough` depth (`research`'s `SKILL.md:75`). If `game-comp-analysis` itself
were running inside a dispatched subagent, those 3-5 `research` subagents
would become a *second* level of delegation nested under it — exactly the
cascade `research`'s rule exists to prevent. `research`'s own `SKILL.md:15-16`
records what that cascade costs when it happens: an unbudgeted run once burned
an entire five-hour usage window in minutes. This skill avoids repeating that
by construction, not by discipline at run time — it stays a main-session
skill, full stop.

## What this skill produces

Both files live inside the *consuming* game project's own repository, never
inside this skill's own repository:

1. **The differentiation statement**, one per run, at `design/comp-analysis.md`.
2. **Candidate pillar records**, one file per candidate pillar, at
   `design/pillars/<slug>.md`, in `game-pillars`'s pillar record shape.

## Consumes, from `game-pillars`

The pillar record shape and the `design/pillars/<slug>.md` path are defined
once, by `game-pillars`; this file does not restate their fields. Also read
`design/concept.md`, in `game-pillars`'s shape, as the concept the gathered
competitors are differentiated against. If `design/concept.md` does not exist
yet in the consuming project, ask the owner for a short spoken description of
the concept to compare against instead, and say plainly in
`design/comp-analysis.md` that no formal concept statement has been recorded
— pointing at `game-pillars` as where to write one — rather than inventing
one on the owner's behalf.

## The differentiation statement — the one and only definition

`design/comp-analysis.md` opens with a YAML frontmatter block carrying
`source: game-comp-analysis` and `updated` — the UTC time of the last write
to the file, in the `YYYY-MM-DDTHH:MMZ` form `game-authoring` defines,
refreshed on every write. The body holds three things:

- The gap between the project's own concept (from `design/concept.md`, or the
  spoken stand-in above) and the gathered competitors — what the concept does
  that they don't, and where it currently looks like more of the same. Where
  this refers to the concept or to a pillar, it cites the record with one of
  the typed wikilinks `game-authoring` defines (`[[concept]]`,
  `[[pillar:<slug>]]`) rather than restating what that record says.
- One per-competitor record, each covering the seven fields below.
- Optionally, one file-level `## Open Questions` heading, covering the
  analysis as a whole rather than any one competitor: what about the
  differentiation is unsettled, stated plainly per `game-authoring`. Omit the
  heading when nothing is open.

**Every claim in this file cites the `research` write-up it came from, by
path.** This is a requirement this skill enforces, not a recommendation: a
sentence describing a competitor with no citation to a `research` output path
is not written down. Citing by path means naming the actual
`docs/research/<slug>-<date>.md` file (and, if `research` split by subtopic,
the specific section) the claim traces to.

## Eliciting competitors

1. Ask the owner which competitors to analyze — by name, or by naming a
   genre/sub-genre if they'd rather point at a category than a list.
2. **Owner names competitors.** Carry that list forward as-is into Dispatching
   `research` below.
3. **Owner names none.** Do not block waiting for a list. Instead, carry
   forward an **open discovery brief** in place of a named list: identify a
   handful of leading competitors in the stated genre or concept, then
   research each one. This folds discovery into the same `research` dispatch
   rather than treating a missing list as a reason to stop.

Either branch reaches `research` in the same turn — a missing list changes
what gets handed to `research`, not whether `research` runs.

## Dispatching `research`

Invoke `research`'s own flow directly, in the main session, per the
no-nesting rule above. This skill supplies fixed answers to `research`'s own
clarifying round in place of the questions it would otherwise ask, but
**`research`'s clarifying round, its pre-flight line, and its veto are left
entirely intact** — this skill answers that round, it does not replace or
skip it, and the owner stays present for both the clarifying round and the
pre-flight veto exactly as in any other `research` invocation.

The fixed answers this skill supplies:

- **Topic/scope** — the competitor list from Eliciting competitors above (the
  owner's named list, or the open discovery brief), plus the fixed seven-field
  list below, which every competitor record must cover.
- **Depth** — `thorough` by default: 3-5 subagents, one wave, one subagent per
  competitor, inside `research`'s own cap (`research`'s `SKILL.md:75`). Only
  depart from `thorough` if the owner asks for a different depth during
  `research`'s own clarifying round.

**The seven fields**, fixed by the spec's Behaviour 5
(`docs/traverse/specs/2026-09-06-game-design-skillset.md`) and required of
every competitor record `research` returns:

1. Genre/sub-genre.
2. Core loop, broken into early-lifecycle milestones.
3. Meta-systems layer, and when each part of it was introduced.
4. Monetization model and timing.
5. Platform.
6. Player sentiment.
7. Strengths and weaknesses.

No field on this list may be dropped between what this skill hands `research`
and what `research` is asked to return — all seven, including the
meta-systems layer field, reach the dispatch, every run.

## Mapping `research`'s findings

Before writing or revising any file this skill produces, invoke
`game-authoring` if it has not already run earlier in this conversation.

Once `research` has written its doc (or docs, if it split by subtopic) to
`docs/research/<slug>-<date>.md`, map its findings into the two files this
skill owns:

1. **`design/comp-analysis.md`** — write the differentiation statement per
   the shape above, citing `research`'s output path for every claim.
2. **Candidate pillar records** — see below.

## Candidate pillar records

Where the gathered competitor findings surface a pillar candidate — a design
direction the project could adopt or should deliberately avoid to
differentiate itself — write it as a pillar record in `game-pillars`'s shape,
at `design/pillars/<slug>.md`, with exactly two fields fixed by this skill:

- `status: candidate`
- `source: game-comp-analysis`

Every other field in the record follows `game-pillars`'s own definition of
the shape; this file does not restate them.

**This skill never writes `status: approved`, under any circumstance.**
Approval is the owner's own act, performed only through `game-pillars` — the
skill that owns pillar approval. A candidate this skill writes and an
approved pillar `game-pillars` writes are the same record shape, so a reader
can always tell which is which from the `status` field alone, without a
second record type to distinguish them.

## Standalone invocation

Run this skill against any game project that already has a concept statement
(or a spoken stand-in, per Consumes above) — nothing here waits on
`game-mechanics`, `game-tech`, `game-gdd`, or `game-critique`, and none of
their output is read or required. The suggested order across the six skills
— `game-pillars` → `game-comp-analysis` → `game-mechanics` → `game-tech` →
`game-gdd` → `game-critique` — is a recommendation, not a requirement.
