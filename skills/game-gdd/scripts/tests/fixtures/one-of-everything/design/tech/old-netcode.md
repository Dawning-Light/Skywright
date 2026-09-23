---
name: old-netcode
title: Co-op runs use peer-to-peer lockstep.
status: superseded
superseded_by: netcode
category: networking-topology
scope: cross-cutting
drivers:
  - design/concept.md
source: game-tech
updated: 2026-08-02T15:30Z
---

## Context

Written when co-op was two players on a LAN.

## Decision

Peer-to-peer lockstep, no server.

## Options considered

- Lockstep: chosen.
- Dedicated server: rejected on cost at the time.

## Consequences

Ruled out drop-in joins, which is what reopened the question.
