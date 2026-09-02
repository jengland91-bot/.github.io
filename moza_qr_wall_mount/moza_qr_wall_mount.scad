// Moza / D1-spec QR steering-wheel wall mount
// Units: mm. Open in OpenSCAD, tweak the fit, F6 to render, File > Export > STL.
//
// The Python generator (generate.py) is what produced the STLs in ./stl.
// This file is the same geometry, for people who prefer to edit OpenSCAD.

$fn = 96;

/* [Fit] */
// Shaft / groove diameters. If a test print is tight, drop these by 0.4 mm.
shaft_d = 39.8;
groove_d = 33.8;

/* [Stub] */
shaft_len = 26.0;
chamfer = 2.2;
fillet_r = 0.0;
groove_flat = 3.8;
groove_from_tip = 10.2;
groove_plate_axial = 1.2;
stub_bore_d = 26.0;
center_hole_d = 8.4;
center_csk_d = 13.8;
center_csk_depth = 8.5;
land_recess = 2.4;       // ring so all six balls catch
pocket_width_deg = 40;
pocket_offset_deg = 90;  // one seat at 12 o'clock
indexed = true;

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
    land_r = shaft_r - land_recess;
    ring_r = indexed ? land_r : groove_r;
    depth = shaft_r - ring_r;
    tip_axial = shaft_r - groove_r; // 45° toward the tip
    plate_axial = min(depth, groove_plate_axial);
    z_tip = fillet_r + shaft_len;
    g_mid = z_tip - groove_from_tip;
    z_g0 = g_mid - groove_flat / 2 - plate_axial;
    z_g1 = g_mid - groove_flat / 2;
    z_g2 = g_mid + groove_flat / 2;
    z_g3 = g_mid + groove_flat / 2 + tip_axial;
    inner_r = stub_bore_d / 2;
    m8_r = center_hole_d / 2;
    csk_r = center_csk_d / 2;
    bore_z = z_tip - center_csk_depth;
    pocket_depth = shaft_r - groove_r;

    pts = [
        [inner_r, 0],
        [inner_r, bore_z],
        [m8_r, bore_z],
        [csk_r, bore_z],
        [csk_r, z_tip],
        [shaft_r - chamfer, z_tip],
        [shaft_r, z_tip - chamfer],
        [shaft_r, z_g3],
        [ring_r, z_g2],
        [ring_r, z_g1],
        [shaft_r, z_g0],
        [shaft_r, 0],
        [inner_r, 0]
    ];
    difference() {
        rotate_extrude()
            polygon(pts);
        if (indexed) {
            for (k = [0:5])
                rotate([0, 0, pocket_offset_deg + k * 60 - pocket_width_deg / 2])
                    rotate_extrude(angle = pocket_width_deg)
                        polygon([
                            [groove_r - 0.2, g_mid - groove_flat / 2],
                            [groove_r - 0.2, g_mid + groove_flat / 2],
                            [shaft_r + 0.8, g_mid + groove_flat / 2 + pocket_depth + 0.6],
                            [shaft_r + 0.8, g_mid - groove_flat / 2 - pocket_depth - 0.6]
                        ]);
        }
    }
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
    lug_t = 4.6;
    pad_r = 8.6;
    fit_screw_r = 22.0;
    x0 = min(shaft_d / 2 - 1.0, fit_screw_r - pad_r);
    x1 = fit_screw_r + pad_r;
    difference() {
        union() {
            for (a = [90, 270])
                rotate([0, 0, a])
                    hull() {
                        translate([x0 + pad_r, 0, 0]) cylinder(h = lug_t, r = pad_r);
                        translate([x1 - pad_r, 0, 0]) cylinder(h = lug_t, r = pad_r);
                    }
        }
        for (a = [90, 270])
            rotate([0, 0, a])
                translate([fit_screw_r, 0, 0])
                    csk_hole(screw_d, screw_csk_d, screw_csk_depth, lug_t);
    }
    qr_stub();
}

if (part == "wall") wall_mount();
else if (part == "profile") profile_mount();
else fit_test();
