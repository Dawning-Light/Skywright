import argparse
import os
import sys

from render_gdd import (
    BadReference,
    InvalidInput,
    iter_wikilink_hits,
    load_design,
    parse_reference,
    read_text,
    record_bodies,
)

_PATH_KIND_BY_DIR = {"pillars": "pillar", "mechanics": "mechanic", "tech": "tech"}


def resolve_target(target):
    """Return ``(kind, ident)`` for a typed-reference string or a record path."""
    if "/" in target or target.endswith(".md"):
        return _target_from_path(target)
    return parse_reference(target)


def _target_from_path(path):
    norm = os.path.normpath(path)
    base = os.path.basename(norm)
    if base == "concept.md":
        return "concept", ""
    if base == "comp-analysis.md":
        return "comp-analysis", ""
    if base == "economy.md":
        raise BadReference(
            "is malformed",
            "`%s` holds many nodes, families, and connections — name the one "
            "you mean with `node:<id>`, `family:<name>`, or `connection:<id>` "
            "instead of a path" % path,
        )
    stem, ext = os.path.splitext(base)
    if ext != ".md":
        raise BadReference("is malformed", "`%s` is not a design record path" % path)
    parent = os.path.basename(os.path.dirname(norm))
    if parent in _PATH_KIND_BY_DIR:
        return _PATH_KIND_BY_DIR[parent], stem
    raise BadReference(
        "is malformed", "`%s` is not a recognized design record path" % path
    )


def find_hits_in_text(text, kind, ident):
    """``(lineno, heading)`` for each line where ``[[kind:ident]]`` appears.

    A thin filter over ``render_gdd.iter_wikilink_hits`` -- the render's own
    citation lists share the same scan, so there is exactly one
    implementation of "find every wikilink hit in a text" rather than two.
    """
    return [
        (lineno, heading)
        for found_kind, found_ident, _literal, heading, lineno in iter_wikilink_hits(text)
        if found_kind == kind and found_ident == ident
    ]


def find_hits(data, design_root, kind, ident):
    project_root = os.path.dirname(design_root)
    seen = []
    for rel, _skill, _anchor, _identifier, _body in record_bodies(data):
        if rel not in seen:
            seen.append(rel)
    hits = []
    for rel in seen:
        text = read_text(os.path.join(project_root, rel))
        for lineno, heading in find_hits_in_text(text, kind, ident):
            hits.append((rel, lineno, heading))
    return hits


def literal_for(kind, ident):
    return "[[%s]]" % kind if not ident else "[[%s:%s]]" % (kind, ident)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "List every reference to one pillar, mechanic, tech decision, "
            "economy node/family/connection, concept, or comp-analysis, found "
            "across design/."
        )
    )
    parser.add_argument(
        "target",
        help=(
            "a typed reference (e.g. pillar:zero-grind) or a record's file path "
            "(e.g. design/pillars/zero-grind.md)"
        ),
    )
    args = parser.parse_args(argv)

    design_root = os.path.join(os.getcwd(), "design")

    try:
        kind, ident = resolve_target(args.target)
    except BadReference as exc:
        sys.stderr.write("%s\n" % exc.reason)
        return 1

    try:
        data = load_design(design_root)
    except InvalidInput as exc:
        sys.stderr.write("%s\n" % exc)
        return 1

    literal = literal_for(kind, ident)
    hits = find_hits(data, design_root, kind, ident)
    if not hits:
        print("No references to %s." % literal)
        return 0

    for rel, lineno, heading in hits:
        if heading:
            print('%s:%d: %s (in "%s")' % (rel, lineno, literal, heading))
        else:
            print("%s:%d: %s" % (rel, lineno, literal))
    return 0


if __name__ == "__main__":
    sys.exit(main())
