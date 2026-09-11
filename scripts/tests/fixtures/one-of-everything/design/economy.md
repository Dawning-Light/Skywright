---
updated: 2026-09-10T16:44Z
nodes:
  - id: ore-vein
    type: source
  - id: ingot-pool
    type: pool
    value_progression:
      model: power
      coefficients: [1.8, 1.42]
      domain: 1-20
      fit: 0.987
  - id: forge
    type: converter
  - id: gold
    type: pool
  - id: mining-xp
    type: pool
  - id: smith-xp
    type: pool
families:
  - family: skill-xp
    type: pool
    members: [mining-xp, smith-xp]
connections:
  - { id: mine, from: ore-vein, to: ingot-pool, kind: resource, rate: 3 }
  - { id: smelt, from: ingot-pool, to: forge, kind: resource, resource: ore }
  - { id: sale, from: forge, to: gold, kind: resource, resource: gold, rate: 5 }
  - { id: forge-gate, from: gold, to: forge, kind: state }
  - { id: xp-gain, from: ore-vein, to: "@skill-xp", kind: resource, resource: xp }
  - { id: skill-rate, from: "@skill-xp", to: "#mine", kind: state, subtype: label-modifier, applies: one-of-family }
---

## ingot-pool

The one pool every forged weapon is paid for out of. Its cost-by-tier curve is
fitted rather than chosen — see `scripts/curve-fit.sh`. What the player spends
it on is [[mechanic:combat]].

### Open question

Whether ingots stack per alloy or share one pool is undecided.

## @skill-xp

Two named skills, `mining-xp` and `smith-xp`, each its own node with its own
progression — never a shared "crafting" track. Only the member matching the
action actually applies, which is what [[connection:skill-rate]] records.
