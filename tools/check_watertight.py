"""Every STL must be watertight with consistent winding and positive volume; every STEP must be a valid solid with volume matching the STL (1 %)."""
import sys, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import trimesh
import cadquery as cq
from cad.export import PART_TABLE

ok = True
for n in PART_TABLE:
    m = trimesh.load(os.path.join(ROOT, "stl", f"{n}.stl"))
    shp = cq.importers.importStep(os.path.join(ROOT, "step", f"{n}.step"))
    valid = all(s.isValid() for s in shp.solids().vals())
    nsol = len(shp.solids().vals())
    vs = sum(s.Volume() for s in shp.solids().vals())
    good = m.is_watertight and m.is_winding_consistent and m.volume > 0 and valid and abs(m.volume - vs) / vs < 0.01
    ok &= good
    print(f"{n:22s} watertight={m.is_watertight} winding={m.is_winding_consistent} STL vol={m.volume/1000:8.2f} cm3 STEP vol={vs/1000:8.2f} cm3 solids={nsol} valid={valid} -> {'ok' if good else 'BAD'}")
a = cq.importers.importStep(os.path.join(ROOT, "step", "assembly.step"))
av = all(s.isValid() for s in a.solids().vals())
print(f"assembly.step: {len(a.solids().vals())} solids, all valid={av}")
ok &= av
print(("PASS" if ok else "FAIL") + ": watertight / valid solids")
sys.exit(0 if ok else 1)
