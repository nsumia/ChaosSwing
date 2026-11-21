"""img/iso.png, img/exploded.png, img/poses.png (+ img/pose_*.png)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cadquery as cq
from PIL import Image, ImageDraw
from cad import params as P, assembly as A
from cad.render import render

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "img"); os.makedirs(IMG, exist_ok=True)
COL = {"stand": (0.58, 0.60, 0.64), "upper": (0.22, 0.48, 0.88), "lower": (0.96, 0.52, 0.12)}
STEEL = (0.80, 0.80, 0.83); BRG = (0.25, 0.25, 0.28)


def color(it):
    if it.kind == "printed":
        return COL[it.group]
    return BRG if it.kind == "bearing" else STEEL


def posed(th1, th2, led=False, nuts=2, offsets=None):
    out = []
    for it in A.build_items(led, nuts):
        s = A.pose_world(it, th1, th2)
        if offsets and it.name in offsets:
            s = s.translate(cq.Vector(*offsets[it.name]))
        out.append((s, color(it)))
    return out


def main():
    focal = (0, -60, P.ZP - 120)
    render(posed(60, 150, led=True, nuts=1), f"{IMG}/iso.png", view=(0.75, -1.0, 0.45), focal=(0, -40, P.ZP - 150), dist=1350, size=(1200, 1200))
    poses = [(0, 0), (90, 0), (90, 90), (150, 150), (180, 0), (120, -60)]
    tiles = []
    for t1, t2 in poses:
        im = render(posed(t1, t2), f"{IMG}/pose_{t1}_{t2}.png", view=(0.0, -1.0, 0.0), focal=(0, 0, P.ZP - 40), dist=1800, size=(700, 700))
        d = ImageDraw.Draw(im); d.text((12, 10), f"upper {t1} deg, lower {t2} deg (absolute, from hanging down)", fill=(0, 0, 0))
        tiles.append(im)
    sheet = Image.new("RGB", (2100, 1400), "white")
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % 3) * 700, (k // 3) * 700))
    sheet.save(f"{IMG}/poses.png")
    # exploded: spread along -y (toward the viewer), upright top lifted
    off = {}
    for it in A.build_items(True, 1):
        dy = {"release_ring": -30, "spacer_ring": -60, "spacer_main_mid": -70, "brg_main_1_inner": -75, "brg_main_1_outer": -90, "upper_arm": -90,
              "brg_main_2_inner": -105, "brg_main_2_outer": -105, "spacer_main_front": -125, "main_washer": -140, "main_bolt_M8x60": -160,
              "elbow_bolt_M8x50": -95, "spacer_elbow_rear": -130, "brg_elb_1_outer": -165, "brg_elb_1_inner": -160, "spacer_elbow_mid": -175,
              "brg_elb_2_outer": -185, "brg_elb_2_inner": -190, "lower_arm": -200, "spacer_elbow_front": -235, "elbow_washer": -250,
              "elbow_nyloc": -265, "tip_bolt_M8x40": -215, "tip_cap": -240, "tip_led_cr2032": -255, "tip_nut_1": -280, "main_nut": 0}.get(it.name, 0)
        dz = 70 if it.name == "upright_top" else (60 if it.name in ("main_nut",) else 0)
        off[it.name] = (0, dy, dz)
    render(posed(0, 0, led=True, nuts=1, offsets=off), f"{IMG}/exploded.png", view=(1.0, -0.55, 0.35), focal=(0, -110, P.ZP - 150), dist=1700, size=(1400, 1200))
    print("renders done")


if __name__ == "__main__":
    main()
