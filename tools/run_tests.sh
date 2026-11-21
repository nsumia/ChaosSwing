#!/usr/bin/env bash
# THE test command for ChaosSwing: builds all parts (STEP/STL/assembly), renders, runs every CAD check and the simulation tests.
# Exits non-zero if any step exits non-zero, a Traceback or a FAIL line appears, or fewer PASS lines than expected are printed.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-$HOME/tools/cad-venv/bin/python}
export PYTHONDONTWRITEBYTECODE=1
EXPECTED_PASS=${EXPECTED_PASS:-26}
log=$(mktemp); trap 'rm -f "$log"' EXIT
reasons=()

run() { # label cmd...
  local label=$1; shift
  echo "--- $label"
  "$@" 2>&1 | grep -v "^Fontconfig error\|vtkXOpenGLRenderWindow.*WARN| bad X server\|^$" | tee -a "$log"
  local rc=${PIPESTATUS[0]}
  [ "$rc" -eq 0 ] || reasons+=("$label exited $rc")
}

run "build parts + assembly (STEP/STL)"      $PY cad/build_all.py
run "mass / CoM / inertia / arm mass ratio"   $PY tools/mass_report.py
run "bed fit"                                 $PY tools/check_bedfit.py
run "watertight / valid solids"               $PY tools/check_watertight.py
run "pivot height vs reach, axial clearances" $PY tools/check_pivot.py
run "collision sweep 36 x 36"                 $PY tools/check_collision.py
run "simulation sanity tests"                 $PY sim/test_sim.py
run "base tipping margin"                     $PY tools/check_tipping.py
run "simulation outputs (divergence plot/GIF)" $PY sim/run_sim.py
run "renders (iso, exploded, poses)"          $PY cad/make_renders.py

for f in img/iso.png img/exploded.png img/poses.png img/divergence.png img/divergence.gif img/tip_trace.png; do
  if [ -s "$f" ]; then echo "PASS: output exists $f"; else echo "FAIL: missing output $f"; reasons+=("missing $f"); fi
done | tee -a "$log"

npass=$(grep -c '^PASS' "$log")
nfail=$(grep -c '^FAIL\|Traceback' "$log")
echo "=== PASS lines: $npass (expected >= $EXPECTED_PASS), FAIL/Traceback lines: $nfail"
[ "$nfail" -eq 0 ] || reasons+=("$nfail FAIL/Traceback lines")
[ "$npass" -ge "$EXPECTED_PASS" ] || reasons+=("only $npass PASS lines")
if [ ${#reasons[@]} -gt 0 ]; then
  printf 'TESTS FAILED: %s\n' "${reasons[@]}"; exit 1
fi
echo "ALL TESTS PASSED"
