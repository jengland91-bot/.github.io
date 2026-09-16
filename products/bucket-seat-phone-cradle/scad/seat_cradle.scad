// =============================================================================
// Bucket Seat Phone Cradle — original design
// Inspired by open-shoulder racing buckets (EVO III silhouette), NOT a copy
// of any MakerWorld / Thingiverse / Recaro / Sparco model.
//
// Product name suggestion: "Open-Shoulder Bucket Phone Cradle"
// Trademark: do NOT brand as Sparco / Recaro. Sell as original design
// compatible with 40mm tubular sim cockpits.
// =============================================================================

/* [Phone slot] */
phone_width     = 88;   // mm — modern phones + slim case
phone_thickness = 16;   // mm — increase to 20 for thick cases
phone_depth     = 55;   // how far phone sits into the seat pocket
lip_height      = 8;    // front retention lip

/* [Seat proportions] */
seat_width      = 110;
seat_height     = 118;
seat_depth      = 78;
back_recline    = 12;   // degrees
shell_wall      = 3.2;
bolster_rise    = 14;   // side bolster height above seat pan

/* [Mount] */
mount_style     = "dovetail"; // dovetail | screw_plate
dovetail_w      = 22;
dovetail_h      = 10;
dovetail_len    = 28;

/* [Quality] */
$fn = 64;

module rounded_box(size, r = 2) {
    hull() {
        for (x = [r, size.x - r], y = [r, size.y - r], z = [r, size.z - r])
            translate([x, y, z]) sphere(r);
    }
}

// Open-shoulder bucket silhouette (no tall head wings — key differentiator
// from classic Recaro-style phone stands)
module seat_shell_outer() {
    // Seat pan
    hull() {
        translate([-seat_width/2, 0, 0])
            rounded_box([seat_width, seat_depth * 0.55, 12], 3);
        // slight taper toward front
        translate([-seat_width/2 + 4, seat_depth * 0.35, 0])
            rounded_box([seat_width - 8, seat_depth * 0.25, 10], 2.5);
    }

    // Backrest — reclined, open shoulders
    translate([0, 8, 10])
        rotate([-back_recline, 0, 0])
            hull() {
                // lower back (wide)
                translate([-seat_width/2 + 2, 0, 0])
                    rounded_box([seat_width - 4, 14, 35], 3);
                // upper back (slightly narrower, open shoulder)
                translate([-seat_width/2 + 8, -2, 55])
                    rounded_box([seat_width - 16, 12, 28], 4);
                // crown — low, no side head guards
                translate([-seat_width/2 + 14, -4, 82])
                    rounded_box([seat_width - 28, 10, 18], 5);
            }

    // Side bolsters (wrap the phone visually)
    for (side = [-1, 1]) {
        hull() {
            translate([side * (seat_width/2 - 6), 18, 6])
                scale([1, 1.2, 1]) sphere(r = 7);
            translate([side * (seat_width/2 - 8), 10, 28])
                scale([0.85, 1, 1.4]) sphere(r = 8);
            translate([side * (seat_width/2 - 12), 6, 55])
                scale([0.7, 0.9, 1.2]) sphere(r = 6);
        }
    }
}

module phone_pocket() {
    translate([
        -phone_width/2,
        seat_depth * 0.22,
        18
    ])
        rotate([-back_recline, 0, 0])
            cube([phone_width, phone_thickness + 0.6, phone_depth + 20]);
}

module charge_notch() {
    translate([
        -6,
        seat_depth * 0.22 + phone_thickness - 1,
        14
    ])
        rotate([-back_recline, 0, 0])
            rounded_box([12, 8, 14], 1.5);
}

// Decorative 5-point harness slots (stylized, non-functional branding cue)
module harness_slots() {
    translate([0, 6, 10])
        rotate([-back_recline, 0, 0]) {
            // shoulder slots
            for (side = [-1, 1])
                translate([side * 16, -2, 62])
                    rotate([90, 0, 0])
                        hull() {
                            translate([-3, 0, 0]) cylinder(h = 16, r = 2.2);
                            translate([3, 8, 0]) cylinder(h = 16, r = 2.2);
                        }
            // lap slots
            for (side = [-1, 1])
                translate([side * 18, 8, 8])
                    rotate([0, 90, 0])
                        cylinder(h = 8, r = 2.4, center = true);
            // crotch slot
            translate([0, 22, 4])
                rotate([90, 0, 0])
                    cylinder(h = 10, r = 2.2);
        }
}

module dovetail_male() {
    // Trapezoid rail on seat back for clamp / adapters
    translate([-dovetail_w/2, -dovetail_h + 1, seat_height * 0.28])
        rotate([90, 0, 0])
            linear_extrude(height = dovetail_len, center = true)
                polygon([
                    [2, 0],
                    [dovetail_w - 2, 0],
                    [dovetail_w, dovetail_h],
                    [0, dovetail_h]
                ]);
}

module seat_cradle() {
    difference() {
        seat_shell_outer();
        phone_pocket();
        charge_notch();
        harness_slots();
        // lighten underside slightly for print time
        translate([-seat_width/2 + 8, 10, -1])
            rounded_box([seat_width - 16, seat_depth * 0.35, 5], 2);
    }
    if (mount_style == "dovetail")
        dovetail_male();
}

seat_cradle();
