"""Collision sweep: upper arm 0-360 deg (10 deg steps), lower arm 0-360 deg relative to it (10 deg steps) = 36 x 36 poses.
Pairs tested (different groups only): upper vs stand, lower vs stand, lower vs upper, and arms vs base top plane.
Method: world-frame AABB prefilter, then exact OCC boolean common volume. Each moving group is also shifted along the hub axis by
-3, -1.5, +1.5, +3 mm: zero overlap at the shifted positions proves >= 3 mm axial clearance between the planes.
Also runs a self-test (lower arm plane moved into the upper arm plane must be detected)."""
import sys, os, math, time, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from multiprocessing import Pool
import cadquery as cq
from cad import params as P, assembly as A

STEP = int(os.environ.get("SWEEP_STEP", 10))
SHIFTS = (0.0, -1.5, 1.5, -3.0, 3.0)
TOL_MM3 = 1.0
_items = None
_bb = None


def _init():
    global _items, _bb
    _items = A.build_items()
    _bb = {}
    for i in _items:
        b = (i.shape if i.group == 'lower' else A.pose_local(i, 0, 0)).BoundingBox()
        _bb[i.name] = np.array([[x, y, z] for x in (b.xmin, b.xmax) for y in (b.ymin, b.ymax) for z in (b.zmin, b.zmax)])


def aabb(item, th1, th2, dz):
    c = _bb[item.name]
    if item.group == "stand":
        pts = c.copy()
    else:
        pts = c.copy()
        if item.group == "lower":
            pts = _rot(pts, th2); pts[:, 1] -= P.L1
        pts = _rot(pts, th1)
    pts[:, 2] += dz if item.group != "stand" else 0.0
    return pts.min(0), pts.max(0)


def _rot(p, deg):
    t = math.radians(deg); c, s = math.cos(t), math.sin(t)
    q = p.copy(); q[:, 0] = p[:, 0] * c - p[:, 1] * s; q[:, 1] = p[:, 0] * s + p[:, 1] * c
    return q


def _overlap(a, b):
    return np.all(a[0] <= b[1]) and np.all(b[0] <= a[1])


def shape_at(item, th1, th2, dz):
    s = A.pose_local(item, th1, th2)
    return s.translate(cq.Vector(0, 0, dz)) if dz else s


def pair_volume(a, b, th1, th2, dz_moving_group, moving):
    sa = shape_at(a, th1, th2, dz_moving_group if a.group == moving else 0.0)
    sb = shape_at(b, th1, th2, dz_moving_group if b.group == moving else 0.0)
    try:
        return sa.intersect(sb).Volume()
    except Exception:
        return float("nan")


def tests_for_pose(args):
    th1, th2, lower_dz_extra, mode = args       # mode: 'all' | 'upper-stand' | 'lower-upper' | 'lower-stand'
    if _items is None:
        _init()
    its = _items
    by = {g: [i for i in its if i.group == g] for g in ("stand", "upper", "lower")}
    n_pairs = n_bool = 0
    worst = 0.0
    bad = []
    plan = {"all": (("upper", ("stand",)), ("lower", ("stand", "upper"))),
            "upper-stand": (("upper", ("stand",)),), "lower-upper": (("lower", ("upper",)),),
            "lower-stand": (("lower", ("stand",)),)}[mode]
    for moving, others in plan:
        for dz in SHIFTS:
            for og in others:
                for a in by[moving]:
                    dza = dz + (lower_dz_extra if moving == "lower" else 0.0)
                    ab = aabb(a, th1, th2, dza)
                    for b in by[og]:
                        n_pairs += 1
                        bb = aabb(b, th1, th2, 0.0 if og == "stand" else 0.0)
                        if not _overlap(ab, bb):
                            continue
                        n_bool += 1
                        sa = shape_at(a, th1, th2, dza)
                        sb = shape_at(b, th1, th2, 0.0)
                        try:
                            v = sa.intersect(sb).Volume()
                        except Exception:
                            v = float("nan")
                        if not (v <= TOL_MM3):
                            bad.append((a.name, b.name, round(th1), round(th2), dz, round(v, 1)))
                        worst = max(worst, v if v == v else 1e9)
    # arms vs base top plane (z) : lowest point of every arm-group solid above the base top
    zmin = 1e9
    for g in ("upper", "lower"):
        for a in by[g]:
            lo, _ = aabb(a, th1, th2, 0.0)
            # local frame: world z = y_local + ZP  (world Z = local y + ZP)
            zmin = min(zmin, lo[1] + P.ZP)
    return n_pairs, n_bool, worst, bad, zmin


def run(angles1, angles_rel, extra=0.0, procs=12, mode="all"):
    """mode 'all' tests every pair at every pose. 'split' (default for the full sweep) is equivalent but cheaper: upper-vs-stand depends only on
    theta1 and lower-vs-upper only on the relative angle, so those two are run over their 36 distinct values; lower-vs-stand is run on all poses."""
    if mode == "all":
        jobs = [(t1, t1 + r, extra, "all") for t1 in angles1 for r in angles_rel]
    else:
        jobs = ([(t1, t1, extra, "upper-stand") for t1 in angles1] + [(0, r, extra, "lower-upper") for r in angles_rel]
                + [(t1, t1 + r, extra, "lower-stand") for t1 in angles1 for r in angles_rel])
    with Pool(procs) as pool:
        res = pool.map(tests_for_pose, jobs, chunksize=4)
    return jobs, res


if __name__ == "__main__":
    t0 = time.time()
    angs = list(range(0, 360, STEP))
    jobs, res = run(angs, angs, mode='split')
    n_pairs = sum(r[0] for r in res); n_bool = sum(r[1] for r in res)
    worst = max(r[2] for r in res); bad = [b for r in res for b in r[3]]
    zmin_low = min(r[4] for r in res)
    print(f"poses swept: {len(angs)} x {len(angs)} = {len(angs)**2} (theta1 x relative angle; {len(jobs)} jobs), shifts {SHIFTS} mm, pair tests {n_pairs}, AABB-passed exact boolean tests {n_bool}")
    print(f"max overlap volume over all poses/pairs/shifts: {worst:.3f} mm^3 (tolerance {TOL_MM3})")
    print(f"lowest arm point (conservative AABB) above desk: {zmin_low:.1f} mm; base top at {P.BASE_T:.1f} mm -> clearance {zmin_low - P.BASE_T:.1f} mm")
    ok = not bad and zmin_low - P.BASE_T >= 15.0
    for b in bad[:10]:
        print("  OVERLAP", b)
    # self-test: push the lower arm plane back by 30 mm into the upper arm plane; the checker must flag it
    _, res2 = run([0, 90], [0, 90, 180], extra=-30.0)
    detected = sum(len(r[3]) for r in res2)
    print(f"self-test (lower group moved back 30 mm): {detected} overlaps flagged -> {'detected' if detected else 'NOT DETECTED'}")
    ok &= detected > 0
    print(("PASS" if ok else "FAIL") + f": collision sweep ({time.time()-t0:.0f} s)")
    sys.exit(0 if ok else 1)
