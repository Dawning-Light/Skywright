#!/usr/bin/env python3
"""Assemble one critic's whole dispatch prompt for ``game-critique``.

Given one persona and one unit, writes a single file holding, in order: the
persona's reference file verbatim; the unit; the unit's dispatch payload under
fixed section labels; and the critique note's path and shape. The file goes in
the OS temp directory, never inside ``design/``. Prints the file's path and
line count on stdout.

``game-critique``'s SKILL.md payload table is the authoritative definition of
what travels with each unit type; this script implements it. An economy graph
that fails ``game-mechanics``' rules is refused rather than sliced on a
best-effort basis: nothing is written, one message goes to stderr, and the
exit code is non-zero.

Run from the consuming project's root, the directory holding ``design/``:

    python3 <skill>/scripts/build_payload.py --persona <name> --unit <unit>

``<unit>`` is a record path (``design/pillars/<slug>.md`` or
``design/mechanics/<slug>.md``) or the heading of a section of
``design/gdd.md``.

Records are parsed through ``game-gdd``'s ``economy_frontmatter.py`` and
wikilinks found through ``render_gdd.py``'s scanner, so this script carries no
parser of its own. Stdlib only.
"""

import argparse
import datetime
import os
import re
import sys
import tempfile

_SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(_SCRIPTS_DIR, os.pardir, os.pardir, "game-gdd", "scripts")
    ),
)

from economy_frontmatter import (  # noqa: E402
    InvalidInput,
    as_list,
    as_text,
    family_name,
    format_flow_list,
    format_flow_mapping,
    format_scalar,
    load_economy,
    parse_frontmatter,
    read_text,
    split_frontmatter,
    split_sections,
    trim_body,
)
from render_gdd import iter_wikilink_hits  # noqa: E402

LINKED_CAP = 8
NONE = "none"


class Refusal(Exception):
    """The payload cannot be built. Carries the whole stderr message."""


# ---------------------------------------------------------------------------
# Reading records
# ---------------------------------------------------------------------------


def load_record(path, rel, skill):
    """``(fields, body, full text)`` for one record file."""
    text = read_text(path)
    fm_text, body = split_frontmatter(text, rel, skill)
    fields = parse_frontmatter(fm_text, rel, skill) if fm_text is not None else {}
    return fields, trim_body(body), text.rstrip("\n")


def list_slugs(directory):
    if not os.path.isdir(directory):
        return []
    return sorted(n[:-3] for n in os.listdir(directory) if n.endswith(".md"))


def relation(value):
    """A single-slug relation field, with ``none`` and absence read as empty."""
    text = as_text(value).strip()
    return "" if text in ("", NONE) else text


def relation_list(value):
    return [v for v in (as_text(x).strip() for x in as_list(value)) if v and v != NONE]


def load_mechanics(root):
    """Every mechanic entry under ``design/mechanics/``, keyed by slug."""
    directory = os.path.join(root, "mechanics")
    mechanics = {}
    for slug in list_slugs(directory):
        rel = "design/mechanics/%s.md" % slug
        fields, body, text = load_record(
            os.path.join(directory, slug + ".md"), rel, "game-mechanics"
        )
        mechanics[slug] = {"slug": slug, "rel": rel, "fields": fields, "body": body, "text": text}
    return mechanics


def approved_pillars(root):
    directory = os.path.join(root, "pillars")
    out = []
    for slug in list_slugs(directory):
        rel = "design/pillars/%s.md" % slug
        fields, _body, text = load_record(
            os.path.join(directory, slug + ".md"), rel, "game-pillars"
        )
        if as_text(fields.get("status", "")).strip() == "approved":
            out.append((rel, text))
    return out


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def fenced(text):
    """``text`` inside a code fence longer than any backtick run it holds."""
    longest = max([len(run) for run in re.findall(r"`+", text)] + [0])
    fence = "`" * max(4, longest + 1)
    return "%smarkdown\n%s\n%s" % (fence, text, fence)


def section(label, parts):
    """One labelled payload section. An empty one says ``none`` under its own
    label, never in another section."""
    parts = [p for p in parts if p]
    return "## %s\n\n%s" % (label, "\n\n".join(parts) if parts else NONE)


def trimmed_entry(slug, mechanics):
    """A related or linked mechanic entry in its trimmed form: ``title``,
    ``## Description``, ``## Consequences``."""
    mech = mechanics.get(slug)
    if mech is None:
        return "`%s`: no mechanic entry by that name exists." % slug
    sections, _ = split_sections(mech["body"])
    lines = [
        "name: %s" % slug,
        "title: %s" % as_text(mech["fields"].get("title", "")).strip(),
    ]
    for heading in ("Description", "Consequences"):
        lines.append("")
        lines.append("## %s" % heading)
        lines.append("")
        if heading in sections:
            lines.append(sections[heading])
        else:
            lines.append("(this entry has no `## %s` heading)" % heading)
    return "`%s`\n\n%s" % (mech["rel"], fenced("\n".join(lines)))


def taxonomy_index(mechanics):
    """Every mechanic entry's ``name``, ``parent`` and ``part_of``, as written."""
    lines = []
    for slug in sorted(mechanics):
        fields = mechanics[slug]["fields"]
        values = []
        for key in ("name", "parent", "part_of"):
            raw = as_text(fields.get(key, "")).strip() if key in fields else ""
            values.append("%s: %s" % (key, raw if raw else "(absent)"))
        lines.append("- " + " · ".join(values))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Linked entries
# ---------------------------------------------------------------------------


def cited(body, kinds):
    """``(kind, ident)`` for each typed reference of ``kinds`` in ``body``,
    deduplicated, in order of first citation."""
    seen = []
    for kind, ident, _literal, _heading, _lineno in iter_wikilink_hits(body):
        if kind in kinds and (kind, ident) not in seen:
            seen.append((kind, ident))
    return seen


def linked_entries(unit, related):
    """``(carried, not_carried)``: the mechanic entries the unit's body cites,
    excluding itself and entries already carried as relations, split at the
    cap."""
    links = [
        ident
        for _kind, ident in cited(unit["body"], ("mechanic",))
        if ident != unit["slug"] and ident not in related
    ]
    return links[:LINKED_CAP], links[LINKED_CAP:]


# ---------------------------------------------------------------------------
# The economy slice
# ---------------------------------------------------------------------------


def flat(mapping):
    """A node or family entry on one line. A nested mapping -- a node's
    ``value_progression`` -- is written as a flow mapping inside it."""
    parts = []
    for key, value in mapping.items():
        if isinstance(value, dict):
            parts.append("%s: %s" % (key, format_flow_mapping(value)))
        elif isinstance(value, list):
            parts.append("%s: %s" % (key, format_flow_list(value)))
        else:
            parts.append("%s: %s" % (key, format_scalar(value, True)))
    return "{ %s }" % ", ".join(parts)


def economy_slice(economy, names):
    """The nodes, families, and connections ``names`` cites, each with its
    prose notes, and each family declaration with its expansion under
    ``game-mechanics``' derived-id rule. ``names`` is ``[(kind, ident)]``."""
    nodes = {as_text(n.get("id", "")).strip(): n for n in economy["nodes"]}
    families = {family_name(f): f for f in economy["families"]}
    conns = {as_text(c.get("id", "")).strip(): c for c in economy["connections"]}
    out = []

    def notes(heading):
        text = economy["sections"].get(heading)
        return "\n\n" + fenced("## %s\n\n%s" % (heading, text)) if text else ""

    def declaration_family(conn):
        for end in ("from", "to"):
            ref = as_text(conn.get(end, "")).strip()
            if ref.startswith("@"):
                return ref[1:]
        return ""

    def expansion(conn, only=None):
        fname = declaration_family(conn)
        members = as_list(families.get(fname, {}).get("members"))
        cid = as_text(conn.get("id", "")).strip()
        lines = []
        for member in members:
            if only is not None and member != only:
                continue
            expanded = dict(conn)
            expanded["id"] = "%s:%s" % (cid, member)
            for end in ("from", "to"):
                if as_text(expanded.get(end, "")).strip() == "@" + fname:
                    expanded[end] = member
            expanded.pop("applies", None)
            lines.append("  - %s" % format_flow_mapping(expanded))
        return lines

    def connection_text(conn, only=None):
        lines = ["- %s" % format_flow_mapping(conn)]
        if declaration_family(conn):
            applies = as_text(conn.get("applies", "")).strip()
            lines.append(
                "  expands to (%s):"
                % (
                    "exactly one live at a time"
                    if applies == "one-of-family"
                    else "all live simultaneously"
                )
            )
            lines.extend(expansion(conn, only))
        return "\n".join(lines)

    for kind, ident in names:
        if kind == "node":
            node = nodes.get(ident)
            if node is None:
                out.append("Node `%s`: no node by that id exists." % ident)
                continue
            out.append("Node `%s`:\n\n- %s%s" % (ident, flat(node), notes(ident)))
        elif kind == "family":
            family = families.get(ident)
            if family is None:
                out.append("Family `%s`: no family by that name exists." % ident)
                continue
            members = as_list(family.get("members"))
            parts = ["Family `@%s`:" % ident, "- %s" % flat(family)]
            parts.append("Members:")
            parts.extend(
                "- %s" % flat(nodes[m]) if m in nodes else "- `%s`" % m
                for m in members
            )
            decls = [c for c in economy["connections"] if declaration_family(c) == ident]
            parts.append("Declarations over it:" if decls else "Declarations over it: none")
            parts.extend(connection_text(c) for c in decls)
            out.append("\n".join(parts) + notes("@" + ident))
        elif kind == "connection":
            base, _sep, member = ident.partition(":")
            conn = conns.get(base)
            if conn is None:
                out.append("Connection `%s`: no connection by that id exists." % ident)
                continue
            out.append(
                "Connection `%s`:\n\n%s" % (ident, connection_text(conn, member or None))
            )
    return out


def load_economy_or_refuse(root):
    path = os.path.join(root, "economy.md")
    if not os.path.isfile(path):
        return None
    try:
        return load_economy(path)
    except InvalidInput as exc:
        raise Refusal(
            "design/economy.md is invalid, so `game-critique` will not critique "
            "against it rather than slice it on a best-effort basis: %s The "
            "upgrade is proposed and confirmed with the owner in "
            "`game-mechanics`." % exc
        )


# ---------------------------------------------------------------------------
# Payloads, one per unit type
# ---------------------------------------------------------------------------


def mechanic_payload(root, slug):
    mechanics = load_mechanics(root)
    unit = mechanics[slug]
    fields = unit["fields"]
    parent = relation(fields.get("parent"))
    children = relation_list(fields.get("children"))
    part_of = relation(fields.get("part_of"))
    parts = relation_list(fields.get("parts"))
    related = set([parent, part_of] + children + parts) - {""}
    carried, not_carried = linked_entries(unit, related)

    economy = load_economy_or_refuse(root)
    names = cited(unit["body"], ("node", "family", "connection"))
    if economy is None:
        slice_parts = (
            ["`design/economy.md` does not exist; the unit names %s."
             % ", ".join("`%s:%s`" % n for n in names)]
            if names else []
        )
    else:
        slice_parts = economy_slice(economy, names)

    return [
        section("The unit under review", ["`%s` (mechanic entry)" % unit["rel"], fenced(unit["text"])]),
        section("Its parent", [trimmed_entry(parent, mechanics)] if parent else []),
        section("Its children", [trimmed_entry(c, mechanics) for c in children]),
        section("Its container (`part_of`)", [trimmed_entry(part_of, mechanics)] if part_of else []),
        section("Its parts", [trimmed_entry(p, mechanics) for p in parts]),
        section("Entries it links to", [trimmed_entry(s, mechanics) for s in carried]),
        section("Linked but not carried", ["\n".join("- `%s`" % s for s in not_carried)]),
        section("Taxonomy index", [taxonomy_index(mechanics)]),
        section("Economy nodes and connections it names", slice_parts),
        section("Approved pillars", pillar_parts(root)),
    ]


def pillar_parts(root):
    return ["`%s`\n\n%s" % (rel, fenced(text)) for rel, text in approved_pillars(root)]


def pillar_payload(root, slug):
    rel = "design/pillars/%s.md" % slug
    _fields, _body, text = load_record(os.path.join(root, "pillars", slug + ".md"), rel, "game-pillars")
    concept_path = os.path.join(root, "concept.md")
    concept = []
    if os.path.isfile(concept_path):
        _f, body, _t = load_record(concept_path, "design/concept.md", "game-pillars")
        concept = ["`design/concept.md`, its body\n\n%s" % fenced(body)]
    return [
        section("The unit under review", ["`%s` (pillar record)" % rel, fenced(text)]),
        section("Concept statement", concept),
    ]


_ATX_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_SOURCE_RE = re.compile(
    r"^\*Source: `([^`]+)`(?:, (node|family|connection) `([^`]+)`)?"
)


def heading_slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def find_gdd_section(gdd_text, name):
    """``(heading text, section text)`` for the one heading ``name`` names."""
    wanted = name.lstrip("#").strip()
    lines = gdd_text.split("\n")
    headings = []
    in_fence = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*(```+|~~~+)", line):
            in_fence = not in_fence
            continue
        match = None if in_fence else _ATX_RE.match(line)
        if match:
            headings.append((i, len(match.group(1)), match.group(2)))
    matches = [h for h in headings if h[2].lower() == wanted.lower()]
    if not matches:
        matches = [h for h in headings if heading_slug(h[2]) == heading_slug(wanted)]
    if not matches:
        raise Refusal(
            "design/gdd.md has no section headed `%s`; name a heading the "
            "rendered GDD carries, or re-render it with `game-gdd`." % wanted
        )
    if len(matches) > 1:
        raise Refusal(
            "design/gdd.md has %d sections headed `%s`; name a record path "
            "instead, or a heading that appears once." % (len(matches), wanted)
        )
    start, level, text = matches[0]
    end = len(lines)
    for i, other_level, _t in headings:
        if i > start and other_level <= level:
            end = i
            break
    return text, "\n".join(lines[start:end]).rstrip("\n")


def addressed_record(root, section_text):
    """The record the section's ``Source:`` caption names, as payload parts."""
    for line in section_text.split("\n")[1:]:
        if not line.strip():
            continue
        match = _SOURCE_RE.match(line.strip())
        if not match:
            return []
        rel, kind, ident = match.groups()
        if rel == "design/economy.md" and kind:
            economy = load_economy_or_refuse(root)
            if economy is None:
                return ["`design/economy.md` does not exist."]
            ident = ident.lstrip("@")
            return ["`design/economy.md`, %s `%s`" % (kind, ident)] + economy_slice(
                economy, [(kind, ident)]
            )
        path = os.path.join(root, os.pardir, *rel.split("/"))
        if not os.path.isfile(path):
            return ["`%s` does not exist." % rel]
        if rel == "design/economy.md":
            load_economy_or_refuse(root)
        return ["`%s`\n\n%s" % (rel, fenced(read_text(path).rstrip("\n")))]
    return []


def gdd_payload(root, name):
    gdd_path = os.path.join(root, "gdd.md")
    if not os.path.isfile(gdd_path):
        raise Refusal(
            "design/gdd.md does not exist, so `%s` is not available as a GDD "
            "section unit; render it with `game-gdd`." % name
        )
    heading, text = find_gdd_section(read_text(gdd_path), name)
    return heading, [
        section("The unit under review", ["Section `%s` of `design/gdd.md`" % heading, fenced(text)]),
        section("The record it addresses", addressed_record(root, text)),
        section("Approved pillars", pillar_parts(root)),
    ]


# ---------------------------------------------------------------------------
# The critique note
# ---------------------------------------------------------------------------


def skill_text():
    return read_text(os.path.join(_SKILL_DIR, "SKILL.md"))


def framework_of(persona, skill):
    for line in skill.split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] == "`%s`" % persona:
            return cells[1]
    return ""


def note_shape(skill):
    """The critique note's definition, verbatim from SKILL.md."""
    match = re.search(
        r"^## The critique note.*?(?=^## )", skill, flags=re.MULTILINE | re.DOTALL
    )
    return match.group(0).rstrip("\n") if match else ""


def note_path(cwd, today, persona, unit_slug):
    """The note's path, with the same-day ordinal already resolved."""
    base = "design/critique/%s-%s-%s" % (today, persona, unit_slug)
    rel = base + ".md"
    ordinal = 2
    while os.path.exists(os.path.join(cwd, *rel.split("/"))):
        rel = "%s-%d.md" % (base, ordinal)
        ordinal += 1
    return rel


def note_part(persona, unit_name, path, today):
    skill = skill_text()
    lines = [
        "# Your critique note",
        "",
        "Write your note at `%s`. Create `design/critique/` if it does not "
        "exist. Its frontmatter:" % path,
        "",
        "```yaml",
        "persona: %s" % persona,
        "framework: %s" % framework_of(persona, skill),
        "date: %s" % today,
        "unit: %s" % unit_name,
        "status: open",
        "```",
        "",
        "The note's path and shape, as `game-critique` defines them:",
        "",
        note_shape(skill),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def resolve_unit(cwd, unit):
    """``(type, slug or section name)`` for the ``--unit`` argument."""
    norm = unit.replace("\\", "/")
    if norm.startswith("./"):
        norm = norm[2:]
    for kind, directory in (("mechanic", "mechanics"), ("pillar", "pillars")):
        match = re.match(r"^design/%s/([^/]+)\.md$" % directory, norm)
        if match:
            if not os.path.isfile(os.path.join(cwd, "design", directory, match.group(1) + ".md")):
                raise Refusal("%s does not exist." % norm)
            return kind, match.group(1)
    if norm.endswith(".md"):
        raise Refusal(
            "`%s` is not a unit: a unit is `design/pillars/<slug>.md`, "
            "`design/mechanics/<slug>.md`, or the heading of a section of "
            "`design/gdd.md`." % unit
        )
    return "gdd", unit


def build(cwd, persona, unit, today):
    """The whole dispatch prompt, and the note path it names."""
    persona_path = os.path.join(_SKILL_DIR, "references", persona + ".md")
    if not os.path.isfile(persona_path):
        known = list_slugs(os.path.join(_SKILL_DIR, "references"))
        raise Refusal(
            "No persona named `%s`; the personas are %s."
            % (persona, ", ".join("`%s`" % k for k in known))
        )
    root = os.path.join(cwd, "design")
    kind, ident = resolve_unit(cwd, unit)
    if kind == "mechanic":
        unit_name, unit_slug = "design/mechanics/%s.md" % ident, ident
        sections = mechanic_payload(root, ident)
    elif kind == "pillar":
        unit_name, unit_slug = "design/pillars/%s.md" % ident, ident
        sections = pillar_payload(root, ident)
    else:
        heading, sections = gdd_payload(root, ident)
        unit_name, unit_slug = heading, heading_slug(heading)

    path = note_path(cwd, today, persona, unit_slug)
    parts = [
        read_text(persona_path).rstrip("\n"),
        "---",
        "# Your dispatch\n\nEverything below is the material `game-critique` "
        "carried for this pass, and this file is your whole brief. Each "
        "section is labelled; a section with nothing in it says `none` under "
        "its own label.",
    ]
    parts.extend(sections)
    parts.extend(["---", note_part(persona, unit_name, path, today)])
    return "\n\n".join(parts) + "\n", path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Write one critic's whole dispatch prompt to a file in the OS temp "
            "directory, and print its path and line count. Run from the "
            "project root."
        )
    )
    parser.add_argument("--persona", required=True, help="a persona name from the persona table")
    parser.add_argument(
        "--unit",
        required=True,
        help="design/pillars/<slug>.md, design/mechanics/<slug>.md, or a design/gdd.md section heading",
    )
    args = parser.parse_args(argv)

    cwd = os.getcwd()
    today = datetime.date.today().isoformat()
    try:
        prompt, path = build(cwd, args.persona, args.unit, today)
    except (Refusal, InvalidInput) as exc:
        sys.stderr.write("%s\n" % exc)
        return 1

    slug = heading_slug(os.path.basename(path)[:-3])
    handle, out_path = tempfile.mkstemp(prefix="skywright-critique-%s-" % slug, suffix=".md")
    with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
        out.write(prompt)
    sys.stdout.write("%s (%d lines)\n" % (out_path, prompt.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
