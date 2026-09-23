import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, "fixtures")
sys.path.insert(0, SCRIPTS_DIR)

import find_references as fr  # noqa: E402
from render_gdd import BadReference  # noqa: E402


class ResolveTargetTypedStringTests(unittest.TestCase):
    def test_typed_pillar(self):
        self.assertEqual(fr.resolve_target("pillar:zero-grind"), ("pillar", "zero-grind"))

    def test_typed_node(self):
        self.assertEqual(fr.resolve_target("node:ingot-pool"), ("node", "ingot-pool"))

    def test_bare_concept(self):
        self.assertEqual(fr.resolve_target("concept"), ("concept", ""))

    def test_bare_comp_analysis(self):
        self.assertEqual(fr.resolve_target("comp-analysis"), ("comp-analysis", ""))

    def test_unknown_type_is_rejected(self):
        with self.assertRaises(BadReference):
            fr.resolve_target("no-such-type:no-such-id")

    def test_untyped_bare_word_is_rejected(self):
        with self.assertRaises(BadReference):
            fr.resolve_target("zero-grind")


class ResolveTargetPathTests(unittest.TestCase):
    def test_pillar_path(self):
        self.assertEqual(
            fr.resolve_target("design/pillars/zero-grind.md"), ("pillar", "zero-grind")
        )

    def test_pillar_path_without_design_prefix(self):
        self.assertEqual(
            fr.resolve_target("pillars/zero-grind.md"), ("pillar", "zero-grind")
        )

    def test_mechanic_path(self):
        self.assertEqual(
            fr.resolve_target("design/mechanics/combat.md"), ("mechanic", "combat")
        )

    def test_tech_path(self):
        self.assertEqual(fr.resolve_target("design/tech/netcode.md"), ("tech", "netcode"))

    def test_concept_path(self):
        self.assertEqual(fr.resolve_target("design/concept.md"), ("concept", ""))

    def test_comp_analysis_path(self):
        self.assertEqual(
            fr.resolve_target("design/comp-analysis.md"), ("comp-analysis", "")
        )

    def test_economy_path_is_rejected(self):
        with self.assertRaises(BadReference):
            fr.resolve_target("design/economy.md")

    def test_unrecognized_path_is_rejected(self):
        with self.assertRaises(BadReference):
            fr.resolve_target("design/ideas.md")


class FindHitsInTextTests(unittest.TestCase):
    def test_matches_typed_reference_on_its_line(self):
        text = "# Heading\n\nServes [[pillar:zero-grind]] well.\n"
        hits = fr.find_hits_in_text(text, "pillar", "zero-grind")
        self.assertEqual(hits, [(3, "# Heading")])

    def test_ignores_reference_of_different_kind_or_ident(self):
        text = "[[pillar:other]]\n[[mechanic:zero-grind]]\n"
        self.assertEqual(fr.find_hits_in_text(text, "pillar", "zero-grind"), [])

    def test_ignores_reference_inside_code_span(self):
        text = "A literal `[[pillar:zero-grind]]` is just text.\n"
        self.assertEqual(fr.find_hits_in_text(text, "pillar", "zero-grind"), [])

    def test_ignores_reference_inside_fenced_block(self):
        text = "```\n[[pillar:zero-grind]]\n```\n"
        self.assertEqual(fr.find_hits_in_text(text, "pillar", "zero-grind"), [])

    def test_ignores_malformed_reference_that_isnt_the_target(self):
        text = "[[no-such-type:no-such-id]]\n[[pillar:zero-grind]]\n"
        self.assertEqual(fr.find_hits_in_text(text, "pillar", "zero-grind"), [(2, "")])

    def test_tracks_most_recent_heading(self):
        text = "## First\nnothing here\n## Second\n[[tech:netcode]]\n"
        self.assertEqual(
            fr.find_hits_in_text(text, "tech", "netcode"), [(4, "## Second")]
        )

    def test_bare_type_match(self):
        text = "recorded in [[concept]].\n"
        self.assertEqual(fr.find_hits_in_text(text, "concept", ""), [(1, "")])


class CliIntegrationTests(unittest.TestCase):
    def run_cli(self, cwd, *args):
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "find_references.py")] + list(args),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result

    def fixture_dir(self):
        return os.path.join(FIXTURES, "one-of-everything")

    def test_reports_every_hit_with_file_line_and_heading(self):
        result = self.run_cli(self.fixture_dir(), "pillar:zero-grind")
        self.assertEqual(result.returncode, 0)
        out = result.stdout.decode()
        self.assertIn("design/mechanics/melee.md:", out)
        self.assertIn("design/pillars/tight-loop.md:", out)
        self.assertIn("[[pillar:zero-grind]]", out)

    def test_path_form_matches_typed_form(self):
        by_typed = self.run_cli(self.fixture_dir(), "pillar:zero-grind").stdout
        by_path = self.run_cli(
            self.fixture_dir(), "design/pillars/zero-grind.md"
        ).stdout
        self.assertEqual(by_typed, by_path)

    def test_zero_hits_reports_none_and_exits_zero(self):
        result = self.run_cli(self.fixture_dir(), "tech:save-format")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No references to [[tech:save-format]]", result.stdout.decode())

    def test_bad_target_exits_nonzero_with_stderr(self):
        result = self.run_cli(self.fixture_dir(), "no-such-type:no-such-id")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr)

    def test_never_reports_the_reference_inside_a_code_span(self):
        result = self.run_cli(self.fixture_dir(), "comp-analysis")
        out = result.stdout.decode()
        self.assertIn("design/pillars/zero-grind.md:", out)
        self.assertNotIn("[[slug]]", out)


if __name__ == "__main__":
    unittest.main()
