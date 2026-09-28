# Skywright

A game-design skillset for coding agents. Nine skills that elicit a game's
design as structured data and render it as a GDD — pillars, competitor
differentiation, mechanics and economy, technical decisions, adversarial
critique, and keeping the records in step with the code — plus the bundled
research skill two of them delegate to.

Distributed as a plugin for Claude Code and Codex.

## How it works

You don't call these skills by name. Describe what you're doing ("we need
design pillars for this game", "write down how the crafting economy works",
"critique the combat mechanics") and your agent loads the matching skill.

Each skill writes small, structured records into **your** game project, under
its own `design/` directory:

```
design/
  concept.md            concept statement            (game-pillars)
  pillars/<slug>.md     one design pillar each       (game-pillars)
  comp-analysis.md      differentiation statement    (game-comp-analysis)
  mechanics/<slug>.md   one mechanic entry each      (game-mechanics)
  economy.md            the economy graph            (game-mechanics)
  tech/<slug>.md        one technical decision each  (game-tech)
  critique/…            critic findings              (game-critique)
  gdd.md, gdd.html      the rendered GDD             (game-gdd)
```

The GDD is a view onto those records and gets regenerated on every render.
Nobody hand-edits it. The records are the source of truth, so they diff,
review, and version like code.

The suggested order is `game-pillars` → `game-comp-analysis` →
`game-mechanics` → `game-tech` → `game-gdd` → `game-critique`. It's only a
recommendation: each skill runs on whatever the project already has, even
nothing. `game-sync` sits outside the order and runs whenever a code change
touches something a design record states.

## The skills

| Skill | Use it when |
| --- | --- |
| `game-pillars` | The project has no concept statement or design pillars yet, or you want to revise them. |
| `game-comp-analysis` | You need to know how your concept differs from competitors in its genre. |
| `game-mechanics` | Mechanics, systems, or the economy need writing down as structured design data. |
| `game-tech` | A technical decision needs making and recording — networking, simulation, persistence, engine. |
| `game-gdd` | The design data needs upkeep — rendering the GDD, checking references, other maintenance. |
| `game-critique` | The design data or rendered GDD needs adversarial review rather than more authoring. |
| `game-sync` | A code change altered behaviour a design record states — fixes and tuning included — or the records need checking against the code. |
| `game-authoring` | Never invoked directly — the shared authoring rule set the design-writing skills load before they write. |
| `research` | Never invoked directly — the web-research capability `game-comp-analysis` and `game-critique` delegate to for competitor and best-practice research. |

## Install

**Claude Code:**

```
/plugin marketplace add Dawning-Light/Skywright
/plugin install skywright
```

**Codex:**

```bash
codex plugin marketplace add Dawning-Light/Skywright
codex plugin add skywright@skywright
```

The skills load in your next Codex session. To update later, run
`codex plugin marketplace upgrade` in Codex, or `/plugin marketplace update`
in Claude Code.

## Requirements

- Python 3. `game-gdd`'s renderer and `game-mechanics`'s economy tool use the
  standard library only, so there are no packages to install.
- bash and awk, for `game-mechanics`'s curve fitting.
- `research` ships in this plugin. `game-comp-analysis` and `game-critique`
  delegate their web research to it, so there's nothing extra to install.

## Upgrading

Until 1.0, a minor version bump (0.1 → 0.2) can change a record shape. If
your existing `design/` fails to render after an upgrade, ask your agent to
audit the design records against the code. That runs `game-sync`'s audit
mode, which backfills what the new version requires.

## Contributing

Bug reports and ideas go to [GitHub Issues](https://github.com/Dawning-Light/Skywright/issues).
Before opening a pull request, read [CONTRIBUTING.md](CONTRIBUTING.md). This
repo has a few rules that are unusual, the main one being that it holds
skills only.

## License

[AGPL-3.0](LICENSE)
