"""Tests for build_payload.py, run against the fixture projects beside this
file. Each test copies a fixture into a scratch directory, runs the script
there as a subprocess, and reads the prompt file it writes."""

import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "build_payload.py")
SKILL_DIR = os.path.dirname(os.path.dirname(HERE))
FIXTURES = os.path.join(HERE, "fixtures")

MECHANIC_LABELS = [
    "The unit under review",
    "Its parent",
    "Its children",
    "Its container (`part_of`)",
    "Its parts",
    "Entries it links to",
    "Linked but not carried",
    "Taxonomy index",
    "Economy nodes and connections it names",
    "Approved pillars",
]


class PayloadTestCase(unittest.TestCase):
    fixture = "linked-project"

    def setUp(self):
        self.scratch = tempfile.mkdtemp()
        self.project = os.path.join(self.scratch, "project")
        self.out_dir = os.path.join(self.scratch, "tmp")
        os.makedirs(self.out_dir)
        shutil.copytree(
            os.path.join(FIXTURES, self.fixture, "design"),
            os.path.join(self.project, "design"),
        )

    def tearDown(self):
        shutil.rmtree(self.scratch)

    def run_script(self, persona, unit):
        env = dict(
            os.environ,
            TMPDIR=self.out_dir,
            TEMP=self.out_dir,
            TMP=self.out_dir,
            PYTHONIOENCODING="utf-8",
        )
        return subprocess.run(
            [sys.executable, SCRIPT, "--persona", persona, "--unit", unit],
            cwd=self.project,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def build(self, persona, unit):
        result = self.run_script(persona, unit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        path, _sep, count = result.stdout.strip().rpartition(" (")
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual(count, "%d lines)" % text.count("\n"))
        self.assertEqual(
            os.path.normcase(os.path.dirname(os.path.realpath(path))),
            os.path.normcase(os.path.realpath(self.out_dir)),
        )
        return text

    def section(self, text, label):
        """The body under ``## <label>``, up to the next label or rule outside
        a fenced record."""
        marker = "\n## %s\n\n" % label
        self.assertIn(marker, text)
        out = []
        fence = None
        for line in text.split(marker, 1)[1].split("\n"):
            if fence is None and (line.startswith("## ") or line == "---"):
                break
            if line.startswith("````"):
                run = line[: len(line) - len(line.lstrip("`"))]
                if fence is None:
                    fence = run
                elif line == fence:
                    fence = None
            out.append(line)
        return "\n".join(out)


class MechanicEntryTests(PayloadTestCase):
    def test_persona_file_comes_first_verbatim(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        with open(os.path.join(SKILL_DIR, "references", "mechanics-literalist.md"), encoding="utf-8") as handle:
            persona = handle.read().rstrip("\n")
        self.assertTrue(text.startswith(persona + "\n"))

    def test_sections_appear_in_order(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        positions = [text.index("\n## %s\n" % label) for label in MECHANIC_LABELS]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(positions[-1], text.index("\n# Your critique note\n"))

    def test_relations_travel_trimmed_with_consequences(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        parent = self.section(text, "Its parent")
        self.assertIn("design/mechanics/base.md", parent)
        self.assertIn("## Consequences", parent)
        self.assertIn("Spending a turn on it rules out moving.", parent)
        self.assertNotIn("## Strong example", parent)

    def test_linked_entries_are_capped_at_eight(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        linked = self.section(text, "Entries it links to")
        for i in range(1, 9):
            self.assertIn("design/mechanics/link-%d.md" % i, linked)
            self.assertIn("Link %d forecloses running while it charges." % i, linked)
        self.assertEqual(linked.count("design/mechanics/link-1.md"), 1)
        self.assertNotIn("link-9", linked)
        self.assertEqual(self.section(text, "Linked but not carried").strip(), "- `link-9`")

    def test_relation_and_self_links_are_not_counted(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        linked = self.section(text, "Entries it links to")
        self.assertNotIn("design/mechanics/base.md", linked)
        self.assertNotIn("design/mechanics/hub.md", linked)

    def test_empty_sections_say_none_under_their_own_label(self):
        text = self.build("mechanics-literalist", "design/mechanics/lonely.md")
        for label in (
            "Its parent",
            "Its children",
            "Its container (`part_of`)",
            "Its parts",
            "Entries it links to",
            "Linked but not carried",
            "Economy nodes and connections it names",
        ):
            self.assertEqual(self.section(text, label).strip(), "none", label)

    def test_taxonomy_index_is_three_fields_per_entry(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        index = self.section(text, "Taxonomy index").strip().split("\n")
        self.assertIn("- name: hub · parent: base · part_of: none", index)
        self.assertEqual(len(index), 12)

    def test_economy_slice_carries_named_nodes_and_expanded_families(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        economy = self.section(text, "Economy nodes and connections it names")
        self.assertIn("Node `mana`", economy)
        self.assertIn("The pool every action is paid from.", economy)
        self.assertIn("Family `@skills`", economy)
        self.assertIn("id: train:fire-xp", economy)
        self.assertIn("id: train:ice-xp", economy)
        self.assertNotIn("refill", economy)

    def test_only_approved_pillars_travel(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        pillars = self.section(text, "Approved pillars")
        self.assertIn("design/pillars/core.md", pillars)
        self.assertNotIn("idea", pillars)


class PillarRecordTests(PayloadTestCase):
    def test_pillar_carries_itself_and_the_concept_body(self):
        text = self.build("pillar-fit", "design/pillars/core.md")
        self.assertIn("Every action costs something.", self.section(text, "The unit under review"))
        concept = self.section(text, "Concept statement")
        self.assertIn("A small fixture game whose actions link to one another.", concept)
        self.assertNotIn("title: Linked Fixture", concept)
        self.assertNotIn("\n## Taxonomy index\n", text)


class GddSectionTests(PayloadTestCase):
    def test_section_carries_its_record_and_the_approved_pillars(self):
        text = self.build("player-motivation", "Lonely Action")
        self.assertIn("### Lonely Action", self.section(text, "The unit under review"))
        record = self.section(text, "The record it addresses")
        self.assertIn("design/mechanics/lonely.md", record)
        self.assertIn("Stands alone: no relation and no link.", record)
        self.assertIn("design/pillars/core.md", self.section(text, "Approved pillars"))
        self.assertIn("unit: Lonely Action", text)
        self.assertIn("design/critique/%s-player-motivation-lonely-action.md" % today(), text)

    def test_missing_gdd_is_refused(self):
        os.remove(os.path.join(self.project, "design", "gdd.md"))
        result = self.run_script("player-motivation", "Lonely Action")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("game-gdd", result.stderr)


class NotePathTests(PayloadTestCase):
    def test_same_day_ordinal_is_resolved(self):
        critique = os.path.join(self.project, "design", "critique")
        os.makedirs(critique)
        for suffix in ("", "-2"):
            name = "%s-mechanics-literalist-hub%s.md" % (today(), suffix)
            open(os.path.join(critique, name), "w").close()
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        self.assertIn(
            "Write your note at `design/critique/%s-mechanics-literalist-hub-3.md`" % today(),
            text,
        )

    def test_first_note_of_the_day_has_no_suffix_and_nothing_is_written_to_design(self):
        text = self.build("mechanics-literalist", "design/mechanics/hub.md")
        self.assertIn(
            "Write your note at `design/critique/%s-mechanics-literalist-hub.md`" % today(),
            text,
        )
        self.assertFalse(os.path.exists(os.path.join(self.project, "design", "critique")))

    def test_note_frontmatter_names_the_framework(self):
        text = self.build("pillar-fit", "design/mechanics/hub.md")
        self.assertIn(
            "framework: Jesse Schell's lens method, and design-pillars-as-filter practice",
            text,
        )
        self.assertIn("## The critique note — the one and only definition", text)


class RefusalTests(PayloadTestCase):
    def test_unknown_persona_is_refused(self):
        result = self.run_script("no-such-persona", "design/mechanics/hub.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mechanics-literalist", result.stderr)
        self.assertEqual(os.listdir(self.out_dir), [])


class InvalidEconomyTests(PayloadTestCase):
    fixture = "invalid-economy"

    def test_invalid_economy_is_refused(self):
        result = self.run_script("mechanics-literalist", "design/mechanics/cast.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("design/economy.md", result.stderr)
        self.assertIn("has no `id`", result.stderr)
        self.assertIn("game-mechanics", result.stderr)
        self.assertEqual(os.listdir(self.out_dir), [])


def today():
    return datetime.date.today().isoformat()


if __name__ == "__main__":
    unittest.main()
