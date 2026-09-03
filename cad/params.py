"""
Stream Deck Plus outer ring + hinged 6 Sigma mount.

Measured on the user's unit (stand removed):
  width  139.6 mm
  height 135.0 mm
  thick   29.9 mm

The ring is only a frame around the outside. Four M3s hold it to the
back plate with the Plus in between. The back plate hinges on a 4040
clamp so you can set the angle, then tighten the M5 nylock.

    python3 cad/generate.py
"""

# ---------------------------------------------------------------------------
# Stream Deck Plus — measured
# ---------------------------------------------------------------------------
BODY_W = 139.6
FACE_H = 135.0
BODY_THICK = 29.9
BODY_CORNER_R = 8.0
CLEAR = 0.5  # extra pocket around the measured body

# USB-C charger / cable gate on the logo end. Sized so a USB-C plug
# can drop in from the edge instead of being threaded through a hole.
CABLE_W = 28.0
CABLE_DEPTH = 22.0

# Optional original stand screws into the back plate.
M3_STAND_SPACING = 52.0
M3_STAND_SLOT = 16.0
M3_STAND_HOLE = 3.4
M3_STAND_FROM_USB_EDGE = 38.0

# ---------------------------------------------------------------------------
# Front ring — picture frame only
# ---------------------------------------------------------------------------
LIP = 4.5
RIM_T = 2.4
WALL = 6.0
WALL_EXTRA = 0.4  # walls slightly taller than 29.9 so the screws can clamp
POST = 26.0  # solid corner around each screw; mid-spans are cut away
STRAP_W = 6.5  # thin face straps that keep the four corners as one part
STRAP_T = 2.2

# ---------------------------------------------------------------------------
# Back plate
# ---------------------------------------------------------------------------
PLATE_T = 4.0
PLATE_RIB = 14.0  # + ribs through the centre (feeds the hinge)
PLATE_BORDER = 13.0  # keep a rim; pockets get cut out of the rest
M3_SCREW = 3.3
M3_TAP = 2.7
M3_HEAD = 6.2
SCREW_INSET = 5.5

# ---------------------------------------------------------------------------
# Hinge (back plate <-> 4040 clamp). M5 + nylock, tighten to lock angle.
# ---------------------------------------------------------------------------
HINGE_EAR_T = 6.0  # each outer clamp ear
HINGE_INNER_T = 8.0  # back-plate ear
HINGE_GAP = 0.4  # clearance each side of the inner ear
HINGE_EAR_R = 10.0
HINGE_HOLE = 5.3  # M5 clearance
HINGE_STANDOFF = 12.0

# ---------------------------------------------------------------------------
# Compact 4040 clamp — sized for a vertical 6 Sigma upright
# ---------------------------------------------------------------------------
EXT = 40.0
EXT_CLEAR = 0.5
CLAMP_WALL = 4.2
CLAMP_LEN = 34.0  # short along the bar
CLAMP_LIP = 6.0
M8_HOLE = 8.5
# Single M8 through the back wall is enough for this weight on a vertical.
