# Game Design Document

## Concept

No concept statement has been recorded yet — `design/concept.md` does not exist. Run `game-pillars` to write one.

## Design Pillars

No approved design pillar has been recorded yet — `design/pillars/` holds no record with `status: approved`. Run `game-pillars` to write one.

## Mechanics

No mechanic entry has been recorded yet — `design/mechanics/` holds no records. Run `game-mechanics` to write one.

## Economy

No economy graph has been recorded yet — `design/economy.md` does not exist. Run `game-mechanics` to write one.

## Competitive Differentiation

No differentiation statement has been recorded yet — `design/comp-analysis.md` does not exist. Run `game-comp-analysis` to write one.

## Technical Design

### Wire Protocol

*Source: `design/tech/wire-protocol.md` · Updated: 2026-09-27T10:00Z · Implementation: built*

Client and server exchange length-prefixed binary frames.

- Status: accepted
- Category: networking-topology
- Scope: contained
- Drivers: none

#### Context

An implementation spec written where the decision belongs, to prove the
render warns about an over-budget `## Decision` without failing.

#### Decision

Frames are length-prefixed binary. Every field of every frame is listed
below, which is the detail the budget exists to push back into the code.

- `field_01`: `u32`
- `field_02`: `u32`
- `field_03`: `u32`
- `field_04`: `u32`
- `field_05`: `u32`
- `field_06`: `u32`
- `field_07`: `u32`
- `field_08`: `u32`
- `field_09`: `u32`
- `field_10`: `u32`
- `field_11`: `u32`
- `field_12`: `u32`
- `field_13`: `u32`
- `field_14`: `u32`
- `field_15`: `u32`
- `field_16`: `u32`
- `field_17`: `u32`
- `field_18`: `u32`
- `field_19`: `u32`
- `field_20`: `u32`
- `field_21`: `u32`
- `field_22`: `u32`
- `field_23`: `u32`
- `field_24`: `u32`
- `field_25`: `u32`
- `field_26`: `u32`
- `field_27`: `u32`
- `field_28`: `u32`
- `field_29`: `u32`
- `field_30`: `u32`
- `field_31`: `u32`
- `field_32`: `u32`
- `field_33`: `u32`
- `field_34`: `u32`
- `field_35`: `u32`
- `field_36`: `u32`
- `field_37`: `u32`
- `field_38`: `u32`
- `field_39`: `u32`
- `field_40`: `u32`

#### Consequences

Commits to a versioned binary format. Forecloses reading a frame by eye.

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
