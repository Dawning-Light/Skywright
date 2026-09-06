---
name: game-pillars
description: Use when a game project has no design pillars yet, or the owner wants to state or revise the concept for a game — conversationally elicits a concept statement and 2-4 design pillars and writes each as its own file in the project. Not for evaluating whether an existing pillar still holds under scrutiny (that is a `game-critique` persona's job) and not for proposing pillars from competitor research (see `game-comp-analysis`, which writes the same record shape with `status: candidate`).
---

# Game Pillars

Elicits, from the owner, a short concept statement and 2-4 design pillars for
a videogame project, and writes each as its own file inside that project's
`design/` directory. This is one of five independent Orrery skills for
game design (`game-pillars`, `game-comp-analysis`, `game-mechanics`,
`game-gdd`, `game-critique`); this file defines the concept-statement and
pillar-record shapes once, and every other skill that reads or writes either
one names this file rather than restating the fields.

## Standalone invocation

Run this skill against any game project, with no other skill present and
regardless of what already exists in that project's `design/` directory.
Nothing here waits on another skill's output, and nothing here refuses to run
for lack of one.

A **suggested** order across the five skills exists —
`game-pillars` → `game-comp-analysis` → `game-mechanics` → `game-gdd` →
`game-critique`, looping back to `game-mechanics` after a critique pass — but
it is a recommendation, not a requirement. Invoking this skill first, last,
or on its own, against a project that has no other design files at all, is a
legal use of it, not an out-of-order one.

## What this skill produces

Two file shapes, both inside the *consuming* game project — never inside
this skill's own repository:

1. **The concept statement**, one per project, at `design/concept.md`.
2. **The pillar record**, one file per pillar, at `design/pillars/<slug>.md`.

Both are the frontmatter-plus-markdown shape this repository's own skills
already use for structured-but-readable records: a YAML frontmatter block
between `---` lines, then a markdown body.

### The concept statement shape

At `design/concept.md`. Frontmatter carries whatever fields the elicitation
below settles — at minimum a `title` for the game and a `status` (this skill
only ever writes `approved`, the same convention the pillar record uses).
Body: 2-4 sentences of prose stating what the game is and what a player does
in it — concrete enough that a reader unfamiliar with the project could
describe it back in one sentence. Not a pitch, not a feature list — a
statement a design pillar can be checked against.

### The pillar record shape — the one and only definition

At `design/pillars/<slug>.md`, one file per pillar. This is the sole
definition of this shape; a later skill that writes or reads a pillar
record (`game-comp-analysis` writing a candidate, `game-gdd` or
`game-critique` reading an approved one) names this file rather than
restating the fields below.

Frontmatter:

- `name` — the slug, matching the filename without its extension.
- `title` — the pillar stated as one sentence.
- `status` — `approved`. This skill only ever writes `approved`;
  `game-comp-analysis` writes the same shape with `status: candidate` for a
  pillar it proposes from competitor research, pending the owner's review.
  `status` is a first-class field for exactly this reason — the two states
  are one record shape, distinguished by this field, never two record types.
- `source` — the skill that wrote the file. This skill always writes
  `game-pillars` here.

A pillar record this skill writes therefore always opens:

```
---
name: <slug>
title: <the pillar, as one sentence>
status: approved
source: game-pillars
---
```

Body: the keep-or-cut test this pillar settles, stated as a rule a reader
could apply to a feature proposal, plus **at least one worked keep and one
worked cut** — a concrete feature proposal on each side, with the verdict
the pillar produces and the one sentence of reasoning that connects the
pillar's wording to that verdict. A pillar record with no worked example is
not usable: nothing in it lets a later reader check whether the pillar
actually arbitrates anything, as opposed to merely sounding decisive.

## The arbitration test

A design pillar is a short statement specific enough to arbitrate a
keep-or-cut dispute over a proposed feature. **A pillar too vague to settle
such a dispute has failed its own purpose** — this is the domain's own
definition of a pillar, not a style preference, and it is the test this
skill applies to every pillar the owner proposes before writing it down.

Apply the test by trying the pillar against two invented feature proposals,
one that should clearly survive it and one that should clearly not, before
accepting the pillar's wording. If either invented proposal fails to produce
a clear verdict, the pillar is too vague as stated — narrow it with the
owner and try again. Do not write a pillar record until this test has
produced at least one keep and one cut.

**Example of a vague aspiration failing the test, and its repair.** The
owner proposes "the game should be fun." Tried against a feature proposal —
say, adding a daily login bonus — the pillar produces no verdict: a daily
login bonus can be defended as fun and attacked as not fun with equal ease,
because "fun" names no property the feature either has or lacks. This is
the pillar failing its own purpose, and the correct response is to say so
to the owner and ask what "fun" is standing in for here, not to write the
vague version down and move on. Suppose the owner clarifies: the game
should reward mastery, not chance. That becomes the pillar, and it now
arbitrates:

- **Worked cut.** A loot box awarding random cosmetic upgrades on a timer,
  unrelated to player skill, is cut: the reward is gated by chance and
  elapsed time, not by anything the player got better at.
- **Worked keep.** A boss encounter whose telegraphed attack patterns can be
  learned and reliably dodged with practice is kept: the reward for beating
  it is gated by the player's improving skill at reading and reacting to
  those patterns, which is exactly what the pillar names.

A pillar that produces both of these verdicts, for reasons traceable to its
own wording rather than to outside judgement, has passed the test and is
ready to write down.

## Eliciting the concept and pillars

1. Ask the owner for a short description of the game: what it is, what a
   player does. Write this back in 2-4 sentences and confirm it with the
   owner before treating it as settled — this becomes `design/concept.md`'s
   body once confirmed.
2. Ask the owner to propose design pillars — 2-4 of them. A proposal at this
   stage may be as informal as the owner likes; formalizing it is this
   skill's job, not the owner's.
3. For each proposed pillar, run the arbitration test above: invent a keep
   candidate and a cut candidate, check that the pillar's current wording
   produces a clear verdict on both, and narrow the wording with the owner
   until it does. Do not skip a pillar that seems obviously fine — the test
   is what makes "obviously fine" checkable rather than assumed.
4. Once a pillar passes the test, pick its slug (a short, lowercase,
   hyphen-separated name for the pillar's own idea — not a restatement of
   the title), and write `design/pillars/<slug>.md` per the shape above,
   with the keep and cut from step 3 as the body's worked examples.
5. Stop once the owner has 2-4 approved pillars. A fifth or later proposal
   in the same session is a signal to ask the owner which existing pillar it
   overlaps, rather than to write a fifth file — this skill does not cap the
   count by refusing a write, but a concept needing more than 4 pillars to
   state is a sign the concept statement itself is still too broad, and that
   is worth naming to the owner before writing more files.

## Writing the files

Write `design/concept.md` and each `design/pillars/<slug>.md` inside the
game project you were invoked against — the project whose `design/`
directory holds (or will hold) its structured design data. Never write
either shape into this skill's own repository. If `design/` or
`design/pillars/` does not yet exist in the consuming project, create it;
an empty `design/` directory is exactly the starting state this skill is
built to run against.
