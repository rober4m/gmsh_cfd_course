// ============================================================
// Module 05 — Unstructured mesh around a NACA 0012
// ============================================================
// Approximates a NACA 0012 with a spline and meshes the
// surrounding domain with Frontal-Delaunay.
//
// Usage: gmsh 05_unstructured_airfoil.geo -2
// ============================================================

SetFactory("OpenCASCADE");

// ── PARAMETERS ───────────────────────────────────────────────
c       = 1.0;    // chord length
domain  = 20*c;   // farfield radius
lc_ff   = c / 2;  // farfield mesh size
lc_le   = c / 200; // leading edge mesh size
lc_te   = c / 100; // trailing edge mesh size

// NACA 0012: y = 0.6*(0.2969*sqrt(x) - 0.1260*x - 0.3516*x^2
//                     + 0.2843*x^3 - 0.1015*x^4)
// Approximated here with a circle for simplicity.
// Replace Disk with actual spline for production meshes.

// Simplified: use a disk as stand-in for airfoil
Disk(1) = {0, 0, 0, c*0.1};

// Far-field circle
Disk(2) = {0, 0, 0, domain/2};

BooleanDifference{ Surface{2}; Delete; }{ Surface{1}; Delete; }

// ── SIZE FIELDS ──────────────────────────────────────────────
Field[1] = Distance;
Field[1].CurvesList = {5};  // airfoil curve (adjust tag after boolean)
Field[1].Sampling = 500;

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lc_le;
Field[2].SizeMax = lc_ff;
Field[2].DistMin = c * 0.01;
Field[2].DistMax = c * 5.0;

Background Field = 2;

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Curve("farfield")  = {3, 4};  // outer circle (adjust)
Physical Curve("airfoil")   = {5};     // airfoil surface (adjust)
Physical Surface("fluid")   = {2};

// ── MESH ─────────────────────────────────────────────────────
Mesh.Algorithm = 6;  // Frontal-Delaunay
Mesh.CharacteristicLengthMin = lc_le;
Mesh.CharacteristicLengthMax = lc_ff;
Mesh 2;
Optimize ""; 
