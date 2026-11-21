"""Mass / CoM / inertia report from CAD volumes x density + hardware. Writes data/mass_report.json (used by sim/).
Fails (exit 1) if the lower/upper arm mass ratio is outside 0.7-1.0 (default tip, LED-cap tip, and solid-print case)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cad import params as P, assembly as A, massprops as M

ok = True
items = A.build_items()
rep = {"assumptions": {"pla_g_cm3": P.PLA_DENSITY * 1e3, "fill_arms": P.FILL_ARMS, "fill_stand": P.FILL_STAND,
                       "bearing_g": P.BEARING_MASS_G, "bearing_inner_fraction": P.BEARING_INNER_FRACTION,
                       "ballast_g": P.BALLAST_G, "ballast_min_g": P.BALLAST_MIN_G}}
print("== per item (name, group, volume cm3, effective mass g) ==")
for i in items:
    print(f"{i.name:22s} {i.group:6s} {i.shape.Volume()/1000:8.2f} cm3 {i.mass():8.1f} g")
rep["items"] = {i.name: {"group": i.group, "volume_cm3": i.shape.Volume() / 1000, "mass_g": i.mass()} for i in items}

variants = {
    "default (tip = bolt + 2 nuts)": (items, None),
    "solid print (fill 1.0)": (items, 1.0),
    "LED cap tip (cap + CR2032 + bolt + 1 nut)": (A.build_items(True, 1), None),
}
rep["variants"] = {}
for name, (its, fa) in variants.items():
    r = M.arm_props(its, fa)
    rep["variants"][name] = r
    u, l = r["upper"], r["lower"]
    print(f"\n== {name} ==")
    for lab, g in (("upper arm group", u), ("lower arm group", l)):
        print(f"{lab:16s} m={g['mass_g']:7.1f} g  CoM=({g['cm_x_mm']:+.2f}, {g['cm_y_mm']:+.2f}) mm from its pivot (d={g['d_mm']:.1f})  "
              f"I_pivot={g['I_pivot_g_mm2']*1e-9:.3e} kg m^2  I_cm={g['I_cm_g_mm2']*1e-9:.3e} kg m^2")
    ok_r = 0.7 <= r["ratio_lower_over_upper"] <= 1.0
    print(f"ratio lower/upper = {r['ratio_lower_over_upper']:.3f}  (target 0.7-1.0)")
    print(f"{'PASS' if ok_r else 'FAIL'}: mass ratio {r['ratio_lower_over_upper']:.3f} within 0.7-1.0 [{name}]")
    ok &= ok_r
    if name.startswith("default"):
        rep["sim_inputs"] = {"L1_m": P.L1 / 1000, "m1_kg": u["mass_g"] / 1000, "d1_m": u["d_mm"] / 1000,
                             "I1p_kgm2": u["I_pivot_g_mm2"] * 1e-9, "m2_kg": l["mass_g"] / 1000, "d2_m": l["d_mm"] / 1000,
                             "I2p_kgm2": l["I_pivot_g_mm2"] * 1e-9, "L2_m": P.L2 / 1000}
rep["stand"] = {"printed_and_hw_g": M.stand_mass(items, 0.0), "total_with_min_ballast_g": M.stand_mass(items, P.BALLAST_MIN_G),
                "total_with_design_ballast_g": M.stand_mass(items, P.BALLAST_G)}
print(f"\n== stand ==\nprinted+hardware {rep['stand']['printed_and_hw_g']:.0f} g, +{P.BALLAST_MIN_G:.0f} g ballast = "
      f"{rep['stand']['total_with_min_ballast_g']:.0f} g, +{P.BALLAST_G:.0f} g = {rep['stand']['total_with_design_ballast_g']:.0f} g")
# ballast pocket capacity
from cad import parts as pt
pv = pt.pocket_shape().intersect(pt.box(-200, 200, -200, 200, 0, P.BASE_T)).val().Volume() / 1000
rep["ballast_pocket_cm3"] = pv
print(f"ballast pocket volume {pv:.0f} cm3 -> sand(1.6 g/cm3) ~{pv*1.6:.0f} g, steel washers/nuts bulk(~4 g/cm3) ~{pv*4:.0f} g "
      f"(needs >= {P.BALLAST_MIN_G:.0f} g of sand)")
print(f"{'PASS' if pv*1.6 >= P.BALLAST_MIN_G else 'FAIL'}: ballast capacity {pv*1.6:.0f} g sand >= {P.BALLAST_MIN_G:.0f} g")
ok &= pv * 1.6 >= P.BALLAST_MIN_G
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"), exist_ok=True)
json.dump(rep, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mass_report.json"), "w"), indent=1)
sys.exit(0 if ok else 1)
