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


class RoundTripCase(ToolCase):
    """A mutation's frontmatter changes exactly as expected, `updated` moves
    to NOW, and the body is byte-for-byte untouched."""

    def expect(self, *replacements):
        text = self.before
        for old, new in replacements:
            self.assertEqual(text.count(old), 1, "fixture must hold %r exactly once" % old)
            text = text.replace(old, new)
        return text.replace(BASE_UPDATED, "updated: %s" % NOW)

    def assert_wrote(self, expected, result):
        code, out, err = result
        self.assertEqual((code, err), (0, ""))
        self.assertIn("`updated` is now %s." % NOW, out)
        after = read(self.path)
        self.assertEqual(after, expected)
        self.assertEqual(body_of(after), body_of(self.before))
        return out


class RefusalCase(ToolCase):
    """A refused command exits 1, says why, and leaves the file untouched."""

    def assert_refused(self, argv, *phrases):
        code, out, err = self.run_tool(*argv)
        self.assertEqual((code, out), (1, ""))
        for phrase in phrases:
            self.assertIn(phrase, err)
        self.assertIn("Nothing was written.", err)
        self.assertEqual(read(self.path), self.before)


class NodeAndConnectionMutationTests(RoundTripCase):
    def test_add_node(self):
        out = self.assert_wrote(
            self.expect((
                "  - id: slag-heap\n    type: drain\n",
                "  - id: slag-heap\n    type: drain\n  - id: silver\n    type: pool\n",
            )),
            self.run_tool("add-node", "silver", "--type", "pool"),
        )
        self.assertIn("added node `silver` (pool)", out)

    def test_remove_node(self):
        self.assert_wrote(
            self.expect(("  - id: slag-heap\n    type: drain\n", "")),
            self.run_tool("remove-node", "slag-heap"),
        )

    def test_add_connection(self):
        last = (
            '  - { id: skill-rate, from: "@skill-xp", to: "#mine", kind: state, '
            "subtype: label-modifier, applies: one-of-family }\n"
        )
        self.assert_wrote(
            self.expect((
                last,
                last + "  - { id: dump, from: forge, to: slag-heap, kind: resource, resource: slag }\n",
            )),
            self.run_tool(
                "add-connection", "dump", "--from", "forge", "--to", "slag-heap",
                "--kind", "resource", "--resource", "slag",
            ),
        )

    def test_add_unclassified_state_connection(self):
        # An absent `subtype` means "not yet classified" -- valid, per
        # game-mechanics -- so the tool writes it.
        last = "applies: one-of-family }\n"
        self.assert_wrote(
            self.expect((
                last,
                last + '  - { id: slag-gate, from: slag-heap, to: "#smelt", kind: state }\n',
            )),
            self.run_tool(
                "add-connection", "slag-gate", "--from", "slag-heap", "--to", "#smelt",
                "--kind", "state",
            ),
        )

    def test_remove_connection(self):
        self.assert_wrote(
            self.expect((
                "  - { id: sale, from: forge, to: gold, kind: resource, resource: gold, rate: 5 }\n",
                "",
            )),
            self.run_tool("remove-connection", "sale"),
        )

    def test_a_change_and_its_inverse_leave_only_updated_moved(self):
        self.assertEqual(self.run_tool("add-node", "silver", "--type", "pool")[0], 0)
        self.assertEqual(self.run_tool("remove-node", "silver")[0], 0)
        self.assertEqual(read(self.path), self.expect())


class NodeAndConnectionRefusalTests(RefusalCase):
    def test_remove_node_still_touched_by_connections(self):
        self.assert_refused(
            ["remove-node", "gold"], "connection `sale`", "connection `forge-gate`", "never cascades"
        )

    def test_remove_node_still_in_a_family(self):
        self.assert_refused(["remove-node", "smith-xp"], "family `@skill-xp`")

    def test_remove_unknown_node(self):
        self.assert_refused(["remove-node", "nope"], "no node has `id: nope`")

    def test_remove_connection_still_targeted(self):
        self.assert_refused(["remove-connection", "mine"], "connection `skill-rate`", "never cascades")

    def test_add_existing_node(self):
        self.assert_refused(["add-node", "gold", "--type", "pool"], "node `gold` already exists")

    def test_colon_in_a_connection_id(self):
        self.assert_refused(
            ["add-connection", "a:b", "--from", "gold", "--to", "slag-heap", "--kind", "resource"],
            "reserved for the derived ids",
        )

    def test_family_on_both_ends(self):
        self.assert_refused(
            ["add-connection", "x", "--from", "@skill-xp", "--to", "@skill-xp", "--kind", "state"],
            "at most one end",
        )

    def test_unresolved_reference(self):
        self.assert_refused(
            ["add-connection", "x", "--from", "gold", "--to", "nowhere", "--kind", "resource"],
            "`to: nowhere`, which resolves to nothing",
        )

    def test_resource_connection_into_a_converter_names_its_resource(self):
        self.assert_refused(
            ["add-connection", "x", "--from", "gold", "--to", "forge", "--kind", "resource"],
            "`--resource`",
        )

    def test_subtype_on_a_resource_connection(self):
        self.assert_refused(
            ["add-connection", "x", "--from", "gold", "--to", "slag-heap", "--kind", "resource",
             "--subtype", "trigger"],
            "only on a `state` connection",
        )

    def test_unrepresentable_free_form_value(self):
        # A newline in a free-form option (here --resource) would make
        # `change()` raise a bare ValueError from deep inside
        # `format_flow_mapping`, before `mutate`'s later ValueError guard
        # around `serialize_economy_frontmatter` -- it must still come out
        # as a clean, ToolError-shaped refusal, not an uncaught traceback.
        self.assert_refused(
            ["add-connection", "dump", "--from", "forge", "--to", "slag-heap",
             "--kind", "resource", "--resource", "slag }\nnodes:\n  - id: evil\n    type: pool"],
            "cannot span lines",
        )


class InvalidFileRefusalTests(ToolCase):
    """A mutation that would leave an invalid file is refused: the tool
    validates the whole result, not only the part it changed."""

    def assert_add_node_refused(self, *phrases):
        code, out, err = self.run_tool("add-node", "silver", "--type", "pool")
        self.assertEqual((code, out), (1, ""))
        for phrase in phrases:
            self.assertIn(phrase, err)
        self.assertIn("Nothing was written.", err)
        self.assertEqual(read(self.path), self.before)

    def test_connection_without_an_id(self):
        self.use_text(read(os.path.join(GDD_FIXTURES, "invalid-economy", "design", "economy.md")))
        self.assert_add_node_refused("has no `id`", "game-mechanics")

    def test_duplicate_node_id(self):
        self.use_text(SMALL.replace("  - id: ingot-pool\n", "  - id: ore-vein\n"))
        self.assert_add_node_refused("node id `ore-vein` is declared more than once")

    def test_unresolved_sigil(self):
        self.use_text(SMALL.replace("to: ingot-pool", 'to: "#nope"'))
        self.assert_add_node_refused("`to: #nope`, which resolves to nothing")

    def test_block_style_connection(self):
        self.use_text(SMALL.replace(
            "  - { id: mine, from: ore-vein, to: ingot-pool, kind: resource }\n",
            "  - id: mine\n    from: ore-vein\n    to: ingot-pool\n    kind: resource\n",
        ))
        self.assert_add_node_refused("block mapping", "flow style")

    def test_non_canonical_frontmatter(self):
        self.use_text(SMALL.replace("nodes:\n", "nodes:\n  # sources first\n"))
        self.assert_add_node_refused(
            "line 3 of the file, `  # sources first`, is not in the canonical form"
        )


class CanonicalFixtureTests(unittest.TestCase):
    def test_base_fixture_is_already_canonical(self):
        doc = et.EconomyFile(os.path.join(FIXTURES, "base-economy.md"))
        self.assertIsNone(et.canonical_problem(doc))


class MutatingScriptTests(ToolCase):
    def test_runs_as_a_script_and_stamps_the_real_clock(self):
        result = self.run_script("add-node", "silver", "--type", "pool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(read(self.path), r"(?m)^updated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")

    def test_usage_error_exits_2(self):
        self.assertEqual(self.run_script("add-node", "silver").returncode, 2)


if __name__ == "__main__":
    unittest.main()
