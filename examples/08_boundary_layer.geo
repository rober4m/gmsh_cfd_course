// ============================================================
// Module 08 — Boundary layer mesh on a flat plate
// ============================================================
// Computes first cell height for target y+ and applies the
// BoundaryLayer field on the plate surface.
//
// Usage: gmsh 08_boundary_layer.geo -2
// ============================================================

// ── PARAMETERS ───────────────────────────────────────────────
L_plate       = 0.3;    // plate length [m]
H_domain      = 0.1;    // domain height [m]
U_ref         = 10.0;   // freestream velocity [m/s]
nu            = 1.5e-5; // kinematic viscosity (air 20°C) [m^2/s]
y_plus_target = 1.0;    // target y+
growth        = 1.18;   // BL growth ratio
n_layers      = 20;     // BL layer count
lc_far        = H_domain / 8;

// ── COMPUTE FIRST CELL HEIGHT ─────────────────────────────────
Re      = U_ref * L_plate / nu;
Cf      = 0.058 * Re^(-0.2);
u_tau   = U_ref * Sqrt(Cf / 2);
delta_y = y_plus_target * nu / u_tau;

Printf("Re        = %g", Re);
Printf("u_tau     = %g m/s", u_tau);
Printf("delta_y   = %g m  (target y+ = %g)", delta_y, y_plus_target);

// ── GEOMETRY ─────────────────────────────────────────────────
Point(1) = {-0.05,       0,        0};
Point(2) = {0,           0,        0};   // plate leading edge
Point(3) = {L_plate,     0,        0};   // plate trailing edge
Point(4) = {L_plate*1.5, 0,        0};
Point(5) = {L_plate*1.5, H_domain, 0};
Point(6) = {-0.05,       H_domain, 0};

Line(1) = {1, 2};   // slip wall (upstream)
Line(2) = {2, 3};   // plate (no-slip)
Line(3) = {3, 4};   // slip wall (downstream)
Line(4) = {4, 5};   // outlet
Line(5) = {5, 6};   // freestream top
Line(6) = {6, 1};   // inlet

Curve Loop(1) = {1, 2, 3, 4, 5, 6};
Plane Surface(1) = {1};

// ── BOUNDARY LAYER FIELD ─────────────────────────────────────
Field[1] = BoundaryLayer;
Field[1].CurvesList    = {2};           // plate (no-slip)
Field[1].Size          = delta_y;
Field[1].Ratio         = growth;
Field[1].NbLayers      = n_layers;
Field[1].Quads         = 1;
Field[1].FanPointsList = {2, 3};        // LE and TE fans

Background Field = 1;

// ── PHYSICAL GROUPS ──────────────────────────────────────────
Physical Curve("inlet")     = {6};
Physical Curve("outlet")    = {4};
Physical Curve("top")       = {5};
Physical Curve("plate")     = {2};
Physical Curve("slip_wall") = {1, 3};
Physical Surface("fluid")   = {1};

// ── MESH ─────────────────────────────────────────────────────
Mesh.CharacteristicLengthMax = lc_far;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.Algorithm = 6;
Mesh 2;
