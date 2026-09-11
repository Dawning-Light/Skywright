#!/usr/bin/env bash
#
# Fixture tests for render_gdd.py.
#
#   bash run_tests.sh            run every fixture, print PASS/FAIL per case
#   UPDATE=1 bash run_tests.sh   regenerate the checked-in expected outputs
#
# A fixture directory holding `expected-stderr.txt` is an invalid-input case
# (non-zero exit, one stderr message, no files written). Every other fixture is
# a valid case, diffed against `expected/gdd.md` and `expected/gdd.html`.
#
# The tests never diff `gdd.css`'s contents against a checked-in copy -- only
# against the live `templates/default.css` -- so the real stylesheet can change
# without touching this file.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$HERE/.." && pwd)"
SKILL_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"
FIXTURES="$HERE/fixtures"
UPDATE="${UPDATE:-0}"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

REAL_TEMPLATE="$SKILL_DIR/templates/default.css"
TEMPLATE_NOTE=""
if [ -f "$REAL_TEMPLATE" ]; then
  RENDER="$SCRIPTS_DIR/render_gdd.py"
  TEMPLATE="$REAL_TEMPLATE"
else
  # The skill's real default.css does not exist yet. Run against a throwaway
  # copy of the skill tree so the CSS-seeding behaviour is still covered, and
  # say so in the output. Nothing is written into the repo.
  mkdir -p "$WORK/skill/scripts" "$WORK/skill/templates"
  cp "$SCRIPTS_DIR/render_gdd.py" "$WORK/skill/scripts/render_gdd.py"
  printf '/* placeholder stylesheet used only by run_tests.sh */\n' \
    > "$WORK/skill/templates/default.css"
  RENDER="$WORK/skill/scripts/render_gdd.py"
  TEMPLATE="$WORK/skill/templates/default.css"
  TEMPLATE_NOTE="note: $REAL_TEMPLATE does not exist; CSS assertions ran against a throwaway placeholder."
fi

FAILURES=0

pass() { printf 'PASS  %s\n' "$1"; }

fail() {
  printf 'FAIL  %s\n' "$1"
  if [ "$#" -gt 1 ]; then
    printf '        %s\n' "$2"
  fi
  FAILURES=$((FAILURES + 1))
}

# check <case name> <message on failure> -- reads a 0/1 result from $?
check() {
  local name="$1" message="$2" rc="$3"
  if [ "$rc" -eq 0 ]; then
    pass "$name"
  else
    fail "$name" "$message"
  fi
}

run_render() {
  # run_render <dir> <stdout file> <stderr file> [args...]
  local dir="$1" outfile="$2" errfile="$3"
  shift 3
  local rc=0
  ( cd "$dir" && python3 "$RENDER" "$@" ) > "$outfile" 2> "$errfile" || rc=$?
  return "$rc"
}

stage_fixture() {
  # stage_fixture <fixture name> <destination dir>
  local name="$1" dest="$2"
  rm -rf "$dest"
  mkdir -p "$dest"
  if [ -d "$FIXTURES/$name/design" ]; then
    cp -r "$FIXTURES/$name/design" "$dest/design"
  fi
}

run_valid_fixture() {
  local name="$1"
  local dir="$WORK/valid-$name"
  local expected="$FIXTURES/$name/expected"
  stage_fixture "$name" "$dir"

  local rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" || rc=$?
  if [ "$rc" -ne 0 ]; then
    fail "$name: exits 0" "exit $rc; stderr: $(cat "$WORK/err")"
    return
  fi
  pass "$name: exits 0"

  if [ "$UPDATE" = "1" ]; then
    mkdir -p "$expected"
    cp "$dir/design/gdd.md" "$expected/gdd.md"
    cp "$dir/design/gdd.html" "$expected/gdd.html"
    printf 'UPDATED  %s/expected/gdd.md, %s/expected/gdd.html\n' "$name" "$name"
  fi

  local f
  for f in gdd.md gdd.html; do
    if [ ! -f "$expected/$f" ]; then
      fail "$name: $f matches expected" "no checked-in $expected/$f (run UPDATE=1)"
      continue
    fi
    if diff -u "$expected/$f" "$dir/design/$f" > "$WORK/diff"; then
      pass "$name: $f matches expected"
    else
      fail "$name: $f matches expected" "$(head -40 "$WORK/diff")"
    fi
  done

  # gdd.css is seeded from the skill's template, byte for byte. Contents are
  # never compared against a checked-in fixture copy.
  if [ -f "$dir/design/gdd.css" ] && cmp -s "$dir/design/gdd.css" "$TEMPLATE"; then
    pass "$name: gdd.css seeded from templates/default.css"
  else
    fail "$name: gdd.css seeded from templates/default.css" "missing or not identical to $TEMPLATE"
  fi

  # Determinism: a second run over the same input produces the same bytes.
  cp "$dir/design/gdd.md" "$WORK/first.md"
  cp "$dir/design/gdd.html" "$WORK/first.html"
  rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" || rc=$?
  if [ "$rc" -eq 0 ] \
    && cmp -s "$WORK/first.md" "$dir/design/gdd.md" \
    && cmp -s "$WORK/first.html" "$dir/design/gdd.html"; then
    pass "$name: re-render is byte-identical"
  else
    fail "$name: re-render is byte-identical" "second run differed (exit $rc)"
  fi

  # A hand-edited gdd.css survives an ordinary re-render...
  printf '/* hand-edited by the owner */\n' > "$dir/design/gdd.css"
  rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" || rc=$?
  if [ "$rc" -eq 0 ] && grep -q 'hand-edited by the owner' "$dir/design/gdd.css"; then
    pass "$name: hand-edited gdd.css survives a re-render"
  else
    fail "$name: hand-edited gdd.css survives a re-render" "gdd.css was overwritten"
  fi

  # ...and is overwritten only by --reset-css.
  rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" --reset-css || rc=$?
  if [ "$rc" -eq 0 ] && cmp -s "$dir/design/gdd.css" "$TEMPLATE"; then
    pass "$name: --reset-css restores gdd.css from the template"
  else
    fail "$name: --reset-css restores gdd.css from the template" "gdd.css was not reset"
  fi
}

run_invalid_fixture() {
  local name="$1"
  local dir="$WORK/invalid-$name"
  stage_fixture "$name" "$dir"

  local rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" || rc=$?
  if [ "$rc" -ne 0 ]; then
    pass "$name: exits non-zero"
  else
    fail "$name: exits non-zero" "exited 0"
  fi

  local line missing=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    if ! grep -qF -- "$line" "$WORK/err"; then
      missing=1
      fail "$name: stderr names \`$line\`" "stderr was: $(cat "$WORK/err")"
    fi
  done < "$FIXTURES/$name/expected-stderr.txt"
  if [ "$missing" -eq 0 ]; then
    pass "$name: stderr names the record, the rule, and the upstream skill"
  fi

  local wrote=""
  local f
  for f in gdd.md gdd.html gdd.css; do
    if [ -e "$dir/design/$f" ]; then
      wrote="$wrote $f"
    fi
  done
  if [ -z "$wrote" ]; then
    pass "$name: writes no output files"
  else
    fail "$name: writes no output files" "wrote:$wrote"
  fi
}

run_missing_design_dir() {
  local name="no-design-directory"
  local dir="$WORK/$name"
  rm -rf "$dir"
  mkdir -p "$dir"

  local rc=0
  run_render "$dir" "$WORK/out" "$WORK/err" || rc=$?
  if [ "$rc" -eq 0 ] && [ -f "$dir/design/gdd.md" ] && [ -f "$dir/design/gdd.html" ]; then
    pass "$name: creates design/ and renders into it"
  else
    fail "$name: creates design/ and renders into it" "exit $rc; stderr: $(cat "$WORK/err")"
  fi

  # The all-absent render is the same one empty-project produces.
  if [ -f "$FIXTURES/empty-project/expected/gdd.md" ] \
    && cmp -s "$dir/design/gdd.md" "$FIXTURES/empty-project/expected/gdd.md"; then
    pass "$name: matches the empty-project render"
  else
    fail "$name: matches the empty-project render" "gdd.md differed from the empty-project expectation"
  fi
}

for fixture_dir in "$FIXTURES"/*/; do
  fixture_name="$(basename "$fixture_dir")"
  if [ -f "$fixture_dir/expected-stderr.txt" ]; then
    run_invalid_fixture "$fixture_name"
  else
    run_valid_fixture "$fixture_name"
  fi
done

run_missing_design_dir

if [ -n "$TEMPLATE_NOTE" ]; then
  printf '\n%s\n' "$TEMPLATE_NOTE"
fi

if [ "$FAILURES" -ne 0 ]; then
  printf '\n%d check(s) failed.\n' "$FAILURES"
  exit 1
fi

printf '\nAll checks passed.\n'
