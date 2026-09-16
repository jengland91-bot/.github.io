// Optional adapter: dovetail receiver -> 4040 / 4080 aluminum profile (M8)
// Broadens the product line beyond tubular Evolve-style frames.

profile_slot    = 8.2;   // T-slot opening
plate_w         = 40;
plate_h         = 40;
plate_t         = 6;
hole_d          = 8.3;   // M8 clearance
dovetail_w      = 22.4;
dovetail_h      = 10.4;
dovetail_len    = 28.4;
$fn = 64;

difference() {
    union() {
        // profile face plate
        translate([-plate_w/2, 0, 0])
            cube([plate_w, plate_t, plate_h]);
        // dovetail block
        translate([0, plate_t + dovetail_h/2, plate_h/2])
            cube([dovetail_w + 8, dovetail_h + 4, dovetail_len + 4], center = true);
    }
    // M8 center hole
    translate([0, -1, plate_h/2])
        rotate([-90, 0, 0])
            cylinder(h = plate_t + 2, r = hole_d/2);
    // female dovetail
    translate([0, plate_t + 1, plate_h/2])
        rotate([90, 0, 0])
            linear_extrude(height = dovetail_len + 1, center = true)
                polygon([
                    [2.2, 0],
                    [dovetail_w - 2.2, 0],
                    [dovetail_w, dovetail_h],
                    [0, dovetail_h]
                ]);
}
