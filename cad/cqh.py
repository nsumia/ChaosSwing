"""Small CadQuery helpers."""
import math
import cadquery as cq


def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def tube(ro, ri, z0, z1, x=0.0, y=0.0):
    return cyl(ro, z0, z1, x, y).cut(cyl(ri, z0 - 1, z1 + 1, x, y))


def hexp(af, z0, z1, x=0.0, y=0.0):
    d = af / math.cos(math.radians(30))
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).polygon(6, d).extrude(z1 - z0)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rotz(shape, ang, cx=0.0, cy=0.0):
    return shape.rotate((cx, cy, 0), (cx, cy, 1), ang)
