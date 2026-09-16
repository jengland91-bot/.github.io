// =============================================================================
// 40mm tube clamp for Evolve-style tubular sim cockpits
// Two-piece clam shell + dovetail receiver for the seat cradle
// Hardware: 2x M5x30 socket cap, 2x M5 nut (or heat-set inserts)
// =============================================================================

tube_od         = 40.4;   // slight clearance over nominal 40mm
clamp_width     = 28;
wall            = 4.5;
pad             = 1.2;    // rubber/felt pad allowance (set 0 if bare clamp)
bolt_d          = 5.3;
nut_trap_af     = 8.2;    // M5 nut across flats + clearance
nut_trap_h      = 4.2;
flange_extra    = 14;     // ears beyond tube
dovetail_w      = 22.4;   // female = male + clearance
dovetail_h      = 10.4;
dovetail_len    = 28.4;
$fn = 96;

module half_clamp(is_front = true) {
    ear = tube_od/2 + wall + flange_extra;
    difference() {
        union() {
            // main body
            hull() {
                translate([0, 0, 0])
                    cylinder(h = clamp_width, r = tube_od/2 + wall + pad);
                for (x = [-1, 1])
                    translate([x * ear, 0, clamp_width/2])
                        rotate([90, 0, 0])
                            cylinder(h = wall + 2, r = 7, center = true);
            }
            if (is_front) {
                // dovetail receiver block
                translate([0, tube_od/2 + wall + pad + dovetail_h/2 + 1, clamp_width/2])
                    cube([dovetail_w + 8, dovetail_h + 6, dovetail_len + 4], center = true);
            }
        }

        // tube bore (split along Y)
        translate([0, 0, -1])
            cylinder(h = clamp_width + 2, r = tube_od/2 + pad);

        // split plane keep only +Y or -Y half
        if (is_front)
            translate([-100, -200, -1]) cube([200, 200, clamp_width + 2]);
        else
            translate([-100, 0, -1]) cube([200, 200, clamp_width + 2]);

        // bolt holes through ears
        for (x = [-1, 1]) {
            translate([x * ear, 0, clamp_width/2])
                rotate([90, 0, 0])
                    cylinder(h = 80, r = bolt_d/2, center = true);
            // nut trap on rear half
            if (!is_front)
                translate([x * ear, -(wall + 1), clamp_width/2])
                    rotate([90, 30, 0])
                        cylinder(h = nut_trap_h, r = nut_trap_af/sqrt(3), $fn = 6);
        }

        if (is_front) {
            // female dovetail
            translate([0, tube_od/2 + wall + pad + 2, clamp_width/2])
                rotate([90, 0, 0])
                    linear_extrude(height = dovetail_len + 1, center = true)
                        polygon([
                            [2.2, 0],
                            [dovetail_w - 2.2, 0],
                            [dovetail_w, dovetail_h],
                            [0, dovetail_h]
                        ]);
            // slide-in access from top
            translate([0, tube_od/2 + wall + pad + dovetail_h/2 + 3, clamp_width])
                cube([dovetail_w + 1, dovetail_h + 2, 20], center = true);
        }
    }
}

// Layout for one-plate print
translate([-45, 0, 0]) rotate([0, 0, 0]) half_clamp(true);
translate([45, 0, 0]) rotate([0, 0, 180]) half_clamp(false);
