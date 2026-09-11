---
name: save-format
title: Saves are a single append-only JSON document per guild.
status: accepted
category: persistence
scope: contained
drivers: []
source: game-tech
date: 2026-09-11
---

## Context

There is no team and no budget for a database, and the only constraint is that
a save must survive a crash mid-run.

## Decision

One append-only JSON document per guild, fsynced at each run boundary.

## Consequences

Commits to a bounded save size. Forecloses partial loads, so a very large
roster will pay the whole parse cost at launch.

## Assumptions to verify

- A 10 MB save parses in under 100 ms on the target hardware.
