"""Printed parts. Arms/ring/spacers are built in the LOCAL frame (pivot at origin, hub axis = z = a);
base/uprights are built directly in the WORLD frame."""
import math
import cadquery as cq
from . import params as P
from .cqh import cyl, tube, hexp, box, rotz

SEAT_R = P.SEAT_D / 2
MID_R = P.MID_BORE_D / 2
HEX_AF_POCKET = P.M8_AF + 0.4        # head pocket across flats
NUT_AF_TRAP = P.M8_AF + P.NUT_EXTRA * 2


def _hub_cuts(body, z0, z1, x=0.0, y=0.0):
    """two 608 seats (7 deep) + wide mid bore, hub spans z0..z1."""
    body = body.cut(cyl(SEAT_R, z0 - 1, z0 + P.BRG_W, x, y))
    body = body.cut(cyl(SEAT_R, z1 - P.BRG_W, z1 + 1, x, y))
    body = body.cut(cyl(MID_R, z0 - 1, z1 + 1, x, y))
    return body


def upper_arm():
    hub = cyl(P.HUB_R, P.UH0, P.UH1)
    bar = box(-P.BAR_W / 2, P.BAR_W / 2, -P.L1, 0, P.UB0, P.UH1)
    boss = cyl(P.ELB_BOSS_R, P.EB0, P.UH1, 0, -P.L1)
    body = hub.union(bar).union(boss)
    body = _hub_cuts(body, P.UH0, P.UH1)
    body = body.cut(cyl(P.M8_CLR / 2, P.EB0 - 1, P.UH1 + 1, 0, -P.L1))
    body = body.cut(hexp(HEX_AF_POCKET, P.EB0 - 1, P.EB0 + P.HEX_POCKET_D, 0, -P.L1))
    return body


def lower_arm():
    hub = cyl(P.HUB_R, P.LH0, P.LH1)
    bar = box(-P.BAR_W / 2, P.BAR_W / 2, -P.L2, 0, P.LB0, P.LH1)
    tip = cyl(P.TIP_BOSS_R, P.LB0, P.LH1, 0, -P.L2)
    body = hub.union(bar).union(tip)
    body = _hub_cuts(body, P.LH0, P.LH1)
    body = body.cut(cyl(P.M8_CLR / 2, P.LB0 - 1, P.LH1 + 1, 0, -P.L2))
    body = body.cut(hexp(HEX_AF_POCKET, P.LB0 - 1, P.LB0 + P.HEX_POCKET_D, 0, -P.L2))
    return body


# ---- tip cap with LED + CR2032 -----------------------------------------------------------
CAP_T = 10.0
CAP_W = 28.0
CAP_IN = 46.0      # extends this far toward the elbow from the tip axis
CAP_OUT = 14.0


def tip_cap():
    z0, z1 = P.LH1, P.LH1 + CAP_T
    ty = -P.L2
    c = box(-CAP_W / 2, CAP_W / 2, ty - CAP_OUT, ty + CAP_IN, z0, z1)
    c = c.cut(cyl(P.M8_CLR / 2, z0 - 1, z1 + 1, 0, ty))
    cell_y = ty + 27.0
    c = c.cut(cyl(10.2, z1 - 3.6, z1 + 1, 0, cell_y))               # CR2032 pocket from the front
    led_y = ty + 10.0
    c = c.cut(cyl(2.65, z0 - 1, z1 + 1, 0, led_y))                    # 5 mm LED
    c = c.cut(box(-1.0, 1.0, led_y, cell_y, z1 - 3.6, z1 + 1))        # lead channel
    return c


# ---- spacers (printed tubes) ---------------------------------------------------------------
def spacer(length):
    return tube(P.SPACER_OD / 2, P.SPACER_ID / 2, 0, length)


def spacer_at(length, z0, x=0.0, y=0.0):
    return tube(P.SPACER_OD / 2, P.SPACER_ID / 2, z0, z0 + length, x, y)


def spacers_plate():
    """print sheet: 2x 10 mm, 2x 4 mm (ring/elbow), 2x 4 mm (front), all printed as upright tubes."""
    items = [10, 10, 4, 4, 4, 4]
    w = None
    for i, L in enumerate(items):
        t = tube(P.SPACER_OD / 2, P.SPACER_ID / 2, 0, L, 16.0 * (i % 3 - 1), 16.0 * (i // 3))
        w = t if w is None else w.union(t)
    return w


# ---- release ring + pin ----------------------------------------------------------------------
PIN_OFFSET = P.BAR_W / 2 + P.PIN_STOP_D / 2 + 0.3


def pin_hole_positions():
    """(arm_angle_deg, x, y) for each pin hole, both sides. y is local (down = -y)."""
    out = []
    for ang in P.PIN_ANGLES:
        for s in (+1, -1):
            th = math.radians(s * ang)
            ux, uy = math.sin(th), -math.cos(th)
            dx, dy = math.cos(th), math.sin(th)      # d/dtheta
            px = P.PIN_R * ux - s * PIN_OFFSET * dx
            py = P.PIN_R * uy - s * PIN_OFFSET * dy
            out.append((s * ang, px, py))
    return out


def release_ring():
    z0, z1 = P.NOSE_D, P.NOSE_D + P.RING_T
    ring = cyl(P.RING_R, z0, z1)
    ring = ring.cut(cyl(P.M8_CLR / 2, z0 - 1, z1 + 1))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = ring.cut(cyl(2.7, z0 - 1, z1 + 1, 10.0 * sx, 10.0 * sy))
    for ang, x, y in pin_hole_positions():
        ring = ring.cut(cyl(P.PIN_HOLE_D / 2, z0 - 1, z1 + 1, x, y))
    # engraved scale every 15 deg (0 = hanging down), long ticks every 30 deg
    for k in range(24):
        a = 15 * k
        r_in = 84.0 if a % 30 == 0 else 91.0
        tick = box(-0.4, 0.4, -(P.RING_R + 1), -r_in, z1 - 1.0, z1 + 1)
        ring = ring.cut(rotz(tick, a))
    # labels at the pin angles
    for ang in P.PIN_ANGLES:
        for s in (+1, -1):
            th = math.radians(s * ang)
            lx, ly = 63.0 * math.sin(th) * 1.0, -63.0 * math.cos(th)
            lbl = (cq.Workplane("XY").workplane(offset=z1).center(lx, ly)
                   .text(str(ang), 5.0, -0.6, combine=False, halign="center", valign="center"))
            ring = ring.cut(lbl)
    return ring


def release_pin():
    """printed stepped pin: 8 mm stop (reaches a=63) + 4 mm shank (through the ring)."""
    stop_len = P.PIN_STOP_END - (P.NOSE_D + P.RING_T)
    shank = cyl(P.PIN_SHANK_D / 2, 0, P.RING_T)
    stop = cyl(P.PIN_STOP_D / 2, P.RING_T, P.RING_T + stop_len)
    return shank.union(stop)


# ---- bearing test coupon -----------------------------------------------------------------------
COUPON_SEATS = (21.9, 22.1, 22.3)


def coupon():
    w = box(-50, 50, -17, 17, 0, P.BRG_W)
    for i, d in enumerate(COUPON_SEATS):
        x = (i - 1) * 32.0
        w = w.cut(cyl(d / 2, -1, P.BRG_W + 1, x, 0))
        lbl = (cq.Workplane("XY").workplane(offset=P.BRG_W).center(x, -14.0)
               .text(f"{d:.1f}", 3.5, -0.5, combine=False, halign="center", valign="center"))
        w = w.cut(lbl)
    return w


# ---- stand (WORLD frame) ------------------------------------------------------------------------
FOOT_HOLES = [(sx * P.FOOT_BOLT_DX, 17.0 + sy * P.FOOT_BOLT_DY) for sx in (-1, 1) for sy in (-1, 1)]
DESK_HOLES = [(sx * (P.BASE_X / 2 - 15.0), y) for sx in (-1, 1) for y in (P.BASE_Y0 + 15.0, P.BASE_Y1 - 15.0)]


def pocket_shape():
    p = box(-P.BASE_X / 2 + P.BASE_WALL, P.BASE_X / 2 - P.BASE_WALL, P.BASE_Y0 + P.BASE_WALL,
            P.BASE_Y1 - P.BASE_WALL, P.BASE_FLOOR, P.BASE_T + 1)
    p = p.cut(box(-P.PAD_X / 2, P.PAD_X / 2, P.PAD_Y0, P.PAD_Y1, P.BASE_FLOOR - 1, P.BASE_T + 2))
    for x, y in DESK_HOLES:
        p = p.cut(cyl(P.DESK_BOSS_R, P.BASE_FLOOR - 1, P.BASE_T + 2, x, y))
    return p


def base():
    b = box(-P.BASE_X / 2, P.BASE_X / 2, P.BASE_Y0, P.BASE_Y1, 0, P.BASE_T)
    b = b.cut(pocket_shape())
    for x, y in DESK_HOLES:     # desk screw holes with head recess
        b = b.cut(cyl(2.75, -1, P.BASE_T + 1, x, y))
        b = b.cut(cyl(5.2, P.BASE_T - 4.0, P.BASE_T + 1, x, y))
    for x, y in FOOT_HOLES:     # upright bolts, nut traps from below
        b = b.cut(cyl(P.M5_CLR / 2, -1, P.BASE_T + 1, x, y))
        b = b.cut(hexp(8.0 + 0.4, -1, 5.0, x, y))
    return b


def upright_lower():
    fl = box(-P.FLANGE_X / 2, P.FLANGE_X / 2, 17.0 - P.FLANGE_Y / 2, 17.0 + P.FLANGE_Y / 2, P.BASE_T, P.BASE_T + P.FLANGE_T)
    col = box(-P.COL_X / 2, P.COL_X / 2, P.COL_Y0, P.COL_Y1, P.BASE_T, P.Z_SPLICE)
    sp = box(-P.SPIGOT_X / 2, P.SPIGOT_X / 2, 17.0 - P.SPIGOT_Y / 2, 17.0 + P.SPIGOT_Y / 2, P.Z_SPLICE - 1, P.Z_SPLICE + P.SPIGOT_H)
    w = fl.union(col).union(sp)
    for x, y in FOOT_HOLES:
        w = w.cut(cyl(P.M5_CLR / 2, P.BASE_T - 1, P.BASE_T + P.FLANGE_T + 1, x, y))
    for dz in (8.0, 22.0):
        w = w.cut(_ycyl(P.M5_CLR / 2, -1, P.COL_Y1 + 1, P.Z_SPLICE + dz))
    return w


def _ycyl(r, y0, y1, z, x=0.0):
    """cylinder along +y from y0 to y1 at height z."""
    return (cq.Workplane("XZ").workplane(offset=-y0).center(x, z).circle(r).extrude(-(y1 - y0)))


def upright_top():
    col = box(-P.COL_X / 2, P.COL_X / 2, P.COL_Y0, P.COL_Y1, P.Z_SPLICE, P.Z_TOP)
    nose = box(-P.NOSE_W / 2, P.NOSE_W / 2, -P.NOSE_D, 0.5, P.ZP - P.NOSE_H / 2, P.Z_TOP)
    w = col.union(nose)
    # socket for the lower part's spigot
    sx, sy = P.SPIGOT_X + 2 * P.SLIDE, P.SPIGOT_Y + 2 * P.SLIDE
    w = w.cut(box(-sx / 2, sx / 2, 17.0 - sy / 2, 17.0 + sy / 2, P.Z_SPLICE - 1, P.Z_SPLICE + P.SPIGOT_H + 0.5))
    for dz in (8.0, 22.0):
        w = w.cut(_ycyl(P.M5_CLR / 2, -1, P.COL_Y1 + 1, P.Z_SPLICE + dz))
        # nut trap on the rear face (y = 34)
        w = w.cut(_ytrap(P.COL_Y1 - 5.0, P.COL_Y1 + 1, P.Z_SPLICE + dz))
    # axle hole + nut slot (open to the top)
    w = w.cut(_ycyl(P.M8_CLR / 2, -P.NOSE_D - 1, 1.0, P.ZP))
    w = w.cut(box(-7.7 - 0.0, 7.7, -(P.NUT_SLOT_A0 + P.M8_NUT_H + 0.3), -P.NUT_SLOT_A0, P.ZP - 9.0, P.Z_TOP + 1))
    # alignment pegs for the ring
    for sx in (-1, 1):
        for sz in (-1, 1):
            w = w.union(_ycyl(2.5, -P.NOSE_D - 3.5, -P.NOSE_D + 0.5, P.ZP + 10.0 * sz, 10.0 * sx))
    return w


def _ytrap(y0, y1, z, x=0.0):
    d = (8.0 + 0.4) / math.cos(math.radians(30))
    return (cq.Workplane("XZ").workplane(offset=-y0).center(x, z).polygon(6, d).extrude(-(y1 - y0)))
