"""Base tipping margin (acceptance 5). Pivot force on the stand from the simulation (rigid bodies, CAD inertias) applied at the main axle.
Quasi-static tip about the side edges (x = +-BASE_X/2): margin = (W_stand + downward pivot force) * b / (|Fx| * H) at every time step, minimum over
a 60 s run. Desk screws / clamp / rubber friction are NOT counted (conservative). Worst case = damping OFF, releases 90..180 deg, all combos listed.
PASS needs margin >= 1.0 for the design ballast over ALL releases. With only the 1 kg minimum ballast the margin is reported (informational WARN
below 1.0: screw or clamp the base down for big releases)."""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "sim"))
import pendulum as pd
from cad import params as P, assembly as A, massprops as M

p = pd.load_params()
items = A.build_items()
H = P.ZP / 1000.0
b = P.BASE_X / 2 / 1000.0
rows = []
for rel in ((90, 90), (120, 120), (150, 150), (180, 180), (150, 0), (180, 0), (90, 180)):
    for damping in (False, True):
        r = pd.simulate(p, *rel, T=60.0, dt=0.005, damping=damping)
        Fx, Fz = pd.pivot_force(p, r)
        m = {}
        for key, ball in (("min", P.BALLAST_MIN_G), ("design", P.BALLAST_G)):
            W = M.stand_mass(items, ball) / 1000.0 * pd.G
            m[key] = float(((W - Fz) * b / (np.abs(Fx) * H + 1e-12)).min())
        rows.append((rel, damping, float(np.abs(Fx).max()), m["min"], m["design"]))
print(f"axle height {H*1000:.0f} mm, half base width {b*1000:.0f} mm, stand {M.stand_mass(items, P.BALLAST_MIN_G):.0f} g with {P.BALLAST_MIN_G:.0f} g ballast, "
      f"{M.stand_mass(items, P.BALLAST_G):.0f} g with {P.BALLAST_G:.0f} g")
print(f"{'release (th1,th2)':20s}{'damping':9s}{'peak|Fx| N':>12s}{'margin 1 kg':>13s}{'margin design':>15s}")
for rel, d, fx, m1, m2 in rows:
    print(f"{str(rel):20s}{'on' if d else 'off':9s}{fx:12.2f}{m1:13.2f}{m2:15.2f}")
worst = min(r[4] for r in rows)
worst_min = min(r[3] for r in rows)
ok_rows = [r for r in rows if r[3] >= 1.0]
print(f"worst margin, design ballast ({P.BALLAST_G:.0f} g): {worst:.2f} ; worst with only {P.BALLAST_MIN_G:.0f} g: {worst_min:.2f}")
if worst_min < 1.0:
    print(f"WARN-INFO: with only {P.BALLAST_MIN_G:.0f} g ballast and no screws, releases above ~90 deg can tip the base (margin < 1): screw or clamp it down")
from cad import parts as pt
pv = pt.pocket_shape().intersect(pt.box(-300, 300, -300, 300, 0, P.BASE_T)).val().Volume() / 1000
cap = pv * 4.0
print(f"pocket {pv:.0f} cm3 holds ~{cap:.0f} g of steel washers/nuts at 4 g/cm3 bulk (ASSUMED) vs design ballast {P.BALLAST_G:.0f} g")
ok = worst >= 1.0 and cap >= P.BALLAST_G
print(("PASS" if ok else "FAIL") + f": tipping margin design ballast {worst:.2f} >= 1.0 and pocket capacity ok")
sys.exit(0 if ok else 1)
