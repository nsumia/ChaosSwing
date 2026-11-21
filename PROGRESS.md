# ChaosSwing progress

## 2026-11-21 v1 (branch agent/chaosswing-v1)
- Parametric CadQuery model (cad/), 10 printable part files + assembly STEP, iso/exploded/pose renders (img/).
- Checks: bed fit, watertight/valid, 36x36 collision sweep with +-3 mm axial shift test, pivot height vs reach, mass/CoM/inertia, arm mass ratio, tipping margin.
- Rigid-body simulation (sim/) with CAD inertias: divergence plot, tip trace, GIF; energy tests. tools/run_tests.sh = single test command.
- Open: no print/measurement yet, damping assumed, tipping margin 1.05 worst case with 3 kg ballast, GitHub repo not created.
