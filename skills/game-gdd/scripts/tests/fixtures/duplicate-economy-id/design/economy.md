---
nodes:
  - id: ore-vein
    type: source
  - id: ore-vein
    type: pool
connections:
  - { id: mine, from: ore-vein, to: ore-vein, kind: resource }
---
