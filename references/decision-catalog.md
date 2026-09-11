# Decision catalog

The only place `game-tech`'s decision categories are defined. `SKILL.md`
references this file and does not restate it; `game-gdd` and `game-critique`
read a record's `category` as an opaque id and never open this file. A
category is added by adding a section here, in the shape every section below
follows:

1. **Settles** — the question the category answers.
2. **Triggered by** — the design-data signals that make it relevant, written
   as descriptions of signals rather than bare keywords. `game-tech` reads
   the consuming project's design data for these signals and quotes the
   triggering phrase verbatim in each proposal.
3. **Tends to force** — related categories a decision here usually reaches
   into.
4. **Typical options** — with their trade-offs, and the option-level
   pairings that make one choice pull another along.
5. **Sources** — named material `game-tech` can point the owner to while
   eliciting.

**Grounding note.** Every category below is sourced, but the categorization
itself — this particular split into nine — is the research's own synthesis
(`docs/research/game-design-tdd-2026-09-11.md`), not a pre-existing
published split. The owner approved it as the domain judgement the research
asked for. "Progress while the game is closed" was not a research finding;
it appears only as a `simulation-model` trigger, never as a category of its
own.

A record whose `category` matches none of the ids below carries `other`.

---

## `simulation-model`

**Settles.** Whether the simulation is deterministic; whether the timestep
is fixed or variable; the tick rate; and how elapsed time is simulated when
the game was not running.

**Triggered by.**
- Real-time multiplayer of any form — two players' simulations must agree.
- Replays, spectating, or sharing a recorded session.
- Physics-driven mechanics, where outcomes depend on integration order and
  timestep.
- Progress that continues while the game is closed — an idle or
  offline-accrual mechanic, a timer that keeps running, a resource that
  accumulates between sessions.

**Tends to force.** `networking-topology`, `persistence`.

**Typical options.**
- **Variable timestep** — simulate whatever wall-clock time elapsed each
  frame. Simplest; outcomes differ run to run, and physics can explode under
  a long frame.
- **Fixed timestep** — simulate in constant ticks, rendering interpolated
  between them. Reproducible; needs an accumulator and interpolation, and
  the tick rate becomes a committed number.
- **Deterministic simulation** — same inputs always produce the same state.
  Pairs with lockstep or rollback netcode and with fixed-point math (or a
  strict floating-point discipline), because the pairing is what makes a
  replay or a remote peer's simulation match. Costs every subsystem the
  freedom to use non-deterministic sources.
- **Non-deterministic simulation** — pairs with a server-authoritative
  topology that ships state rather than inputs.
- **Elapsed-time catch-up** — for progress while closed: replay every
  missed tick (exact, unbounded cost), compute a closed-form result (cheap,
  only for mechanics with a closed form), or cap the catch-up at a maximum
  window (bounded, and a design decision about what the cap means).

**Sources.**
- Tim Ford, GDC 2017 — *Overwatch* gameplay architecture and netcode;
  simulation locked to a fixed 60Hz tick as the foundation for prediction
  and rollback.
- BMAD-METHOD `decision-catalog.yaml` — the "deterministic simulation pairs
  with rollback netcode, fixed-point math, lockstep multiplayer" pairing.

---

## `networking-topology`

**Settles.** None, peer-to-peer, listen server, or dedicated server; where
authority lives; and whether clients predict, roll back, or run lockstep.

**Triggered by.**
- Co-operative play with another player.
- Player-versus-player play.
- Parties, groups, or sessions that mix players from different accounts.
- Player-to-player trading, or any state two players share and both can
  change.

**Tends to force.** `simulation-model`, `persistence`, `platform-targets`.

**Typical options.**
- **Single-player only** — the decision that makes this category moot.
  Recording it `accepted` is how an owner stops the trigger from re-firing.
- **P2P lockstep** — every peer runs the same deterministic simulation on
  the same inputs; requires `simulation-model` deterministic. Latency is
  the slowest peer's; cheating is hard to police.
- **P2P rollback** — lockstep with prediction: each peer runs ahead on
  predicted inputs and rewinds when real ones arrive. Pairs with
  deterministic simulation and a fixed tick. Feels "as responsive as
  offline" (the GGPO framing); costs the ability to re-simulate several
  ticks in one frame.
- **Listen server** — one player's client is the authority. No hosting
  cost; host advantage and host migration are the price.
- **Dedicated authoritative server, with client prediction and lag
  compensation** — the server owns the state; clients predict their own
  actions and are corrected. Anti-cheat and consistency come with a hosting
  bill and an offline-play foreclosure.

**Sources.**
- Glenn Fiedler, "What Every Programmer Needs To Know About Game
  Networking" (*Gaffer On Games*) — the field's most-cited foundational
  reference on lockstep, prediction, and state synchronization.
- Valve, "Source Multiplayer Networking" — prediction, interpolation, and
  lag compensation on an authoritative server.
- Tony Cannon, GGPO — rollback netcode; "as responsive as offline" as the
  design target.
- Jamie Fristrom, Torpex Games — on the Xbox 360 TCR cost of shipping, and
  the recommendation to keep a small studio's game single-player to cut it.

---

## `persistence`

**Settles.** The save format; versioning and migration between versions;
atomic writes; and where saves live — local, cloud, or on a server.

**Triggered by.**
- Any progression that persists across sessions: levels, unlocks,
  inventory, currency, quest state, settings the design treats as part of
  the game.

**Tends to force.** `simulation-model`, `networking-topology`,
`content-pipeline`.

**Typical options.**
- **Versioned envelope with stepwise migration** — every save carries a
  version number, and loading runs each migration step in order. The only
  option that survives shipping a second version.
- **Atomic write** — write to a temporary file and rename over the old
  save, so a crash mid-write leaves the old save intact. Pairs with the
  envelope above; cheap enough that its absence is a decision to record.
- **Local** — files on the player's machine. Simplest; no sync, no
  cross-device play.
- **Cloud-synced local** — local files mirrored by a platform service
  (Steam Cloud, console cloud saves). Conflict resolution becomes a design
  question.
- **Server-authoritative** — the server holds the canonical state. Pairs
  with a dedicated-server `networking-topology`; forecloses offline play.

**Sources.**
- Jurie Horneman — "add version numbers to everything"; the failure mode of
  saving before a load has completed, which wipes the save.
- Tom Francis — "loading a savegame is time travel": every system must be
  restorable to an arbitrary earlier state.
- BlackSands devlog — commit to one save system early rather than retrofit
  one.

---

## `performance-budget`

**Settles.** The target frame rate; the frame-time and memory budgets; and
how those budgets are partitioned across subsystems.

**Triggered by.**
- Platforms stated in the concept or comp-analysis (a mobile target and a
  PC target imply different ceilings).
- A 3D presentation.
- Large simultaneous entity counts — crowds, swarms, bullet-hell density,
  big simulations.

**Tends to force.** `platform-targets`, `engine`.

**Typical options.**
- **30 vs. 60 fps** (or higher) — the target fixes the frame budget: about
  33 ms or 16 ms per frame.
- **Subsystem partition** — an explicit ms allotment per subsystem (sim,
  physics, rendering, AI, audio) on each of CPU and GPU, so an overrun is
  attributable.
- **Memory ceiling** — a total and a per-subsystem partition, especially
  where a console or mobile target fixes the total.

**Sources.**
- Christian Gyrling, Naughty Dog, GDC 2015 — "Parallelizing the Naughty
  Dog Engine Using Fibers"; frame budgeting under a fixed target.
- Jason Gregory, *Game Engine Architecture* — budgeting frame time and
  memory across subsystems.

---

## `platform-targets`

**Settles.** Which platforms ship; which input methods are first-class; and
the certification burden that follows.

**Triggered by.**
- Platforms named in the concept statement, a pillar, or the comp-analysis.
- Input methods named or implied — touch, controller, mouse and keyboard.

**Tends to force.** `performance-budget`, `networking-topology`, `engine`.

**Typical options.**
- **PC** — widest input variety; least certification.
- **Console** — fixed hardware and a certification pass per platform
  (Xbox XR, Sony TRC, Nintendo Lotcheck), whose requirements reach into
  save handling, suspend/resume, and networking.
- **Mobile** — touch-first input, store review, tight memory and thermal
  budgets.
- **Web** — browser sandbox; constrains persistence and networking options.
- **Input methods** — mouse and keyboard, controller, touch; each first-class
  method is a UI and interaction commitment, not a mapping.

**Sources.**
- Microsoft console certification requirements — the shape of a
  certification checklist.
- Jamie Fristrom (Torpex) — the certification cost of a console release,
  and how multiplayer multiplies it.

---

## `content-pipeline`

**Settles.** How authored content is stored and built; file formats; and
the asset build.

**Triggered by.**
- Large authored tables — items, affixes, bestiaries, quests, dialogue,
  crafting recipes.
- Procedural generation, which needs its inputs authored somewhere.
- Modding, which fixes the content format as a public interface.

**Tends to force.** `persistence`, `engine`.

**Typical options.**
- **Text data files** (JSON, YAML, CSV) — diffable, mergeable, mod-friendly;
  need a load-and-validate step.
- **Engine-native assets** (ScriptableObjects, Godot resources, Unreal data
  assets) — editor tooling for free; opaque to diff and to modders.
- **Spreadsheet export** — designers author in a spreadsheet, a build step
  exports. Pairs with text data files.
- **Asset build with dependency tracking** — rebuild only what changed; the
  option that scales past a few hundred assets.

**Sources.**
- Rémi Quenin, GDC 2018 — *Far Cry 5*'s asset build and dependency
  pipeline.
- Bitsquid — the data-driven engine talks on flat, text-authored content.

---

## `build-and-tooling`

**Settles.** Version control; continuous integration; build automation.

**Triggered by.** **No design-data trigger.** Nothing in a concept, pillar,
mechanic, economy graph, or comp-analysis calls for this category, so
`game-tech` never proposes it on the strength of data. It is reached only by
a full walk of the catalog or by the owner naming it.

**Tends to force.** `engine`.

**Typical options.**
- **Git, with LFS for binary assets** vs. **Perforce** — the former is the
  default for a solo or small team; the latter earns its cost on
  binary-heavy projects with many contributors.
- **CI or none** — an automated build on every push, or a manual build. On
  a solo project "none" is a legitimate decision to record, not an
  oversight.

**Sources.** The weakest-sourced category in the research: only generic
vendor material was found, no named practitioner source. The catalog says
so rather than citing something it does not have.

---

## `engine`

**Settles.** The engine or framework the game is built on.

**Triggered by.** **Sequencing gate.** Proposed only once every *triggered*
`platform-targets`, `simulation-model`, and `networking-topology` decision
has a record — `open` or `accepted`. A category among those three that no
data triggers does not hold the gate; one the owner declined in the current
invocation counts as settled for that invocation only. The gate exists
because engine choice comes after concept, features, platform, and budget
are known, not before.

**When the owner already has an engine**, it is recorded `accepted` as-is,
with `## Context` stating that the engine was already in place, without
re-arguing the choice. The gate does not apply to recording a fact.

**Tends to force.** `engine-architecture`.

**Typical options.**
- **Unity** — C#, broad platform reach, mature asset store; licensing has
  shifted before.
- **Godot** — open source, node/scene model, GDScript or C#; younger
  console path.
- **Unreal** — C++ with Blueprint, strongest 3D rendering; heaviest for a
  solo 2D project.
- **GameMaker** — 2D-focused, fastest to first playable in its niche.
- **A framework** (LÖVE, MonoGame, Bevy) — a library rather than an editor;
  full control, and every tool is the owner's to build.
- **Custom engine** — the option the source warns against for a project
  whose goal is shipping a game rather than an engine.

**Sources.**
- Miko Charbonneau, "Choosing the Perfect Game Engine" — engine choice
  follows concept, features, platform, and budget.
- Mark Easton, "Diary of a game 1 – Capturing architectural decisions",
  *Game Developer* 2019 — ADR-01 on a solo project choosing LÖVE over a
  full engine, and the record of why.

---

## `engine-architecture`

**Settles.** How the project adopts the chosen engine's own canonical
architectural split.

**Triggered by.** **Sequencing gate.** Proposed only after an `engine`
record is `accepted`, and that record is always among this record's
`drivers`. Without an accepted engine there is no split to adopt.

**Tends to force.** Nothing further in this catalog.

**Typical options** — one canonical split per major engine, and no more:
- **Unity** — ScriptableObject for data, MonoBehaviour for behaviour.
- **Godot** — node and scene composition, "tailored to the individual needs
  of a project" in the engine's own words.
- **Unreal** — a C++ foundation with Blueprint on top.
- **Any other engine or framework** — no catalog-supplied options; the
  owner states the split, and the record carries it.

**Sources.**
- Unity, Godot, and Epic official documentation — each engine's own
  architecture guidance, and nothing beyond it. Deeper engine guidance is a
  documented future extension, not something this catalog carries.
