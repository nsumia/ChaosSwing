"""Assembly model: list of items with group (stand/upper/lower), kind, frame (L local / W world) and shapes.
Groups: stand = fixed; upper = rotates about the main axle; lower = rotates about the elbow (built with its pivot at the origin)."""
import functools, math
import cadquery as cq
from . import params as P, parts as pt
from .cqh import cyl, tube, hexp


class Item:
    def __init__(self, name, group, kind, frame, wp, mass_g=None, fill=None, qty=1, material=""):
        self.name, self.group, self.kind, self.frame = name, group, kind, frame
        self.shape = wp.val() if hasattr(wp, "val") else wp
        self.mass_override, self.fill, self.qty, self.material = mass_g, fill, qty, material

    def density(self):
        """g/mm3 effective (volume * density * fill, or the override mass spread over the volume)."""
        v = self.shape.Volume()
        if self.mass_override is not None:
            return self.mass_override / v
        if self.kind == "printed":
            return P.PLA_DENSITY * self.fill
        return P.STEEL_DENSITY

    def mass(self):
        return self.shape.Volume() * self.density()


# ---- hardware solids ----------------------------------------------------------------------------
def bolt(x, y, z_under, length, shank_r=4.0):
    s = cyl(shank_r, z_under - length, z_under, x, y)
    return s.union(hexp(P.M8_AF, z_under, z_under + P.M8_HEAD_H, x, y))


def bolt_fwd(x, y, z_under, length, shank_r=4.0):
    """head behind (rear, lower z), shank pointing forward (+z)."""
    s = cyl(shank_r, z_under, z_under + length, x, y)
    return s.union(hexp(P.M8_AF, z_under - P.M8_HEAD_H, z_under, x, y))


def nut(x, y, z0, h=P.M8_NUT_H):
    return hexp(P.M8_AF, z0, z0 + h, x, y).cut(cyl(4.0, z0 - 1, z0 + h + 1, x, y))


def washer(x, y, z0):
    return tube(P.M8_WASHER_OD / 2, P.M8_CLR / 2, z0, z0 + P.M8_WASHER_T, x, y)


R_INNER = 6.0      # bearing inner race outer radius
R_OUTER_IN = 6.2   # outer race inner radius (0.2 gap)


def bearing_parts(name, group_in, group_out, z0, x, y):
    inner = tube(R_INNER, 4.0, z0, z0 + P.BRG_W, x, y)
    outer = tube(P.BRG_OD / 2, R_OUTER_IN, z0, z0 + P.BRG_W, x, y)
    mi = P.BEARING_MASS_G * P.BEARING_INNER_FRACTION
    mo = P.BEARING_MASS_G - mi
    return [Item(name + "_inner", group_in, "bearing", "L", inner, mass_g=mi, material="steel"),
            Item(name + "_outer", group_out, "bearing", "L", outer, mass_g=mo, material="steel")]


def to_local_from_world(sh):
    """inverse of local->world"""
    return sh.translate(cq.Vector(0, 0, -P.ZP)).rotate((0, 0, 0), (1, 0, 0), -90)


def to_world_from_local(sh):
    return sh.rotate((0, 0, 0), (1, 0, 0), 90).translate(cq.Vector(0, 0, P.ZP))


@functools.lru_cache(maxsize=None)
def build_items(led_cap=False, tip_nuts=P.TIP_NUTS):
    it = []
    A = it.append
    # ---- stand, printed (world frame)
    A(Item("base", "stand", "printed", "W", pt.base(), fill=P.FILL_STAND, material="PLA/PETG"))
    A(Item("upright_lower", "stand", "printed", "W", pt.upright_lower(), fill=P.FILL_STAND, material="PLA/PETG"))
    A(Item("upright_top", "stand", "printed", "W", pt.upright_top(), fill=P.FILL_STAND, material="PLA/PETG"))
    A(Item("release_ring", "stand", "printed", "L", pt.release_ring(), fill=P.FILL_STAND, material="PLA"))
    # ---- stand hardware (main axle), local frame
    A(Item("main_bolt_M8x60", "stand", "steel", "L", bolt(0, 0, P.MAIN_HEAD_UNDER, P.MAIN_BOLT_LEN)))
    A(Item("main_washer", "stand", "steel", "L", washer(0, 0, P.MAIN_HEAD_UNDER - P.M8_WASHER_T)))
    A(Item("main_nut", "stand", "steel", "L", nut(0, 0, P.NUT_SLOT_A0 + 0.15)))
    A(Item("spacer_ring", "stand", "printed", "L", pt.spacer_at(P.GAP_RING, P.NOSE_D + P.RING_T), fill=P.FILL_SMALL, material="PLA"))
    A(Item("spacer_main_mid", "stand", "printed", "L", pt.spacer_at(P.BRG_GAP, P.UH0 + P.BRG_W), fill=P.FILL_SMALL, material="PLA"))
    A(Item("spacer_main_front", "stand", "printed", "L", pt.spacer_at(P.S_MAIN_FRONT, P.UH1), fill=P.FILL_SMALL, material="PLA"))
    # ---- upper arm group
    A(Item("upper_arm", "upper", "printed", "L", pt.upper_arm(), fill=P.FILL_ARMS, material="PLA"))
    for it_ in bearing_parts("brg_main_1", "stand", "upper", P.UH0, 0, 0) + bearing_parts("brg_main_2", "stand", "upper", P.UH1 - P.BRG_W, 0, 0):
        A(it_)
    ey = -P.L1
    A(Item("elbow_bolt_M8x60", "upper", "steel", "L", bolt_fwd(0, ey, P.ELB_HEAD_UNDER, P.ELB_BOLT_LEN)))
    A(Item("spacer_elbow_rear", "upper", "printed", "L", pt.spacer_at(P.S_ELB_REAR, P.UH1, 0, ey), fill=P.FILL_SMALL, material="PLA"))
    A(Item("spacer_elbow_mid", "upper", "printed", "L", pt.spacer_at(P.BRG_GAP, P.LH0 + P.BRG_W, 0, ey), fill=P.FILL_SMALL, material="PLA"))
    A(Item("spacer_elbow_front", "upper", "printed", "L", pt.spacer_at(P.S_ELB_FRONT, P.LH1, 0, ey), fill=P.FILL_SMALL, material="PLA"))
    A(Item("elbow_washer", "upper", "steel", "L", washer(0, ey, P.LH1 + P.S_ELB_FRONT)))
    A(Item("elbow_nyloc", "upper", "steel", "L", nut(0, ey, P.LH1 + P.S_ELB_FRONT + P.M8_WASHER_T, P.M8_NYLOC_H), mass_g=6.0))
    for it_ in bearing_parts("brg_elb_1", "upper", "lower", P.LH0, 0, ey) + bearing_parts("brg_elb_2", "upper", "lower", P.LH1 - P.BRG_W, 0, ey):
        A(it_)
    # ---- lower arm group: built with the pivot at the origin; lower bearings were created at the elbow position,
    # so shift all lower-group items (incl. the elbow bearings' outer races) back by +L1 below.
    A(Item("lower_arm", "lower", "printed", "L", pt.lower_arm(), fill=P.FILL_ARMS, material="PLA"))
    ty = -P.L2
    A(Item("tip_bolt_M8x40", "lower", "steel", "L", bolt_fwd(0, ty, P.TIP_HEAD_UNDER, P.TIP_BOLT_LEN)))
    z = P.LH1
    if led_cap:
        A(Item("tip_cap", "lower", "printed", "L", pt.tip_cap(), fill=P.FILL_ARMS, material="PLA"))
        A(Item("tip_led_cr2032", "lower", "steel", "L", cyl(1.0, P.LH1 + 6.4, P.LH1 + 9.9, 0, ty + 27.0), mass_g=3.5))
        z = P.LH1 + pt.CAP_T
    for k in range(tip_nuts):
        A(Item(f"tip_nut_{k+1}", "lower", "steel", "L", nut(0, ty, z + k * P.M8_NUT_H)))
    out = []
    for i in it:
        if i.group == "lower" and i.kind == "bearing":
            i.shape = i.shape.translate(cq.Vector(0, P.L1, 0))      # lower-group frame: pivot at origin
        out.append(i)
    return out


# ---- posing --------------------------------------------------------------------------------------------
def pose_local(item, th1, th2):
    """shape of `item` in the LOCAL frame for absolute angles th1 (upper) / th2 (lower), degrees, ccw viewed from the viewer."""
    s = item.shape
    if item.group == "stand":
        return s if item.frame == "L" else to_local_from_world(s)
    if item.group == "upper":
        return s.rotate((0, 0, 0), (0, 0, 1), th1)
    s = s.rotate((0, 0, 0), (0, 0, 1), th2).translate(cq.Vector(0, -P.L1, 0))
    return s.rotate((0, 0, 0), (0, 0, 1), th1)


def pose_world(item, th1, th2):
    if item.group == "stand" and item.frame == "W":
        return item.shape
    return to_world_from_local(pose_local(item, th1, th2))
