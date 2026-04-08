// ============================================================
// Module 06 — Size fields: cylinder + wake refinement
// ============================================================
// Demonstrates Distance, Threshold, Box, and Min fields.
//
// Usage: gmsh 06_size_fields.geo -2
// ============================================================

SetFactory("OpenCASCADE");

// ── PARAMETERS ───────────────────────────────────────────────
L  = 10.0; H = 2.0; r = 0.15; xc = 2.0; yc = H/2;
lc_far  = H / 4;
lc_cyl  = r / 10;
lc_wake = r / 3;

// ── GEOMETRY ─────────────────────────────────────────────────
Rectangle(1) = {0, 0, 0, L, H};
Disk(2)      = {xc, yc, 0, r};
BooleanDifference{ Surface{1}; Delete; }{ Surface{2}; Delete; }

// ── SIZE FIELDS ──────────────────────────────────────────────
// Cylinder surface refinement
Field[1] = Distance;
Field[1].CurvesList = {5, 6, 7, 8};  // cylinder curves (check tags)
Field[1].Sampling   = 300;

Field[2] = Threshold;
Field[2].InField    = 1;
Field[2].SizeMin    = lc_cyl;
Field[2].SizeMax    = lc_far;
Field[2].DistMin    = r * 0.3;
Field[2].DistMax    = r * 8;
Field[2].StopAtDistMax = 1;

// Wake box refinement
Field[3] = Box;
Field[3].XMin = xc;       Field[3].XMax = L * 0.85;
Field[3].YMin = yc-r*4;   Field[3].YMax = yc+r*4;
Field[3].ZMin = -1;        Field[3].ZMax = 1;
Field[3].VIn  = lc_wake;
Field[3].VOut = lc_far;

// Combine: take minimum
Field[10] = Min;
Field[10].FieldsList = {2, 3};
Background Field = 10;

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Curve("inlet")    = {4};
Physical Curve("outlet")   = {2};
Physical Curve("walls")    = {1, 3};
Physical Curve("cylinder") = {5, 6, 7, 8};
Physical Surface("fluid")  = {1};

Mesh.CharacteristicLengthMin = lc_cyl * 0.5;
Mesh.CharacteristicLengthMax = lc_far;
Mesh.Algorithm = 6;
Mesh 2;
