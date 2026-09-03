// Moza / D1-spec QR steering-wheel wall mount
// Units: mm. Open in OpenSCAD, tweak the fit, F6 to render, File > Export > STL.
//
// The Python generator (generate.py) is what produced the STLs in ./stl.
// This file is the same geometry, for people who prefer to edit OpenSCAD.

$fn = 120;

/* [Fit] */
shaft_d = 39.8;
lead_d_delta = 2.0;

/* [Stub] */
ball_d = 6.5;
ball_cutout_top = 22.7;
ball_ring_from_face = ball_cutout_top - ball_d / 2;
dimple_r = ball_d / 2 + 0.2;
dimple_inset = 0.75;
collar_blend = 2.0;
lip_flat = 3.0;
stub_bore_d = 22.0;
chamfer = 2.0;
fillet_r = 0.0;
pocket_angles = [15, 45, 75, 105, 135, 165, 225, 255, 285, 315];
indexed = true;
center_hole_d = 8.4;
center_csk_d = 14.0;
pad_bolt_web = 3.0;

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
    lead_r = (shaft_d - lead_d_delta) / 2;
    inner_r = stub_bore_d / 2;
    g_mid = fillet_r + ball_ring_from_face;
    z_collar = g_mid - dimple_r - collar_blend;
    z_full = z_collar + collar_blend;
    z_tip = ball_cutout_top + lip_flat;
    pts = [
        [inner_r, 0],
        [inner_r, z_tip],
        [shaft_r - chamfer, z_tip],
        [shaft_r, z_tip - chamfer],
        [shaft_r, z_full],
        [lead_r, z_collar],
        [lead_r, 0],
        [inner_r, 0]
    ];
    difference() {
        rotate_extrude()
            polygon(pts);
        if (indexed) {
            for (a = pocket_angles)
                rotate([0, 0, a])
                    translate([shaft_r - dimple_inset, 0, g_mid])
                        sphere(r = dimple_r);
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
        // M8 in the plate — drop it in through the open stub.
        translate([0, 0, -0.2])
            cylinder(h = plate_t + 0.4, d = center_hole_d);
        translate([0, 0, pad_bolt_web])
            cylinder(h = plate_t, d = center_csk_d);
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
    lug_t = 8.0;
    extra = 7.0;
    sx = 15.0;
    sy = 26.0;
    pad_r = 11.0;
    corner_r = 10.0;
    ns_r = 11.0;
    ew_r = 10.0;
    half_w = max(shaft_d / 2 + extra, sx + pad_r);
    half_l = sy + pad_r;
    shaft_r = shaft_d / 2;
    g_mid = lug_t + fillet_r + ball_ring_from_face;
    z_g0 = g_mid - dimple_r;
    difference() {
        hull() {
            translate([half_w - corner_r, half_l - corner_r, 0])
                cylinder(h = lug_t, r = corner_r);
            translate([-half_w + corner_r, half_l - corner_r, 0])
                cylinder(h = lug_t, r = corner_r);
            translate([half_w - corner_r, -half_l + corner_r, 0])
                cylinder(h = lug_t, r = corner_r);
            translate([-half_w + corner_r, -half_l + corner_r, 0])
                cylinder(h = lug_t, r = corner_r);
        }
        // Stepped M8 in the pad — short bolt, cap sits here, stub tip is open.
        translate([0, 0, -0.2])
            cylinder(h = lug_t + 0.4, d = center_hole_d);
        translate([0, 0, pad_bolt_web])
            cylinder(h = lug_t, d = center_csk_d);
        // U-bites at top / bottom / sides
        translate([0, half_l, -0.2])
            cylinder(h = lug_t + 0.4, r = ns_r);
        translate([0, -half_l, -0.2])
            cylinder(h = lug_t + 0.4, r = ns_r);
        translate([half_w, 0, -0.2])
            cylinder(h = lug_t + 0.4, r = ew_r);
        translate([-half_w, 0, -0.2])
            cylinder(h = lug_t + 0.4, r = ew_r);
        for (x = [sx, -sx])
            for (y = [sy, -sy])
                translate([x, y, 0])
                    csk_hole(screw_d, screw_csk_d, screw_csk_depth, lug_t);
    }
    difference() {
        translate([0, 0, lug_t])
            qr_stub();
        for (k = [0:5])
            rotate([0, 0, 120 + k * 60])
                translate([shaft_r, 0, (lug_t + z_g0) / 2])
                    rotate([0, 90, 0])
                        cylinder(h = 16, d = 14, center = true);
    }
}

if (part == "wall") wall_mount();
else if (part == "profile") profile_mount();
else fit_test();
