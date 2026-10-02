---
updated: 2026-10-01T09:00Z
nodes:
  - id: mana
    type: pool
  - id: well
    type: source
  - id: fire-xp
    type: pool
  - id: ice-xp
    type: pool
families:
  - family: skills
    type: pool
    members: [fire-xp, ice-xp]
connections:
  - { id: refill, from: well, to: mana, kind: resource, rate: 2 }
  - { id: train, from: mana, to: "@skills", kind: resource }
---

## mana

The pool every action is paid from.
