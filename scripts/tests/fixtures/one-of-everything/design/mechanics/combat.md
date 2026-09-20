---
name: combat
title: Combat
parent: none
children: [melee, ranged]
part_of: none
parts: []
updated: 2026-09-10T12:00Z
---

## Description

Real-time combat resolved per swing. A hit lands when `atk > def`, and a
critical multiplies damage by 1.5 & applies the weapon's "on-crit" rider. The
weapons it is fought with are paid for out of [[node:ingot-pool]], and the
skills it advances are [[family:skill-xp]].

## Strong example

A player who forged a high-`atk` blade cuts through a low-`def` pack in two
swings.

## Weak example

A player brings a blade whose `atk` is below every enemy's `def` and cannot
damage anything at all, with no in-run way to recover.

## Open Questions

Whether a swing may be cancelled mid-animation is undecided.
