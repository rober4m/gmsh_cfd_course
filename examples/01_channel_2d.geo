// ============================================================
// Module 01 — Simple 2D channel (built-in kernel)
// ============================================================
// A rectangular channel domain: inlet on the left, outlet on
// the right, no-slip walls on top and bottom.
//
// Usage: gmsh 01_channel_2d.geo -2
// ============================================================

// ── PARAMETERS ───────────────────────────────────────────────
L  = 4.0;     // channel length [m]
H  = 1.0;     // channel height [m]
lc = H / 10;  // characteristic mesh size

// ── GEOMETRY ─────────────────────────────────────────────────
Point(1) = {0, 0, 0, lc};
Point(2) = {L, 0, 0, lc};
Point(3) = {L, H, 0, lc};
Point(4) = {0, H, 0, lc};

Line(1) = {1, 2};   // bottom wall
Line(2) = {2, 3};   // outlet
Line(3) = {3, 4};   // top wall
Line(4) = {4, 1};   // inlet

Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Curve("inlet")  = {4};
Physical Curve("outlet") = {2};
Physical Curve("walls")  = {1, 3};
Physical Surface("fluid") = {1};

// ── MESH ─────────────────────────────────────────────────────
Mesh.CharacteristicLengthMax = lc;
Mesh 2;
