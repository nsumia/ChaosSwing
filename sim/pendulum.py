"""Rigid-body double pendulum (planar) using the CAD mass/inertia numbers (data/mass_report.json).

Angles are measured from the downward vertical, counter-clockwise as seen by the viewer (theta=0 hangs down).
Body 1 pivots about the main axle: mass m1, CoM at d1 along the arm, inertia I1p about the pivot.
Body 2 pivots about the elbow: mass m2, CoM at d2, inertia I2p about the elbow.
Joint damping is an ASSUMPTION: viscous torque -b*omega at each joint (default 5e-5 N m s/rad per joint, see README).
This is a SIMULATION, not a measurement.
"""
import json, os
import numpy as np
from scipy.integrate import solve_ivp

G = 9.81
HERE = os.path.dirname(os.path.abspath(__file__))
B_DEFAULT = 5.0e-5   # N m s / rad per joint (ASSUMED: brief ~2e-4 N m bearing torque at ~7 rad/s plus some air drag)


def load_params(path=None):
    path = path or os.path.join(HERE, "..", "data", "mass_report.json")
    s = json.load(open(path))["sim_inputs"]
    return dict(L1=s["L1_m"], m1=s["m1_kg"], d1=s["d1_m"], I1=s["I1p_kgm2"], m2=s["m2_kg"], d2=s["d2_m"], I2=s["I2p_kgm2"],
                L2=s["L2_m"])


def mass_matrix_terms(p):
    M11 = p["I1"] + p["m2"] * p["L1"] ** 2
    M22 = p["I2"]
    c = p["m2"] * p["L1"] * p["d2"]
    A = p["m1"] * p["d1"] + p["m2"] * p["L1"]
    return M11, M22, c, A


def accel(p, th1, w1, th2, w2, b1, b2):
    M11, M22, c, A = mass_matrix_terms(p)
    d = th1 - th2
    Q1 = -b1 * w1 + b2 * (w2 - w1)
    Q2 = -b2 * (w2 - w1)
    r1 = Q1 - c * np.sin(d) * w2 ** 2 - G * A * np.sin(th1)
    r2 = Q2 + c * np.sin(d) * w1 ** 2 - G * p["m2"] * p["d2"] * np.sin(th2)
    a11, a12, a22 = M11, c * np.cos(d), M22
    det = a11 * a22 - a12 * a12
    return (a22 * r1 - a12 * r2) / det, (a11 * r2 - a12 * r1) / det


def energy(p, th1, w1, th2, w2):
    M11, M22, c, A = mass_matrix_terms(p)
    T = 0.5 * M11 * w1 ** 2 + 0.5 * M22 * w2 ** 2 + c * np.cos(th1 - th2) * w1 * w2
    V = -G * (A * np.cos(th1) + p["m2"] * p["d2"] * np.cos(th2))
    return T + V


def simulate(p, th1_deg, th2_deg, T=30.0, dt=0.01, damping=True, b=B_DEFAULT, w1=0.0, w2=0.0):
    b1 = b2 = b if damping else 0.0

    def f(t, y):
        a1, a2 = accel(p, y[0], y[1], y[2], y[3], b1, b2)
        return [y[1], a1, y[3], a2]

    t = np.arange(0.0, T + 1e-12, dt)
    sol = solve_ivp(f, (0, T), [np.radians(th1_deg), w1, np.radians(th2_deg), w2], t_eval=t, method="DOP853", rtol=1e-11, atol=1e-12)
    th1, w1s, th2, w2s = sol.y
    return dict(t=sol.t, th1=th1, w1=w1s, th2=th2, w2=w2s, E=energy(p, th1, w1s, th2, w2s), p=p, b=b1)


def pivot_force(p, r, b=None):
    """force of the pendulum on the stand at the main axle (N): (Fx right, Fz up), from sum m a_cm - m g. Damping torques are internal/axle only."""
    t, th1, w1, th2, w2 = r["t"], r["th1"], r["w1"], r["th2"], r["w2"]
    bb = r["b"]
    a1, a2 = accel(p, th1, w1, th2, w2, bb, bb)
    # CoM accelerations (X right, Z up); position = L (sin, -cos)
    def acc(L, th, w, al):
        return L * (np.cos(th) * al - np.sin(th) * w ** 2), L * (np.sin(th) * al + np.cos(th) * w ** 2)
    ax1, az1 = acc(p["d1"], th1, w1, a1)
    ax2a, az2a = acc(p["L1"], th1, w1, a1)
    ax2b, az2b = acc(p["d2"], th2, w2, a2)
    sx = p["m1"] * ax1 + p["m2"] * (ax2a + ax2b)
    sz = p["m1"] * az1 + p["m2"] * (az2a + az2b)
    Fs_x, Fs_z = sx, sz + (p["m1"] + p["m2"]) * G            # force by stand on pendulum
    return -Fs_x, -Fs_z


def tip_xy(p, th1, th2, tip_r=None):
    L1, L2 = p["L1"], p["L2"]
    ex, ez = L1 * np.sin(th1), -L1 * np.cos(th1)
    return ex, ez, ex + L2 * np.sin(th2), ez - L2 * np.cos(th2)
