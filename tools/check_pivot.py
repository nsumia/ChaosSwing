"""Pivot height vs reach (acceptance 3): axle height above the base top >= (L1 + L2 + tip radius) + 15 mm, measured from the CAD arm solids;
arms never touch the base/desk; stack clearances >= 3 mm in the axial direction (design values from the solids)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import math
from cad import params as P, assembly as A

items = A.build_items()
ok = True
# straight-down pose: lowest point of every arm-group solid
zs = {}
for it in items:
    if it.group in ("upper", "lower"):
        zs[it.name] = A.pose_world(it, 0, 0).BoundingBox().zmin
low_name = min(zs, key=zs.get)
low = zs[low_name]
reach = P.ZP - low
req = reach + 15.0
print(f"tip radius (lower arm boss) {P.TIP_BOSS_R:.1f} mm; reach from the axle measured on the CAD = {reach:.1f} mm (nominal L1+L2+tip = {P.REACH_NOMINAL:.1f}); lowest solid: {low_name}")
print(f"required axle height above base top >= reach + 15 = {req:.1f} mm; design PIVOT_H = {P.PIVOT_H:.1f} mm")
c = P.PIVOT_H >= req
print(("PASS" if c else "FAIL") + f": pivot height vs reach (margin {P.PIVOT_H - req:.1f} mm)")
ok &= c
c = abs(reach - P.REACH_NOMINAL) < 1.0
print(("PASS" if c else "FAIL") + f": measured reach matches nominal within 1 mm ({reach:.1f} vs {P.REACH_NOMINAL:.1f})")
ok &= c
clear = low - P.BASE_T
c = clear >= 15
print(("PASS" if c else "FAIL") + f": arms hang {clear:.1f} mm above the base top (>= 15) and {low:.1f} mm above the desk")
ok &= c
# axial stack gaps (design numbers cross-checked against the solids' bounding boxes)
bb = {it.name: A.pose_local(it, 0, 0).BoundingBox() for it in items} if False else {it.name: it.shape.BoundingBox() for it in items}
gaps = {
    "ring front -> upper hub rear": bb["upper_arm"].zmin - bb["release_ring"].zmax,
    "upper hub front -> main washer": bb["main_washer"].zmin - bb["upper_arm"].zmax,
    "upper elbow boss front -> lower hub rear": bb["lower_arm"].zmin - bb["upper_arm"].zmax,
    "lower hub front -> elbow washer": bb["elbow_washer"].zmin - bb["lower_arm"].zmax,
    "main bolt head top -> lower bar rear": bb["lower_arm"].zmin + 0 - bb["main_bolt_M8x60"].zmax,
}
# lower bar rear face is P.LB0 (hub is wider than the bar)
gaps["main bolt head top -> lower bar rear"] = P.LB0 - bb["main_bolt_M8x60"].zmax
gaps["upper bar front vs lower bar rear"] = P.LB0 - bb["upper_arm"].zmax
for k, v in gaps.items():
    g = v >= P.CLR_MIN - 1e-9
    ok &= g
    print(f"  axial gap {k}: {v:.1f} mm {'ok' if g else 'TOO SMALL'}")
print(("PASS" if ok else "FAIL") + ": pivot / clearance summary")
sys.exit(0 if ok else 1)
