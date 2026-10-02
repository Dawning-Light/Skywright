# Linked Fixture — Game Design Document

## Concept

*Source: `design/concept.md` · Updated: 2026-10-01T09:00Z*

A small fixture game whose actions link to one another.

## Design Pillars

### Core

*Source: `design/pillars/core.md` · Updated: 2026-10-01T09:00Z*

Every action costs something.

Keep a feature when it has a stated cost; cut it when it is free.

#### Worked keep

A charged attack that drains mana. **Kept** — it costs mana.

#### Worked cut

A free heal. **Cut** — it costs nothing.

*1 candidate pillar proposed by `game-comp-analysis` awaits review — approve or discard it with `game-pillars`.*

## Mechanics

### Base Action

*Source: `design/mechanics/base.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: `hub`
- Part of: none
- Parts: none

#### Description

The action every other action specializes.

#### Consequences

Spending a turn on it rules out moving.

#### Strong example

A worked case of Base Action doing what it is for.

#### Weak example

A worked case of Base Action failing.

### Hub Action

*Source: `design/mechanics/hub.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: `base`
- Children: none
- Part of: none
- Parts: none

#### Description

A specialization of [[mechanic:base]] that also reads [[mechanic:hub]], [[mechanic:link-1]], [[mechanic:link-2]], [[mechanic:link-3]], [[mechanic:link-4]], [[mechanic:link-5]], [[mechanic:link-6]], [[mechanic:link-7]], [[mechanic:link-8]], and [[mechanic:link-9]]. It draws from [[node:mana]] and feeds [[family:skills]]; [[mechanic:link-1]] is cited twice.

#### Consequences

Each use drains [[node:mana]].

#### Strong example

A worked case of Hub Action doing what it is for.

#### Weak example

A worked case of Hub Action failing.

### Link 1

*Source: `design/mechanics/link-1.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 1 takes two seconds to trigger.

#### Consequences

Link 1 forecloses running while it charges.

#### Strong example

A worked case of Link 1 doing what it is for.

#### Weak example

A worked case of Link 1 failing.

### Link 2

*Source: `design/mechanics/link-2.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 2 takes two seconds to trigger.

#### Consequences

Link 2 forecloses running while it charges.

#### Strong example

A worked case of Link 2 doing what it is for.

#### Weak example

A worked case of Link 2 failing.

### Link 3

*Source: `design/mechanics/link-3.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 3 takes two seconds to trigger.

#### Consequences

Link 3 forecloses running while it charges.

#### Strong example

A worked case of Link 3 doing what it is for.

#### Weak example

A worked case of Link 3 failing.

### Link 4

*Source: `design/mechanics/link-4.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 4 takes two seconds to trigger.

#### Consequences

Link 4 forecloses running while it charges.

#### Strong example

A worked case of Link 4 doing what it is for.

#### Weak example

A worked case of Link 4 failing.

### Link 5

*Source: `design/mechanics/link-5.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 5 takes two seconds to trigger.

#### Consequences

Link 5 forecloses running while it charges.

#### Strong example

A worked case of Link 5 doing what it is for.

#### Weak example

A worked case of Link 5 failing.

### Link 6

*Source: `design/mechanics/link-6.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 6 takes two seconds to trigger.

#### Consequences

Link 6 forecloses running while it charges.

#### Strong example

A worked case of Link 6 doing what it is for.

#### Weak example

A worked case of Link 6 failing.

### Link 7

*Source: `design/mechanics/link-7.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 7 takes two seconds to trigger.

#### Consequences

Link 7 forecloses running while it charges.

#### Strong example

A worked case of Link 7 doing what it is for.

#### Weak example

A worked case of Link 7 failing.

### Link 8

*Source: `design/mechanics/link-8.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 8 takes two seconds to trigger.

#### Consequences

Link 8 forecloses running while it charges.

#### Strong example

A worked case of Link 8 doing what it is for.

#### Weak example

A worked case of Link 8 failing.

### Link 9

*Source: `design/mechanics/link-9.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Link 9 takes two seconds to trigger.

#### Consequences

Link 9 forecloses running while it charges.

#### Strong example

A worked case of Link 9 doing what it is for.

#### Weak example

A worked case of Link 9 failing.

### Lonely Action

*Source: `design/mechanics/lonely.md` · Updated: 2026-10-01T09:00Z · Implementation: designed*

- Parent: none
- Children: none
- Part of: none
- Parts: none

#### Description

Stands alone: no relation and no link.

#### Strong example

A worked case of Lonely Action doing what it is for.

#### Weak example

A worked case of Lonely Action failing.

## Economy

*Source: `design/economy.md` · Updated: 2026-10-01T09:00Z*

### Nodes

#### Mana

*Source: `design/economy.md`, node `mana`*

- Type: pool
- Value progression: none recorded

The pool every action is paid from.

#### Well

*Source: `design/economy.md`, node `well`*

- Type: source
- Value progression: none recorded

#### Fire Xp

*Source: `design/economy.md`, node `fire-xp`*

- Type: pool
- Value progression: none recorded

#### Ice Xp

*Source: `design/economy.md`, node `ice-xp`*

- Type: pool
- Value progression: none recorded

### Families

#### Skills

*Source: `design/economy.md`, family `@skills`*

- Type: pool
- Members: `fire-xp`, `ice-xp`

Declarations over this family:

- **train** — `mana` → `@skills`, kind: resource; expands to 2 connections, all live simultaneously (expanded ids follow `game-mechanics`' derived-id rule)

### Connections

#### Refill

*Source: `design/economy.md`, connection `refill`*

- From: `well`
- To: `mana`
- Kind: resource
- Rate: 2

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
