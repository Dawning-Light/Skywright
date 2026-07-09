---
name: research
description: Use when asked to research a topic using the internet and produce a written findings doc — e.g. "research X", "look into X and write it up", "find out about X". Not for a narrow single-fact lookup the user clearly wants answered inline rather than saved to a file, and not for automatic folder-drop pickup of research tasks or checking API rate limits before starting — neither is implemented. Thorough/deep-dive runs may delegate subtopic research to the `gemini` CLI instead of parallel `Agent` subagents, when `GEMINI_API_KEY` is set and `gemini` is on PATH.
---

# research

## Overview

Researches a topic using web tools (`WebSearch`/`WebFetch`, plus parallel `Agent`
subagents or the `gemini` CLI at higher depth) and writes the findings to a durable
markdown doc in the current project's `research/` folder. Every run is a fresh
investigation — no folder-watching, no rate-limit checking before starting. Works
from any project directory, not just this repo.

## When to Use

- "research X", "look into X and write it up", "find out about X"

**Not for:**
- A narrow factual lookup the user clearly wants answered inline, not saved to a
  file — if unsure which they want, ask during the clarifying round below.
- Automatic/folder-drop pickup of research tasks — explicit request only.
- Checking usage/rate limits before starting — not implemented.

## Process

### 1. Clarifying round

Iterative, one question at a time — mirrors `superpowers:brainstorming`'s style, not
a fixed intake form. Converge quickly; this is orientation, not a full brainstorming
session. Establish:

- **Scope/angle** — narrow an ambiguous or overly broad topic.
- **Depth for this run** — exactly one of:
  - **quick** — a handful of direct searches; best for a narrow, single-fact-shaped
    ask.
  - **thorough** — the topic is broken into subtopics, each researched
    independently and in parallel.
  - **deep dive** — same as thorough, with more subtopics and/or more sources
    pursued per subtopic.
- **Backend for thorough/deep dive** (asked only when relevant, after depth is
  chosen): if depth is thorough or deep dive, check whether `GEMINI_API_KEY` is set
  in the environment and `gemini` is on PATH.
  - Either missing → proceed with Agent subagents; don't ask, don't mention it —
    this is the expected common case, not a failure.
  - Both present → ask one more question: use Gemini or Agent subagents for this
    run's subtopic research? Whatever's picked applies to the whole run, not
    per-subtopic.

No hard cap on question count, but don't over-interview — keep it a short exchange.

### 2. First-time Gemini permission setup (conditional)

Only relevant if the question above was asked and answered "Gemini." Before
dispatching anything, check whether the durable Bash permission rule from
"Invocation & security mechanics" (below) is already present in
`~/.claude/settings.json`'s `permissions.allow` array (treat a missing file, or a
missing `permissions.allow` key, as "not granted yet").

- **Already granted** → skip straight to Execution.
- **Not yet granted**:
  - Explain what's needed: the checked-in deny-by-default policy file at
    `skills/research/gemini-policy.toml`, plus a Bash permission rule scoped to the
    exact invocation shape in "Invocation & security mechanics" — never
    `--approval-mode yolo`.
  - Ask whether to set it up now. Use the `update-config` skill to make the
    settings change, following its confirmation flow — never write the rule
    silently.
  - **Declined** → fall back to Agent subagents for this run only. The offer
    returns on a future Gemini-eligible run; declining once doesn't permanently
    disable the feature.
  - **Accepted** → once `update-config` confirms the rule is written, proceed to
    Execution with Gemini.

### 3. Execution (depth-gated)

- **Quick** — run inline in the main conversation. A handful of direct
  `WebSearch`/`WebFetch` calls. No subagents.
- **Thorough** — break the topic into subtopics. Dispatch one parallel `Agent`
  (general-purpose) per subtopic; each researches independently via
  `WebSearch`/`WebFetch` and reports back a digest. This keeps heavy search output
  out of the main conversation's context.
- **Deep dive** — same subagent-per-subtopic pattern as thorough, but with more
  subtopics and/or more sources pursued per subagent. Judge the right count at run
  time based on the topic — there's no fixed number.
- **Thorough / Deep dive, Gemini backend** (chosen in the clarifying round and set
  up per §2 above) — break the topic into subtopics exactly as the Agent-subagent
  path would. For each subtopic, dispatch one `gemini` call via a **background**
  `Bash` call (`run_in_background: true`) so subtopics run in parallel, mirroring
  the Agent-subagent fan-out:

  ```
  gemini -o json --policy "C:/Projects/Orrery/skills/research/gemini-policy.toml" --skip-trust -p '<subtopic prompt>'
  ```

  **Quote the subtopic prompt safely before interpolating it**: replace every `'`
  in the prompt text with `'\''`, then wrap the whole result in single quotes. Use
  single quotes (not double quotes) for this argument — the prompt text is
  arbitrary and a double-quoted form is vulnerable to shell injection from
  characters like `"`, `` ` ``, `$`, or `\` inside it.

  Once each background call completes, read its output, parse the JSON, and
  extract the response text — that becomes the subtopic's digest, flowing into
  synthesis identically to an Agent subagent's digest. (See "Invocation & security
  mechanics" for the exact field name and any parsing caveats.)

If a subagent or `gemini` call fails, times out, or (for `gemini`) returns
unparseable JSON, don't block the whole write-up on it, don't silently drop the
subtopic, and don't retry the subtopic on the other backend — note the gap
explicitly in Open Questions (see Output).

### 4. Synthesis

Fold every result — direct findings (quick) or subagents'/`gemini`'s digests
(thorough/deep dive) — into one write-up following the Output template below.
Contradictory findings across sources go into Open Questions/caveats; never
silently pick a side.

### 5. Write and report

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
| `gemini` call fails, times out, or returns unparseable JSON (Gemini backend) | Same as an Agent subagent failing — note the gap in Open Questions, don't block the write-up, don't silently drop the subtopic, don't retry on the other backend |
| `GEMINI_API_KEY` unset or `gemini` not on PATH | Skip the backend-choice question; use Agent subagents — expected, not an error |
| Gemini permission rule not yet granted and setup declined | Fall back to Agent subagents for this run only |

## Common Mistakes

- Skipping the clarifying round and guessing depth/scope — always confirm both,
  even briefly.
- Using subagents for a "quick" run, or running "thorough"/"deep dive" inline
  without subagents — depth determines execution mode, not the other way around.
- Pasting the full write-up into chat instead of a short summary plus file path.
- Fabricating findings when a topic turns up nothing useful — report the gap
  instead.
- Overwriting a same-day prior doc on the same topic instead of appending a
  numeric suffix.
- Asking the backend-choice question when `GEMINI_API_KEY`/`gemini` aren't both
  available — check first, ask only when genuinely eligible.
- Writing the Gemini permission rule to `~/.claude/settings.json` silently instead
  of confirming via the `update-config` skill.
- Using `--approval-mode yolo` instead of the checked-in policy file — never bypass
  the Policy Engine.
- Double-quoting the subtopic prompt when building the `gemini` command, or
  otherwise skipping the single-quote escaping step — both are shell-injection
  risks.
