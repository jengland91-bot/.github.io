// Moza / D1-spec QR steering-wheel wall mount
// Units: mm. Open in OpenSCAD, tweak the fit, F6 to render, File > Export > STL.
//
// The Python generator (generate.py) is what produced the STLs in ./stl.
// This file is the same geometry, for people who prefer to edit OpenSCAD.

$fn = 96;

/* [Fit] */
// Shaft / groove diameters. If a test print is tight, drop these by 0.4 mm.
shaft_d = 40.4;
groove_d = 36.4;

/* [Stub] */
shaft_len = 26.0;
chamfer = 2.4;
fillet_r = 0.0;
groove_flat = 1.4;
groove_from_tip = 8.8;
stub_bore_d = 26.0;
center_hole_d = 8.4;
center_csk_d = 13.8;
center_csk_depth = 8.5;

/* [Plate] */
plate_d = 98.0;
plate_t = 8.0;
rim_chamfer = 1.8;
screw_r = 36.0;
screw_d = 4.8;
screw_csk_d = 9.8;
screw_csk_depth = 2.4;

part = "wall"; // [wall, profile, fit_test]

module qr_stub() {
    shaft_r = shaft_d / 2;
    groove_r = groove_d / 2;
    depth = shaft_r - groove_r;
    z_tip = fillet_r + shaft_len;
    g_mid = z_tip - groove_from_tip;
    z_g0 = g_mid - groove_flat / 2 - depth;
    z_g1 = g_mid - groove_flat / 2;
    z_g2 = g_mid + groove_flat / 2;
    z_g3 = g_mid + groove_flat / 2 + depth;
    inner_r = stub_bore_d / 2;
    m8_r = center_hole_d / 2;
    csk_r = center_csk_d / 2;
    bore_z = z_tip - center_csk_depth;

    pts = [
        [inner_r, 0],
        [inner_r, bore_z],
        [m8_r, bore_z],
        [csk_r, bore_z],
        [csk_r, z_tip],
        [shaft_r - chamfer, z_tip],
        [shaft_r, z_tip - chamfer],
        [shaft_r, z_g3],
        [groove_r, z_g2],
        [groove_r, z_g1],
        [shaft_r, z_g0],
        [shaft_r, 0],
        [inner_r, 0]
    ];
    rotate_extrude()
        polygon(pts);
}

module csk_hole(d, csk_d, csk_h, through_h) {
    translate([0, 0, -0.2])
        cylinder(h = through_h + 0.4, d = d);
    translate([0, 0, through_h - csk_h])
        cylinder(h = csk_h + 0.2, d1 = d, d2 = csk_d);
}

module wall_plate() {
    difference() {
        hull() {
            cylinder(h = plate_t - rim_chamfer, d = plate_d);
            translate([0, 0, 0])
                cylinder(h = plate_t, d = plate_d - rim_chamfer * 0.8);
            cylinder(h = 0.2, d = plate_d - rim_chamfer * 2);
        }
        for (a = [0, 90, 180, 270])
            rotate([0, 0, a])
                translate([screw_r, 0, 0])
                    csk_hole(screw_d, screw_csk_d, screw_csk_depth, plate_t);
        // opening the stub sits in
        translate([0, 0, -0.2])
            cylinder(h = plate_t + 0.4, d = shaft_d + 2 * fillet_r - 0.4);
    }
}

module profile_plate() {
    wall_plate();
}

module wall_mount() {
    wall_plate();
    translate([0, 0, plate_t]) qr_stub();
}

module profile_mount() {
    profile_plate();
    translate([0, 0, plate_t]) qr_stub();
}

module fit_test() {
    difference() {
        cylinder(h = 5, d = 62);
        translate([0, 0, -0.2])
            cylinder(h = 5.4, d = center_hole_d);
    }
    translate([0, 0, 5]) qr_stub();
}

if (part == "wall") wall_mount();
else if (part == "profile") profile_mount();
else fit_test();
