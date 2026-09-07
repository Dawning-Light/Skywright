---
name: game-critique
description: Use when a game project's design data or rendered GDD needs adversarial review rather than more authoring — dispatches independent critic personas, each grounded in one named framework and each given exactly one design unit, and writes every persona's findings as its own critique note in the project. Not for eliciting or editing the design data itself (see `game-pillars`, `game-mechanics`) and not for rendering the GDD a critique cites (see `game-gdd`).
---

# Game Critique

Reviews a game's design by dispatching independent critic personas against it.
This is the fifth of five independent Orrery skills for game design
(`game-pillars`, `game-comp-analysis`, `game-mechanics`, `game-gdd`,
`game-critique`). It defines no design-data shape of its own — every record it
reads is defined once, by the skill that writes it, and this file names that
skill rather than restating the fields. It defines exactly one shape: the
critique note.

A **unit** is the thing a critic is pointed at: one pillar record, one mechanic
entry, or one GDD section. Everything below is measured in units — what a
dispatch carries, what the budget counts, what a critique note is filed
against.

The point of dispatching rather than critiquing inline is that a session which
authored a design validates it instead of finding its flaws. Every rule under
**The dispatch contract** exists to keep the critic away from the reasoning
that produced what it is reading; a shortcut through any one of them turns
this skill back into the failure it was built against.

## Standalone invocation

Run this skill against any game project, regardless of how much or how little
design data currently exists. Nothing here waits on another skill's output and
nothing here refuses to run for lack of one. The suggested order across the
five skills — `game-pillars` → `game-comp-analysis` → `game-mechanics` →
`game-gdd` → `game-critique`, looping back to `game-mechanics` after a
critique pass — is a recommendation, not a requirement this skill enforces.

A project with no `design/gdd.md` still gets a critique: its records are
critiqued directly, and the owner is told once that GDD sections were not
available as units. A GDD section named as a unit when no `design/gdd.md`
exists is dropped from the unit set, with `game-gdd` named as what would
produce it; the remaining units still run.

## The personas

Each persona is one named framework rendered as a checklist. Each has its own
reference file under `references/`, and that file is the whole of what the
persona knows about how to critique.

| Persona | Framework | Reference file |
| --- | --- | --- |
| `mechanics-literalist` | Björk & Holopainen's game design pattern catalog, and the Game Ontology Project taxonomy | `references/mechanics-literalist.md` |
| `player-motivation` | Quantic Foundry's twelve validated player motivations | `references/player-motivation.md` |
| `pillar-fit` | Jesse Schell's lens method, and design-pillars-as-filter practice | `references/pillar-fit.md` |

This table is the persona list. A persona is added by adding a row and its
reference file; nothing else in this skill changes, because every rule below
is written against "each persona in the table" rather than against any
persona by name. The skillset's design names three personas — a
mechanics-literalist, a player-motivation critic, and a pillar-fit critic —
and all three now have a row and a reference file, so the table is the full
intended set.

**Subsetting.** An invocation may name a subset of the personas in the table
and dispatch only those — a targeted follow-up pass after addressing an
earlier round's feedback is the ordinary reason. When the invocation names
none, the default is every persona in the table.

## The dispatch contract

Binding on every dispatch this skill makes.

**A persona is a fresh agent that has never seen the authoring session.**
Dispatch it with the host's fresh-agent mechanism — the **dispatch call** in
the Adapter section below — which starts an agent whose context is the
dispatch prompt and nothing more. Some hosts also offer a **context-inheriting
fork**: an agent that continues the dispatching session's own context and can
therefore see every message that session exchanged, including the reasoning
that produced the design under review. Never dispatch a persona as a fork. The
distinction is named here rather than left implicit because both mechanisms
are "dispatch an agent", both succeed silently, and a fork produces a critique
that reads as independent while having read exactly the material the critic is
supposed to be blind to.

**Exactly one unit per dispatch.** Never the whole design, and never two units
in one prompt. Each persona critiques **one unit at a time** because independent LLM
critique degrades past a few thousand characters of input and under-identifies
weaknesses relative to a human reviewer (the spec's Problem §2). One unit per
dispatch is what keeps every individual read inside the length the research
shows critique quality holds at; batching two units to save a dispatch spends
the whole reason this skill exists.

**The persona's reference file is inlined verbatim into the dispatch prompt.**
Read `references/<persona>.md` and paste its full text into the prompt. Do not
name the path and trust the agent to open it, and do not summarise it —
exactly the reason `research`'s own subagent brief is inlined rather than
referenced: paraphrasing drops exactly the lines that matter, and the lines
that matter here are the checks and the re-grounding rule. A rule the
dispatched agent never reads does not bind it.

**No persona sees another persona's output.** Not at dispatch, not at
follow-up, not in a summary. A persona's dispatch prompt carries no other
persona's findings, and a follow-up sent to one persona quotes no other
persona's note. This binds the dispatches, not the owner: the owner reads
every note, and comparing them is the point of running more than one persona.

**A persona dispatches no agent of its own.** One level of delegation. This
session dispatches personas; personas are leaves. The ban lives inside each
persona's own reference file, which is where the dispatched agent will
actually read it.

**The dispatch payload — the one and only definition of what a persona can
see.** Each dispatch carries the unit, the material below, and nothing else.
What travels depends on the unit type:

| Unit type | What travels with it |
| --- | --- |
| Pillar record, `design/pillars/<slug>.md` | that file's full text; `design/concept.md`'s body |
| Mechanic entry, `design/mechanics/<slug>.md` | that file's full text; the taxonomy index (below); the `title` and `## Description` only of its `parent` and of each entry in its `children`; the nodes and connections of `design/economy.md` that the entry's own text names, connections each named by its `id`; for each family the entry's own text names, both the family declaration and its expanded members, each named by the derived id `game-mechanics` defines; every `design/pillars/<slug>.md` record whose `status` is `approved`, in full |
| GDD section, a section of `design/gdd.md` | that section's text; the record it addresses, by the path or identifier the section names (`game-gdd` guarantees every rendered section names its record); every `design/pillars/<slug>.md` record whose `status` is `approved`, in full |

**The taxonomy index** is every mechanic entry's `name` and `parent`, and
nothing else — two fields per entry, no titles, no descriptions, no bodies. It
travels with a mechanic entry because whether a `parent` edge resolves to an
entry that exists, and whether `parent` and `children` agree in both
directions, are properties of the taxonomy's *shape* that cannot be read off a
single entry. It stays two fields wide for the same reason one unit per
dispatch is the rule: a list of slugs is a bounded read, a directory of entries
is not.

Related entries travel as title-plus-description rather than in full, and the
economy graph travels only as the nodes the unit names, for that same reason —
the bound on the read is what preserves the critique.

**Invalid when a connection in `design/economy.md` has no `id`, or when the
file carries block-style edges or slash-joined headings:** this skill writes
nothing, so it proposes no upgrade of its own. It reports it as invalid
rather than critiquing it on a best-effort basis — a finding about a
connection that cannot be cited back to a record is not a finding the owner
can resolve — naming which of these behaviours the file fails, and pointing
to `game-mechanics`, where the upgrade is proposed and confirmed with the
owner.

**Approved pillar records travel in full**, unlike related mechanic entries,
because a pillar-fit check run against a trimmed pillar cannot read the
keep-or-cut test the check exists to apply — a title alone gives nothing to
run the unit against. This still holds the same bound: `game-pillars` guides
a project toward 2-4 approved pillars rather than refusing a larger count, so
in the ordinary case "every approved pillar record" is a small, fixed-shape
read, not a directory.

**Every check a persona runs is runnable against this payload.** The table
above is the single authoritative statement of what a persona holds; a persona
reference file states checks and never states its own data requirements. A new
check that needs material this table does not carry is added to this table
first — the payload widens by an edit here, never by an assumption there. A
check that would need a **second unit** is not addable at all, because one unit
per dispatch is the rule it would break; such a check is rewritten to run
against what the payload does carry, and to report what it could not reach.

**One note per pass.** Each persona writes exactly one critique note per
dispatch, at the path and in the shape defined below.

## The re-grounding rule

A persona may revise or withdraw a finding **only after** restating that
finding against its own named framework and confirming that the pushback
actually changes that framework's verdict for this specific case — **never
solely because the owner disagreed.**

This rule is stated here as the dispatch-level rule, and it is stated again,
in the persona's own voice, inside each persona reference file. Both copies
are required: this one governs what this skill will accept back from a
persona, and the inlined one is the only copy the dispatched agent ever reads.
Models concede more readily under sequential conversational rebuttal than
under any other critique shape, so the follow-up conversation this skill
enables is precisely where the sycophancy failure would otherwise reopen.

## The dispatch budget

**Hard cap: 9 agents per invocation.** Every persona-times-unit pair is one
agent, so the cap is on their product, not on either factor alone. Two things
fix the number at nine. It sits at the order of magnitude `research` already
established for a deliberately bounded fan-out — that skill's hardest ceiling
is 8 — rather than at whatever number a given project's contents would ask
for. And it divides evenly by the full persona set of three, so a default pass
spends the whole budget on three units with nothing stranded: a cap of 8 would
leave one agent unusable by a full pass, and a cap of 6 would hold a default
pass to two units, thin for a round-trip that asks the owner to read every
note it produces.

Before the first dispatch, multiply the chosen persona count by the chosen
unit count. If the product exceeds 9, stop and put the arithmetic to the
owner with three ways forward, and take one of them:

- **Narrow the unit set** — critique fewer units this invocation.
- **Narrow the persona subset** — one persona instead of three triples how
  many units fit under the same cap.
- **Run in batches** — dispatch at most 9, report those notes, and dispatch
  the next batch only after the owner confirms.

Never raise the cap, and never silently drop units to fit under it. A project
whose unit count makes even batching unwieldy is a signal to narrow the pass
with the owner, not to dispatch more agents.

## The critique note — the one and only definition

One file per persona per pass, at
`design/critique/<YYYY-MM-DD>-<persona>-<unit-slug>.md`, inside the
*consuming* game project — never inside this skill's own repository. Create
`design/critique/` if it does not exist.

- `<YYYY-MM-DD>` — the actual current date. Check it rather than guessing; a
  wrong date also breaks the repeat rule below.
- `<persona>` — the persona's name exactly as the persona table spells it.
- `<unit-slug>` — the unit's own slug: for a pillar record or mechanic entry,
  its filename without `.md`; for a GDD section, the section heading
  lowercased with non-alphanumerics replaced by hyphens.

**Same-day repeats.** If that exact path already exists, the new note takes
the suffix `-2` before `.md`. If `-2` also exists, it takes `-3`, and so on to
the first free ordinal. The first note of the day carries no suffix, the first
repeat is `-2` and never `-1`, and no existing note is ever overwritten. This
applies whenever the same persona critiques the same unit twice on the same
day — the second dispatch is a new pass, not an edit of the first.

A **follow-up** is not a repeat: it is the same pass continuing, and it edits
the existing note in place rather than writing a new one.

Frontmatter:

- `persona` — the persona that wrote the note, as spelled in the persona table.
- `framework` — the named framework that persona critiques from.
- `date` — the `YYYY-MM-DD` in the filename.
- `unit` — the path of the record critiqued (`design/pillars/<slug>.md`,
  `design/mechanics/<slug>.md`), or the name of the GDD section critiqued.
- `status` — `open`, `addressed`, or `withdrawn`. A persona only ever writes
  `open`. `addressed` is set once the owner has changed the design or
  accepted the finding; `withdrawn` is set only when every finding in the note
  has been withdrawn under the re-grounding rule above.

Body: one finding per check that failed, each naming the check it came from,
in the finding shape that persona's reference file defines, plus any check the
persona recorded as applicable but unrunnable against its payload. A pass in
which every check that applied and could run passed still writes its note, with
a body stating that and no findings — a clean pass is a recorded result, not a
missing file. An unrunnable check reported here is a defect in the dispatch
payload above, not in the design under review; take it to the payload table.

## Procedure

1. **Settle the unit set** with the owner: which pillars, mechanic entries, or
   GDD sections are under review. Where the owner names none, propose a set
   from what `design/` currently holds and confirm it before continuing.
2. **Settle the persona subset.** Use the personas the invocation named; where
   it named none, use every persona in the table.
3. **Check the budget.** Multiply persona count by unit count. If it exceeds
   9, apply the overflow rule above and settle a smaller pass before
   dispatching anything.
4. **Assemble each unit's dispatch payload** per the payload table above,
   including the taxonomy index for every mechanic entry. Where
   `design/gdd.md` is absent, drop GDD-section units and tell the owner once.
5. **Dispatch.** For each persona-unit pair, make the **dispatch call** with a
   prompt carrying, in this order: the persona reference file's full text; the
   unit; that unit's dispatch payload from step 4; and the critique-note path
   and shape above. Record the agent identifier the call returns — that
   identifier is what the follow-up call addresses.
6. **Collect the notes.** Confirm each dispatched persona wrote its note at
   the expected path. A persona that returned findings without writing the
   file has not completed its pass; re-dispatch it rather than writing the
   note on its behalf.
7. **Report** the note paths to the owner, one line each. Do not merge the
   notes into a single verdict or reconcile disagreements between personas —
   the disagreement is information the owner reads, and reconciling it here
   would substitute this session's judgement for the frameworks'.

## Follow-up: pushing back on a finding

The owner reads a note, disagrees with a finding, and wants to argue with the
critic rather than receive a fixed objection list.

1. Make the **follow-up call** to that persona's agent identifier from step 5,
   carrying the owner's pushback and nothing from any other persona.
2. The persona answers under the re-grounding rule, and either states that the
   finding stands or states which check now passes and why.
3. Where a finding was revised or withdrawn, the persona edits its existing
   note in place. Where every finding in the note was withdrawn, the note's
   `status` becomes `withdrawn`.

## Adapter — host dispatch and follow-up mechanisms

The only section that names a host's tools. Everything above is written in
terms of the two calls named here; a move to another host rewrites this
section and nothing else.

| Call | On a Claude Code host | Notes |
| --- | --- | --- |
| **dispatch call** | the agent-dispatch tool (`Agent`, `Task` in some builds), with `subagent_type` set to a general-purpose fresh agent and the whole dispatch prompt in `prompt` | returns an agent identifier the follow-up call addresses. `subagent_type: "fork"` is the context-inheriting form the dispatch contract bars — never select it here |
| **follow-up call** | the agent-messaging tool (`SendMessage`), addressed by the identifier the dispatch call returned | reaches only an agent dispatched by this same session |

**A host with no addressable dispatch.** Codex receives this skill under the
same global distribution and has a fresh-agent equivalent of the dispatch call
but no follow-up call. There, everything through step 7 of the Procedure runs
unchanged: the personas are dispatched, they read their inlined reference
files, and they write their critique notes. What is unavailable is the live
follow-up conversation. Handle the owner's pushback there by making a fresh
**dispatch call** carrying the persona's reference file, the same unit and its
material, the prior critique note, and the pushback — the persona then answers
under the re-grounding rule against that note.

**Addressability is session-bound.** Even where the follow-up call exists, it
reaches a persona only within the session that dispatched it. A later session
cannot resume the original agent, and must not pretend to: it re-dispatches
the persona fresh, with its reference file, the unit, and the prior critique
note as input — the same procedure the no-follow-up-call host uses above.
