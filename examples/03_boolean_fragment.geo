// ============================================================
// Module 03 — Boolean fragments: fluid + solid domain
// ============================================================
// Creates a fluid domain (box minus sphere cavity) and a solid
// sphere sharing a conformal interface. Suitable for CHT setup.
//
// Usage: gmsh 03_boolean_fragment.geo -3
// ============================================================

SetFactory("OpenCASCADE");

// ── PARAMETERS ───────────────────────────────────────────────
Lx = 6.0;  Ly = 2.0;  Lz = 2.0;   // box dimensions
r  = 0.3;                           // sphere radius

// ── GEOMETRY ─────────────────────────────────────────────────
Box(1)    = {-Lx/2, -Ly/2, -Lz/2,  Lx, Ly, Lz};
Sphere(2) = {0, 0, 0, r};

// Fragment: produces fluid (box with spherical cavity) + solid sphere
// Both share the sphere surface conformally
BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; }

Printf("Volumes after fragment: %g", #Volume[]);
Printf("Surfaces after fragment: %g", #Surface[]);

// ── PHYSICAL GROUPS ──────────────────────────────────────────
// Inspect tags in GUI and adjust
Physical Volume("fluid")  = {1};
Physical Volume("solid")  = {2};
// Shared sphere surface — find its tag and add here:
// Physical Surface("interface") = {tag};

// Outer box faces:
// Physical Surface("inlet")    = {tag};
// Physical Surface("outlet")   = {tag};
// Physical Surface("walls")    = {tag, tag, tag, tag};

// ── MESH ─────────────────────────────────────────────────────
Mesh.CharacteristicLengthMax = Ly / 5;
Mesh.Algorithm3D = 4;   // Netgen frontal
Mesh 3;
Optimize "Netgen";
