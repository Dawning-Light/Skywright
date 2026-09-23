---
nodes:
  - id: ore-vein
    type: source
  - id: ingot-pool
    type: pool
connections:
  - { id: mine, from: ore-vein, to: ingot-pool, kind: resource }
  - { from: ingot-pool, to: ore-vein, kind: state, subtype: trigger }
---

## ore-vein

Where ore comes from.
