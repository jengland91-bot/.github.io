"""
Stream Deck Plus outer ring + back plate for a 6 Sigma / 40-series rig.

The ring is only a frame around the outside. It does not cover keys, dials,
or the touch strip. Four M3 screws hold the ring to the back plate and the
Plus sits in the pocket between them. The back plate bolts to the cockpit
with two M8 T-nuts.

Official Elgato numbers: 140 x 138 x 110 mm with stand, stand screws M3 x 8.
FACE_H and BODY_THICK are estimates — if the ring is tight, raise CLEAR.

    python3 cad/generate.py
"""

# ---------------------------------------------------------------------------
# Stream Deck Plus (stand removed)
# ---------------------------------------------------------------------------
BODY_W = 140.0
FACE_H = 122.0  # face top-to-bottom (logo edge to dial edge)
BODY_THICK = 30.0  # stand-face to control-face, generous
BODY_CORNER_R = 8.0
CLEAR = 0.8

# USB-C lives on the back edge, logo end. Notch is oversized.
USB_W = 16.0
USB_H = 12.0

# Optional original stand screws into the back plate (slots).
M3_STAND_SPACING = 52.0
M3_STAND_SLOT = 16.0
M3_STAND_HOLE = 3.4
M3_STAND_FROM_USB_EDGE = 38.0

# ---------------------------------------------------------------------------
# Front ring — picture frame only
# ---------------------------------------------------------------------------
LIP = 4.5  # how far the ring sits on the bezel. Keys start ~12 mm in.
RIM_T = 3.2  # thickness of the visible frame on the face
WALL = 6.0  # side walls down to the back plate (needs meat for corner screws)

# ---------------------------------------------------------------------------
# Back plate + 40-series mount (6 Sigma 4040 / 4080 face)
# ---------------------------------------------------------------------------
PLATE_T = 5.0
M3_SCREW = 3.3  # clearance through the plate
M3_TAP = 2.7  # self-tap into the ring posts
M3_HEAD = 6.2
SCREW_INSET = 5.5  # from the outer corner toward the centre

EXT = 40.0
M8_HOLE = 8.5
M8_SLOT = 14.0  # slotted so the plate can slide on the rail
M8_SPACING = 30.0
M8_PAD_T = 6.0  # extra pad on the extrusion side
