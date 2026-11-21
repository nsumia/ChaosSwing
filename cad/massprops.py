"""Mass / CoM / inertia from CAD volumes (OCC), per group, about the pivot axis (local z through the origin)."""
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Ax1, gp_Pnt, gp_Dir
from . import params as P
from . import assembly as A


def _unit(shape):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, g)
    c = g.CentreOfMass()
    return g.Mass(), (c.X(), c.Y(), c.Z()), g.MomentOfInertia(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)))


def group_props(items, group, fill_arms=None):
    m = mx = my = I = 0.0
    for it in items:
        if it.group != group:
            continue
        vol, c, iz = _unit(it.shape)
        d = it.density()
        if fill_arms is not None and it.kind == "printed" and it.fill == P.FILL_ARMS:
            d = P.PLA_DENSITY * fill_arms
        mi = vol * d
        m += mi; mx += mi * c[0]; my += mi * c[1]; I += iz * d
    cx, cy = mx / m, my / m
    return {"mass_g": m, "cm_x_mm": cx, "cm_y_mm": cy, "d_mm": -cy, "I_pivot_g_mm2": I,
            "I_cm_g_mm2": I - m * (cx * cx + cy * cy)}


def arm_props(items, fill_arms=None):
    """upper about main pivot; lower about elbow; returns dict with ratio."""
    u = group_props(items, "upper", fill_arms)
    l = group_props(items, "lower", fill_arms)
    return {"upper": u, "lower": l, "ratio_lower_over_upper": l["mass_g"] / u["mass_g"]}


def stand_mass(items, ballast_g):
    printed = sum(i.mass() for i in items if i.group == "stand")
    return printed + ballast_g
