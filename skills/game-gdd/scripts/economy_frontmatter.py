"""The one parser of design records' frontmatter, and ``design/economy.md``'s
reader, validator, and writer.

``render_gdd.py`` reads every record it renders through the parsing half of
this module; ``game-mechanics``' ``economy-tool`` reads, validates, and
rewrites ``design/economy.md`` through all of it. Neither defines a parser of
its own, so the file the tool writes and the file the render reads are read by
the same code.

Stdlib only.
"""

import re


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


def frontmatter_span(text, path, skill):
    """Where the frontmatter block sits in ``text``, or None if it has none.

    Returns ``(start, end, body_start)``: ``text[start:end]`` is everything
    between the two ``---`` fence lines, without the newline before the
    closing one, and ``text[body_start:]`` is everything after the closing
    fence's line. The offsets index ``text`` exactly as given, so a caller can
    replace the block and leave every other byte alone.
    """
    lines = text.split("\n")
    if not text.startswith("---") or lines[0].strip() != "---":
        return None
    start = len(lines[0]) + 1
    offset = start
    for line in lines[1:]:
        if line.strip() == "---":
            end = max(start, offset - 1)
            return start, end, min(offset + len(line) + 1, len(text))
        offset += len(line) + 1
    raise InvalidInput(
        "%s: the frontmatter block opens with `---` but is never closed by a "
        "matching `---` line; fix it with `%s`." % (path, skill)
    )


def split_frontmatter(text, path, skill):
    """Return ``(frontmatter_text_or_None, body_text)``."""
    span = frontmatter_span(text, path, skill)
    if span is None:
        return None, text
    start, end, body_start = span
    return text[start:end], text[body_start:]


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
# The ``updated`` field
#
# Every record shape may carry ``updated: YYYY-MM-DDTHH:MMZ`` -- UTC, 24-hour,
# the form ``game-authoring`` defines. Absent is valid (records written before
# the field existed carry none); malformed is not.
# ---------------------------------------------------------------------------

UPDATED_FORM = "YYYY-MM-DDTHH:MMZ"
_UPDATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")


def read_updated(fields, rel, skill):
    """Return a record's ``updated`` value, or ``""`` when it carries none."""
    value = as_text(fields.get("updated", "")).strip()
    if not value:
        return ""
    if not _UPDATED_RE.match(value):
        raise InvalidInput(
            "%s: `updated: %s` is not the required `%s` UTC form (for example "
            "`2026-09-11T20:42Z`); fix it with `%s`. The `updated` form is "
            "defined by `game-authoring`." % (rel, value, UPDATED_FORM, skill)
        )
    return value


# ---------------------------------------------------------------------------
# Body helpers
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def trim_body(text):
    """Strip leading/trailing blank lines; normalise line endings."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip("\n").rstrip()


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
        if FENCE_RE.match(line):
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


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().replace("\r\n", "\n").replace("\r", "\n")


# ---------------------------------------------------------------------------
# The economy graph
#
# The record shape ``game-mechanics`` defines for ``design/economy.md``: read,
# validated, and -- below -- written back.
# ---------------------------------------------------------------------------

ECONOMY_REL = "design/economy.md"


def load_economy(path):
    return parse_economy(read_text(path))


def parse_economy(text, headings=True):
    """Parse and validate the full text of ``design/economy.md``.

    Returns the economy dict ``render_gdd.py`` renders from; raises
    InvalidInput naming the first rule the file fails. ``headings=False``
    skips only the body-heading rule -- for ``economy-tool``, which rewrites
    the frontmatter and leaves the body to its author.
    """
    rel = ECONOMY_REL
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
        "updated": read_updated(fields, rel, "game-mechanics"),
        "sections": sections,
        "section_order": order,
    }
    if headings:
        validate_economy(economy)
    else:
        validate_economy_records(economy)
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
    """Every rule ``game-mechanics`` defines for the economy graph -- its
    frontmatter records and its body headings both."""
    validate_economy_records(economy)
    validate_economy_headings(economy)


def validate_economy_records(economy):
    """The frontmatter's rules: every node, family, and connection has its
    id, no id is declared twice, and every family member and connection end
    resolves. Records the declared ids on ``economy`` as ``node_ids``,
    ``family_names``, and ``conn_ids``."""
    node_ids = []
    for node in economy["nodes"]:
        node_id = as_text(node.get("id", "")).strip()
        if not node_id:
            raise InvalidInput(
                "design/economy.md: node `%s` has no `id` — a node with no id "
                "cannot be referenced; fix it with `game-mechanics`."
                % conn_repr(node)
            )
        if node_id in node_ids:
            raise InvalidInput(
                "design/economy.md: node id `%s` is declared more than once; "
                "every node id is unique within the file; fix it with "
                "`game-mechanics`." % node_id
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
        if fname in family_names:
            raise InvalidInput(
                "design/economy.md: family `@%s` is declared more than once; "
                "every family name is unique within the file; fix it with "
                "`game-mechanics`." % fname
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
        if conn_id in conn_ids:
            raise InvalidInput(
                "design/economy.md: connection id `%s` is declared more than "
                "once; every connection id is unique within the file; fix it "
                "with `game-mechanics`." % conn_id
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

    economy["node_ids"] = node_ids
    economy["family_names"] = family_names
    economy["conn_ids"] = conn_ids


def validate_economy_headings(economy):
    """The body's rule: every ``## `` heading names exactly one declared node,
    family (``@<name>``), or member. Checks against the ids
    ``validate_economy_records`` recorded, so it runs after that."""
    node_set = set(economy["node_ids"])
    family_set = set(economy["family_names"])
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


def ref_resolves(ref, node_set, family_set, conn_set):
    if ref.startswith("@"):
        return ref[1:] in family_set
    if ref.startswith("#"):
        return ref[1:] in conn_set
    return ref in node_set


# ---------------------------------------------------------------------------
# Serializing
#
# The parser's inverse, for the economy graph's frontmatter: one canonical
# form, the one ``game-mechanics`` specifies and hand-authored files already
# use -- block-style nodes and families, a flow-style ``[a, b]`` for a list of
# scalars, and every ``connections`` entry a one-line ``{ k: v }`` mapping.
# Keys keep the order they were parsed in. A block this module parses and then
# writes back byte-for-byte is in canonical form; ``economy-tool`` refuses to
# rewrite one that is not, rather than silently reformatting it.
# ---------------------------------------------------------------------------

# Quoted wherever they appear: a leading sigil (`@` family, `#` connection) or
# quote character, and edge whitespace the parser would strip.
_QUOTE_ALWAYS_RE = re.compile(r"""^[@#'"]|^\s|\s$""")
# Quoted inside a flow list or mapping, where they would split the value.
_QUOTE_IN_FLOW_RE = re.compile(r"[,\[\]{}]")


def format_scalar(value, flow):
    """One scalar as written: bare, or quoted wherever the parser needs it."""
    text = str(value)
    if text == "":
        return '""'
    if "\n" in text:
        raise ValueError("a frontmatter value cannot span lines: `%s`" % text)
    quote = (
        _QUOTE_ALWAYS_RE.search(text) is not None
        or text.startswith("[")
        or (flow and _QUOTE_IN_FLOW_RE.search(text) is not None)
    )
    if not quote:
        return text
    if '"' not in text:
        return '"%s"' % text
    if "'" not in text:
        return "'%s'" % text
    raise ValueError(
        "a frontmatter value cannot hold both quote characters: `%s`" % text
    )


def format_flow_list(values):
    return "[%s]" % ", ".join(format_scalar(v, True) for v in values)


def format_flow_mapping(mapping):
    """One ``{ k: v, ... }`` line -- the form every connection is written in."""
    parts = []
    for key, value in mapping.items():
        if isinstance(value, dict):
            raise ValueError("a flow mapping cannot nest a mapping under `%s`" % key)
        if isinstance(value, list):
            parts.append("%s: %s" % (key, format_flow_list(value)))
        else:
            parts.append("%s: %s" % (key, format_scalar(value, True)))
    if not parts:
        return "{}"
    return "{ %s }" % ", ".join(parts)


def serialize_economy_frontmatter(fields):
    """``fields`` as a frontmatter block, in canonical form.

    The text between the two ``---`` fences, without a trailing newline --
    the same span ``frontmatter_span`` locates. Raises ValueError for a value
    the parser could not read back unchanged.
    """
    lines = []
    for key, value in fields.items():
        _emit(lines, 0, key, value, flow_items=(key == "connections"))
    return "\n".join(lines)


def _emit(lines, indent, key, value, flow_items=False):
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            raise ValueError("mapping `%s` is empty and has no written form" % key)
        lines.append("%s%s:" % (pad, key))
        for sub_key, sub_value in value.items():
            _emit(lines, indent + 2, sub_key, sub_value)
    elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
        lines.append("%s%s:" % (pad, key))
        for item in value:
            if flow_items:
                lines.append("%s  - %s" % (pad, format_flow_mapping(item)))
            else:
                _emit_block_item(lines, indent + 2, item)
    elif isinstance(value, list):
        if any(isinstance(v, (dict, list)) for v in value):
            raise ValueError("list `%s` mixes mappings or lists with scalars" % key)
        lines.append("%s%s: %s" % (pad, key, format_flow_list(value)))
    else:
        lines.append("%s%s: %s" % (pad, key, format_scalar(value, False)))


def _emit_block_item(lines, indent, item):
    """One ``- key: value`` list item, its other keys aligned under the first."""
    if not item:
        raise ValueError("an empty mapping in a list has no written form")
    sub = []
    for key, value in item.items():
        _emit(sub, indent + 2, key, value)
    lines.append("%s- %s" % (" " * indent, sub[0][indent + 2:]))
    lines.extend(sub[1:])
