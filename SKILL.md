---
name: research
description: Use when asked to research a topic using the internet and produce a written findings doc — e.g. "research X", "look into X and write it up", "find out about X". Not for a narrow single-fact lookup the user clearly wants answered inline rather than saved to a file, and not for automatic folder-drop pickup of research tasks or checking API rate limits before starting — neither is implemented.
---

# research

## Overview

Researches a topic using the host's web-research tools, plus parallel subagents at
higher depth, and writes the findings to a durable markdown doc in the
current project's `research/` folder. Every run is a fresh investigation — no
folder-watching, no rate-limit checking before starting. Works from any project
directory, not just this repo.

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

- **Quick** — run inline in the main conversation. A handful of direct web-research
  calls. No subagents.
- **Thorough** — break the topic into subtopics. Dispatch one parallel general-purpose
  subagent per subtopic; each researches independently and reports back a digest. This keeps heavy search output
  out of the main conversation's context.
- **Deep dive** — same subagent-per-subtopic pattern as thorough, but with more
  subtopics and/or more sources pursued per subagent. Judge the right count at run
  time based on the topic — there's no fixed number.

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

**Location** — `research/<slug>-<date>.md` at the *current* project's root (`slug`:
lowercase, hyphen-separated words drawn from the topic; `date`: `YYYY-MM-DD`, the
actual current date — check it rather than guessing, since a wrong date also
breaks the collision check below):

- Create the `research/` folder if it doesn't exist.
- Tracked in git, not gitignored — a durable artifact, same tier as
  `docs/superpowers/specs/` and `plans/` in this repo.
- Docs accumulate indefinitely; never prune or overwrite a prior run's doc.
- Naming collision (same slug+date, e.g. two runs on the same topic same day):
  append a numeric suffix (`-2`, `-3`, ...) rather than overwriting.

## Edge Cases

| Situation | Response |
|---|---|
| No useful results found (obscure/niche topic) | Say so plainly in Open Questions/caveats — don't fabricate findings to fill the template |
| A subagent fails or times out (thorough/deep dive) | Note the gap explicitly in Open Questions; don't block the write-up, don't silently drop the subtopic |
| Contradictory findings across sources | Capture in Open Questions/caveats — don't silently pick a side |
| `research/` folder missing | Create it |
| Same slug+date already exists | Append a numeric suffix, don't overwrite |

## Common Mistakes

- Skipping the clarifying round and guessing purpose/scope/depth instead of asking
  — the round was deepened because shallow orientation produced write-ups that
  missed what was actually wanted.
- Repeating the "just dive in" skip-ahead reminder on every question instead of
  stating it once at the start of the round.
- Using subagents for a "quick" run, or running "thorough"/"deep dive" inline
  without subagents — depth determines execution mode, not the other way around.
- Pasting the full write-up into chat instead of a short summary plus file path.
- Fabricating findings when a topic turns up nothing useful — report the gap
  instead.
- Overwriting a same-day prior doc on the same topic instead of appending a
  numeric suffix.
