---
name: combat
title: Combat
parent: none
children: [melee, ranged]
---

## Description

Real-time combat resolved per swing. A hit lands when `atk > def`, and a
critical multiplies damage by 1.5 & applies the weapon's "on-crit" rider.

## Strong example

A player who forged a high-`atk` blade cuts through a low-`def` pack in two
swings.

## Weak example

A player brings a blade whose `atk` is below every enemy's `def` and cannot
damage anything at all, with no in-run way to recover.
