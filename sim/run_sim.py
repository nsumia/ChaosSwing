"""Writes img/divergence.png, img/tip_trace.png, img/divergence.gif and data/sim_summary.json.
Two releases 0.1 deg apart (upper arm 150 deg held by the pin, lower arm held in line by hand, both released from rest).
SIMULATION (rigid bodies, CAD inertias, assumed viscous joint damping), not a measurement."""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pendulum as pd

ROOT = os.path.join(HERE, "..")
IMG = os.path.join(ROOT, "img"); os.makedirs(IMG, exist_ok=True)
REL = (150.0, 150.0)
DTH = 0.1
T = 40.0
p = pd.load_params()
Emin = -pd.G * (pd.mass_matrix_terms(p)[3] + p["m2"] * p["d2"])
ra = pd.simulate(p, REL[0], REL[1], T=T, dt=0.005)
rb = pd.simulate(p, REL[0] + DTH, REL[1], T=T, dt=0.005)
t = ra["t"]
sep1 = np.degrees(np.abs(ra["th1"] - rb["th1"])); sep2 = np.degrees(np.abs(ra["th2"] - rb["th2"]))
Ea = ra["E"] - Emin
tip_a = pd.tip_xy(p, ra["th1"], ra["th2"]); tip_b = pd.tip_xy(p, rb["th1"], rb["th2"])

# ---- divergence.png
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
ax[0, 0].plot(t, np.degrees(ra["th2"]), lw=1, label=f"release A: {REL[0]:.1f} / {REL[1]:.1f} deg")
ax[0, 0].plot(t, np.degrees(rb["th2"]), lw=1, label=f"release B: {REL[0]+DTH:.1f} / {REL[1]:.1f} deg")
ax[0, 0].set_title("lower-arm angle (unwrapped)"); ax[0, 0].set_xlabel("t [s]"); ax[0, 0].set_ylabel("deg"); ax[0, 0].legend(fontsize=8)
ax[0, 1].semilogy(t, np.maximum(sep1, 1e-4), label="|d theta1|"); ax[0, 1].semilogy(t, np.maximum(sep2, 1e-4), label="|d theta2|")
ax[0, 1].axhline(DTH, color="k", ls=":", lw=0.8); ax[0, 1].set_title("separation of the two releases (0.1 deg start)"); ax[0, 1].set_xlabel("t [s]"); ax[0, 1].set_ylabel("deg"); ax[0, 1].legend(fontsize=8)
ax[1, 0].plot(t, Ea * 1000); ax[1, 0].set_title("mechanical energy above hanging rest (damped)"); ax[1, 0].set_xlabel("t [s]"); ax[1, 0].set_ylabel("mJ")
ax[1, 1].plot(tip_a[2] * 1000, tip_a[3] * 1000, lw=0.5, label="A"); ax[1, 1].plot(tip_b[2] * 1000, tip_b[3] * 1000, lw=0.5, label="B", alpha=0.8)
ax[1, 1].set_aspect("equal"); ax[1, 1].set_title("lower-arm tip trace (mm, axle at origin)"); ax[1, 1].legend(fontsize=8)
fig.suptitle(f"ChaosSwing SIMULATION (not a measurement): rigid bodies from CAD inertias, assumed joint damping {pd.B_DEFAULT:.0e} N m s/rad", fontsize=10)
fig.tight_layout(); fig.savefig(f"{IMG}/divergence.png", dpi=110); plt.close(fig)

# ---- tip_trace.png
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
for a, tip, c, lab in ((ax[0], tip_a, "tab:blue", "release A"), (ax[1], tip_b, "tab:orange", "release B (+0.1 deg)")):
    a.plot(tip[2] * 1000, tip[3] * 1000, lw=0.4, color=c); a.set_aspect("equal"); a.set_title(f"{lab}: tip trace, {T:.0f} s"); a.plot(0, 0, "k+")
    a.set_xlim(-330, 330); a.set_ylim(-330, 330)
fig.suptitle("SIMULATION: same start except 0.1 deg on the upper arm", fontsize=10); fig.tight_layout(); fig.savefig(f"{IMG}/tip_trace.png", dpi=110); plt.close(fig)

# ---- GIF (PIL drawing, 2x supersampled)
W = 420; S = 2; scale = (W * S / 2 - 30 * S) / 0.33    # px per metre
FPS = 10; DUR = 20.0
idx = np.arange(0, int(DUR * 200) + 1, 200 // FPS)    # dt=0.005 -> 200 samples/s
cx = cy = W * S // 2


def px(x, z):
    return cx + x * scale, cy - z * scale


frames = []
trail = 140
for k, i in enumerate(idx):
    im = Image.new("RGB", (W * S, W * S), "white"); d = ImageDraw.Draw(im)
    for r, col, tip in ((rb, (240, 130, 30), tip_b), (ra, (30, 100, 220), tip_a)):
        j0 = max(0, i - trail * (200 // FPS) // 4)
        pts = [px(tip[2][m], tip[3][m]) for m in range(j0, i + 1, 4)]
        if len(pts) > 1:
            d.line(pts, fill=tuple(int(255 - (255 - c) * 0.55) for c in col), width=S)
        e = px(tip[0][i], tip[1][i]); tp = px(tip[2][i], tip[3][i])
        d.line([px(0, 0), e, tp], fill=col, width=5 * S)
        d.ellipse([e[0] - 5 * S, e[1] - 5 * S, e[0] + 5 * S, e[1] + 5 * S], fill=col)
        d.ellipse([tp[0] - 7 * S, tp[1] - 7 * S, tp[0] + 7 * S, tp[1] + 7 * S], fill=col)
    d.ellipse([cx - 6 * S, cy - 6 * S, cx + 6 * S, cy + 6 * S], fill=(60, 60, 60))
    d.text((10 * S, 8 * S), f"SIMULATION  t = {t[i]:5.1f} s   blue: {REL[0]:.1f}/{REL[1]:.0f} deg   orange: {REL[0]+DTH:.1f}/{REL[1]:.0f} deg", fill=(0, 0, 0))
    d.text((10 * S, 22 * S), f"tip separation {1000*np.hypot(tip_a[2][i]-tip_b[2][i], tip_a[3][i]-tip_b[3][i]):6.1f} mm", fill=(0, 0, 0))
    frames.append(im.resize((W, W), Image.LANCZOS).quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
frames[0].save(f"{IMG}/divergence.gif", save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0, optimize=True)

sep_tip = 1000 * np.hypot(tip_a[2] - tip_b[2], tip_a[3] - tip_b[3])
first = lambda thr: float(t[np.argmax(sep_tip > thr)]) if sep_tip.max() > thr else None
summ = {"release_deg": REL, "delta_deg": DTH, "damping_Nms_per_rad": pd.B_DEFAULT, "T_s": T,
        "t_tip_separation_gt_10mm_s": first(10), "t_tip_separation_gt_100mm_s": first(100),
        "max_tip_separation_mm": float(sep_tip.max()),
        "energy_above_rest_mJ_start": float(Ea[0] * 1000),
        "t_energy_below_25pct_s": float(t[np.argmax(Ea < 0.25 * Ea[0])]) if (Ea < 0.25 * Ea[0]).any() else None,
        "t_energy_below_10pct_s": float(t[np.argmax(Ea < 0.10 * Ea[0])]) if (Ea < 0.10 * Ea[0]).any() else None}
# damping sensitivity (single trajectories of a chaotic system: indicative only, NOT monotonic in b)
def last_flip(r):
    """time of the last crossing of the lower arm through 'folded over the upper arm' (relative angle = 180 deg): proxy for the end of wild motion"""
    rel = r["th2"] - r["th1"]
    k = np.floor((rel + np.pi) / (2 * np.pi))
    ch = np.nonzero(np.diff(k))[0]
    return float(r["t"][ch[-1]]) if len(ch) else None


summ["t_last_lower_arm_flip_s_release_A"] = last_flip(ra)
sens = {}
for b in (2e-5, 5e-5, 1e-4, 2e-4):
    r = pd.simulate(p, REL[0], REL[1], T=120.0, dt=0.01, b=b)
    E = r["E"] - Emin
    sens[str(b)] = {"t_last_lower_arm_flip_s": last_flip(r), "t_E_below_25pct_s": float(r["t"][np.argmax(E < 0.25 * E[0])]) if (E < 0.25 * E[0]).any() else None,
                    "t_E_below_10pct_s": float(r["t"][np.argmax(E < 0.10 * E[0])]) if (E < 0.10 * E[0]).any() else None}
summ["damping_sensitivity"] = sens
json.dump(summ, open(os.path.join(ROOT, "data", "sim_summary.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
print("wrote img/divergence.png img/tip_trace.png img/divergence.gif")
