# Contributing to Skywright

Thanks for helping. Skywright is small and opinionated, so please read this
before opening a pull request.

## Open an issue first

Use [GitHub Issues](https://github.com/Dawning-Light/Skywright/issues) for
bugs, ideas, and gaps you've noticed. If a change goes beyond a typo or an
obvious bug fix (a new skill, a new record field, or a change to how a skill
behaves), open an issue before you write it. Changes like that usually touch
several coupled skills, so it's cheaper to agree on the shape before the
work starts.

A good bug report names the skill, the agent and version you ran it under,
what you asked for, and what the skill did instead. If a script failed, also
include the smallest `design/` input that reproduces the failure.

## The repo holds skills only

This repo holds the skills under `skills/`, the plugin manifests, the
README, this file, `AGENTS.md` and its `CLAUDE.md` import, and the license
files. That's everything.

**Never commit a spec, plan, design document, research write-up, backlog, or
notes file**, whether under `docs/`, at the root, or anywhere else. That
holds even when your own workflow (a brainstorming or planning skill, say)
would normally write one into the repo. Keep that material outside the repo,
and commit only the resulting change to `skills/`. If something needs
tracking, open an issue for it.

## Layout

- `skills/<name>/SKILL.md`: one skill per directory, with its own
  `scripts/`, `references/`, and `templates/` where it needs them. A plugin
  install deploys each skill's whole directory tree, so a skill must not
  reach outside its own directory at runtime. The exceptions are below.
- `.claude-plugin/plugin.json`: the Claude Code manifest.
- `.codex-plugin/plugin.json`: the Codex manifest.
- `.claude-plugin/marketplace.json`: the marketplace for both. Codex reads
  it from the same path, so there's only one marketplace file.
- `AGENTS.md`: instructions for coding agents working in this repo.
  `CLAUDE.md` only imports it, because Claude Code doesn't read `AGENTS.md`
  by itself.

`game-mechanics` and `game-gdd` are coupled on purpose. `game-mechanics`'s
`economy-tool` imports `economy_frontmatter` from `game-gdd/scripts/` by
relative path, and its tests read `game-gdd`'s fixtures the same way.
`game-critique` is coupled to `game-gdd` the same way: its
`build_payload.py` imports `economy_frontmatter` and `render_gdd` from
`game-gdd/scripts/`, so it reads records through the one frontmatter parser.
All three must stay siblings under one `skills/` root. Don't add another
cross-skill import without discussing it in an issue first.

## Writing a skill

- **The description is a trigger.** A `SKILL.md`'s `description:` exists
  only to tell an agent *when* to load the skill. Start it with "Use when",
  name the situations that should pull the skill in, and add a
  "Not for X (see `y`)" clause only where a neighbouring skill is easy to
  confuse with this one. Leave out what the skill does, its steps, and what
  it writes, because all of that belongs in the body. An agent that reads a
  workflow summary in the description tends to follow the summary and skip
  the skill. Keep it to one or two sentences, well under 500 characters.
- **Work in any game project.** Don't name a specific consuming project, or
  assume its engine, language, or directory layout beyond `design/`.
- **Write output into the consuming project.** Every record a skill writes
  goes under that project's `design/` directory, never into this repo.
- **Define each record shape once.** The skill that writes a record defines
  its shape. Other skills name that skill instead of restating its fields.
  `game-authoring` holds the rules every design-writing skill shares.
- **State facts directly.** A skill can't point to a spec, an issue, or
  another repo for its reasoning, because the reader won't have them. If a
  rule needs a reason, write the reason into the skill.
- **Keep the skill count in sync.** Adding or removing a skill changes the
  count and list in `README.md`, in the `description` of both `plugin.json`
  files, in `marketplace.json`, and in `AGENTS.md`. Adding or removing a
  game-design skill also changes the "one of seven independent skills"
  sentence that several `SKILL.md` files open with. Before you open the PR,
  `grep -rn` for the old count to catch any you missed.

## Scripts and tests

Scripts use **Python 3 with the standard library only**, or bash and awk.
Don't add a dependency, a package manifest, or a network call. A script that
reads or writes a design record goes through `game-gdd/scripts/economy_frontmatter.py`,
so the repo has exactly one frontmatter parser.

Every script ships with tests beside it in `scripts/tests/`. Before you open
a PR, run all six suites from the repo root:

```bash
skills/game-gdd/scripts/tests/run_tests.sh
python3 -m unittest skills/game-gdd/scripts/tests/test_economy_frontmatter.py
python3 -m unittest skills/game-gdd/scripts/tests/test_find_references.py
python3 -m unittest skills/game-mechanics/scripts/tests/test_economy_tool.py
bash skills/game-mechanics/scripts/tests/test_curve_fit.sh
python3 -m unittest skills/game-critique/scripts/tests/test_build_payload.py
```

If you add a suite, add it to that list here and in `AGENTS.md`.

If you change a skill's prose, also check the change against a real agent.
Install your branch locally in both agents (see below), run
`claude plugin validate`, and try the situations the change is supposed to
handle.

To install a local checkout:

```bash
# Claude Code
claude plugin marketplace add /path/to/Skywright
claude plugin install skywright@skywright

# Codex
codex plugin marketplace add /path/to/Skywright
codex plugin add skywright@skywright
```

## Commits and pull requests

- **Branch from `main`** and open the PR against `main`. PRs are merged
  with a merge commit, so keep each commit on the branch meaningful.
- **Use [Conventional Commits](https://www.conventionalcommits.org/)** with
  the skill name as the scope:
  `feat(game-tech): …`, `fix(game-sync): …`, `docs(game-critique): …`,
  `test(game-mechanics): …`. For repo-wide changes, drop the scope:
  `chore: …`, `docs: …`. Write the subject in the imperative mood and in
  lower case, with no trailing period.
- **Keep one concern per commit.** If a change spans several skills, one
  commit per skill is fine, as long as each commit leaves the tests passing.
- **Write the PR description in two parts.** A *Summary* says what changed
  and why, and flags anything that breaks an existing `design/` corpus. A
  *Test plan* is a checklist of the suites and manual checks you ran, with
  their results.
- **Don't bump the version.** Releases do that.

## Versioning and releases

Skywright follows [Semantic Versioning](https://semver.org/). The version
lives in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`,
and the two must always match.

A change that makes an existing `design/` corpus fail to render, or changes
a record shape, is breaking. Before 1.0, a breaking change bumps the minor
version and anything else bumps the patch. The release commit is a
`chore: …` commit that bumps both manifests, and its PR description tells
users how to migrate.

## AI-assisted contributions

These are welcome, since this is a skillset for coding agents. You're still
responsible for everything you submit: read the diff, run the tests, and
make sure the change follows the rules above, especially the rule against
committing design documents, which agent workflows break most often.

## License

Skywright is licensed under [AGPL-3.0](LICENSE), with an
[output exception](LICENSE-EXCEPTION.md) that leaves the files a skill
creates in or copies into a user's project free of the AGPL. By
contributing, you agree that your contribution is licensed under the same
terms, exception included.

If your change makes a skill write or copy something new into a user's
project, that material falls under the exception. Don't contribute
anything to a `templates/` directory that you can't license that way, such
as third-party code under a copyleft license.
