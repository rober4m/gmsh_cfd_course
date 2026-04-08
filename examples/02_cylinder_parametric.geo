// ============================================================
// Module 02 — Parametric cylinder in channel (OCC kernel)
// ============================================================
// Fully parametric 2D domain. Change L, H, r, xc and remesh.
//
// Usage: gmsh 02_cylinder_parametric.geo -2
// ============================================================

// ── PARAMETERS ───────────────────────────────────────────────
L   = 10.0;    // domain length
H   = 2.0;     // domain height
r   = 0.2;     // cylinder radius
xc  = 2.5;     // cylinder centre x
yc  = H / 2;   // cylinder centre y (centred)

lc_far = H / 6;
lc_cyl = r / 12;

// ── KERNEL ───────────────────────────────────────────────────
SetFactory("OpenCASCADE");

// ── GEOMETRY ─────────────────────────────────────────────────
Rectangle(1) = {0, 0, 0, L, H};
Disk(2)      = {xc, yc, 0, r};
BooleanDifference{ Surface{1}; Delete; }{ Surface{2}; Delete; }

Printf("Surfaces after boolean: %g", #Surface[]);
Printf("Curves after boolean:   %g", #Curve[]);

// ── SIZE FIELDS ──────────────────────────────────────────────
// Identify cylinder curves (those near the cylinder centre)
// In practice: inspect tags in GUI and replace the list below
Field[1] = Distance;
Field[1].CurvesList = {5, 6, 7, 8};  // adjust after inspection
Field[1].Sampling   = 200;

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lc_cyl;
Field[2].SizeMax = lc_far;
Field[2].DistMin = r * 0.5;
Field[2].DistMax = r * 8;

Background Field = 2;

// ── PHYSICAL GROUPS ──────────────────────────────────────────
// Inspect tags in GUI; adjust as needed
Physical Curve("inlet")    = {4};
Physical Curve("outlet")   = {2};
Physical Curve("walls")    = {1, 3};
Physical Curve("cylinder") = {5, 6, 7, 8};
Physical Surface("fluid")  = {1};

// ── MESH ─────────────────────────────────────────────────────
Mesh.CharacteristicLengthMin = lc_cyl * 0.5;
Mesh.CharacteristicLengthMax = lc_far;
Mesh.Algorithm = 6;
Mesh 2;
