---
name: wire-protocol
title: Client and server exchange length-prefixed binary frames.
status: accepted
category: networking-topology
scope: contained
implementation: built
drivers: []
source: game-tech
updated: 2026-09-27T10:00Z
---

## Context

An implementation spec written where the decision belongs, to prove the
render warns about an over-budget `## Decision` without failing.

## Decision

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

## Consequences

Commits to a versioned binary format. Forecloses reading a frame by eye.
