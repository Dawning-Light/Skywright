#!/usr/bin/env bash
# Contract suite for ../curve-fit.sh.
#
# Every series below is generated from a formula written here in the test, and
# the expected coefficients are that same formula's own constants -- so each
# assertion is exact by construction rather than eyeballed against a real-world
# dataset. A fit that recovers its generating formula must return those
# constants back.
#
# Tolerances (absolute, on each coefficient):
#   TOL       1e-6   linear, poly:2, poly:3, exponential, logarithmic.
#   TOL_Q     1e-4   poly:4 only. The normal equations at quartic carry moments
#                    up to sum(x^8); over x=1..7 that spans ~5.8e6, and the
#                    Gram matrix's conditioning costs several digits. This
#                    widened tolerance is the measured price of that
#                    conditioning -- and is exactly why curve-fit.sh caps the
#                    polynomial degree at 4 rather than admitting higher ones.
#   TOL_R2    1e-9   coefficient of determination for an exact fit (want 1).
set -u
cd "$(dirname "$0")/.." || exit 2

CF=curve-fit.sh
TOL=1e-6
TOL_Q=1e-4
TOL_R2=1e-9
fail=0

if [ ! -f "$CF" ]; then
  echo "FAIL missing script: $CF"
  exit 1
fi

# ---------------------------------------------------------------- helpers ---

# field <output> <name> -- the value of the `name: value` line, or empty.
field() {
  printf '%s\n' "$1" | awk -v k="$2" '
    index($0, k ": ") == 1 { print substr($0, length(k) + 3); exit }'
}

# near <label> <got> <want> <tol>
near() {
  awk -v g="$2" -v w="$3" -v t="$4" 'BEGIN{
    d = g - w; if (d < 0) d = -d; exit (d <= t) ? 0 : 1 }' \
    || { echo "FAIL $1: got '$2', want '$3' (tol $4)"; fail=1; }
}

# eq <label> <got> <want>
eq() {
  [ "$2" = "$3" ] || { echo "FAIL $1: got '$2', want '$3'"; fail=1; }
}

# coeffs <label> <output> <space-separated wanted list> <tol>
coeffs() {
  local got
  got=$(field "$2" coefficients)
  awk -v g="$got" -v e="$3" -v t="$4" 'BEGIN{
    ng = split(g, G, " "); ne = split(e, E, " ")
    if (ng != ne) exit 1
    for (i = 1; i <= ne; i++) { d = G[i] - E[i]; if (d < 0) d = -d; if (d > t) exit 1 }
    exit 0 }' \
    || { echo "FAIL $1: coefficients '$got', want '$3' (tol $4)"; fail=1; }
}

# recovers <label> <model-arg> <points> <wanted model> <wanted coeffs> <tol>
# Asserts exit 0, four fields on stdout, the reported model, its coefficients,
# and an exact fit (R2 = 1) -- the whole success contract in one call.
recovers() {
  local label=$1 marg=$2 pts=$3 wmodel=$4 wcoef=$5 tol=$6 out rc lines
  out=$(bash "$CF" fit --model "$marg" --points "$pts" 2>/dev/null); rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FAIL $label: exit $rc, want 0"; fail=1; return
  fi
  lines=$(printf '%s\n' "$out" | grep -c .)
  eq "$label stdout line count" "$lines" "4"
  eq "$label model" "$(field "$out" model)" "$wmodel"
  coeffs "$label" "$out" "$wcoef" "$tol"
  near "$label fit" "$(field "$out" fit)" "1" "$TOL_R2"
}

# refuses <label> <args...> -- asserts non-zero exit and captures stderr into
# the global REFUSAL for a follow-up substring check.
REFUSAL=""
refuses() {
  local label=$1; shift
  local rc
  REFUSAL=$(bash "$CF" "$@" 2>&1 >/dev/null); rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "FAIL $label: exit 0, want non-zero"; fail=1
  fi
}

# says <label> <substring>
says() {
  case "$REFUSAL" in
    *"$2"*) ;;
    *) echo "FAIL $1: diagnostic '$REFUSAL' does not name '$2'"; fail=1 ;;
  esac
}

# ----------------------------------------------------------------- series ---

# L: y = 5 + 2x over x = 1..6.
L="1:7,2:9,3:11,4:13,5:15,6:17"
# Q: y = 1 + 2x + 3x^2 over x = 1..6.
Q="1:6,2:17,3:34,4:57,5:86,6:121"
# C: y = 1 + 2x + 3x^2 + 4x^3 over x = 1..7.
C="1:10,2:49,3:142,4:313,5:586,6:985,7:1534"
# P4: y = 1 + x + x^2 + x^3 + x^4 over x = 1..7.
P4="1:5,2:31,3:121,4:341,5:781,6:1555,7:2801"
# E: y = 3 * 2^x over x = 1..7, i.e. a*e^(bx) with a = 3, b = ln 2. Every value
# is an exact double, so the ln-space fit recovers a and b to machine precision.
E="1:6,2:12,3:24,4:48,5:96,6:192,7:384"
E_B=$(awk 'BEGIN{ printf "%.17g", log(2) }')
# G: y = 2 + 3*ln(x) over x = 1..8, generated here from that same formula.
G=$(awk 'BEGIN{
  s = ""
  for (x = 1; x <= 8; x++) s = s (x == 1 ? "" : ",") sprintf("%d:%.17g", x, 2 + 3 * log(x))
  print s }')

# ---------------------------------- each family recovers its own generator ---

recovers "linear recovery"      linear      "$L"  "linear"      "5 2"       "$TOL"
recovers "poly:2 recovery"      poly:2      "$Q"  "poly:2"      "1 2 3"     "$TOL"
recovers "poly:3 recovery"      poly:3      "$C"  "poly:3"      "1 2 3 4"   "$TOL"
recovers "poly:4 recovery"      poly:4      "$P4" "poly:4"      "1 1 1 1 1" "$TOL_Q"
recovers "exponential recovery" exponential "$E"  "exponential" "3 $E_B"    "$TOL"
recovers "logarithmic recovery" logarithmic "$G"  "logarithmic" "2 3"       "$TOL"

# The domain field reports the x range the fit was taken over.
out=$(bash "$CF" fit --model linear --points "$L" 2>/dev/null)
eq "linear domain" "$(field "$out" domain)" "1 6"

# ------------------------------------- auto picks the generating family ------

recovers "auto on linear series"      auto "$L"  "linear"      "5 2"    "$TOL"
recovers "auto on quadratic series"   auto "$Q"  "poly:2"      "1 2 3"  "$TOL"
recovers "auto on exponential series" auto "$E"  "exponential" "3 $E_B" "$TOL"
recovers "auto on logarithmic series" auto "$G"  "logarithmic" "2 3"    "$TOL"

# The linear series is fitted exactly by poly:2 as well (with a near-zero
# quadratic term), so `auto` only reports `linear` if its tie-break prefers the
# family with fewer coefficients. This asserts that tie-break directly.
out=$(bash "$CF" fit --model poly:2 --points "$L" 2>/dev/null)
near "poly:2 also fits the linear series exactly" "$(field "$out" fit)" "1" "$TOL_R2"

# ----------------------------------------------------- refusals, not fudges --

refuses "under-determined poly:3" fit --model poly:3 --points "1:1,2:2,3:3"
says    "under-determined poly:3" "poly:3"
says    "under-determined poly:3" "4 points"

refuses "under-determined linear" fit --model linear --points "1:1"
says    "under-determined linear" "linear"

refuses "exponential with a non-positive y" \
  fit --model exponential --points "1:5,2:0,3:20"
says    "exponential with a non-positive y" "exponential"
says    "exponential with a non-positive y" "y > 0"

refuses "exponential with a negative y" \
  fit --model exponential --points "1:5,2:-3,3:20"
says    "exponential with a negative y" "exponential"

refuses "logarithmic with a non-positive x" \
  fit --model logarithmic --points "0:1,1:2,2:3"
says    "logarithmic with a non-positive x" "logarithmic"
says    "logarithmic with a non-positive x" "x > 0"

# The degree cap is a refusal too, and the script's own usage text carries the
# reason for it rather than leaving a caller to guess.
refuses "poly:5 is above the degree cap" fit --model poly:5 --points "$P4"
says    "poly:5 is above the degree cap" "2, 3, or 4"

usage=$(bash "$CF" 2>&1 >/dev/null)
case "$usage" in
  *conditioning*) ;;
  *) echo "FAIL usage text: does not give the reason for the degree cap"; fail=1 ;;
esac

# --------------------------------- auto skips, rather than fails, on those ---

# x = 1 and x = 2 with y = 0 at x = 1: exponential is inadmissible (y <= 0) and
# poly:2 is under-determined at two points, but linear and logarithmic are both
# admissible. `auto` must still return a fit rather than failing the call.
out=$(bash "$CF" fit --model auto --points "1:0,2:4" 2>/dev/null); rc=$?
eq   "auto skips inadmissible families (exit)"  "$rc" "0"
eq   "auto skips inadmissible families (model)" "$(field "$out" model)" "linear"
coeffs "auto skips inadmissible families" "$out" "-4 4" "$TOL"

# When no family at all is admissible, `auto` refuses and says why per family.
refuses "auto with no admissible family" fit --model auto --points "1:5"
says    "auto with no admissible family" "linear"
says    "auto with no admissible family" "poly:2"

# ------------------------------------------------------------ expected value --

# 0.5*10 + 0.3*20 + 0.2*50 = 5 + 6 + 10 = 21, over probabilities summing to 1.
out=$(bash "$CF" ev --table "0.5:10,0.3:20,0.2:50" 2>/dev/null); rc=$?
eq   "ev exit"             "$rc" "0"
near "ev expected_value"   "$(field "$out" expected_value)"   "21" "$TOL"
near "ev probability_sum"  "$(field "$out" probability_sum)"  "1"  "$TOL"

# A table that does not sum to 1 is reported as such rather than normalised
# away: 0.5*10 + 0.2*20 = 9 over a probability sum of 0.7.
out=$(bash "$CF" ev --table "0.5:10,0.2:20" 2>/dev/null); rc=$?
eq   "ev partial-table exit"            "$rc" "0"
near "ev partial-table expected_value"  "$(field "$out" expected_value)"  "9"   "$TOL"
near "ev partial-table probability_sum" "$(field "$out" probability_sum)" "0.7" "$TOL"

refuses "ev with a negative probability" ev --table "0.5:10,-0.2:20"
says    "ev with a negative probability" "probability"

refuses "ev with a malformed entry" ev --table "0.5:10,bogus"
refuses "ev with an empty table"    ev --table ""

# ---------------------------------------------------- verb and arg handling --

for bad in bogus --help "" fitt; do
  rc=0
  bash "$CF" "$bad" >/dev/null 2>&1 || rc=$?
  [ "$rc" -eq 2 ] || { echo "FAIL first arg '$bad': exit $rc, want 2"; fail=1; }
done

# Usage on stderr, not stdout, for that case.
sout=$(bash "$CF" bogus 2>/dev/null)
[ -z "$sout" ] || { echo "FAIL unknown verb: wrote '$sout' to stdout, want stderr only"; fail=1; }

refuses "fit with no --points"       fit --model linear
refuses "fit with no --model"        fit --points "$L"
refuses "fit with an unknown model"  fit --model sigmoid --points "$L"
refuses "fit with an unknown option" fit --model linear --points "$L" --degree 2

# ------------------------------------------------- bash and awk, nothing else --

# The script may not reach for another interpreter, a third-party package, or
# the network. Checked as a whole-word grep over the script's own text, so a
# short name like `bc` or `nc` cannot false-positive inside another word.
# `node` is deliberately absent from this list: the script's usage text has to
# say which economy-graph node the output is written into, and that mention is
# not a Node.js invocation.
for banned in python python3 perl ruby jq bc dc curl wget nc ssh pip npm; do
  if grep -qwF -- "$banned" "$CF"; then
    echo "FAIL $CF: reaches for a banned tool: '$banned'"; fail=1
  fi
done
head -n 1 "$CF" | grep -q 'bash' \
  || { echo "FAIL $CF: shebang does not name bash"; fail=1; }

[ "$fail" -eq 0 ] && echo "PASS game-curve-fit"
exit "$fail"
