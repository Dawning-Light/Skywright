# Skywright

A game-design skillset for coding agents, distributed as a Claude Code and
Codex plugin. Eight skills under `skills/`, and the manifests that package
them. Nothing else.

## This repo is skills-only

No spec, plan, design document, research write-up, backlog, or any other
design-history file is ever committed here — not under `docs/`, not at the
root, not anywhere. This holds even when a skill workflow would normally
write one: if brainstorming or planning work is needed for a change to these
skills, it is written outside this repo, and only the resulting change to
`skills/` is committed.

Ideas and defects that need tracking go to this repo's GitHub Issues, not to
a file.

## Layout

- `skills/<name>/SKILL.md` — one skill each, with its own `scripts/`,
  `references/`, and `templates/` subdirectories where it has them. A plugin
  install deploys each skill's whole directory tree.
- `.claude-plugin/` — `plugin.json` and a single-plugin `marketplace.json`.
- `.codex-plugin/plugin.json` — the Codex manifest.

`skills/game-mechanics` and `skills/game-gdd` are coupled: `game-mechanics`'s
`economy-tool` imports `economy_frontmatter` from `game-gdd/scripts/` by
relative path, and its tests read `game-gdd`'s fixtures the same way. The two
must stay siblings under one `skills/` root.

## Tests

```bash
skills/game-gdd/scripts/tests/run_tests.sh
python3 -m unittest skills/game-gdd/scripts/tests/test_economy_frontmatter.py
python3 -m unittest skills/game-gdd/scripts/tests/test_find_references.py
python3 -m unittest skills/game-mechanics/scripts/tests/test_economy_tool.py
```

Python 3 standard library only; no dependencies to install.
