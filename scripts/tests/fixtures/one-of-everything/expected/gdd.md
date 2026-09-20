# Forge & Foray — Game Design Document

## Concept

*Source: `design/concept.md` · Updated: 2026-09-10T09:15Z*

Forge & Foray is a crafting-led action RPG in which the player mines ore, smelts
it into ingots, and forges the weapons they then carry into short, hand-authored
dungeon runs. Every run ends back at the forge, where the loot becomes the next
weapon. What the genre's leaders do instead is recorded in [[comp-analysis]].

### Open Questions

Whether a run may end anywhere other than the forge is undecided.

## Design Pillars

### Always Earned

*Source: `design/pillars/always-earned.md` · Updated: 2026-09-09T18:20Z*

Every capability is earned through investment, never granted by a slot.

The pillar [[concept]] leans on hardest: the forge is open to anyone who
invests in it.

#### The test

A capability reachable only by picking a class at creation fails this pillar.
One reachable by anyone who invests in it passes.

#### Worked keep

Heavy-armour proficiency trained by wearing heavy armour. **Kept.**

#### Worked cut

A "Smith" class that alone may use the forge. **Cut.**

### Zero Grind

*Source: `design/pillars/zero-grind.md` · Updated: 2026-09-10T08:05Z*

Progress always comes from a decision the player made, never from time they waited.

Sits beside [[pillar:always-earned]], applies to [[mechanic:combat]], and is
what [[comp-analysis]] measures the competitors against. A literal `[[slug]]`
inside a code span is prose about the syntax, not a reference.

#### The test

Given a proposed feature, ask whether its reward is gated by a choice the player
made or by elapsed time. Gated by time alone, it is cut.

#### Worked keep

A forge recipe that unlocks once the player has *chosen* to smelt three
different alloys. **Kept** — the gate is a decision.

#### Worked cut

A daily login chest. **Cut** — the gate is the calendar.

#### Open Questions

Whether a cosmetic reward may be time-gated without failing this pillar is
undecided.

*1 candidate pillar proposed by `game-comp-analysis` awaits review — approve or discard it with `game-pillars`.*

## Mechanics

### Combat

*Source: `design/mechanics/combat.md` · Updated: 2026-09-10T12:00Z*

- Parent: none
- Children: `melee`, `ranged`
- Part of: none
- Parts: none

#### Description

Real-time combat resolved per swing. A hit lands when `atk > def`, and a
critical multiplies damage by 1.5 & applies the weapon's "on-crit" rider. The
weapons it is fought with are paid for out of [[node:ingot-pool]], and the
skills it advances are [[family:skill-xp]].

#### Strong example

A player who forged a high-`atk` blade cuts through a low-`def` pack in two
swings.

#### Weak example

A player brings a blade whose `atk` is below every enemy's `def` and cannot
damage anything at all, with no in-run way to recover.

#### Open Questions

Whether a swing may be cancelled mid-animation is undecided.

### Melee

*Source: `design/mechanics/melee.md` · Updated: 2026-09-10T12:04Z*

- Parent: `combat`
- Children: none
- Part of: none
- Parts: none

#### Description

Close-range swings that trade reach for damage. Serves [[pillar:zero-grind]]:
every swing is a decision, never a wait.

A fenced block is never scanned for references, so the broken one below is
inert text rather than a render failure:

```
[[no-such-type:no-such-id]]
```

#### Strong example

A player closes distance during an enemy's wind-up and lands a free swing.

#### Weak example

A player swings into a shielded enemy forever because nothing signals that
melee is the wrong tool here.

### Ranged

*Source: `design/mechanics/ranged.md` · Updated: 2026-09-10T12:07Z*

- Parent: `combat`
- Children: none
- Part of: none
- Parts: none

#### Description

Distance attacks that trade damage for safety. Whether two players see the same
shot land is what [[tech:netcode]] decides.

#### Strong example

A player kites a slow enemy around a pillar and wins without taking a hit.

#### Weak example

Every encounter is won by backing away and firing, which makes melee pointless.

### Inventory

*Source: `design/mechanics/inventory.md` · Updated: 2026-09-10T12:10Z*

- Parent: none
- Children: none
- Part of: none
- Parts: `stack-limits`

#### Description

Where carried items live between runs.

#### Strong example

A player drops a spare blade to make room for ore and finishes the run.

#### Weak example

Capacity is large enough that nothing is ever dropped, so the choice the
mechanic exists to pose never comes up.

### Stack Limits

*Source: `design/mechanics/stack-limits.md` · Updated: 2026-09-10T12:12Z*

- Parent: none
- Children: none
- Part of: `inventory`
- Parts: none

#### Description

How many of one item share a slot. A part of the inventory, not a kind of it.

#### Strong example

Ore stacks to 99, so a long dig costs one slot instead of ninety-nine.

#### Weak example

Every item stacks to 1, which makes the limit a second, redundant capacity
cap rather than a distinct decision.

## Economy

*Source: `design/economy.md` · Updated: 2026-09-10T16:44Z*

### Nodes

#### Ore Vein

*Source: `design/economy.md`, node `ore-vein`*

- Type: source
- Value progression: none recorded

#### Ingot Pool

*Source: `design/economy.md`, node `ingot-pool`*

- Type: pool
- Value progression: model power; coefficients 1.8, 1.42; domain 1-20; fit 0.987

The one pool every forged weapon is paid for out of. Its cost-by-tier curve is
fitted rather than chosen — see `scripts/curve-fit.sh`. What the player spends
it on is [[mechanic:combat]].

###### Open question

Whether ingots stack per alloy or share one pool is undecided.

#### Forge

*Source: `design/economy.md`, node `forge`*

- Type: converter
- Value progression: none recorded

#### Gold

*Source: `design/economy.md`, node `gold`*

- Type: pool
- Value progression: none recorded

#### Mining Xp

*Source: `design/economy.md`, node `mining-xp`*

- Type: pool
- Value progression: none recorded

#### Smith Xp

*Source: `design/economy.md`, node `smith-xp`*

- Type: pool
- Value progression: none recorded

### Families

#### Skill Xp

*Source: `design/economy.md`, family `@skill-xp`*

- Type: pool
- Members: `mining-xp`, `smith-xp`

Two named skills, `mining-xp` and `smith-xp`, each its own node with its own
progression — never a shared "crafting" track. Only the member matching the
action actually applies, which is what [[connection:skill-rate]] records.

Declarations over this family:

- **xp-gain** — `ore-vein` → `@skill-xp`, kind: resource, resource: xp; expands to 2 connections, all live simultaneously (expanded ids follow `game-mechanics`' derived-id rule)
- **skill-rate** — `@skill-xp` → `#mine`, kind: state, subtype: label-modifier; expands to 2 connections, one-of-family: exactly one live at a time (expanded ids follow `game-mechanics`' derived-id rule)

### Connections

#### Mine

*Source: `design/economy.md`, connection `mine`*

- From: `ore-vein`
- To: `ingot-pool`
- Kind: resource
- Rate: 3

#### Smelt

*Source: `design/economy.md`, connection `smelt`*

- From: `ingot-pool`
- To: `forge`
- Kind: resource
- Rate: none recorded
- Resource: ore

#### Sale

*Source: `design/economy.md`, connection `sale`*

- From: `forge`
- To: `gold`
- Kind: resource
- Rate: 5
- Resource: gold

#### Forge Gate

*Source: `design/economy.md`, connection `forge-gate`*

- From: `gold`
- To: `forge`
- Kind: state
- Subtype: none recorded
- Rate: none recorded

## Competitive Differentiation

*Source: `design/comp-analysis.md` · Updated: 2026-09-10T14:02Z*

Forge & Foray differentiates on loop length: its competitors all separate
crafting from combat across sessions, where [[concept]] closes both inside one
fifteen-minute run. Where it currently looks like more of the same is its
rarity-tier itemization, which every competitor below also ships.

| Competitor | Loop length | Crafting is | Source |
| --- | --- | --- | --- |
| Anvilfall | ~2 hours | a separate mode | `docs/research/anvilfall-2026-09-01.md` |
| Deepdelve | ~45 minutes | a vendor menu | `docs/research/deepdelve-2026-09-01.md` |

What the concept does that they don't:

- Closes crafting and combat inside a single run.
- Makes the forge the run's *destination*, not its lobby.
- Prices every weapon out of one visible pool.

### Open Questions

Whether the co-op runs [[tech:netcode]] is deciding are a differentiator at all
is unsettled — one competitor above may ship them first.

## Technical Design

### Netcode

*Source: `design/tech/netcode.md` · Updated: 2026-09-11T11:00Z*

How do two players share one dungeon run?

**Open — not yet decided.**

- Status: open
- Category: networking-topology
- Scope: cross-cutting
- Drivers: `design/concept.md`, `design/mechanics/combat.md`, `economy:#mine`

#### Context

The concept commits to short co-op runs, and combat resolves per swing, so
a hit that lands on one client and not the other is visible immediately.

#### Options considered

- Lockstep: cheap bandwidth, brittle under packet loss.
- Dedicated authoritative server: predictable, costs hosting.
- Host-migrating listen server: no hosting bill, ugly migrations.

### Save Format

*Source: `design/tech/save-format.md` · Updated: 2026-09-04T07:45Z*

Saves are a single append-only JSON document per guild.

- Status: accepted
- Category: persistence
- Scope: contained
- Drivers: none

#### Context

There is no team and no budget for a database, and the only constraint is that
a save must survive a crash mid-run.

#### Decision

One append-only JSON document per guild, fsynced at each run boundary.

#### Consequences

Commits to a bounded save size. Forecloses partial loads, so a very large
roster will pay the whole parse cost at launch.

#### Assumptions to verify

- A 10 MB save parses in under 100 ms on the target hardware.

*`old-netcode` superseded by `netcode`.*

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
