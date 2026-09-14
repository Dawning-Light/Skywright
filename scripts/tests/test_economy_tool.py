import contextlib
import importlib.machinery
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
TOOL = os.path.join(SCRIPTS_DIR, "economy-tool")
FIXTURES = os.path.join(HERE, "fixtures")
GDD_FIXTURES = os.path.normpath(
    os.path.join(SCRIPTS_DIR, os.pardir, os.pardir, "game-gdd", "scripts", "tests", "fixtures")
)

# `economy-tool` has no `.py` extension, so load it by path.
_loader = importlib.machinery.SourceFileLoader("economy_tool", TOOL)
_spec = importlib.util.spec_from_loader("economy_tool", _loader)
et = importlib.util.module_from_spec(_spec)
_loader.exec_module(et)

NOW = "2026-09-14T12:00Z"
BASE_UPDATED = "updated: 2026-09-10T16:44Z"

SMALL = """---
nodes:
  - id: ore-vein
    type: source
  - id: ingot-pool
    type: pool
connections:
  - { id: mine, from: ore-vein, to: ingot-pool, kind: resource }
---

## ore-vein

Where ore comes from.
"""


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def body_of(text):
    return text[et.frontmatter_span(text, "design/economy.md", "game-mechanics")[2]:]


class ToolCase(unittest.TestCase):
    """Each test runs against its own copy of ``fixture``, at ``self.path``."""

    fixture = os.path.join(FIXTURES, "base-economy.md")

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.path = os.path.join(self.tmp, "economy.md")
        shutil.copyfile(self.fixture, self.path)
        self.before = read(self.path)

    def use_text(self, text):
        with open(self.path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        self.before = text

    def run_tool(self, *argv):
        """Run the tool in-process with `updated` pinned to NOW."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = et.main(["--file", self.path] + list(argv), now=NOW)
        return code, out.getvalue(), err.getvalue()

    def run_script(self, *argv, **kwargs):
        """Run the tool as a real subprocess, against the real clock."""
        return subprocess.run(
            [sys.executable, kwargs.get("tool", TOOL), "--file", self.path] + list(argv),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )


class QueryTests(ToolCase):
    def tearDown(self):
        self.assertEqual(read(self.path), self.before)

    def test_list_nodes(self):
        code, out, _ = self.run_tool("list-nodes", "--type", "pool")
        self.assertEqual(code, 0)
        self.assertEqual(
            out, "ingot-pool  pool\ngold        pool\nmining-xp   pool\nsmith-xp    pool\n"
        )

    def test_show_node(self):
        code, out, _ = self.run_tool("show-node", "ingot-pool")
        self.assertEqual(code, 0)
        self.assertEqual(
            out,
            "node `ingot-pool`:\n"
            "  - id: ingot-pool\n"
            "    type: pool\n"
            "    value_progression:\n"
            "      model: power\n"
            "      coefficients: [1.8, 1.42]\n"
            "      domain: 1-20\n"
            "      fit: 0.987\n"
            "families: none\n"
            "connections touching it (2):\n"
            "  - { id: mine, from: ore-vein, to: ingot-pool, kind: resource, rate: 3 }\n"
            "  - { id: smelt, from: ingot-pool, to: forge, kind: resource, resource: ore }\n",
        )

    def test_show_family_member(self):
        _, out, _ = self.run_tool("show-node", "mining-xp")
        self.assertIn("families: @skill-xp\nconnections touching it: none\n", out)
        self.assertIn("declarations over @skill-xp (2):\n", out)

    def test_list_connections_filtered(self):
        _, out, _ = self.run_tool("list-connections", "--kind", "state")
        self.assertEqual(
            out,
            "{ id: forge-gate, from: gold, to: forge, kind: state }\n"
            '{ id: skill-rate, from: "@skill-xp", to: "#mine", kind: state, '
            "subtype: label-modifier, applies: one-of-family }\n",
        )
        _, out, _ = self.run_tool("list-connections", "--to", "#mine")
        self.assertIn("id: skill-rate", out)
        self.assertEqual(out.count("\n"), 1)

    def test_show_connection(self):
        _, out, _ = self.run_tool("show-connection", "mine")
        self.assertIn("state connections targeting it (1):\n", out)
        self.assertIn("id: skill-rate", out)

    def test_list_and_show_families(self):
        _, out, _ = self.run_tool("list-families")
        self.assertEqual(out, "@skill-xp  pool  mining-xp, smith-xp\n")
        _, out, _ = self.run_tool("show-family", "@skill-xp")
        self.assertIn("  - family: skill-xp\n    type: pool\n    members: [mining-xp, smith-xp]\n", out)
        self.assertIn("declarations over it (2):\n", out)

    def test_unknown_node(self):
        code, _, err = self.run_tool("show-node", "nope")
        self.assertEqual(code, 1)
        self.assertIn("no node has `id: nope`", err)

    def test_missing_file(self):
        os.remove(self.path)
        code, _, err = self.run_tool("list-nodes")
        self.assertEqual(code, 1)
        self.assertIn("does not exist", err)
        self.use_text(self.before)


class ScriptTests(ToolCase):
    def test_finds_game_gdd_through_a_symlinked_skill_directory(self):
        # How a consuming project opts in: `<project>/.claude/skills/game-mechanics`
        # is a symlink to this skill, with no `game-gdd` beside it.
        link = os.path.join(self.tmp, "skills", "game-mechanics")
        os.makedirs(os.path.dirname(link))
        try:
            os.symlink(os.path.dirname(SCRIPTS_DIR), link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable here")
        result = self.run_script("list-nodes", tool=os.path.join(link, "scripts", "economy-tool"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ore-vein", result.stdout)


if __name__ == "__main__":
    unittest.main()
