"""Build every printed part (print orientation) -> step/ and stl/, and the full assembly STEP (assembled pose).
Usage: python cad/build_all.py [outdir]   (default: repo root)"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cadquery as cq
from cad import params as P, assembly as A
from cad.export import PART_TABLE, print_shape

COLORS = {"stand": (0.55, 0.57, 0.60), "upper": (0.25, 0.50, 0.85), "lower": (0.95, 0.55, 0.15)}
POSE = (60.0, 150.0)       # theta1, theta2 (absolute, deg) used for the assembly STEP


def _fix_stamp(path):
    """make STEP output deterministic: replace the FILE_NAME timestamp written by OpenCascade"""
    import re
    t = open(path).read()
    t = re.sub(r"(FILE_NAME\('[^']*',')[^']*(')", r"\g<1>2000-01-01T00:00:00\g<2>", t, count=1)
    open(path, "w").write(t)


def main(root=None):
    root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.makedirs(f"{root}/step", exist_ok=True); os.makedirs(f"{root}/stl", exist_ok=True)
    for n in PART_TABLE:
        s = print_shape(n)
        cq.exporters.export(cq.Workplane("XY").add(s), f"{root}/step/{n}.step")
        _fix_stamp(f"{root}/step/{n}.step")
        cq.exporters.export(cq.Workplane("XY").add(s), f"{root}/stl/{n}.stl", tolerance=0.02, angularTolerance=0.1)
        bb = s.BoundingBox()
        print(f"exported {n}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
    asm = cq.Assembly(name="ChaosSwing")
    for it in A.build_items(led_cap=True, tip_nuts=1):
        col = COLORS[it.group] if it.kind == "printed" else (0.78, 0.78, 0.8) if it.kind == "steel" else (0.2, 0.2, 0.22)
        asm.add(cq.Workplane("XY").add(A.pose_world(it, *POSE)), name=it.name, color=cq.Color(*col))
    # OpenCascade orders the colour/style entities of an assembly STEP non-deterministically (pointer hash order), so the committed
    # file is only rewritten on request: CS_REGEN_ASSEMBLY=1 python cad/build_all.py. A normal test run leaves it untouched.
    target = f"{root}/step/assembly.step"
    if os.environ.get("CS_REGEN_ASSEMBLY") == "1" or not os.path.exists(target):
        asm.save(target)
        _fix_stamp(target)
    else:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            asm.save(f"{td}/a.step")      # still build + save it, to prove the assembly exports
        print("assembly.step kept (set CS_REGEN_ASSEMBLY=1 to rewrite)")
    print("exported assembly.step")


if __name__ == "__main__":
    main(*sys.argv[1:])
