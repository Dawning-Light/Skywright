# Game Design Document

## Concept

No concept statement has been recorded yet — `design/concept.md` does not exist. Run `game-pillars` to write one.

## Design Pillars

No approved design pillar has been recorded yet — `design/pillars/` holds no record with `status: approved`. Run `game-pillars` to write one.

## Mechanics

### Armory

*Source: `design/mechanics/armory.md` · Updated: 2026-09-20T09:00Z*

- Parent: none
- Children: `gauntlets`
- Part of: none
- Parts: none

#### Description

The room a character's gear is stored and swapped in.

### Gauntlets

*Source: `design/mechanics/gauntlets.md` · Updated: 2026-09-20T09:01Z*

- Parent: `armory`
- Children: none
- Part of: `loadout`
- Parts: none

#### Description

Carries both relations: a kind of armory, and a part of a loadout. It nests
under `parent`, so `loadout` lists a part that renders elsewhere.

### Loadout

*Source: `design/mechanics/loadout.md` · Updated: 2026-09-20T09:02Z*

- Parent: none
- Children: none
- Part of: none
- Parts: `gauntlets`, `quick-slots`, `salvage-rules`

#### Description

The set of gear a character takes into a run.

### Quick Slots

*Source: `design/mechanics/quick-slots.md` · Updated: 2026-09-20T09:03Z*

- Parent: none
- Children: none
- Part of: `loadout`
- Parts: none

#### Description

Composition alone: no parent, so this nests under its container.

### Salvage Rules

*Source: `design/mechanics/salvage-rules.md` · Updated: 2026-09-20T09:06Z*

- Parent: `no-such-mechanic`
- Children: none
- Part of: `loadout`
- Parts: none

#### Description

A dangling parent. It renders as a root rather than falling back to its
`part_of`, so the typo stays visible.

### Ring One

*Source: `design/mechanics/ring-one.md` · Updated: 2026-09-20T09:04Z*

- Parent: none
- Children: none
- Part of: `ring-two`
- Parts: `ring-two`

#### Description

Half of a deliberate two-entry composition cycle. Every record in a cycle
still renders exactly once.

### Ring Two

*Source: `design/mechanics/ring-two.md` · Updated: 2026-09-20T09:05Z*

- Parent: none
- Children: none
- Part of: `ring-one`
- Parts: `ring-one`

#### Description

The other half of the cycle.

## Economy

No economy graph has been recorded yet — `design/economy.md` does not exist. Run `game-mechanics` to write one.

## Competitive Differentiation

No differentiation statement has been recorded yet — `design/comp-analysis.md` does not exist. Run `game-comp-analysis` to write one.

## Technical Design

No open or accepted technical decision has been recorded yet — `design/tech/` holds no record with `status: open` or `status: accepted`. Run `game-tech` to write one.

## Supporting Documents Not Rendered

A GDD practice commonly names nine supporting-document types. This file renders the core GDD — the ninth — as a document of its own, and folds one more into it. The remaining seven are named here, with the reason each is absent, so a reader can tell a deliberate omission from a forgotten one.

- **Technical Design Document** — not absent, and not a separate document: at solo and small-team scale technical design folds into the GDD, so it renders above as `## Technical Design`, from the technical decision records `game-tech` writes, rather than as a standalone `design/tdd.md`.
- **Concept Document** — out of scope for this skillset, not merely undone: the concept statement `game-pillars` writes already serves this role, and it renders above as `## Concept`.
- **Marketing & Business Plan** — out of scope for this skillset: a business concern outside this skillset's design-quality scope.
- **Art Bible** — absent for a grounding reason: the schema this skillset builds — pillars, mechanic entries, the economy graph, technical decision records — carries no visual data to render one from.
- **Story/Narrative Bible** — absent for a grounding reason: the same schema carries no narrative data to render one from.
- **Level Design Document** — absent for a grounding reason: the same schema carries no level or spatial data to render one from.
- **Sound Design Document** — absent for a grounding reason: the same schema carries no audio data to render one from.
- **Test Plan** — absent for a grounding reason: the same schema carries no QA data to render one from.

Each of the five grounding-reason documents above is a documented future extension, not a silent omission — rendering one without the data it needs would mean inventing content rather than deriving it.
