#!/usr/bin/env bash
# curve-fit.sh -- fits a curve to a value series, and computes the expected
# value of a probability table. bash and awk only: no other interpreter, no
# third-party package, no network.
#
# This script does not read or write design/economy.md, or any other file. It
# takes points on the command line and prints numbers. Reading a graph node's
# value series, calling this script, and writing the four printed fields back
# into that node's `value_progression` object is a procedure described in
# skills/game-mechanics/SKILL.md -- deliberately not logic performed here, so
# that one parser owns the economy file and this script's contract stays
# testable with no fixture project.
set -u

SELF=${0##*/}

usage() {
  cat <<'EOF'
usage:
  curve-fit.sh fit --model <linear|poly:2|poly:3|poly:4|exponential|logarithmic|auto>
                   --points "<x>:<y>[,<x>:<y>...]"
  curve-fit.sh ev  --table "<probability>:<value>[,<probability>:<value>...]"

Any first argument other than `fit` or `ev` prints this text on stderr and
exits 2.

fit
  Prints four fields, one per line, in the shape of an economy-graph node's
  `value_progression` object:

    model: <the fitted family>
    coefficients: <space-separated, ascending powers>
    domain: <min x> <max x>
    fit: <coefficient of determination>

  Coefficient meaning, by family:

    linear         y = c0 + c1*x                        -> "c0 c1"
    poly:<n>       y = c0 + c1*x + ... + cn*x^n         -> "c0 c1 ... cn"
    exponential    y = c0 * e^(c1*x)                    -> "c0 c1"
    logarithmic    y = c0 + c1*ln(x)                    -> "c0 c1"

  Polynomials are fitted by normal equations solved with Gaussian elimination
  and partial pivoting. `exponential` fits a straight line to (x, ln y);
  `logarithmic` fits a straight line to (ln x, y).

  `poly:<n>` accepts n of 2, 3, or 4 only. Two reasons, and both are about
  what the method can honestly deliver: normal-equations conditioning degrades
  sharply past cubic -- the Gram matrix carries moments up to sum(x^2n), and by
  quartic that costs several significant digits of every coefficient it
  returns -- and a game progression table rarely carries enough points to
  justify a higher degree anyway, so a quintic or beyond is fitting noise, not
  a progression. A higher n is refused rather than attempted.

  The reported `fit` is the coefficient of determination measured in the
  original y space for every family, not in the transformed space the
  exponential and logarithmic fits are solved in. This is what makes the four
  families comparable to each other, and so what makes `auto` meaningful. Where
  every y is identical (no variance to explain), `fit` is 1 for an exact fit
  and 0 otherwise.

  `auto` fits each family the data admits and reports the best-fitting one. It
  considers exactly four, in this fixed order:

    linear (2 coefficients), logarithmic (2), exponential (2), poly:2 (3)

  A family beats the current best only by a coefficient of determination
  greater by more than 1e-9. The order above ascends in coefficient count, so a
  tie -- an exactly-linear series, which poly:2 also fits perfectly with a
  near-zero quadratic term -- always resolves to the simpler family. A family
  whose own constraint fails is skipped with a note on stderr, not fatal;
  `auto` fails only when no family at all is admissible.

ev
  Prints two fields, one per line:

    expected_value: <sum of probability * value>
    probability_sum: <sum of probability>

  The probability sum is printed rather than checked so a caller can see a
  table that does not sum to 1, instead of having a malformed table silently
  averaged into a plausible-looking number.

refusals (exit non-zero, with a diagnostic naming the constraint and the model)
  - fewer points than the model has coefficients
  - a non-positive y under `exponential`
  - a non-positive x under `logarithmic`
  - a negative probability under `ev`
  - a polynomial degree outside 2..4
  Exit 2 for a usage error (unknown verb, unknown model, missing or malformed
  argument); exit 1 for a constraint the data itself fails.
EOF
}

die_usage() {
  printf '%s: %s\n' "$SELF" "$1" >&2
  usage >&2
  exit 2
}

verb=${1-}
[ $# -gt 0 ] && shift

case "$verb" in
  fit|ev) ;;
  *)
    printf '%s: unknown verb: %s\n' "$SELF" "${verb:-<none>}" >&2
    usage >&2
    exit 2
    ;;
esac

model=""
points=""
table=""

while [ $# -gt 0 ]; do
  case "$1" in
    --model=*)  model=${1#--model=};   shift ;;
    --points=*) points=${1#--points=}; shift ;;
    --table=*)  table=${1#--table=};   shift ;;
    --model|--points|--table)
      [ $# -ge 2 ] || die_usage "$1 needs a value"
      case "$1" in
        --model)  model=$2 ;;
        --points) points=$2 ;;
        --table)  table=$2 ;;
      esac
      shift 2
      ;;
    *) die_usage "$verb: unknown option: $1" ;;
  esac
done

if [ "$verb" = fit ]; then
  [ -n "$table" ] && die_usage "fit: --table belongs to ev, not fit"
  [ -n "$model" ] || die_usage "fit: --model is required"
  [ -n "$points" ] || die_usage "fit: --points is required"
  case "$model" in
    linear|exponential|logarithmic|auto|poly:2|poly:3|poly:4) ;;
    poly:*)
      die_usage "fit: polynomial degree must be 2, 3, or 4 (got '${model#poly:}'); normal-equations conditioning degrades sharply past cubic, and a game progression table rarely carries enough points to justify a higher degree"
      ;;
    *) die_usage "fit: unknown model: '$model'" ;;
  esac
else
  [ -n "$model$points" ] && die_usage "ev: --model and --points belong to fit, not ev"
  [ -n "$table" ] || die_usage "ev: --table is required"
fi

# ---------------------------------------------------------------------------
# Everything below is arithmetic, and so is awk's. bash parses arguments; awk
# parses the series, fits, and prints.
# ---------------------------------------------------------------------------

if [ "$verb" = ev ]; then
  exec awk -v self="$SELF" -v table="$table" '
    function isnum(v) {
      return v ~ /^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$/
    }
    function trim(v) { sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v); return v }
    function bad(msg) { printf "%s: ev: %s\n", self, msg > "/dev/stderr"; exit 2 }

    BEGIN {
      n = split(table, parts, ",")
      ev = 0; psum = 0; m = 0
      for (i = 1; i <= n; i++) {
        entry = trim(parts[i])
        if (entry == "") continue
        if (split(entry, kv, ":") != 2) bad("malformed entry '\''" entry "'\'' (want <probability>:<value>)")
        p = trim(kv[1]); v = trim(kv[2])
        if (!isnum(p) || !isnum(v)) bad("non-numeric entry '\''" entry "'\''")
        p += 0; v += 0
        if (p < 0) {
          printf "%s: ev: refusing to compute: a probability must be >= 0; got probability %.10g for value %.10g\n", self, p, v > "/dev/stderr"
          exit 1
        }
        ev += p * v
        psum += p
        m++
      }
      if (m == 0) bad("--table contained no entries")
      printf "expected_value: %.10g\n", ev
      printf "probability_sum: %.10g\n", psum
    }
  ' </dev/null
fi

exec awk -v self="$SELF" -v model="$model" -v points="$points" '
  function isnum(v) {
    return v ~ /^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$/
  }
  function trim(v) { sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v); return v }
  function bad(msg) { printf "%s: fit: %s\n", self, msg > "/dev/stderr"; exit 2 }
  function refuse(msg) {
    printf "%s: fit: refusing to fit: %s\n", self, msg > "/dev/stderr"
    exit 1
  }

  # A family, as it is named back to the caller and in every diagnostic.
  function label(name, deg) { return (name == "poly") ? ("poly:" deg) : name }

  # Least squares for yv = c0 + c1*t + ... + cdeg*t^deg, by normal equations
  # solved with Gaussian elimination and partial pivoting. Fills coef[0..deg].
  # Returns 1 on success, 0 if the system is singular -- which happens when the
  # series carries fewer distinct t values than the model has coefficients, and
  # is reported as a refusal rather than papered over with a pseudo-inverse.
  function polyfit(t, yv, n, deg, coef,
                   m, i, j, k, r, A, b, s, piv, mx, tmp, f, scale) {
    m = deg + 1
    scale = 0
    for (i = 1; i <= m; i++) {
      for (j = 1; j <= m; j++) {
        s = 0
        for (k = 1; k <= n; k++) s += t[k] ^ (i + j - 2)
        A[i, j] = s
        tmp = (s < 0) ? -s : s
        if (tmp > scale) scale = tmp
      }
      s = 0
      for (k = 1; k <= n; k++) s += yv[k] * (t[k] ^ (i - 1))
      b[i] = s
    }
    if (scale <= 0) return 0

    for (i = 1; i <= m; i++) {
      piv = i
      mx = (A[i, i] < 0) ? -A[i, i] : A[i, i]
      for (r = i + 1; r <= m; r++) {
        tmp = (A[r, i] < 0) ? -A[r, i] : A[r, i]
        if (tmp > mx) { mx = tmp; piv = r }
      }
      if (mx <= 1e-12 * scale) return 0
      if (piv != i) {
        for (j = 1; j <= m; j++) { tmp = A[i, j]; A[i, j] = A[piv, j]; A[piv, j] = tmp }
        tmp = b[i]; b[i] = b[piv]; b[piv] = tmp
      }
      for (r = i + 1; r <= m; r++) {
        f = A[r, i] / A[i, i]
        if (f == 0) continue
        for (j = i; j <= m; j++) A[r, j] -= f * A[i, j]
        b[r] -= f * b[i]
      }
    }

    for (i = m; i >= 1; i--) {
      s = b[i]
      for (j = i + 1; j <= m; j++) s -= A[i, j] * coef[j - 1]
      coef[i - 1] = s / A[i, i]
    }
    return 1
  }

  # Coefficient of determination, always measured against the original y.
  function rsquared(yv, pred, n,   i, mean, sst, ssr, d) {
    mean = 0
    for (i = 1; i <= n; i++) mean += yv[i]
    mean /= n
    sst = 0; ssr = 0
    for (i = 1; i <= n; i++) {
      d = yv[i] - mean; sst += d * d
      d = yv[i] - pred[i]; ssr += d * d
    }
    if (sst <= 0) return (ssr <= 0) ? 1 : 0
    return 1 - ssr / sst
  }

  # Fits one family against the parsed series. On success fills FC[0..FNC-1]
  # and FR2 and returns 1. On a constraint failure sets FWHY and returns 0 --
  # which an explicit --model turns into a refusal and `auto` turns into a skip.
  function fitmodel(name, deg,   i, j, ncoef, d, t, yv, pred, C) {
    FWHY = ""; FNC = 0; FR2 = 0
    delete FC

    ncoef = (name == "poly") ? (deg + 1) : 2
    if (N < ncoef) {
      FWHY = sprintf("model '\''%s'\'' needs at least %d points (one per fitted coefficient), got %d", \
                     label(name, deg), ncoef, N)
      return 0
    }

    if (name == "exponential") {
      for (i = 1; i <= N; i++) {
        if (Y[i] <= 0) {
          FWHY = sprintf("model '\''exponential'\'' requires every y > 0, because it fits a straight line to ln(y); got y = %.10g at x = %.10g", \
                         Y[i], X[i])
          return 0
        }
      }
      for (i = 1; i <= N; i++) { t[i] = X[i]; yv[i] = log(Y[i]) }
      if (!polyfit(t, yv, N, 1, C)) {
        FWHY = sprintf("model '\''exponential'\'': the normal equations are singular; the series carries fewer than 2 distinct x values")
        return 0
      }
      FC[0] = exp(C[0]); FC[1] = C[1]; FNC = 2
      for (i = 1; i <= N; i++) pred[i] = FC[0] * exp(FC[1] * X[i])

    } else if (name == "logarithmic") {
      for (i = 1; i <= N; i++) {
        if (X[i] <= 0) {
          FWHY = sprintf("model '\''logarithmic'\'' requires every x > 0, because it fits a straight line to ln(x); got x = %.10g", X[i])
          return 0
        }
      }
      for (i = 1; i <= N; i++) { t[i] = log(X[i]); yv[i] = Y[i] }
      if (!polyfit(t, yv, N, 1, C)) {
        FWHY = sprintf("model '\''logarithmic'\'': the normal equations are singular; the series carries fewer than 2 distinct x values")
        return 0
      }
      FC[0] = C[0]; FC[1] = C[1]; FNC = 2
      for (i = 1; i <= N; i++) pred[i] = FC[0] + FC[1] * log(X[i])

    } else {
      d = (name == "poly") ? deg : 1
      for (i = 1; i <= N; i++) { t[i] = X[i]; yv[i] = Y[i] }
      if (!polyfit(t, yv, N, d, C)) {
        FWHY = sprintf("model '\''%s'\'': the normal equations are singular; the series carries fewer than %d distinct x values", \
                       label(name, deg), d + 1)
        return 0
      }
      FNC = d + 1
      for (i = 0; i < FNC; i++) FC[i] = C[i]
      for (i = 1; i <= N; i++) {
        pred[i] = 0
        for (j = 0; j < FNC; j++) pred[i] += FC[j] * (X[i] ^ j)
      }
    }

    FR2 = rsquared(Y, pred, N)
    return 1
  }

  function emit(m, c, ncoef, r2,   i, s, xmin, xmax) {
    s = ""
    for (i = 0; i < ncoef; i++) s = s ((i > 0) ? " " : "") sprintf("%.10g", c[i])
    xmin = X[1]; xmax = X[1]
    for (i = 2; i <= N; i++) {
      if (X[i] < xmin) xmin = X[i]
      if (X[i] > xmax) xmax = X[i]
    }
    printf "model: %s\n", m
    printf "coefficients: %s\n", s
    printf "domain: %.10g %.10g\n", xmin, xmax
    printf "fit: %.10g\n", r2
  }

  BEGIN {
    EPS = 1e-9

    n = split(points, parts, ",")
    N = 0
    for (i = 1; i <= n; i++) {
      entry = trim(parts[i])
      if (entry == "") continue
      if (split(entry, kv, ":") != 2) bad("malformed point '\''" entry "'\'' (want <x>:<y>)")
      xs = trim(kv[1]); ys = trim(kv[2])
      if (!isnum(xs) || !isnum(ys)) bad("non-numeric point '\''" entry "'\''")
      N++
      X[N] = xs + 0
      Y[N] = ys + 0
    }
    if (N == 0) bad("--points contained no points")

    if (model == "auto") {
      # Ascending in coefficient count, so the strictly-greater-by-EPS test
      # below resolves any tie to the family with the fewest coefficients.
      nf = 4
      FAM[1] = "linear";      FDEG[1] = 0
      FAM[2] = "logarithmic"; FDEG[2] = 0
      FAM[3] = "exponential"; FDEG[3] = 0
      FAM[4] = "poly";        FDEG[4] = 2

      best = ""; bestr = 0; bestnc = 0; skipped = ""
      for (k = 1; k <= nf; k++) {
        if (fitmodel(FAM[k], FDEG[k])) {
          if (best == "" || FR2 > bestr + EPS) {
            best = label(FAM[k], FDEG[k])
            bestr = FR2
            bestnc = FNC
            for (i = 0; i < FNC; i++) BC[i] = FC[i]
          }
        } else {
          skipped = skipped sprintf("  skipped %s: %s\n", label(FAM[k], FDEG[k]), FWHY)
        }
      }

      if (best == "") {
        printf "%s: fit: refusing to fit: model '\''auto'\'' found no admissible family:\n%s", \
               self, skipped > "/dev/stderr"
        exit 1
      }
      if (skipped != "") printf "%s: fit: auto:\n%s", self, skipped > "/dev/stderr"
      emit(best, BC, bestnc, bestr)
      exit 0
    }

    if (model ~ /^poly:/) {
      name = "poly"
      deg = substr(model, 6) + 0
    } else {
      name = model
      deg = 0
    }

    if (!fitmodel(name, deg)) refuse(FWHY)
    emit(label(name, deg), FC, FNC, FR2)
    exit 0
  }
' </dev/null
