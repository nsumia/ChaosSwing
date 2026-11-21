"""ChaosSwing parameters (mm, g, degrees). Every key dimension lives here.

Axial convention: 'a' = distance from the upright front face toward the viewer.
Local CAD frame: x = lateral, y = along the arm (arms hang toward -y), z = a (hub axis).
World frame: X right, Y away from viewer (upright at Y>0), Z up; local -> world: (x,y,z) -> (x,-z,y+ZP).
"""
import math

# ---- materials / assumptions ------------------------------------------------
PLA_DENSITY = 1.24e-3      # g/mm3 (solid PLA)
STEEL_DENSITY = 7.85e-3    # g/mm3
FILL_ARMS = 0.60           # ASSUMPTION: effective solid fraction of an arm print (4 perimeters, 25 % infill, 5 top/bottom layers)
FILL_STAND = 0.50          # ASSUMPTION: base/upright/ring effective solid fraction (conservative = light for the tipping check)
FILL_SMALL = 1.00          # spacers, pins, coupon printed solid
BEARING_MASS_G = 12.0      # 608ZZ typical mass (estimate)
BEARING_INNER_FRACTION = 0.30   # share of bearing mass on the inner race (stationary on the bolt); rest rotates with the arm

# ---- printer ----------------------------------------------------------------
BED = (220.0, 220.0, 250.0)

# ---- fits ---------------------------------------------------------------------
SEAT_D = 22.1              # 608 seat (coupon: 21.9 / 22.1 / 22.3)
M8_CLR = 8.4
M5_CLR = 5.4
NUT_EXTRA = 0.2            # across-flats allowance for nut traps
SLIDE = 0.25               # sliding fit allowance

# ---- arms ---------------------------------------------------------------------
L1 = 160.0                 # upper arm pivot spacing
L2 = 150.0                 # lower arm pivot to tip axis
BAR_W = 18.0
BAR_T = 10.0
HUB_R = 16.0
BRG_W = 7.0
BRG_OD = 22.0
BRG_ID = 8.0
BRG_GAP = 10.0             # spacing between the two bearings of a joint (>= 10)
HUB_W = 2 * BRG_W + BRG_GAP        # 24
MID_BORE_D = 15.0
ELB_BOSS_R = 14.0
ELB_BOSS_T = 12.0
TIP_BOSS_R = 11.0          # tip radius of the lower arm (reach contribution)

# ---- M8 hardware ----------------------------------------------------------------
M8_AF = 13.0
M8_HEAD_H = 5.3
M8_NUT_H = 6.5
M8_NYLOC_H = 8.0
M8_WASHER_T = 1.6
M8_WASHER_OD = 16.0
SPACER_OD = 11.6
SPACER_ID = 8.4

# ---- axial stack (a) ----------------------------------------------------------------
NOSE_D = 36.0              # cantilever length: axle plane sits this far in front of the upright
RING_T = 4.0
GAP_RING = 4.0             # ring front face -> upper hub rear
CLR_MIN = 3.0              # required minimum axial clearance between planes
UH0 = NOSE_D + RING_T + GAP_RING      # 44 upper hub rear
UH1 = UH0 + HUB_W                     # 68 upper hub front
S_MAIN_FRONT = 4.0                    # spacer (stand axle) in front of the upper hub
S_ELB_REAR = 4.0                      # spacer between upper elbow boss and lower hub
S_ELB_FRONT = 4.0                     # spacer in front of the lower hub
UB0 = UH1 - BAR_T                     # upper bar rear face
EB0 = UH1 - ELB_BOSS_T                # elbow boss rear face
HEX_POCKET_D = 5.8                    # head pocket depth (head 5.3)
MAIN_HEAD_UNDER = UH1 + S_MAIN_FRONT + M8_WASHER_T       # 73.6
MAIN_BOLT_LEN = 60.0
NUT_SLOT_A0 = 26.0                    # main nut slot (a) in the nose
LH0 = UH1 + S_ELB_REAR                # 72 lower hub rear
LH1 = LH0 + HUB_W                     # 96 lower hub front
LB0 = LH1 - BAR_T                     # 86 lower bar rear
ELB_BOLT_LEN = 60.0                    # ISO 4014 M8x60: thread b=22 -> thread starts at a=99.8, past the lower hub (96)
ELB_HEAD_UNDER = EB0 + HEX_POCKET_D   # 61.8
TIP_BOLT_LEN = 40.0
TIP_HEAD_UNDER = LB0 + HEX_POCKET_D   # 91.8
TIP_NUTS = 2                          # default tip mass: bolt + 2 nuts ~ 32 g

# ---- ring / pin ---------------------------------------------------------------------
RING_R = 100.0
PIN_ANGLES = (90, 120, 150, 180)
PIN_R = 70.0
PIN_STOP_D = 8.0
PIN_SHANK_D = 4.0
PIN_HOLE_D = PIN_SHANK_D + 0.15
PIN_STOP_END = 63.0                   # stop reaches into upper bar plane (a 58..68)

# ---- stand ----------------------------------------------------------------------------
BASE_T = 40.0
BASE_X = 218.0
BASE_Y0, BASE_Y1 = -115.0, 95.0
BASE_WALL = 8.0
BASE_FLOOR = 6.0
PAD_X = 108.0
PAD_Y0, PAD_Y1 = -27.0, 61.0
COL_X = 44.0
COL_Y0, COL_Y1 = 0.0, 34.0           # column occupies y in [0, 34] (front face y = 0)
FLANGE_X, FLANGE_Y, FLANGE_T = 100.0, 80.0, 5.0
FOOT_BOLT_DX, FOOT_BOLT_DY = 36.0, 28.0
FOOT_BOLT_LEN = 45.0
SPLICE_H = 170.0                     # splice plane above base top
SPIGOT_X, SPIGOT_Y, SPIGOT_H = 24.0, 18.0, 30.0
PIVOT_H = 345.0                      # main axle above base top (needs >= reach + 15)
NOSE_W, NOSE_H = 32.0, 36.0
BALLAST_G = 3000.0                   # design ballast: steel washers/nuts (pocket holds ~3.8 kg); sand >= 1000 g is the spec minimum
BALLAST_MIN_G = 1000.0
DESK_BOSS_R = 9.0

ZP = BASE_T + PIVOT_H                # world z of the main axle
Z_SPLICE = BASE_T + SPLICE_H
Z_TOP = ZP + NOSE_H / 2

# ---- derived checks used by tests --------------------------------------------------------
REACH_NOMINAL = L1 + L2 + TIP_BOSS_R
