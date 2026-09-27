---
name: game-sync
description: Use when a code change alters behaviour, a value, a name, or a rule that a game design record states — fixes and tuning included — or when design records need checking against the code. Not for authoring new design (see `game-mechanics`, `game-tech`).
---

# Game Sync

Keeps a game project's design records in step with its code. A record states
the design; its `implementation` field says whether that design exists in
code. Once a record is `built` — or `partial`, for everything outside its
`## Not yet built` list — the record and the code must agree. A mismatch is
put to the owner, who decides whether the record catches up or the code has
a bug. A `designed` record is pure intent and is never checked against code.

This is the seventh of seven independent skills for game design
(`game-pillars`, `game-comp-analysis`, `game-mechanics`, `game-tech`,
`game-gdd`, `game-critique`, `game-sync`). It defines no record shape and
writes no record itself: every record change it makes is made by invoking
the skill that owns the record — `game-mechanics` for mechanic entries and
the economy graph, `game-tech` for technical decision records — so
`game-authoring`'s rules govern every write. The owner confirms each change
before it is written. It never edits code.

## Standalone invocation

Run this skill against any game project whose `design/` directory holds
records and whose code sits beside them. It is outside the suggested
authoring order the other skills share (`game-pillars` →
`game-comp-analysis` → `game-mechanics` → `game-tech` → `game-gdd` →
`game-critique`): it is invoked whenever code changes, at any point in that
order. A project with no mechanic entries, no technical decision records,
and no economy graph has nothing to check; say so and stop.

## What it reads

Each at the path and field names its defining skill fixes, never restated
here:

- **The mechanic entry**, `design/mechanics/<slug>.md` — shape defined by
  `game-mechanics`, including its `implementation` field and the
  `## Not yet built` heading `partial` requires.
- **The technical decision record**, `design/tech/<slug>.md` — shape
  defined by `game-tech`, including the same field and heading, which it
  carries only while `accepted`.
- **The economy graph**, `design/economy.md` — shape defined by
  `game-mechanics`. It has no `implementation` field, since it spans many
  systems and one value would be wrong for most of it. It is checked only
  where the owner names it (the whole graph, or named nodes, families, or
  connections), with the named part treated as `built`.
- **The code**, wherever the project keeps it.

Pillars, the concept statement, and the differentiation statement state
intent rather than behaviour, and are never checked against code.

`game-gdd`'s `scripts/find_references.py` lists every record citing a given
record; run it from the project root, as `game-gdd` describes. Unlike the
render, it runs on a corpus still missing `implementation` values.

## Update mode — after a code change

Input: a change, given as a diff, a branch, a commit range, or a
description.

1. **Find affected records.** Search `design/` for records whose claims the
   change touches, using the names and terms in the change — identifiers,
   values, user-facing strings — and `find_references.py` to widen from a
   hit to the records citing it. List the candidates, each with the claim
   it makes, quoted.
2. **Revise each through its owner.** For each record whose claim the change
   alters, write the revision through the owning skill: the new value, name,
   or rule, rewritten per `game-authoring` rules 1–2, with `updated` moved.
   When the change builds something a record describes, propose moving
   `implementation` forward — `designed` → `partial` → `built` — and
   adjusting `## Not yet built` to match. When a record has no
   `implementation` value, propose one as in audit mode, step 5.
3. **Escalate decision changes.** When the change contradicts an accepted
   technical decision record's chosen option, or changes what its
   `## Consequences` commits to or forecloses, do not revise the record. Put
   it to the owner as a supersede, carried out by `game-tech` under its own
   supersede rule.
4. **Report** which records changed, which were checked and left alone, and
   any escalations.

## Audit mode — checking records against the code

On request, over the whole corpus or a subset the owner names.

1. **Select records.** Every `built` record, and every `partial` record with
   its `## Not yet built` items excluded from the check. `designed` records
   are skipped. Records that require `implementation` but lack it — every
   mechanic entry, and every `accepted` technical decision record — are
   collected separately, for step 5. An `open` or `superseded` technical
   decision record correctly carries no `implementation` field and is never
   collected for backfill. The economy graph is included only where the
   owner names it.
2. **Extract claims.** From each selected record, the concrete, checkable
   claims: values, names, counts, sequencing, and rules. Design rationale,
   feel, and examples are not claims.
3. **Check against code.** Look each claim up in the codebase and give it
   one verdict: `matches`, `mismatch`, or `not found`. A pass larger than
   one batch is split across subagents under the dispatch budget below.
4. **Report in chat**, grouped by record: each `mismatch` and `not found`
   claim, quoted, with its code location and what the code actually does,
   then the count of claims that matched. Nothing is written to a file — a
   stored drift report would itself go stale. For each `mismatch` the owner
   chooses: the record catches up (carried out as in update mode, steps
   2–3), or the code is wrong (reported for the owner to fix or track — this
   skill never edits code). A `not found` claim goes to the owner the same
   way: the record may be less built than its `implementation` says, or the
   code may name the thing differently.
5. **Backfill `implementation`.** For each record collected in step 1,
   propose a value from what the code shows, with the evidence — the code
   that implements it, or its absence — and write the confirmed value
   through the owning skill, with `## Not yet built` for `partial`. There is
   no default: a missing value is never assumed to be `designed`, since that
   would hide exactly the built records this audit exists to check.

**Upgrading a corpus.** A mechanic entry or `accepted` technical decision
record written before the `implementation` field existed fails `game-gdd`'s
render, which names the first such record per run and points here. Run audit
mode over the whole corpus: step 1 collects every mechanic entry and every
`accepted` tech record still missing the field, and for those it reduces to
step 5 — an `open` or `superseded` tech record is untouched, since it never
carries the field. Once the render passes, run it again to check the records
the backfill classified `built` or `partial`.

## The dispatch budget

A pass over at most 8 selected records runs in this session, with no
subagents. A larger pass is split into batches of at most 8 records, one
subagent per batch:

- **At most 4 subagents at once.** More than 4 batches run in waves of 4;
  dispatch the next wave only once the last one has returned.
- **State the arithmetic before the first dispatch** — records selected,
  batches, waves — so the owner can narrow the pass before it starts.
- **More than 12 batches (over 96 records) waits for the owner.** Put it to
  them to narrow the pass to a named subset, or to confirm the full run.
- **Never raise the batch size or the concurrency cap** to fit a corpus;
  narrow the pass instead.

Each subagent is a fresh agent made with the host's agent-dispatch call, not
a fork of this session, which would carry this whole conversation into every
batch. It is a leaf: it dispatches no agent of its own and edits no file.
Its prompt carries the batch's record paths, audit steps 2–3 verbatim, the
`partial` exclusion from step 1, the path to the code, and the result shape
below. It returns one JSON array, one object per claim:

```json
[
  {
    "record": "design/mechanics/stack-limits.md",
    "claim": "Ore stacks to 99.",
    "verdict": "mismatch",
    "location": "src/inventory/stacks.py:42",
    "actual": "Every item stacks to 64."
  }
]
```

`verdict` is exactly one of `matches`, `mismatch`, `not found`. `location`
is a `path:line` in the code, or `null` for `not found`. `actual` states what
the code does instead for a `mismatch`, and is `null` otherwise. Merge the
arrays here and report per audit step 4.

## Out of this skill's job

Editing code; deciding for the owner which side of a mismatch is wrong;
critique of the design itself (`game-critique`); rendering (`game-gdd`);
authoring new design (`game-mechanics`, `game-tech`).
