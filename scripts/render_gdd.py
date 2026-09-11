#!/usr/bin/env python3
"""Render a game project's GDD from the structured records under ``design/``.

Reads the six inputs the ``game-gdd`` skill names (concept statement, pillar
records, mechanic entries, the economy graph, the differentiation statement,
technical decision records) and writes three files into the *consuming*
project's ``design/`` directory:

    design/gdd.md    the machine-readable render
    design/gdd.html  the human-readable render
    design/gdd.css   seeded once from <script dir>/../templates/default.css

Invalid input blocks the whole render: nothing is written, one message goes to
stderr naming the failing record, the rule it fails, and the upstream skill
that fixes it, and the exit code is non-zero.

Stdlib only. Deterministic: byte-identical output for byte-identical input.
"""

import argparse
import os
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------


class InvalidInput(Exception):
    """One record fails one rule. Carries the whole stderr message."""


# ---------------------------------------------------------------------------
# Frontmatter parsing
#
# Hand-rolled against the shapes the other five skills define -- never a
# general-purpose YAML parser. Handles: ``key: value``, ``key: [a, b]``, block
# lists, lists of maps with nested keys, nested block maps, single-line flow
# mappings ``{ k: v, ... }``, and double/single-quoted scalars.
# ---------------------------------------------------------------------------

_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*:(\s|$)")


def split_frontmatter(text, path, skill):
    """Return ``(frontmatter_text_or_None, body_text)``."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    raise InvalidInput(
        "%s: the frontmatter block opens with `---` but is never closed by a "
        "matching `---` line; fix it with `%s`." % (path, skill)
    )


def _tokenize(text):
    """Return ``[(indent, stripped_text, lineno)]``, dropping blanks/comments."""
    out = []
    for lineno, raw in enumerate(text.split("\n"), start=1):
        if not raw.strip():
            continue
        if raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        out.append((indent, raw.strip(), lineno))
    return out


def parse_frontmatter(text, path, skill):
    """Parse a frontmatter block into a dict of str / list / dict values."""
    toks = _tokenize(text)
    if not toks:
        return {}
    try:
        value, idx = _parse_mapping(toks, 0, toks[0][0])
    except _ParseError as exc:
        raise InvalidInput(
            "%s: frontmatter could not be parsed (line %d: `%s`); fix it with "
            "`%s`." % (path, exc.lineno, exc.text, skill)
        )
    if idx != len(toks):
        indent, snippet, lineno = toks[idx]
        raise InvalidInput(
            "%s: frontmatter could not be parsed (line %d: `%s`); fix it with "
            "`%s`." % (path, lineno, snippet, skill)
        )
    return value


class _ParseError(Exception):
    def __init__(self, lineno, text):
        Exception.__init__(self, text)
        self.lineno = lineno
        self.text = text


def _parse_mapping(toks, idx, indent):
    result = {}
    while idx < len(toks):
        ind, text, lineno = toks[idx]
        if ind < indent:
            break
        if text.startswith("-"):
            break
        if ind > indent:
            raise _ParseError(lineno, text)
        if not _KEY_RE.match(text):
            raise _ParseError(lineno, text)
        key, _, rest = text.partition(":")
        key = key.strip()
        rest = rest.strip()
        idx += 1
        if rest:
            result[key] = parse_scalar(rest)
            continue
        if idx < len(toks) and toks[idx][0] > ind:
            child_ind = toks[idx][0]
            if toks[idx][1].startswith("-"):
                result[key], idx = _parse_sequence(toks, idx, child_ind)
            else:
                result[key], idx = _parse_mapping(toks, idx, child_ind)
        else:
            result[key] = ""
    return result, idx


def _parse_sequence(toks, idx, indent):
    items = []
    while idx < len(toks):
        ind, text, lineno = toks[idx]
        if ind < indent or not text.startswith("-"):
            break
        if ind > indent:
            raise _ParseError(lineno, text)
        body = text[1:]
        stripped = body.lstrip(" ")
        item_indent = ind + 1 + (len(body) - len(stripped))
        if stripped.startswith("{"):
            items.append(parse_flow_mapping(stripped, lineno))
            idx += 1
        elif _KEY_RE.match(stripped):
            sub = [(item_indent, stripped, lineno)] + toks[idx + 1:]
            value, consumed = _parse_mapping(sub, 0, item_indent)
            items.append(value)
            idx += consumed
        else:
            items.append(parse_scalar(stripped))
            idx += 1
    return items, idx


def parse_flow_mapping(text, lineno=0):
    """Parse a single-line ``{ k: v, ... }`` flow mapping."""
    inner = text.strip()
    if not (inner.startswith("{") and inner.endswith("}")):
        raise _ParseError(lineno, text)
    inner = inner[1:-1]
    result = {}
    for part in _split_top_level(inner):
        if not part:
            continue
        key, sep, value = part.partition(":")
        if not sep:
            raise _ParseError(lineno, text)
        result[key.strip()] = parse_scalar(value.strip())
    return result


def _split_top_level(text):
    parts = []
    buf = []
    depth = 0
    quote = None
    for ch in text:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_scalar(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        return [parse_scalar(p) for p in _split_top_level(text[1:-1]) if p]
    return text


def as_list(value):
    """Coerce a frontmatter value to a list of strings."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [v for v in value if v != ""]
    if isinstance(value, dict):
        return []
    return [value]


def as_text(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return "; ".join("%s %s" % (k, as_text(v)) for k, v in value.items())
    return "" if value is None else str(value)


# ---------------------------------------------------------------------------
# Body helpers
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
_ATX_RE = re.compile(r"^(#{1,6})(\s+.*)$")


def trim_body(text):
    """Strip leading/trailing blank lines; normalise line endings."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip("\n").rstrip()


def demote_headings(body, delta):
    """Demote every ATX heading outside a fenced code block by ``delta``."""
    if delta <= 0:
        return body
    out = []
    in_fence = False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        match = _ATX_RE.match(line)
        if match:
            level = min(6, len(match.group(1)) + delta)
            out.append("#" * level + match.group(2))
        else:
            out.append(line)
    return "\n".join(out)


def split_sections(body):
    """Split a body into ``{heading_text: section_body}`` on ``## `` headings.

    Preserves first-seen order; deeper headings stay inside their section.
    """
    sections = {}
    order = []
    current = None
    buf = []
    in_fence = False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
        if not in_fence:
            match = re.match(r"^##(?!#)\s*(.*)$", line)
            if match:
                if current is not None:
                    sections[current] = trim_body("\n".join(buf))
                current = match.group(1).strip()
                if current not in order:
                    order.append(current)
                buf = []
                continue
        if current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = trim_body("\n".join(buf))
    return sections, order


# ---------------------------------------------------------------------------
# Loading the six inputs
# ---------------------------------------------------------------------------


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().replace("\r\n", "\n").replace("\r", "\n")


def list_md(directory):
    """Every ``*.md`` file in ``directory``, sorted by slug."""
    if not os.path.isdir(directory):
        return []
    names = [n for n in os.listdir(directory) if n.endswith(".md")]
    return sorted(names, key=lambda n: n[:-3])


def load_record(path, rel, skill):
    text = read_text(path)
    fm_text, body = split_frontmatter(text, rel, skill)
    fields = parse_frontmatter(fm_text, rel, skill) if fm_text is not None else {}
    return fields, trim_body(body)


def load_design(root):
    """Read every input under ``root``. Raises InvalidInput; writes nothing."""
    data = {
        "concept": None,
        "pillars": [],
        "candidates": [],
        "mechanics": [],
        "economy": None,
        "comp": None,
        "tech_live": [],
        "tech_superseded": [],
    }

    concept_path = os.path.join(root, "concept.md")
    if os.path.isfile(concept_path):
        fields, body = load_record(concept_path, "design/concept.md", "game-pillars")
        data["concept"] = {"title": as_text(fields.get("title", "")), "body": body}

    pillars_dir = os.path.join(root, "pillars")
    for name in list_md(pillars_dir):
        slug = name[:-3]
        rel = "design/pillars/%s" % name
        fields, body = load_record(os.path.join(pillars_dir, name), rel, "game-pillars")
        record = {
            "slug": slug,
            "rel": rel,
            "title": as_text(fields.get("title", "")) or slug,
            "status": as_text(fields.get("status", "")),
            "body": body,
        }
        if record["status"] == "approved":
            data["pillars"].append(record)
        elif record["status"] == "candidate":
            data["candidates"].append(record)

    mechanics_dir = os.path.join(root, "mechanics")
    for name in list_md(mechanics_dir):
        slug = name[:-3]
        rel = "design/mechanics/%s" % name
        fields, body = load_record(
            os.path.join(mechanics_dir, name), rel, "game-mechanics"
        )
        parent = as_text(fields.get("parent", "")).strip()
        data["mechanics"].append(
            {
                "slug": slug,
                "rel": rel,
                "title": as_text(fields.get("title", "")) or slug,
                "parent": "" if parent in ("", "none") else parent,
                "children": [c for c in as_list(fields.get("children")) if c != "none"],
                "body": body,
            }
        )

    economy_path = os.path.join(root, "economy.md")
    if os.path.isfile(economy_path):
        data["economy"] = load_economy(economy_path)

    comp_path = os.path.join(root, "comp-analysis.md")
    if os.path.isfile(comp_path):
        _, body = load_record(comp_path, "design/comp-analysis.md", "game-comp-analysis")
        data["comp"] = {"body": body}

    tech_dir = os.path.join(root, "tech")
    for name in list_md(tech_dir):
        slug = name[:-3]
        rel = "design/tech/%s" % name
        fields, body = load_record(os.path.join(tech_dir, name), rel, "game-tech")
        record = {
            "slug": slug,
            "rel": rel,
            "title": as_text(fields.get("title", "")) or slug,
            "status": as_text(fields.get("status", "")).strip(),
            "category": as_text(fields.get("category", "")).strip(),
            "scope": as_text(fields.get("scope", "")).strip(),
            "drivers": as_list(fields.get("drivers")),
            "superseded_by": as_text(fields.get("superseded_by", "")).strip(),
            "body": body,
            "headings": set(),
        }
        sections, _ = split_sections(body)
        record["headings"] = set(sections.keys())
        validate_tech(record)
        if record["status"] == "superseded":
            data["tech_superseded"].append(record)
        else:
            data["tech_live"].append(record)

    return data


def load_economy(path):
    rel = "design/economy.md"
    text = read_text(path)
    fm_text, body = split_frontmatter(text, rel, "game-mechanics")
    if fm_text is None:
        raise InvalidInput(
            "design/economy.md: the file has no `---` frontmatter block, so it "
            "declares no `nodes` or `connections`; fix it with `game-mechanics`."
        )
    check_flow_style(fm_text)
    fields = parse_frontmatter(fm_text, rel, "game-mechanics")

    nodes = []
    for entry in as_list(fields.get("nodes")):
        if not isinstance(entry, dict):
            raise InvalidInput(
                "design/economy.md: node entry `%s` is not a mapping of fields; "
                "fix it with `game-mechanics`." % as_text(entry)
            )
        nodes.append(entry)

    families = []
    for entry in as_list(fields.get("families")):
        if not isinstance(entry, dict):
            raise InvalidInput(
                "design/economy.md: family entry `%s` is not a mapping of "
                "fields; fix it with `game-mechanics`." % as_text(entry)
            )
        families.append(entry)

    connections = []
    for entry in as_list(fields.get("connections")):
        if not isinstance(entry, dict):
            raise InvalidInput(
                "design/economy.md: connection entry `%s` is not a mapping of "
                "fields; fix it with `game-mechanics`." % as_text(entry)
            )
        connections.append(entry)

    sections, order = split_sections(trim_body(body))
    economy = {
        "nodes": nodes,
        "families": families,
        "connections": connections,
        "sections": sections,
        "section_order": order,
    }
    validate_economy(economy)
    return economy


def check_flow_style(fm_text):
    """Every ``connections:`` entry must be a single-line flow mapping."""
    lines = fm_text.split("\n")
    in_connections = False
    conn_indent = 0
    for raw in lines:
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if not in_connections:
            if indent == 0 and re.match(r"^connections:\s*$", stripped):
                in_connections = True
                conn_indent = None
            continue
        if indent == 0:
            in_connections = False
            continue
        if stripped.startswith("-"):
            if conn_indent is None:
                conn_indent = indent
            if indent != conn_indent:
                continue
            body = stripped[1:].strip()
            if not (body.startswith("{") and body.endswith("}")):
                raise InvalidInput(
                    "design/economy.md: connection entry `- %s` is written as a "
                    "block mapping, not the single-line `{ ... }` flow style "
                    "every connection requires; fix it with `game-mechanics`."
                    % body
                )


def family_name(family):
    for key in ("family", "name"):
        if key in family and family[key]:
            return as_text(family[key]).strip()
    return ""


def conn_repr(conn):
    """A readable rendering of a connection entry, for an error message."""
    parts = ["%s: %s" % (k, as_text(v)) for k, v in conn.items()]
    return "{ %s }" % ", ".join(parts)


def validate_economy(economy):
    node_ids = []
    for node in economy["nodes"]:
        node_id = as_text(node.get("id", "")).strip()
        if not node_id:
            raise InvalidInput(
                "design/economy.md: node `%s` has no `id` — a node with no id "
                "cannot be referenced; fix it with `game-mechanics`."
                % conn_repr(node)
            )
        node_ids.append(node_id)
    node_set = set(node_ids)

    family_names = []
    for family in economy["families"]:
        fname = family_name(family)
        if not fname:
            raise InvalidInput(
                "design/economy.md: family `%s` has no `family` name — a family "
                "with no name cannot be referenced; fix it with "
                "`game-mechanics`." % conn_repr(family)
            )
        family_names.append(fname)
    family_set = set(family_names)

    for family in economy["families"]:
        fname = family_name(family)
        for member in as_list(family.get("members")):
            if member not in node_set:
                raise InvalidInput(
                    "design/economy.md: family `@%s` lists member `%s`, which "
                    "resolves to no declared node; a reference that resolves to "
                    "nothing is invalid; fix it with `game-mechanics`."
                    % (fname, member)
                )

    conn_ids = []
    for conn in economy["connections"]:
        conn_id = as_text(conn.get("id", "")).strip()
        if not conn_id:
            raise InvalidInput(
                "design/economy.md: connection `%s` has no `id` — a connection "
                "with no id is invalid; fix it with `game-mechanics`."
                % conn_repr(conn)
            )
        conn_ids.append(conn_id)
    conn_set = set(conn_ids)

    for conn in economy["connections"]:
        conn_id = as_text(conn.get("id", "")).strip()
        for end in ("from", "to"):
            ref = as_text(conn.get(end, "")).strip()
            if not ref:
                raise InvalidInput(
                    "design/economy.md: connection `%s` has no `%s` — a "
                    "connection must name both of its ends; fix it with "
                    "`game-mechanics`." % (conn_id, end)
                )
            if not ref_resolves(ref, node_set, family_set, conn_set):
                raise InvalidInput(
                    "design/economy.md: connection `%s` has `%s: %s`, which "
                    "resolves to nothing; a reference that resolves to nothing "
                    "is invalid; fix it with `game-mechanics`."
                    % (conn_id, end, ref)
                )

    for heading in economy["section_order"]:
        if "/" in heading:
            raise InvalidInput(
                "design/economy.md: body heading `## %s` joins two ids with `/`; "
                "a heading must name exactly one node id, family `@<name>`, or "
                "member id; fix it with `game-mechanics`." % heading
            )
        if heading.startswith("@"):
            if heading[1:] not in family_set:
                raise InvalidInput(
                    "design/economy.md: body heading `## %s` resolves to no "
                    "declared family; a reference that resolves to nothing is "
                    "invalid; fix it with `game-mechanics`." % heading
                )
        elif heading not in node_set:
            raise InvalidInput(
                "design/economy.md: body heading `## %s` resolves to no node, "
                "family, or member; a reference that resolves to nothing is "
                "invalid; fix it with `game-mechanics`." % heading
            )

    economy["node_ids"] = node_ids
    economy["family_names"] = family_names
    economy["conn_ids"] = conn_ids


def ref_resolves(ref, node_set, family_set, conn_set):
    if ref.startswith("@"):
        return ref[1:] in family_set
    if ref.startswith("#"):
        return ref[1:] in conn_set
    return ref in node_set


TECH_STATUSES = ("open", "accepted", "superseded")
TECH_SCOPES = ("contained", "cross-cutting")


def validate_tech(record):
    rel = record["rel"]
    if record["status"] not in TECH_STATUSES:
        if not record["status"]:
            raise InvalidInput(
                "%s: `status` is missing; it must be exactly one of the closed "
                "set (open, accepted, superseded); fix it with `game-tech`." % rel
            )
        raise InvalidInput(
            "%s: `status: %s` is outside the closed set (open, accepted, "
            "superseded); fix it with `game-tech`." % (rel, record["status"])
        )
    if record["scope"] not in TECH_SCOPES:
        if not record["scope"]:
            raise InvalidInput(
                "%s: `scope` is missing; it must be exactly one of the closed "
                "set (contained, cross-cutting); fix it with `game-tech`." % rel
            )
        raise InvalidInput(
            "%s: `scope: %s` is outside the closed set (contained, "
            "cross-cutting); fix it with `game-tech`." % (rel, record["scope"])
        )
    required = [("Context", "every record")]
    if record["status"] in ("accepted", "superseded"):
        required.append(("Decision", "`status: %s`" % record["status"]))
        required.append(("Consequences", "`status: %s`" % record["status"]))
    if record["scope"] == "cross-cutting":
        required.append(("Options considered", "`scope: cross-cutting`"))
    for heading, because in required:
        if heading not in record["headings"]:
            raise InvalidInput(
                "%s: %s requires a `## %s` body heading, which this record does "
                "not have; fix it with `game-tech`." % (rel, because, heading)
            )
    if record["status"] == "superseded" and not record["superseded_by"]:
        raise InvalidInput(
            "%s: `status: superseded` requires a `superseded_by` field naming "
            "the replacing record, which this record does not have; fix it with "
            "`game-tech`." % rel
        )


# ---------------------------------------------------------------------------
# Shared render data
# ---------------------------------------------------------------------------


def build_context(data):
    """Anchor targets and reference resolution shared by both renders."""
    economy = data["economy"]
    ctx = {
        "pillars": set(p["slug"] for p in data["pillars"]),
        "mechanics": set(m["slug"] for m in data["mechanics"]),
        "tech": set(t["slug"] for t in data["tech_live"]),
        "nodes": set(economy["node_ids"]) if economy else set(),
        "families": set(economy["family_names"]) if economy else set(),
        "connections": set(economy["conn_ids"]) if economy else set(),
        "has_concept": data["concept"] is not None,
        "has_comp": data["comp"] is not None,
    }
    return ctx


def anchor_for_economy_ref(ref, ctx):
    if ref.startswith("@"):
        if ref[1:] in ctx["families"]:
            return "#family-%s" % ref[1:]
    elif ref.startswith("#"):
        if ref[1:] in ctx["connections"]:
            return "#connection-%s" % ref[1:]
    elif ref in ctx["nodes"]:
        return "#node-%s" % ref
    return None


def anchor_for_driver(ref, ctx):
    if ref == "design/concept.md" and ctx["has_concept"]:
        return "#concept"
    if ref == "design/comp-analysis.md" and ctx["has_comp"]:
        return "#competitive-differentiation"
    match = re.match(r"^design/pillars/(.+)\.md$", ref)
    if match and match.group(1) in ctx["pillars"]:
        return "#pillar-%s" % match.group(1)
    match = re.match(r"^design/mechanics/(.+)\.md$", ref)
    if match and match.group(1) in ctx["mechanics"]:
        return "#mechanic-%s" % match.group(1)
    match = re.match(r"^design/tech/(.+)\.md$", ref)
    if match and match.group(1) in ctx["tech"]:
        return "#tech-%s" % match.group(1)
    if ref.startswith("economy:"):
        return anchor_for_economy_ref(ref[len("economy:"):].strip(), ctx)
    return None


def is_declaration(conn):
    return (
        as_text(conn.get("from", "")).strip().startswith("@")
        or as_text(conn.get("to", "")).strip().startswith("@")
    )


def declaration_family(conn):
    for end in ("from", "to"):
        ref = as_text(conn.get(end, "")).strip()
        if ref.startswith("@"):
            return ref[1:]
    return ""


def value_progression_parts(node):
    """Return the four ``value_progression`` sub-fields, or None if absent."""
    raw = node.get("value_progression")
    if raw is None or raw == "" or raw == []:
        return None
    if not isinstance(raw, dict):
        return None
    parts = []
    for key in ("model", "coefficients", "domain", "fit"):
        value = raw.get(key)
        text = as_text(value).strip() if value is not None else ""
        parts.append((key, text if text else "none recorded"))
    return parts


def connection_meta(conn):
    """``(kind, subtype, resource, rate)`` as stripped strings."""
    return (
        as_text(conn.get("kind", "")).strip(),
        as_text(conn.get("subtype", "")).strip(),
        as_text(conn.get("resource", "")).strip(),
        as_text(conn.get("rate", "")).strip(),
    )


# ---------------------------------------------------------------------------
# Fixed text
# ---------------------------------------------------------------------------

ABSENT_CONCEPT = (
    "No concept statement has been recorded yet — `design/concept.md` does not "
    "exist. Run `game-pillars` to write one."
)
ABSENT_PILLARS = (
    "No approved design pillar has been recorded yet — `design/pillars/` holds "
    "no record with `status: approved`. Run `game-pillars` to write one."
)
ABSENT_MECHANICS = (
    "No mechanic entry has been recorded yet — `design/mechanics/` holds no "
    "records. Run `game-mechanics` to write one."
)
ABSENT_ECONOMY = (
    "No economy graph has been recorded yet — `design/economy.md` does not "
    "exist. Run `game-mechanics` to write one."
)
ABSENT_COMP = (
    "No differentiation statement has been recorded yet — "
    "`design/comp-analysis.md` does not exist. Run `game-comp-analysis` to "
    "write one."
)
ABSENT_TECH = (
    "No open or accepted technical decision has been recorded yet — "
    "`design/tech/` holds no record with `status: open` or `status: accepted`. "
    "Run `game-tech` to write one."
)

SUPPORTING_INTRO = (
    "A GDD practice commonly names nine supporting-document types. This file "
    "renders the core GDD — the ninth — as a document of its own, and folds "
    "one more into it. The remaining seven are named here, with the reason "
    "each is absent, so a reader can tell a deliberate omission from a "
    "forgotten one."
)

SUPPORTING_DOCS = [
    (
        "Technical Design Document",
        "not absent, and not a separate document: at solo and small-team scale "
        "technical design folds into the GDD, so it renders above as "
        "`## Technical Design`, from the technical decision records `game-tech` "
        "writes, rather than as a standalone `design/tdd.md`.",
    ),
    (
        "Concept Document",
        "out of scope for this skillset, not merely undone: the concept "
        "statement `game-pillars` writes already serves this role, and it "
        "renders above as `## Concept`.",
    ),
    (
        "Marketing & Business Plan",
        "out of scope for this skillset: a business concern outside this "
        "skillset's design-quality scope.",
    ),
    (
        "Art Bible",
        "absent for a grounding reason: the schema this skillset builds — "
        "pillars, mechanic entries, the economy graph, technical decision "
        "records — carries no visual data to render one from.",
    ),
    (
        "Story/Narrative Bible",
        "absent for a grounding reason: the same schema carries no narrative "
        "data to render one from.",
    ),
    (
        "Level Design Document",
        "absent for a grounding reason: the same schema carries no level or "
        "spatial data to render one from.",
    ),
    (
        "Sound Design Document",
        "absent for a grounding reason: the same schema carries no audio data "
        "to render one from.",
    ),
    (
        "Test Plan",
        "absent for a grounding reason: the same schema carries no QA data to "
        "render one from.",
    ),
]

SUPPORTING_CLOSING = (
    "Each of the five grounding-reason documents above is a documented future "
    "extension, not a silent omission — rendering one without the data it "
    "needs would mean inventing content rather than deriving it."
)

HEADER_NOTE = (
    "Rendered by `game-gdd` from the structured records under `design/`. Edit "
    "those records and re-render; edits made here do not survive the next "
    "render."
)


def candidate_line(count):
    if count == 1:
        return (
            "*1 candidate pillar proposed by `game-comp-analysis` awaits review "
            "— approve or discard it with `game-pillars`.*"
        )
    return (
        "*%d candidate pillars proposed by `game-comp-analysis` await review — "
        "approve or discard them with `game-pillars`.*" % count
    )


def candidate_text(count):
    """The same sentence without the markdown italics, for HTML."""
    return candidate_line(count).strip("*")


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------


def ref_code(ref):
    return "`%s`" % ref


def code_list(refs):
    return ", ".join(ref_code(r) for r in refs)


def build_markdown(data):
    blocks = []
    concept = data["concept"]
    title = concept["title"].strip() if concept else ""
    if title:
        blocks.append("# %s — Game Design Document" % title)
    else:
        blocks.append("# Game Design Document")

    blocks.extend(md_concept(data))
    blocks.extend(md_pillars(data))
    blocks.extend(md_mechanics(data))
    blocks.extend(md_economy(data))
    blocks.extend(md_comp(data))
    blocks.extend(md_tech(data))
    blocks.extend(md_supporting())

    text = "\n\n".join(b for b in blocks if b is not None and b != "")
    return text.rstrip("\n") + "\n"


def md_caption(text):
    return "*Source: %s*" % text


def md_concept(data):
    out = ["## Concept"]
    concept = data["concept"]
    if concept is None:
        out.append(ABSENT_CONCEPT)
        return out
    out.append(md_caption("`design/concept.md`"))
    if concept["body"]:
        out.append(demote_headings(concept["body"], 1))
    return out


def md_pillars(data):
    out = ["## Design Pillars"]
    pillars = data["pillars"]
    if not pillars:
        out.append(ABSENT_PILLARS)
    for pillar in pillars:
        out.append("### %s" % pillar["title"])
        out.append(md_caption("`%s`" % pillar["rel"]))
        if pillar["body"]:
            out.append(demote_headings(pillar["body"], 2))
    if data["candidates"]:
        out.append(candidate_line(len(data["candidates"])))
    return out


def md_mechanics(data):
    out = ["## Mechanics"]
    mechanics = data["mechanics"]
    if not mechanics:
        out.append(ABSENT_MECHANICS)
        return out
    for mech in mechanics:
        out.append("### %s" % mech["title"])
        out.append(md_caption("`%s`" % mech["rel"]))
        parent = ref_code(mech["parent"]) if mech["parent"] else "none"
        children = code_list(mech["children"]) if mech["children"] else "none"
        out.append("- Parent: %s\n- Children: %s" % (parent, children))
        if mech["body"]:
            out.append(demote_headings(mech["body"], 2))
    return out


def md_economy(data):
    out = ["## Economy"]
    economy = data["economy"]
    if economy is None:
        out.append(ABSENT_ECONOMY)
        return out
    out.append(md_caption("`design/economy.md`"))

    out.append("### Nodes")
    if not economy["nodes"]:
        out.append("No nodes are declared.")
    for node in economy["nodes"]:
        node_id = as_text(node.get("id", "")).strip()
        out.append("#### %s" % node_id)
        out.append(md_caption("`design/economy.md`, node `%s`" % node_id))
        fields = ["- Type: %s" % (as_text(node.get("type", "")).strip() or "none recorded")]
        parts = value_progression_parts(node)
        if parts is None:
            fields.append("- Value progression: none recorded")
        else:
            fields.append(
                "- Value progression: %s"
                % "; ".join("%s %s" % (k, v) for k, v in parts)
            )
        out.append("\n".join(fields))
        notes = economy["sections"].get(node_id)
        if notes:
            out.append(demote_headings(notes, 3))

    out.append("### Families")
    if not economy["families"]:
        out.append("No families are declared.")
    for family in economy["families"]:
        fname = family_name(family)
        out.append("#### @%s" % fname)
        out.append(md_caption("`design/economy.md`, family `@%s`" % fname))
        members = as_list(family.get("members"))
        fields = [
            "- Type: %s" % (as_text(family.get("type", "")).strip() or "none recorded"),
            "- Members: %s" % (code_list(members) if members else "none recorded"),
        ]
        out.append("\n".join(fields))
        notes = economy["sections"].get("@%s" % fname)
        if notes:
            out.append(demote_headings(notes, 3))
        declarations = [
            c for c in economy["connections"]
            if is_declaration(c) and declaration_family(c) == fname
        ]
        if not declarations:
            out.append("No declarations are written over this family.")
            continue
        out.append("Declarations over this family:")
        bullets = []
        for conn in declarations:
            bullets.append("- %s" % declaration_sentence(conn, len(members)))
        out.append("\n".join(bullets))

    out.append("### Connections")
    plain = [c for c in economy["connections"] if not is_declaration(c)]
    if not plain:
        out.append("No connections are declared.")
    for conn in plain:
        conn_id = as_text(conn.get("id", "")).strip()
        kind, subtype, resource, rate = connection_meta(conn)
        out.append("#### %s" % conn_id)
        out.append(md_caption("`design/economy.md`, connection `%s`" % conn_id))
        fields = [
            "- From: %s" % ref_code(as_text(conn.get("from", "")).strip()),
            "- To: %s" % ref_code(as_text(conn.get("to", "")).strip()),
            "- Kind: %s" % (kind or "none recorded"),
        ]
        if kind == "state":
            fields.append("- Subtype: %s" % (subtype or "none recorded"))
        fields.append("- Rate: %s" % (rate or "none recorded"))
        if resource:
            fields.append("- Resource: %s" % resource)
        out.append("\n".join(fields))
    return out


def declaration_sentence(conn, member_count):
    conn_id = as_text(conn.get("id", "")).strip()
    kind, subtype, resource, rate = connection_meta(conn)
    meta = ["kind: %s" % (kind or "none recorded")]
    if subtype:
        meta.append("subtype: %s" % subtype)
    if resource:
        meta.append("resource: %s" % resource)
    if rate:
        meta.append("rate: %s" % rate)
    applies = as_text(conn.get("applies", "")).strip()
    if applies == "one-of-family":
        expansion = (
            "expands to %d connections, one-of-family: exactly one live at a "
            "time" % member_count
        )
    else:
        expansion = (
            "expands to %d connections, all live simultaneously" % member_count
        )
    return "**%s** — %s → %s, %s; %s (expanded ids follow `game-mechanics`' derived-id rule)" % (
        conn_id,
        ref_code(as_text(conn.get("from", "")).strip()),
        ref_code(as_text(conn.get("to", "")).strip()),
        ", ".join(meta),
        expansion,
    )


def md_comp(data):
    out = ["## Competitive Differentiation"]
    comp = data["comp"]
    if comp is None:
        out.append(ABSENT_COMP)
        return out
    out.append(md_caption("`design/comp-analysis.md`"))
    if comp["body"]:
        out.append(demote_headings(comp["body"], 1))
    return out


def md_tech(data):
    out = ["## Technical Design"]
    live = data["tech_live"]
    if not live:
        out.append(ABSENT_TECH)
    for record in live:
        out.append("### %s" % record["title"])
        out.append(md_caption("`%s`" % record["rel"]))
        if record["status"] == "open":
            out.append("**Open — not yet decided.**")
        drivers = record["drivers"]
        fields = [
            "- Status: %s" % record["status"],
            "- Category: %s" % (record["category"] or "none recorded"),
            "- Scope: %s" % record["scope"],
            "- Drivers: %s" % (code_list(drivers) if drivers else "none"),
        ]
        out.append("\n".join(fields))
        if record["body"]:
            out.append(demote_headings(record["body"], 2))
    for record in data["tech_superseded"]:
        out.append(
            "*`%s` superseded by `%s`.*" % (record["slug"], record["superseded_by"])
        )
    return out


def md_supporting():
    out = ["## Supporting Documents Not Rendered", SUPPORTING_INTRO]
    bullets = []
    for name, reason in SUPPORTING_DOCS:
        bullets.append("- **%s** — %s" % (name, reason))
    out.append("\n".join(bullets))
    out.append(SUPPORTING_CLOSING)
    return out


# ---------------------------------------------------------------------------
# Markdown -> HTML, for record bodies
# ---------------------------------------------------------------------------


def h(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
_LINK_RE = re.compile(r"\[([^\[\]]*)\]\(([^()\s]*)\)")
_STRONG_RE = re.compile(r"\*\*(.+?)\*\*")
_EM_STAR_RE = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
_EM_UNDER_RE = re.compile(r"(?<![\w_])_([^_\n]+)_(?![\w_])")


def inline(text, ctx):
    """Convert inline markdown in ``text`` to HTML, escaping everything."""
    out = []
    pos = 0
    for match in _CODE_SPAN_RE.finditer(text):
        out.append(_inline_plain(text[pos:match.start()], ctx))
        out.append("<code>%s</code>" % h(match.group(1)))
        pos = match.end()
    out.append(_inline_plain(text[pos:], ctx))
    return "".join(out)


def _inline_plain(text, ctx):
    if not text:
        return ""
    escaped = h(text)

    def wiki(match):
        slug = match.group(1).strip()
        if slug in ctx["pillars"]:
            return '<a href="#pillar-%s">%s</a>' % (slug, slug)
        if slug in ctx["mechanics"]:
            return '<a href="#mechanic-%s">%s</a>' % (slug, slug)
        return "<code>%s</code>" % slug

    escaped = _WIKILINK_RE.sub(wiki, escaped)
    escaped = _LINK_RE.sub(
        lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), escaped
    )
    escaped = _STRONG_RE.sub(lambda m: "<strong>%s</strong>" % m.group(1), escaped)
    escaped = _EM_STAR_RE.sub(lambda m: "<em>%s</em>" % m.group(1), escaped)
    escaped = _EM_UNDER_RE.sub(lambda m: "<em>%s</em>" % m.group(1), escaped)
    return escaped


_HR_RE = re.compile(r"^\s*(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
_BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
_ORDERED_RE = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")


def md_to_html(text, demote, ctx):
    """A pragmatic markdown subset -> HTML. Never raises on arbitrary prose."""
    try:
        return _md_to_html(text, demote, ctx)
    except Exception:  # never let a body break the render
        return ["<p>%s</p>" % inline(text.strip(), ctx)]


def _md_to_html(text, demote, ctx):
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence = _FENCE_RE.match(line)
        if fence:
            i += 1
            buf = []
            while i < n and not _FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1
            out.append("<pre><code>%s</code></pre>" % h("\n".join(buf)))
            continue
        heading = _ATX_RE.match(line)
        if heading:
            level = min(6, len(heading.group(1)) + demote)
            out.append(
                "<h%d>%s</h%d>" % (level, inline(heading.group(2).strip(), ctx), level)
            )
            i += 1
            continue
        if _HR_RE.match(line):
            out.append("<hr>")
            i += 1
            continue
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>")
            out.extend(_indent(_md_to_html("\n".join(buf), demote, ctx), 2))
            out.append("</blockquote>")
            continue
        if (
            "|" in line
            and i + 1 < n
            and "|" in lines[i + 1]
            and _TABLE_SEP_RE.match(lines[i + 1])
        ):
            rows = [line]
            i += 2
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(lines[i])
                i += 1
            out.extend(_render_table(rows, ctx))
            continue
        if _BULLET_RE.match(line) or _ORDERED_RE.match(line):
            items, i = _collect_list(lines, i)
            nodes, _ = _build_list_tree(items, 0, items[0][0])
            if nodes:
                out.extend(_render_list_nodes(nodes, ctx))
            continue
        buf = []
        while i < n and lines[i].strip():
            candidate = lines[i]
            if buf and (
                _ATX_RE.match(candidate)
                or _FENCE_RE.match(candidate)
                or _HR_RE.match(candidate)
                or candidate.lstrip().startswith(">")
                or _BULLET_RE.match(candidate)
                or _ORDERED_RE.match(candidate)
            ):
                break
            buf.append(candidate.strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf), ctx))
    return out


def _indent(lines, pad):
    prefix = " " * pad
    return [prefix + line for line in lines]


def _split_row(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def _render_table(rows, ctx):
    header = _split_row(rows[0])
    body = [_split_row(r) for r in rows[1:]]
    out = ['<div class="table-wrap">', "  <table>", "    <thead>", "      <tr>"]
    for cell in header:
        out.append("        <th>%s</th>" % inline(cell, ctx))
    out.append("      </tr>")
    out.append("    </thead>")
    if body:
        out.append("    <tbody>")
        for row in body:
            out.append("      <tr>")
            for cell in row:
                out.append("        <td>%s</td>" % inline(cell, ctx))
            out.append("      </tr>")
        out.append("    </tbody>")
    out.append("  </table>")
    out.append("</div>")
    return out


def _collect_list(lines, i):
    """Collect one list block as ``[(indent, ordered, [text lines])]``."""
    items = []
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            nxt = i + 1
            while nxt < n and not lines[nxt].strip():
                nxt += 1
            if nxt < n and (_BULLET_RE.match(lines[nxt]) or _ORDERED_RE.match(lines[nxt])):
                i = nxt
                continue
            break
        bullet = _BULLET_RE.match(line)
        ordered = _ORDERED_RE.match(line)
        if bullet or ordered:
            match = ordered or bullet
            items.append((len(match.group(1)), ordered is not None, [match.group(2)]))
            i += 1
            continue
        if items and line.startswith(" "):
            items[-1][2].append(line.strip())
            i += 1
            continue
        break
    return items, i


def _build_list_tree(items, index, indent):
    """Group flat list items into a tree by indentation."""
    nodes = []
    i = index
    while i < len(items):
        item_indent, ordered, content = items[i]
        if item_indent < indent:
            break
        if item_indent > indent:
            children, i = _build_list_tree(items, i, item_indent)
            if nodes:
                nodes[-1]["children"].extend(children)
            continue
        nodes.append({"ordered": ordered, "content": content, "children": []})
        i += 1
    return nodes, i


def _render_list_nodes(nodes, ctx):
    tag = "ol" if nodes[0]["ordered"] else "ul"
    out = ["<%s>" % tag]
    for node in nodes:
        text = inline(" ".join(node["content"]).strip(), ctx)
        if node["children"]:
            out.append("  <li>%s" % text)
            out.extend(_indent(_render_list_nodes(node["children"], ctx), 4))
            out.append("  </li>")
        else:
            out.append("  <li>%s</li>" % text)
    out.append("</%s>" % tag)
    return out


# ---------------------------------------------------------------------------
# HTML render
# ---------------------------------------------------------------------------


class Html(object):
    def __init__(self):
        self.lines = []

    def add(self, pad, text):
        self.lines.append(" " * pad + text)

    def extend(self, pad, lines):
        for line in lines:
            self.lines.append(" " * pad + line)

    def blank(self):
        self.lines.append("")

    def text(self):
        return "\n".join(self.lines).rstrip("\n") + "\n"


def dl_open(out, pad):
    out.add(pad, '<dl class="fields">')


def dl_field(out, pad, label, value_html, unrecorded=False):
    out.add(pad + 2, "<dt>%s</dt>" % h(label))
    cls = ' class="unrecorded"' if unrecorded else ""
    out.add(pad + 2, "<dd%s>%s</dd>" % (cls, value_html))


def dl_close(out, pad):
    out.add(pad, "</dl>")


def linked_code(ref, anchor):
    code = "<code>%s</code>" % h(ref)
    if anchor:
        return '<a href="%s">%s</a>' % (anchor, code)
    return code


def build_html(data, ctx):
    out = Html()
    concept = data["concept"]
    title = concept["title"].strip() if concept else ""
    doc_title = ("%s — Game Design Document" % title) if title else "Game Design Document"

    out.add(0, "<!DOCTYPE html>")
    out.add(0, '<html lang="en">')
    out.add(0, "<head>")
    out.add(0, '<meta charset="utf-8">')
    out.add(0, '<meta name="viewport" content="width=device-width, initial-scale=1">')
    out.add(0, "<title>%s</title>" % h(doc_title))
    out.add(0, '<link rel="stylesheet" href="gdd.css">')
    out.add(0, "</head>")
    out.add(0, "<body>")
    out.add(0, '<div class="gdd-layout">')
    html_toc(out, data)
    out.add(0, '<main class="gdd">')
    out.add(0, '<header class="gdd-header">')
    out.add(2, '<p class="gdd-kicker">Game Design Document</p>')
    out.add(2, "<h1>%s</h1>" % h(title if title else "Game Design Document"))
    out.add(2, '<p class="gdd-note">%s</p>' % inline(HEADER_NOTE, ctx))
    out.add(0, "</header>")
    out.blank()

    html_concept(out, data, ctx)
    out.blank()
    html_pillars(out, data, ctx)
    out.blank()
    html_mechanics(out, data, ctx)
    out.blank()
    html_economy(out, data, ctx)
    out.blank()
    html_comp(out, data, ctx)
    out.blank()
    html_tech(out, data, ctx)
    out.blank()
    html_supporting(out, ctx)

    out.add(0, "</main>")
    out.add(0, "</div>")
    out.add(0, "</body>")
    out.add(0, "</html>")
    return out.text()


def html_toc(out, data):
    out.add(0, '<nav class="toc" aria-label="Table of contents">')
    out.add(2, '<p class="toc-title">Contents</p>')
    out.add(2, '<ol class="toc-list">')
    out.add(4, '<li><a href="#concept">Concept</a></li>')

    _toc_entry(
        out,
        "#design-pillars",
        "Design Pillars",
        [("#pillar-%s" % p["slug"], p["title"]) for p in data["pillars"]],
    )
    _toc_entry(
        out,
        "#mechanics",
        "Mechanics",
        [("#mechanic-%s" % m["slug"], m["title"]) for m in data["mechanics"]],
    )
    _toc_entry(
        out,
        "#economy",
        "Economy",
        [
            ("#economy-nodes", "Nodes"),
            ("#economy-families", "Families"),
            ("#economy-connections", "Connections"),
        ]
        if data["economy"] is not None
        else [],
    )
    out.add(
        4,
        '<li><a href="#competitive-differentiation">Competitive '
        "Differentiation</a></li>",
    )
    _toc_entry(
        out,
        "#technical-design",
        "Technical Design",
        [("#tech-%s" % t["slug"], t["title"]) for t in data["tech_live"]],
    )
    out.add(
        4,
        '<li><a href="#supporting-documents">Supporting Documents Not '
        "Rendered</a></li>",
    )
    out.add(2, "</ol>")
    out.add(0, "</nav>")


def _toc_entry(out, href, label, children):
    if not children:
        out.add(4, '<li><a href="%s">%s</a></li>' % (href, h(label)))
        return
    out.add(4, '<li><a href="%s">%s</a>' % (href, h(label)))
    out.add(6, "<ol>")
    for child_href, child_label in children:
        out.add(8, '<li><a href="%s">%s</a></li>' % (h(child_href), h(child_label)))
    out.add(6, "</ol></li>")


def section_open(out, section_id, classes, source, absent):
    cls = "gdd-section %s" % classes
    if absent:
        cls += " absent"
    out.add(
        0,
        '<section id="%s" class="%s" data-source="%s">'
        % (section_id, cls, h(source)),
    )


def html_body(out, pad, body, demote, ctx):
    out.add(pad, '<div class="body">')
    out.extend(pad + 2, md_to_html(body, demote, ctx))
    out.add(pad, "</div>")


def html_concept(out, data, ctx):
    concept = data["concept"]
    section_open(out, "concept", "concept", "design/concept.md", concept is None)
    out.add(2, "<h2>Concept</h2>")
    if concept is None:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_CONCEPT, ctx))
    else:
        out.add(2, '<p class="source"><code>design/concept.md</code></p>')
        if concept["body"]:
            html_body(out, 2, concept["body"], 1, ctx)
    out.add(0, "</section>")


def html_pillars(out, data, ctx):
    pillars = data["pillars"]
    section_open(out, "design-pillars", "pillars", "design/pillars/", not pillars)
    out.add(2, "<h2>Design Pillars</h2>")
    if not pillars:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_PILLARS, ctx))
    for pillar in pillars:
        out.add(
            2,
            '<article id="pillar-%s" class="record pillar" data-source="%s">'
            % (h(pillar["slug"]), h(pillar["rel"])),
        )
        out.add(4, "<h3>%s</h3>" % h(pillar["title"]))
        out.add(4, '<p class="source"><code>%s</code></p>' % h(pillar["rel"]))
        if pillar["body"]:
            html_body(out, 4, pillar["body"], 2, ctx)
        out.add(2, "</article>")
    if data["candidates"]:
        out.add(
            2,
            '<p class="candidate-note">%s</p>'
            % inline(candidate_text(len(data["candidates"])), ctx),
        )
    out.add(0, "</section>")


def html_mechanics(out, data, ctx):
    mechanics = data["mechanics"]
    section_open(out, "mechanics", "mechanics", "design/mechanics/", not mechanics)
    out.add(2, "<h2>Mechanics</h2>")
    if not mechanics:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_MECHANICS, ctx))
    for mech in mechanics:
        out.add(
            2,
            '<article id="mechanic-%s" class="record mechanic" data-source="%s">'
            % (h(mech["slug"]), h(mech["rel"])),
        )
        out.add(4, "<h3>%s</h3>" % h(mech["title"]))
        out.add(4, '<p class="source"><code>%s</code></p>' % h(mech["rel"]))
        dl_open(out, 4)
        if mech["parent"]:
            anchor = (
                "#mechanic-%s" % mech["parent"]
                if mech["parent"] in ctx["mechanics"]
                else None
            )
            dl_field(out, 4, "Parent", linked_code(mech["parent"], anchor))
        else:
            dl_field(out, 4, "Parent", "none", unrecorded=True)
        if mech["children"]:
            items = []
            for child in mech["children"]:
                anchor = "#mechanic-%s" % child if child in ctx["mechanics"] else None
                items.append(linked_code(child, anchor))
            dl_field(out, 4, "Children", ", ".join(items))
        else:
            dl_field(out, 4, "Children", "none", unrecorded=True)
        dl_close(out, 4)
        if mech["body"]:
            html_body(out, 4, mech["body"], 2, ctx)
        out.add(2, "</article>")
    out.add(0, "</section>")


def html_economy(out, data, ctx):
    economy = data["economy"]
    section_open(out, "economy", "economy", "design/economy.md", economy is None)
    out.add(2, "<h2>Economy</h2>")
    if economy is None:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_ECONOMY, ctx))
        out.add(0, "</section>")
        return
    out.add(2, '<p class="source"><code>design/economy.md</code></p>')

    out.add(2, '<h3 id="economy-nodes">Nodes</h3>')
    if not economy["nodes"]:
        out.add(2, '<p class="absent">No nodes are declared.</p>')
    for node in economy["nodes"]:
        node_id = as_text(node.get("id", "")).strip()
        out.add(
            2,
            '<article id="node-%s" class="record economy-node" '
            'data-source="design/economy.md#%s">' % (h(node_id), h(node_id)),
        )
        out.add(4, "<h4>%s</h4>" % h(node_id))
        out.add(4, '<p class="source">node <code>%s</code></p>' % h(node_id))
        dl_open(out, 4)
        node_type = as_text(node.get("type", "")).strip()
        if node_type:
            dl_field(out, 4, "Type", h(node_type))
        else:
            dl_field(out, 4, "Type", "none recorded", unrecorded=True)
        parts = value_progression_parts(node)
        if parts is None:
            dl_field(out, 4, "Value progression", "none recorded", unrecorded=True)
        else:
            dl_field(
                out,
                4,
                "Value progression",
                h("; ".join("%s %s" % (k, v) for k, v in parts)),
            )
        dl_close(out, 4)
        notes = economy["sections"].get(node_id)
        if notes:
            html_body(out, 4, notes, 3, ctx)
        out.add(2, "</article>")

    out.add(2, '<h3 id="economy-families">Families</h3>')
    if not economy["families"]:
        out.add(2, '<p class="absent">No families are declared.</p>')
    for family in economy["families"]:
        fname = family_name(family)
        out.add(
            2,
            '<article id="family-%s" class="record economy-family" '
            'data-source="design/economy.md#@%s">' % (h(fname), h(fname)),
        )
        out.add(4, "<h4>@%s</h4>" % h(fname))
        out.add(4, '<p class="source">family <code>@%s</code></p>' % h(fname))
        dl_open(out, 4)
        ftype = as_text(family.get("type", "")).strip()
        if ftype:
            dl_field(out, 4, "Type", h(ftype))
        else:
            dl_field(out, 4, "Type", "none recorded", unrecorded=True)
        members = as_list(family.get("members"))
        if members:
            items = []
            for member in members:
                anchor = "#node-%s" % member if member in ctx["nodes"] else None
                items.append(linked_code(member, anchor))
            dl_field(out, 4, "Members", ", ".join(items))
        else:
            dl_field(out, 4, "Members", "none recorded", unrecorded=True)
        dl_close(out, 4)
        notes = economy["sections"].get("@%s" % fname)
        if notes:
            html_body(out, 4, notes, 3, ctx)
        out.add(4, '<p class="declarations-title">Declarations over this family</p>')
        declarations = [
            c for c in economy["connections"]
            if is_declaration(c) and declaration_family(c) == fname
        ]
        if not declarations:
            out.add(
                4,
                '<p class="absent">No declarations are written over this '
                "family.</p>",
            )
        else:
            out.add(4, '<ul class="declarations">')
            for conn in declarations:
                html_declaration(out, 6, conn, len(members), ctx)
            out.add(4, "</ul>")
        out.add(2, "</article>")

    out.add(2, '<h3 id="economy-connections">Connections</h3>')
    plain = [c for c in economy["connections"] if not is_declaration(c)]
    if not plain:
        out.add(2, '<p class="absent">No connections are declared.</p>')
    for conn in plain:
        html_connection(out, conn, ctx)
    out.add(0, "</section>")


def edge_link(ref, ctx):
    anchor = anchor_for_economy_ref(ref, ctx)
    if anchor:
        return '<a href="%s">%s</a>' % (anchor, h(ref))
    return h(ref)


def html_declaration(out, pad, conn, member_count, ctx):
    conn_id = as_text(conn.get("id", "")).strip()
    kind, subtype, resource, rate = connection_meta(conn)
    src = as_text(conn.get("from", "")).strip()
    dst = as_text(conn.get("to", "")).strip()
    meta = ["kind: %s" % (kind or "none recorded")]
    if subtype:
        meta.append("subtype: %s" % subtype)
    if resource:
        meta.append("resource: %s" % resource)
    if rate:
        meta.append("rate: %s" % rate)
    applies = as_text(conn.get("applies", "")).strip()
    if applies == "one-of-family":
        expansion = (
            "expands to %d connections · one-of-family: exactly one live at a "
            "time" % member_count
        )
    else:
        expansion = "expands to %d connections · all live simultaneously" % member_count
    out.add(
        pad,
        '<li id="connection-%s" class="economy-connection declaration" '
        'data-source="design/economy.md#%s">' % (h(conn_id), h(conn_id)),
    )
    out.add(pad + 2, '<code class="conn-id">%s</code>' % h(conn_id))
    out.add(
        pad + 2,
        '<span class="edge">%s → %s</span>' % (edge_link(src, ctx), edge_link(dst, ctx)),
    )
    out.add(pad + 2, '<span class="meta">%s</span>' % h(" · ".join(meta)))
    out.add(pad + 2, '<span class="expansion">%s</span>' % h(expansion))
    out.add(pad, "</li>")


def html_connection(out, conn, ctx):
    conn_id = as_text(conn.get("id", "")).strip()
    kind, subtype, resource, rate = connection_meta(conn)
    kind_class = " kind-%s" % kind if kind in ("resource", "state") else ""
    out.add(
        2,
        '<article id="connection-%s" class="record economy-connection%s" '
        'data-source="design/economy.md#%s">' % (h(conn_id), kind_class, h(conn_id)),
    )
    out.add(4, "<h4>%s</h4>" % h(conn_id))
    out.add(4, '<p class="source">connection <code>%s</code></p>' % h(conn_id))
    dl_open(out, 4)
    src = as_text(conn.get("from", "")).strip()
    dst = as_text(conn.get("to", "")).strip()
    dl_field(out, 4, "From", linked_code(src, anchor_for_economy_ref(src, ctx)))
    dl_field(out, 4, "To", linked_code(dst, anchor_for_economy_ref(dst, ctx)))
    if kind:
        dl_field(out, 4, "Kind", h(kind))
    else:
        dl_field(out, 4, "Kind", "none recorded", unrecorded=True)
    if kind == "state":
        if subtype:
            dl_field(out, 4, "Subtype", h(subtype))
        else:
            dl_field(out, 4, "Subtype", "none recorded", unrecorded=True)
    if rate:
        dl_field(out, 4, "Rate", h(rate))
    else:
        dl_field(out, 4, "Rate", "none recorded", unrecorded=True)
    if resource:
        dl_field(out, 4, "Resource", h(resource))
    dl_close(out, 4)
    out.add(2, "</article>")


def html_comp(out, data, ctx):
    comp = data["comp"]
    section_open(
        out,
        "competitive-differentiation",
        "comp-analysis",
        "design/comp-analysis.md",
        comp is None,
    )
    out.add(2, "<h2>Competitive Differentiation</h2>")
    if comp is None:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_COMP, ctx))
    else:
        out.add(2, '<p class="source"><code>design/comp-analysis.md</code></p>')
        if comp["body"]:
            html_body(out, 2, comp["body"], 1, ctx)
    out.add(0, "</section>")


def html_tech(out, data, ctx):
    live = data["tech_live"]
    section_open(out, "technical-design", "tech", "design/tech/", not live)
    out.add(2, "<h2>Technical Design</h2>")
    if not live:
        out.add(2, '<p class="absent">%s</p>' % inline(ABSENT_TECH, ctx))
    for record in live:
        classes = "record tech-record status-%s scope-%s" % (
            record["status"],
            record["scope"],
        )
        out.add(
            2,
            '<article id="tech-%s" class="%s" data-source="%s">'
            % (h(record["slug"]), classes, h(record["rel"])),
        )
        out.add(4, "<h3>%s</h3>" % h(record["title"]))
        out.add(4, '<p class="source"><code>%s</code></p>' % h(record["rel"]))
        if record["status"] == "open":
            out.add(4, '<p class="open-note">Open — not yet decided.</p>')
        dl_open(out, 4)
        dl_field(out, 4, "Status", h(record["status"]))
        if record["category"]:
            dl_field(out, 4, "Category", h(record["category"]))
        else:
            dl_field(out, 4, "Category", "none recorded", unrecorded=True)
        dl_field(out, 4, "Scope", h(record["scope"]))
        if record["drivers"]:
            items = []
            for driver in record["drivers"]:
                items.append(linked_code(driver, anchor_for_driver(driver, ctx)))
            dl_field(out, 4, "Drivers", ", ".join(items))
        else:
            dl_field(out, 4, "Drivers", "none", unrecorded=True)
        dl_close(out, 4)
        if record["body"]:
            html_body(out, 4, record["body"], 2, ctx)
        out.add(2, "</article>")
    for record in data["tech_superseded"]:
        out.add(
            2,
            '<p class="superseded-note"><code>%s</code> superseded by '
            "<code>%s</code>.</p>" % (h(record["slug"]), h(record["superseded_by"])),
        )
    out.add(0, "</section>")


def html_supporting(out, ctx):
    section_open(out, "supporting-documents", "supporting", "game-gdd", False)
    out.add(2, "<h2>Supporting Documents Not Rendered</h2>")
    out.add(2, "<p>%s</p>" % inline(SUPPORTING_INTRO, ctx))
    out.add(2, '<ul class="supporting-list">')
    for name, reason in SUPPORTING_DOCS:
        out.add(
            4,
            "<li><strong>%s</strong> — %s</li>" % (h(name), inline(reason, ctx)),
        )
    out.add(2, "</ul>")
    out.add(2, "<p>%s</p>" % inline(SUPPORTING_CLOSING, ctx))
    out.add(0, "</section>")


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------


def write_text(path, text):
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalised.endswith("\n"):
        normalised += "\n"
    normalised = normalised.rstrip("\n") + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalised)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Render design/gdd.md and design/gdd.html from the structured "
            "records under design/."
        )
    )
    parser.add_argument(
        "--reset-css",
        action="store_true",
        help="overwrite design/gdd.css from the skill's default template",
    )
    args = parser.parse_args(argv)

    root = os.path.join(os.getcwd(), "design")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template = os.path.join(script_dir, os.pardir, "templates", "default.css")
    template = os.path.normpath(template)

    try:
        data = load_design(root)
        ctx = build_context(data)
        markdown = build_markdown(data)
        html = build_html(data, ctx)
    except InvalidInput as exc:
        sys.stderr.write("%s\n" % exc)
        return 1

    if not os.path.isdir(root):
        os.makedirs(root)

    write_text(os.path.join(root, "gdd.md"), markdown)
    write_text(os.path.join(root, "gdd.html"), html)

    css_path = os.path.join(root, "gdd.css")
    if os.path.isfile(template) and (args.reset_css or not os.path.exists(css_path)):
        shutil.copyfile(template, css_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
