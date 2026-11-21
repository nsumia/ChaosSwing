"""Print-orientation shapes for every printed part (PART_TABLE) -- single source for exports and checks."""
import cadquery as cq
from . import params as P, parts as pt

# name: (builder, material, qty, flip, supports, note)
PART_TABLE = {
    "base": (pt.base, "PLA or PETG", 1, False, "none", "ballast pocket open at the top; nut traps open at the bottom"),
    "upright_lower": (pt.upright_lower, "PLA or PETG", 1, False, "none", "flange on the bed, spigot up"),
    "upright_top": (pt.upright_top, "PLA or PETG", 1, True, "none", "printed upside down: top face + cantilever nose on the bed"),
    "release_ring": (pt.release_ring, "PLA", 1, False, "none", "flat, engraved scale up"),
    "release_pin": (pt.release_pin, "PLA", 2, True, "none", "8 mm stop on the bed, shank up; print 2 (more spares)"),
    "upper_arm": (pt.upper_arm, "PLA", 1, True, "none", "front face on the bed, hubs vertical; 4 perimeters, 25-30 % gyroid"),
    "lower_arm": (pt.lower_arm, "PLA", 1, True, "none", "front face on the bed, hubs vertical; 4 perimeters, 25-30 % gyroid"),
    "tip_cap_led": (pt.tip_cap, "PLA", 1, False, "none", "OPTIONAL: rear face on the bed, CR2032 pocket up"),
    "spacers": (pt.spacers_plate, "PLA", 1, False, "none", "6 tubes: 2x 10 mm, 4x 4 mm; print solid (100 % infill)"),
    "bearing_test_coupon": (pt.coupon, "PLA", 1, False, "none", "print first: seats 21.9 / 22.1 / 22.3 mm"),
}


def print_shape(name):
    builder, _, _, flip, _, _ = PART_TABLE[name]
    s = builder().val()
    if flip:
        s = s.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
