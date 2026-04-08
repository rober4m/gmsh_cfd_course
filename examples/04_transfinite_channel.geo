// ============================================================
// Module 04 — Structured 2D channel (Transfinite)
// ============================================================
// Fully structured quad mesh with wall-normal bunching.
//
// Usage: gmsh 04_transfinite_channel.geo -2
// ============================================================

// ── PARAMETERS ───────────────────────────────────────────────
L      = 4.0;
H      = 1.0;
Nx     = 80;      // streamwise nodes
Ny     = 30;      // wall-normal nodes
growth = 1.15;    // geometric progression toward wall

// ── GEOMETRY ─────────────────────────────────────────────────
Point(1) = {0, 0, 0};
Point(2) = {L, 0, 0};
Point(3) = {L, H, 0};
Point(4) = {0, H, 0};

Line(1) = {1, 2};   // bottom
Line(2) = {2, 3};   // right (outlet)
Line(3) = {3, 4};   // top
Line(4) = {4, 1};   // left (inlet)

Curve Loop(1)    = {1, 2, 3, 4};
Plane Surface(1) = {1};

// ── TRANSFINITE ───────────────────────────────────────────────
Transfinite Curve{1, 3}  = Nx;
Transfinite Curve{2}     = Ny Using Progression growth;
Transfinite Curve{-4}    = Ny Using Progression growth;

Transfinite Surface{1} = {1, 2, 3, 4};
Recombine Surface{1};

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Curve("inlet")   = {4};
Physical Curve("outlet")  = {2};
Physical Curve("bottom")  = {1};
Physical Curve("top")     = {3};
Physical Surface("fluid") = {1};

Mesh 2;
