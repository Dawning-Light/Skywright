---
name: netcode
title: How do two players share one dungeon run?
status: open
category: networking-topology
scope: cross-cutting
drivers:
  - design/concept.md
  - design/mechanics/combat.md
  - economy:#mine
source: game-tech
date: 2026-09-11
---

## Context

The concept commits to short co-op runs, and combat resolves per swing, so
a hit that lands on one client and not the other is visible immediately.

## Options considered

- Lockstep: cheap bandwidth, brittle under packet loss.
- Dedicated authoritative server: predictable, costs hosting.
- Host-migrating listen server: no hosting bill, ugly migrations.
