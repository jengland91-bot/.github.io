"""
Stream Deck Plus sim-cockpit faceplate + 40-series mount.

Numbers are millimetres. Official Elgato spec for the Plus (with stand):
140 x 138 x 110 mm, touch strip 108 x 14 mm, stand screws M3 x 8.

Housing-without-stand, key pitch, dial size, and M3 spacing are measured
from product photos and the XLR Dock envelope (137 x 115 x 76 mm), then
given extra clearance so a first print fits. Print `fit_gauge.stl` and the
1:1 paper template before committing to the full parts.

If a cutout is tight or loose, change the value here and re-run:

    python3 cad/generate.py
"""

# ---------------------------------------------------------------------------
# Stream Deck Plus body (stand removed)
# ---------------------------------------------------------------------------
BODY_W = 140.0
BODY_D = 116.0  # front lip to USB-C back, estimated
BODY_H = 28.0  # thickness of the plastic housing, excluding dials / stand
BODY_CORNER_R = 8.0
CLEAR = 0.8  # extra pocket around the body

# USB-C on the back, centred. Slot is oversized so the cable drops in.
USB_W = 14.0
USB_H = 10.0
USB_Z_FROM_FLOOR = 8.0

# Original stand screws: two M3 into the bottom of the housing.
# Slots, not holes, so a few millimetres of error still works.
M3_SPACING = 52.0  # centre-to-centre, left-right
M3_SLOT_LEN = 16.0  # front-back
M3_HOLE = 3.4
M3_HEAD = 6.6
M3_FROM_BACK = 38.0  # distance from inner back wall to screw centre

# ---------------------------------------------------------------------------
# Face layout (origin at face centre, +X right, +Y toward the dials)
# Touch strip 108 x 14 mm is the official scale anchor. Keys and dials
# are aligned to its four zones (108 / 4 = 27 mm pitch).
# ---------------------------------------------------------------------------
TOP_BEZEL = 12.0
KEY_SIZE = 20.8
KEY_CORNER_R = 1.6
KEY_PITCH_X = 27.0
KEY_PITCH_Y = 26.2
KEY_CLEAR = 0.7  # extra cutout around each key so they press freely
KEY_ROWS = 2
KEY_COLS = 4

GAP_KEYS_TOUCH = 6.0
TOUCH_W = 108.0
TOUCH_H = 14.0
TOUCH_CLEAR = 1.2

GAP_TOUCH_DIAL = 11.5
DIAL_D = 24.2  # knob cap diameter
DIAL_CLEAR = 2.4  # hole bigger than the cap so it can pass through
DIAL_PITCH = 27.0
BOTTOM_BEZEL = 10.0

FACE_W = BODY_W

# Derived face height from the stack of features.
FACE_H = (
    TOP_BEZEL
    + KEY_SIZE
    + KEY_PITCH_Y
    + GAP_KEYS_TOUCH
    + TOUCH_H
    + GAP_TOUCH_DIAL
    + DIAL_D
    + BOTTOM_BEZEL
)


def key_xs():
    n = KEY_COLS
    return [-(n - 1) * KEY_PITCH_X / 2 + i * KEY_PITCH_X for i in range(n)]


def key_ys():
    y0 = -FACE_H / 2 + TOP_BEZEL + KEY_SIZE / 2
    return [y0 + r * KEY_PITCH_Y for r in range(KEY_ROWS)]


def touch_center_y():
    return key_ys()[-1] + KEY_SIZE / 2 + GAP_KEYS_TOUCH + TOUCH_H / 2


def dial_xs():
    return key_xs()


def dial_center_y():
    return touch_center_y() + TOUCH_H / 2 + GAP_TOUCH_DIAL + DIAL_D / 2


# ---------------------------------------------------------------------------
# Faceplate
# ---------------------------------------------------------------------------
PLATE_THICK = 2.2
PLATE_MARGIN = 3.0  # extra border around the 140 x FACE_H face
PLATE_R = 7.0
SKIRT_H = 5.5
SKIRT_WALL = 2.2
LIP = 0.7  # inward snap lip at the bottom of the skirt

# ---------------------------------------------------------------------------
# Cradle (the tray the Plus drops into)
# ---------------------------------------------------------------------------
WALL = 4.0
FLOOR = 4.5
CRADLE_INNER_W = BODY_W + CLEAR
CRADLE_INNER_D = BODY_D + CLEAR
CRADLE_INNER_H = BODY_H + 2.0
CRADLE_CORNER_R = 7.0
FRONT_LIP = 3.2  # stops the unit sliding out toward the driver
LEDGE = 1.6  # faceplate sits on this around the pocket

# ---------------------------------------------------------------------------
# 40-series clamp (6 Sigma / 4040 / 4080 / 40120, 8 mm T-slot, M8 T-nuts)
# ---------------------------------------------------------------------------
EXT = 40.0
EXT_CLEAR = 0.5  # U-channel inner size = EXT + EXT_CLEAR
CLAMP_WALL = 5.5
CLAMP_LEN = 56.0  # along the extrusion
CLAMP_LIP = 10.0  # wrap around the neighbouring faces so it cannot spin
M8_HOLE = 8.5
M8_SPACING = 28.0  # two bolts in the same T-slot
M8_FROM_BACK = 8.0  # through the back wall of the U

# ---------------------------------------------------------------------------
# Hinge (cradle <-> clamp). Real M5 bolt + nylock, tighten to lock angle.
# ---------------------------------------------------------------------------
HINGE_EAR_T = 8.0
HINGE_EAR_R = 12.0
HINGE_HOLE = 5.3  # M5 clearance
HINGE_SPAN = 28.0  # between inner faces of the ears
HINGE_STANDOFF = 18.0  # how far the pivot sits off the clamp back
