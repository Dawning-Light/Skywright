import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, "fixtures")
sys.path.insert(0, SCRIPTS_DIR)

import economy_frontmatter as ef  # noqa: E402


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def fixture_economy(name):
    return os.path.join(FIXTURES, name, "design", "economy.md")


class FrontmatterSpanTests(unittest.TestCase):
    def test_span_brackets_the_block_and_the_body(self):
        text = "---\na: 1\nb: 2\n---\n\n## body\n"
        start, end, body = ef.frontmatter_span(text, "x.md", "s")
        self.assertEqual(text[start:end], "a: 1\nb: 2")
        self.assertEqual(text[body:], "\n## body\n")

    def test_empty_block(self):
        text = "---\n---\nbody\n"
        start, end, body = ef.frontmatter_span(text, "x.md", "s")
        self.assertEqual(text[start:end], "")
        self.assertEqual(text[body:], "body\n")

    def test_closing_fence_on_the_last_line(self):
        text = "---\na: 1\n---"
        start, end, body = ef.frontmatter_span(text, "x.md", "s")
        self.assertEqual(text[start:end], "a: 1")
        self.assertEqual(text[body:], "")

    def test_no_frontmatter(self):
        self.assertIsNone(ef.frontmatter_span("## just a body\n", "x.md", "s"))
        self.assertIsNone(ef.frontmatter_span("----\na: 1\n", "x.md", "s"))

    def test_unclosed_block_raises(self):
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.frontmatter_span("---\na: 1\n", "x.md", "game-pillars")
        self.assertIn("never closed", str(caught.exception))
        self.assertIn("game-pillars", str(caught.exception))

    def test_split_frontmatter_is_the_span_sliced(self):
        for text in (
            "---\na: 1\n---\nbody\n",
            "---\n---\n",
            "---\na: 1\n---",
            "--- \na: 1\n ---\n\nbody",
        ):
            start, end, body = ef.frontmatter_span(text, "x.md", "s")
            self.assertEqual(
                ef.split_frontmatter(text, "x.md", "s"), (text[start:end], text[body:])
            )
        self.assertEqual(ef.split_frontmatter("body\n", "x.md", "s"), (None, "body\n"))


ORPHAN = """---
nodes:
  - id: a
    type: pool
connections: []
---

## gone

Orphaned.
"""


class ParseEconomyTests(unittest.TestCase):
    def test_heading_rule_applies_by_default(self):
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.parse_economy(ORPHAN)
        self.assertIn("body heading `## gone` resolves to no node", str(caught.exception))

    def test_headings_false_skips_only_the_heading_rule(self):
        economy = ef.parse_economy(ORPHAN, headings=False)
        self.assertEqual(economy["node_ids"], ["a"])

    def test_headings_false_still_checks_records(self):
        text = ORPHAN.replace(
            "connections: []", "connections:\n  - { id: c, from: a, to: nowhere, kind: resource }"
        )
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.parse_economy(text, headings=False)
        self.assertIn("`to: nowhere`, which resolves to nothing", str(caught.exception))

    def test_load_economy_is_parse_economy_on_the_file(self):
        path = fixture_economy("one-of-everything")
        self.assertEqual(ef.load_economy(path), ef.parse_economy(ef.read_text(path)))


class DuplicateIdTests(unittest.TestCase):
    def test_duplicate_node_id(self):
        text = ORPHAN.replace("connections: []", "  - id: a\n    type: pool\nconnections: []")
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.parse_economy(text, headings=False)
        self.assertIn("node id `a` is declared more than once", str(caught.exception))

    def test_duplicate_connection_id(self):
        text = ORPHAN.replace(
            "connections: []",
            "connections:\n"
            "  - { id: c, from: a, to: a, kind: resource }\n"
            "  - { id: c, from: a, to: a, kind: resource }",
        )
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.parse_economy(text, headings=False)
        self.assertIn("connection id `c` is declared more than once", str(caught.exception))

    def test_duplicate_family_name(self):
        text = ORPHAN.replace(
            "connections: []",
            "families:\n"
            "  - family: f\n    type: pool\n    members: [a]\n"
            "  - family: f\n    type: pool\n    members: [a]\n"
            "connections: []",
        )
        with self.assertRaises(ef.InvalidInput) as caught:
            ef.parse_economy(text, headings=False)
        self.assertIn("family `@f` is declared more than once", str(caught.exception))



class SerializerTests(unittest.TestCase):
    def assert_round_trips(self, path):
        text = read(path)
        fm_text, _ = ef.split_frontmatter(text, path, "s")
        fields = ef.parse_frontmatter(fm_text, path, "s")
        self.assertEqual(ef.serialize_economy_frontmatter(fields), fm_text)

    def test_one_of_everything_round_trips_byte_for_byte(self):
        self.assert_round_trips(fixture_economy("one-of-everything"))

    def test_invalid_economy_round_trips_byte_for_byte(self):
        self.assert_round_trips(fixture_economy("invalid-economy"))

    def test_duplicate_economy_id_round_trips_byte_for_byte(self):
        self.assert_round_trips(fixture_economy("duplicate-economy-id"))

    def test_connections_are_flow_and_other_lists_block(self):
        fields = {
            "nodes": [{"id": "a", "type": "pool"}],
            "families": [{"family": "f", "type": "pool", "members": ["a"]}],
            "connections": [{"id": "c", "from": "a", "to": "@f", "kind": "state"}],
        }
        self.assertEqual(
            ef.serialize_economy_frontmatter(fields),
            "nodes:\n"
            "  - id: a\n"
            "    type: pool\n"
            "families:\n"
            "  - family: f\n"
            "    type: pool\n"
            "    members: [a]\n"
            "connections:\n"
            '  - { id: c, from: a, to: "@f", kind: state }',
        )

    def test_nested_mapping_and_empty_list_round_trip(self):
        fields = {
            "updated": "2026-09-14T12:00Z",
            "nodes": [
                {
                    "id": "a",
                    "type": "pool",
                    "value_progression": {
                        "model": "linear",
                        "coefficients": "-2 3",
                        "domain": "1 10",
                        "fit": "1",
                    },
                }
            ],
            "connections": [],
        }
        text = ef.serialize_economy_frontmatter(fields)
        self.assertEqual(
            text,
            "updated: 2026-09-14T12:00Z\n"
            "nodes:\n"
            "  - id: a\n"
            "    type: pool\n"
            "    value_progression:\n"
            "      model: linear\n"
            "      coefficients: -2 3\n"
            "      domain: 1 10\n"
            "      fit: 1\n"
            "connections: []",
        )
        self.assertEqual(ef.parse_frontmatter(text, "x.md", "s"), fields)

    def test_quoting(self):
        self.assertEqual(ef.format_scalar("@f", True), '"@f"')
        self.assertEqual(ef.format_scalar("#c", False), '"#c"')
        self.assertEqual(ef.format_scalar("a, b", True), '"a, b"')
        self.assertEqual(ef.format_scalar("a, b", False), "a, b")
        self.assertEqual(ef.format_scalar("", True), '""')
        self.assertEqual(ef.format_scalar('"x', False), "'\"x'")
        self.assertEqual(ef.format_scalar("2026-09-14T12:00Z", False), "2026-09-14T12:00Z")

    def test_unrepresentable_values_raise(self):
        with self.assertRaises(ValueError):
            ef.format_scalar("two\nlines", False)
        with self.assertRaises(ValueError):
            ef.format_scalar("\"it's", False)
        with self.assertRaises(ValueError):
            ef.serialize_economy_frontmatter({"nodes": [{"id": "a", "value_progression": {}}]})


if __name__ == "__main__":
    unittest.main()
