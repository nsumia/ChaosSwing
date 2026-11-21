"""Bed fit: every exported printable STEP (print orientation) must fit 220 x 220 x 250 mm. Prints a table; exit 1 on any failure."""
import sys, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import cadquery as cq
from cad import params as P
from cad.export import PART_TABLE

bx, by, bz = P.BED
ok = True
print(f"{'part':22s}{'X':>8s}{'Y':>8s}{'Z':>8s}   margin to {bx:.0f}x{by:.0f}x{bz:.0f}   qty")
for n, row in PART_TABLE.items():
    f = os.path.join(ROOT, "step", f"{n}.step")
    bb = cq.importers.importStep(f).val().BoundingBox()
    dx, dy, dz = bb.xlen, bb.ylen, bb.zlen
    fit = (dx <= bx and dy <= by) or (dx <= by and dy <= bx)
    fit &= dz <= bz
    ok &= fit
    print(f"{n:22s}{dx:8.1f}{dy:8.1f}{dz:8.1f}   {min(bx-dx, by-dy):6.1f} / {bz-dz:6.1f}       {row[2]}   {'ok' if fit else 'DOES NOT FIT'}")
print(("PASS" if ok else "FAIL") + ": bed fit (all printable parts)")
sys.exit(0 if ok else 1)
