"""Simulation sanity tests. Prints PASS:/FAIL: lines; exit 1 on any failure."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pendulum as pd

p = pd.load_params()
fails = 0


def check(name, ok, info=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + (f"  [{info}]" if info else ""))
    fails += (not ok)


# 1. energy conservation, damping off, 10 s, big release (chaotic regime) and a small one
for th in ((120.0, 120.0), (150.0, 30.0), (40.0, -20.0)):
    r = pd.simulate(p, *th, T=10.0, damping=False)
    E = r["E"]
    scale = E.max() - (-pd.G * (pd.mass_matrix_terms(p)[3] + p["m2"] * p["d2"]))   # span vs minimum possible energy
    drift = (E.max() - E.min()) / scale * 100
    check(f"energy conserved (damping off, 10 s, release {th})", drift < 1.0, f"max-min drift {drift:.2e} % of E above the hanging minimum")

# 2. energy decays monotonically with damping
r = pd.simulate(p, 120.0, 120.0, T=60.0, damping=True)
dE = np.diff(r["E"])
check("energy decays monotonically (damping on, 60 s)", dE.max() < 1e-9, f"max dE = {dE.max():.2e} J, E0={r['E'][0]:.4f} -> E60={r['E'][-1]:.4f} J")

# 3. small-angle period vs linear normal modes
M11, M22, c, A = pd.mass_matrix_terms(p)
K = np.array([[pd.G * A, 0], [0, pd.G * p["m2"] * p["d2"]]])
Mm = np.array([[M11, c], [c, M22]])
w = np.sqrt(np.sort(np.linalg.eigvals(np.linalg.solve(Mm, K)).real))
r = pd.simulate(p, 0.2, 0.0, T=20.0, damping=False, dt=0.002)
sp = np.abs(np.fft.rfft(r["th1"] - r["th1"].mean() ))
fr = np.fft.rfftfreq(len(r["t"]), 0.002) * 2 * np.pi
pk = fr[np.argsort(sp)[::-1][:1]][0]
check("small-angle motion shows a linear normal-mode frequency", min(abs(pk - w)) < 0.15, f"FFT peak {pk:.2f} rad/s, modes {w[0]:.2f}, {w[1]:.2f} rad/s")

# 4. sensitive dependence: 0.1 deg apart diverges
ra = pd.simulate(p, 150.0, 150.0, T=40.0, damping=True)
rb = pd.simulate(p, 150.1, 150.0, T=40.0, damping=True)
sep = np.abs(ra["th2"] - rb["th2"])
check("two releases 0.1 deg apart diverge (|dtheta2| > 60 deg within 40 s)", sep.max() > np.radians(60), f"max |dtheta2| = {np.degrees(sep.max()):.0f} deg")
check("initial separation is 0.1 deg", abs(np.degrees(abs(ra['th1'][0] - rb['th1'][0])) - 0.1) < 1e-9)

# 5. pivot force: static value equals total weight
Fx, Fz = pd.pivot_force(p, pd.simulate(p, 0.0, 0.0, T=0.1, damping=False))
check("static pivot force = weight", abs(Fz[0] + (p["m1"] + p["m2"]) * pd.G) < 1e-9 and abs(Fx[0]) < 1e-12, f"Fz={Fz[0]:.4f} N")
print(f"summary: {fails} failing sim checks")
sys.exit(1 if fails else 0)
