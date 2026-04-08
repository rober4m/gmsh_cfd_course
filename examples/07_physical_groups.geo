// ============================================================
// Module 07 — Physical groups on a 3D pipe
// ============================================================
// Demonstrates complete physical group assignment for a 3D
// pipe suitable for OpenFOAM, Fluent, and SU2.
//
// Usage: gmsh 07_physical_groups.geo -3
// ============================================================

SetFactory("OpenCASCADE");

// ── PARAMETERS ───────────────────────────────────────────────
r = 0.025;   // pipe radius [m]
L = 0.2;     // pipe length [m]
lc = r / 5;

// ── GEOMETRY ─────────────────────────────────────────────────
Cylinder(1) = {0, 0, 0,  L, 0, 0,  r};
// Cylinder creates: volume (tag 1), inlet surface (2), outlet surface (3),
// lateral surface (4). Inspect in GUI to confirm.

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Surface("inlet")  = {2};
Physical Surface("outlet") = {3};
Physical Surface("wall")   = {4};
Physical Volume("fluid")   = {1};

// ── MESH ─────────────────────────────────────────────────────
Mesh.CharacteristicLengthMax = r / 3;
Mesh.Algorithm3D = 4;   // Netgen
Mesh 3;
Optimize "Netgen";
