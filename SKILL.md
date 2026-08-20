---
name: research
description: Use when asked to research a topic using the internet and produce a written findings doc — e.g. "research X", "look into X and write it up", "find out about X". Not for a narrow single-fact lookup the user clearly wants answered inline rather than saved to a file, and not for automatic folder-drop pickup of research tasks or checking API rate limits before starting — neither is implemented.
---

# research

## Overview

Researches a topic using the host's web-research tools, plus parallel subagents at
higher depth, and writes the findings to a durable markdown doc in the
current project's `docs/research/` folder. Every run is a fresh investigation — no
folder-watching, no rate-limit checking before starting. Works from any project
directory, not just this repo.

Subagent dispatch is budgeted (see Execution). An unbudgeted run of this skill
once burned an entire five-hour usage window in minutes; the caps below are the
fix and are not negotiable at run time.

## When to Use

- "research X", "look into X and write it up", "find out about X"

**Not for:**
- A narrow factual lookup the user clearly wants answered inline, not saved to a
  file — if unsure which they want, ask during the clarifying round below.
- Automatic/folder-drop pickup of research tasks — explicit request only.
- Checking usage/rate limits before starting — not implemented.

## Process

### 1. Clarifying round

Adaptive, one question at a time — mirrors `superpowers:brainstorming`'s style.
State once, at the very start of the round, that the owner can say "just dive in"
at any point to cut the round short; the skill then fills in best-guess defaults
for anything left unasked. Don't repeat this reminder on later questions.

No fixed sequence — ask whichever of the following is most useful to ask next
given what's already in the request, skipping anything the initial request
already answered:

- **Purpose** — what the findings are for, or what decision they inform.
- **Scope/angle** — narrow an ambiguous or overly broad topic.
- **Sub-questions** — the specific things that matter most within the topic.
- **Prior context** — what the owner already knows, and any docs/sources the
  write-up should build on rather than re-derive.
- **Depth for this run** — exactly one of:
  - **quick** — a handful of direct searches; best for a narrow, single-fact-shaped
    ask.
  - **thorough** — the topic is broken into subtopics, each researched
    independently and in parallel.
  - **deep dive** — same as thorough, with more subtopics and/or more sources
    pursued per subtopic.

Applies at every depth, including quick. No hard cap on question count, but the
round itself should stay a short exchange — it's the depth of the questions that's
increasing, not the length of the round.

### 2. Execution (depth-gated)

Depth sets a budget, not a mood. These caps are hard:

| Depth | Subagents | Dispatch shape |
|---|---|---|
| quick | 0 — runs inline in the main conversation | a handful of direct web-research calls |
| thorough | 3–5 | one wave |
| deep dive | 6–8 | waves of at most 4, checkpoint between waves |

Needing more than 8 subtopics means the topic is too broad for one run — say so
and propose splitting it into two runs, rather than raising the cap.

**One level of delegation.** The main session dispatches research subagents; those
subagents are leaves and must not dispatch subagents of their own. Cascading
delegation is what turns a research run into a runaway — nothing prevents it by
default, so the ban has to live inside each subagent's own prompt, which is where
the brief puts it.

**Every subagent prompt carries `references/subagent-brief.md` verbatim.** Read
that file and inline its text into each prompt — don't point the subagent at the
path and trust it to go read it. Paraphrasing drops exactly the lines that matter.
It bans nesting, cloning, and large-file ingestion, and sets per-agent fetch,
turn, and output-size budgets.

**Sonnet by default.** Dispatch with `model: "sonnet"`. Opus is opt-in per
subtopic: name the subtopic and the reason in chat before dispatching, and use at
most one Opus agent per run.

**Pre-flight.** Before the first dispatch, post a single line stating the plan —
agent count, model, per-agent budget, wave count — so it can be vetoed before
anything runs. One line, not a proposal document; don't wait for approval unless
the owner objects.

**Persist as you go.** Before dispatching, create `docs/research/` and write the
doc skeleton (header + section stubs). As each digest returns, write it straight
to `docs/research/<slug>-<date>-parts/<subtopic-slug>.md`. A dead session then
costs one agent's work, not the whole run. Delete the parts folder once the final
doc is written — it's folded in by then.

**Checkpoint between waves (deep dive).** After each wave returns, post one line
with what's still open plus each agent's actual token cost if the harness reported
it, then dispatch the next wave. If agents are running far above budget, stop and
report instead of dispatching more.

**The ingestion rules bind the main session too.** No `git clone`, no reading a
file or page over ~200KB into context — during a quick run, while synthesizing, or
at any other point. A 39MB scrape costs the same whoever pulls it in.

**Gaps get one narrow follow-up, never a bigger budget.** A subagent that reports
hitting its budget with items uncovered earns at most one follow-up agent scoped
to just those items, under the same brief. After that, the gap goes in Open
Questions.

If a subagent fails or times out, don't block the whole write-up on it and don't
silently drop the subtopic — note the gap explicitly in Open Questions (see
Output).

### 3. Synthesis

Fold every result — direct findings (quick) or subagents' digests
(thorough/deep dive) — into one write-up following the Output template below.
Contradictory findings across sources go into Open Questions/caveats; never
silently pick a side.

### 4. Write and report

Write the doc to disk (see Output) *before* reporting anything in chat. Then post a
brief chat-visible summary — a few sentences on the key findings — plus the file
path. Don't paste the full write-up into chat; the file holds the detail.

## Output

**Format** — fixed default, overridable for a single run if the user asks for a
different shape (e.g. "just give me a comparison table") — the override applies to
that run only, not future runs:

- Header: topic, date, depth level used
- Short executive summary
- One section per subtopic, with findings
- Sources list (links)
- Open questions / caveats — unresolved or contradictory findings, gaps from a
  failed subagent, anything the write-up couldn't settle

**Location** — `docs/research/<slug>-<date>.md` at the *current* project's root
(`slug`: lowercase, hyphen-separated words drawn from the topic; `date`:
`YYYY-MM-DD`, the actual current date — check it rather than guessing, since a
wrong date also breaks the collision check below):

- Create the `docs/research/` folder if it doesn't exist.
- Tracked in git, not gitignored — a durable artifact, same tier as
  `docs/superpowers/specs/` and `plans/` in this repo.
- Docs accumulate indefinitely; never prune or overwrite a prior run's doc.
- Naming collision (same slug+date, e.g. two runs on the same topic same day):
  append a numeric suffix (`-2`, `-3`, ...) rather than overwriting.
- `<slug>-<date>-parts/` is transient scaffolding for a run in flight — delete it
  once the final doc is written. A parts folder left behind means a run died
  mid-flight; that's deliberate, and it's the first place to look when salvaging.

## Edge Cases

| Situation | Response |
|---|---|
| No useful results found (obscure/niche topic) | Say so plainly in Open Questions/caveats — don't fabricate findings to fill the template |
| A subagent fails or times out (thorough/deep dive) | Note the gap explicitly in Open Questions; don't block the write-up, don't silently drop the subtopic |
| A subagent reports hitting its fetch/turn budget with items uncovered | One follow-up agent scoped to just those items, same brief; after that the gap goes in Open Questions |
| Topic seems to need more than 8 subtopics | Propose splitting into two runs — don't raise the cap |
| Contradictory findings across sources | Capture in Open Questions/caveats — don't silently pick a side |
| `docs/research/` folder missing | Create it |
| Same slug+date already exists | Append a numeric suffix, don't overwrite |
| A prior run died mid-flight and its work needs salvaging | Check for a leftover `<slug>-<date>-parts/` folder first — cheapest source. Then: digests that reported back sit in the parent transcript at `~/.claude/projects/<proj>/<session-id>.jsonl` inside `<task-notification>` → `<result>` blocks; agents that never reported back leave full transcripts at `%TEMP%/claude/<proj>/<session-id>/tasks/<agent-id>.output` (the last long assistant text block is usually the digest); raw artifacts sit in that session's `scratchpad/`. Extract before temp is cleaned |

## Common Mistakes

- Skipping the clarifying round and guessing purpose/scope/depth instead of asking
  — the round was deepened because shallow orientation produced write-ups that
  missed what was actually wanted.
- Repeating the "just dive in" skip-ahead reminder on every question instead of
  stating it once at the start of the round.
- Using subagents for a "quick" run, or running "thorough"/"deep dive" inline
  without subagents — depth determines execution mode, not the other way around.
- Reading the no-nesting rule as "this skill can't use subagents." The main
  session dispatches them; only the subagents themselves are barred from
  dispatching further.
- Paraphrasing or trimming `references/subagent-brief.md` instead of pasting it
  verbatim — the dropped line is always the one that mattered.
- Letting subagents inherit the main session's model instead of setting
  `model: "sonnet"`, or reaching for Opus without naming the subtopic and reason.
- Treating "deep dive" as a licence to dispatch as many agents as the topic seems
  to want. The cap is 8, in waves of 4.
- Holding every digest in memory and writing the doc only at the very end — a dead
  session then loses everything. Write each part file as it lands.
- Pasting the full write-up into chat instead of a short summary plus file path.
- Fabricating findings when a topic turns up nothing useful — report the gap
  instead.
- Overwriting a same-day prior doc on the same topic instead of appending a
  numeric suffix.
