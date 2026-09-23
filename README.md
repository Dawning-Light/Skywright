# Skywright

Eight skills that elicit a game's design as structured data and render it as
a GDD — pillars, competitor differentiation, mechanics and economy,
technical decisions, and adversarial critique — plus the bundled research
skill two of them delegate to.

Everything these skills produce lives in **your** game project, under its own
`design/` directory. This repo holds only the skills.

## The skills

| Skill | Use it when |
| --- | --- |
| `game-pillars` | The project has no concept statement or design pillars yet, or you want to revise them. |
| `game-comp-analysis` | You need to know how your concept differs from competitors in its genre. |
| `game-mechanics` | Mechanics, systems, or the economy need writing down as structured design data. |
| `game-tech` | A technical decision needs making and recording — networking, simulation, persistence, engine. |
| `game-gdd` | The design data needs upkeep — rendering the GDD, checking references, other maintenance. |
| `game-critique` | The design data or rendered GDD needs adversarial review rather than more authoring. |
| `game-authoring` | Never invoked directly — the shared authoring rule set the other six load before they write. |
| `research` | Never invoked directly — the web-research capability `game-comp-analysis` and `game-critique` delegate to for competitor and best-practice research. |

## Install

**Claude Code:**

```
/plugin marketplace add Dawning-Light/Skywright
/plugin install skywright
```

**Codex:** the repo ships a `.codex-plugin/plugin.json` pointing at `./skills/`.

## Requirements

- Python 3 — `game-gdd`'s renderer and `game-mechanics`'s economy tool are
  standard-library only, with no packages to install.
- `research` ships in this plugin — `game-comp-analysis` and `game-critique`
  delegate their web research to it directly; nothing extra to install.

## License

MIT
