---
updated: 2026-09-14T12:00Z
nodes:
  - id: resource-node
    type: source
  - id: monster
    type: source
  - id: boss
    type: source
  - id: character-inventory
    type: pool
  - id: character-bank
    type: pool
  - id: gear-pool
    type: pool
  - id: tool-power
    type: pool
  - id: fame
    type: pool
  - id: renown
    type: pool
  - id: mining-xp
    type: pool
  - id: fishing-xp
    type: pool
  - id: lumberjack-xp
    type: pool
  - id: cooking-xp
    type: pool
  - id: sword-weapon-proficiency-xp
    type: pool
  - id: shield-weapon-proficiency-xp
    type: pool
  - id: staff-weapon-proficiency-xp
    type: pool
  - id: wand-weapon-proficiency-xp
    type: pool
  - id: bow-weapon-proficiency-xp
    type: pool
  - id: crossbow-weapon-proficiency-xp
    type: pool
  - id: dagger-weapon-proficiency-xp
    type: pool
  - id: fighter-class-proficiency-xp
    type: pool
  - id: mage-class-proficiency-xp
    type: pool
  - id: rogue-class-proficiency-xp
    type: pool
  - id: blacksmithing-xp
    type: pool
  - id: tailoring-xp
    type: pool
  - id: leatherworking-xp
    type: pool
  - id: woodworking-xp
    type: pool
  - id: refining-station
    type: converter
  - id: crafting-station
    type: converter
  - id: self-repair
    type: converter
  - id: guild-tier-gate
    type: gate
connections:
  - { id: gather, from: resource-node, to: character-inventory, kind: resource }
  - { id: deposit, from: character-inventory, to: character-bank, kind: resource }
  - { id: refine-input, from: character-bank, to: refining-station, kind: resource, resource: raw-material }
  - { id: refine-output, from: refining-station, to: character-bank, kind: resource, resource: refined-material }
  - { id: craft-input, from: character-bank, to: crafting-station, kind: resource, resource: raw-material }
  - { id: craft-gear, from: crafting-station, to: gear-pool, kind: resource, resource: gear }
  - { id: tool-gather-rate, from: tool-power, to: "#gather", kind: state, subtype: label-modifier }
  - { id: self-input, from: character-inventory, to: self-repair, kind: resource, resource: material }
  - { id: self-output, from: self-repair, to: gear-pool, kind: resource, resource: gear }
  - { id: monster-loot, from: monster, to: character-inventory, kind: resource }
  - { id: boss-loot, from: boss, to: character-inventory, kind: resource }
  - { id: boss-fame, from: boss, to: fame, kind: resource }
  - { id: boss-renown, from: boss, to: renown, kind: resource }
  - { id: fame-tier, from: fame, to: guild-tier-gate, kind: state, subtype: activator }
  - { id: gather-in-mining, from: resource-node, to: mining-xp, kind: resource, resource: xp }
  - { id: gather-rate-mining, from: mining-xp, to: "#gather", kind: state, subtype: label-modifier }
  - { id: mining-fame, from: mining-xp, to: fame, kind: resource }
  - { id: mining-renown, from: mining-xp, to: renown, kind: resource }
  - { id: gather-in-fishing, from: resource-node, to: fishing-xp, kind: resource, resource: xp }
  - { id: gather-rate-fishing, from: fishing-xp, to: "#gather", kind: state, subtype: label-modifier }
  - { id: fishing-fame, from: fishing-xp, to: fame, kind: resource }
  - { id: fishing-renown, from: fishing-xp, to: renown, kind: resource }
  - { id: gather-in-lumberjack, from: resource-node, to: lumberjack-xp, kind: resource, resource: xp }
  - { id: gather-rate-lumberjack, from: lumberjack-xp, to: "#gather", kind: state, subtype: label-modifier }
  - { id: lumberjack-fame, from: lumberjack-xp, to: fame, kind: resource }
  - { id: lumberjack-renown, from: lumberjack-xp, to: renown, kind: resource }
  - { id: refine-cook-xp, from: refining-station, to: cooking-xp, kind: resource, resource: xp }
  - { id: cook-refine-rate, from: cooking-xp, to: "#refine-output", kind: state, subtype: label-modifier }
  - { id: cook-fame, from: cooking-xp, to: fame, kind: resource }
  - { id: cook-renown, from: cooking-xp, to: renown, kind: resource }
  - { id: monster-sword-weapon-xp, from: monster, to: sword-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-sword-weapon-xp, from: boss, to: sword-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: sword-weapon-monster, from: sword-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: sword-weapon-fame, from: sword-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: sword-weapon-renown, from: sword-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-shield-weapon-xp, from: monster, to: shield-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-shield-weapon-xp, from: boss, to: shield-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: shield-weapon-monster, from: shield-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: shield-weapon-fame, from: shield-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: shield-weapon-renown, from: shield-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-staff-weapon-xp, from: monster, to: staff-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-staff-weapon-xp, from: boss, to: staff-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: staff-weapon-monster, from: staff-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: staff-weapon-fame, from: staff-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: staff-weapon-renown, from: staff-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-wand-weapon-xp, from: monster, to: wand-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-wand-weapon-xp, from: boss, to: wand-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: wand-weapon-monster, from: wand-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: wand-weapon-fame, from: wand-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: wand-weapon-renown, from: wand-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-bow-weapon-xp, from: monster, to: bow-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-bow-weapon-xp, from: boss, to: bow-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: bow-weapon-monster, from: bow-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: bow-weapon-fame, from: bow-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: bow-weapon-renown, from: bow-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-crossbow-weapon-xp, from: monster, to: crossbow-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-crossbow-weapon-xp, from: boss, to: crossbow-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: crossbow-weapon-monster, from: crossbow-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: crossbow-weapon-fame, from: crossbow-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: crossbow-weapon-renown, from: crossbow-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-dagger-weapon-xp, from: monster, to: dagger-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-dagger-weapon-xp, from: boss, to: dagger-weapon-proficiency-xp, kind: resource, resource: xp }
  - { id: dagger-weapon-monster, from: dagger-weapon-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: dagger-weapon-fame, from: dagger-weapon-proficiency-xp, to: fame, kind: resource }
  - { id: dagger-weapon-renown, from: dagger-weapon-proficiency-xp, to: renown, kind: resource }
  - { id: monster-fighter-class-xp, from: monster, to: fighter-class-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-fighter-class-xp, from: boss, to: fighter-class-proficiency-xp, kind: resource, resource: xp }
  - { id: fighter-class-monster, from: fighter-class-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: fighter-class-fame, from: fighter-class-proficiency-xp, to: fame, kind: resource }
  - { id: fighter-class-renown, from: fighter-class-proficiency-xp, to: renown, kind: resource }
  - { id: monster-mage-class-xp, from: monster, to: mage-class-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-mage-class-xp, from: boss, to: mage-class-proficiency-xp, kind: resource, resource: xp }
  - { id: mage-class-monster, from: mage-class-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: mage-class-fame, from: mage-class-proficiency-xp, to: fame, kind: resource }
  - { id: mage-class-renown, from: mage-class-proficiency-xp, to: renown, kind: resource }
  - { id: monster-rogue-class-xp, from: monster, to: rogue-class-proficiency-xp, kind: resource, resource: xp }
  - { id: boss-rogue-class-xp, from: boss, to: rogue-class-proficiency-xp, kind: resource, resource: xp }
  - { id: rogue-class-monster, from: rogue-class-proficiency-xp, to: monster, kind: state, subtype: label-modifier }
  - { id: rogue-class-fame, from: rogue-class-proficiency-xp, to: fame, kind: resource }
  - { id: rogue-class-renown, from: rogue-class-proficiency-xp, to: renown, kind: resource }
  - { id: craft-blacksmithing-xp, from: crafting-station, to: blacksmithing-xp, kind: resource, resource: xp }
  - { id: blacksmithing-self-repair, from: blacksmithing-xp, to: self-repair, kind: state, subtype: activator }
  - { id: blacksmithing-fame, from: blacksmithing-xp, to: fame, kind: resource }
  - { id: blacksmithing-renown, from: blacksmithing-xp, to: renown, kind: resource }
  - { id: craft-tailoring-xp, from: crafting-station, to: tailoring-xp, kind: resource, resource: xp }
  - { id: tailoring-self-repair, from: tailoring-xp, to: self-repair, kind: state, subtype: activator }
  - { id: tailoring-fame, from: tailoring-xp, to: fame, kind: resource }
  - { id: tailoring-renown, from: tailoring-xp, to: renown, kind: resource }
  - { id: craft-leatherworking-xp, from: crafting-station, to: leatherworking-xp, kind: resource, resource: xp }
  - { id: leatherworking-self-repair, from: leatherworking-xp, to: self-repair, kind: state, subtype: activator }
  - { id: leatherworking-fame, from: leatherworking-xp, to: fame, kind: resource }
  - { id: leatherworking-renown, from: leatherworking-xp, to: renown, kind: resource }
  - { id: craft-woodworking-xp, from: crafting-station, to: woodworking-xp, kind: resource, resource: xp }
  - { id: woodworking-self-repair, from: woodworking-xp, to: self-repair, kind: state, subtype: activator }
  - { id: woodworking-fame, from: woodworking-xp, to: fame, kind: resource }
  - { id: woodworking-renown, from: woodworking-xp, to: renown, kind: resource }
---

## mining-xp

One of three gathering skills — `mining-xp`, `fishing-xp`, `lumberjack-xp` —
each its own track, never a shared one. `cooking-xp` runs the same
feedback-loop shape and is annotated here alongside them, but it feeds off
`refining-station`, not `resource-node`.

## cooking-xp

Refining's named skill; it state-modifies `#refine-output` the way the three
gathering skills modify `#gather`.
