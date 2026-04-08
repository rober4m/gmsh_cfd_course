# Module 08 — Boundary Layer Meshes

[← Previous](07-physical-groups.md) | [Course Home](../README.md) | [Next →](09-export.md)

---

## Boundary layer meshes

Near-wall regions require fine, anisotropic cells aligned with the wall. Gmsh generates them with the `BoundaryLayer` field.

---

## First cell height: y⁺ formula

```geo
// Compute delta_y for target y+
Re      = U_ref * L_ref / nu;
Cf      = 0.058 * Re^(-0.2);         // Schlichting flat plate
u_tau   = U_ref * Sqrt(Cf / 2);
delta_y = y_plus_target * nu / u_tau;
Printf("First cell height: %g m", delta_y);
```

Target y⁺ by model:
- RANS low-Re (e.g. k-ω SST): y⁺ ≤ 1
- RANS with wall functions: y⁺ = 30–200
- Wall-modelled LES: y⁺ = 30–100
- Wall-resolved LES/DNS: y⁺ ≈ 1

---

## BoundaryLayer field

```geo
Field[1] = BoundaryLayer;
Field[1].CurvesList   = {5, 6, 7, 8};  // 2D wall curves
Field[1].SurfacesList = {10, 11};       // 3D wall surfaces
Field[1].Size         = delta_y;        // first cell height
Field[1].Ratio        = 1.2;           // growth ratio
Field[1].NbLayers     = 15;            // number of layers
Field[1].Quads        = 1;             // structured quad/prism BL
Field[1].FanPointsList = {p1, p2};     // fan at corners/leading edges
Field[1].IntersectMetrics = 1;         // avoid BL collision in narrow regions
Background Field = 1;
```

---

## Fan points

At sharp convex corners and airfoil leading edges, BL cells from adjacent walls would collide. Fan points spread them in a radial pattern:

```geo
Field[1].FanPointsList = {leading_edge_pt, trailing_edge_pt};
```

---

## Flat plate example with computed delta_y

```geo
L_plate = 0.3; U_ref = 10.0; nu = 1.5e-5; y_plus_target = 1.0;

Re      = U_ref * L_plate / nu;
Cf      = 0.058 * Re^(-0.2);
u_tau   = U_ref * Sqrt(Cf / 2);
delta_y = y_plus_target * nu / u_tau;
Printf("delta_y = %g m", delta_y);

SetFactory("OpenCASCADE");
// ... domain geometry ...

Field[1] = BoundaryLayer;
Field[1].CurvesList = {plate_curve_tag};
Field[1].Size       = delta_y;
Field[1].Ratio      = 1.18;
Field[1].NbLayers   = 20;
Field[1].Quads      = 1;
Field[1].FanPointsList = {le_tag, te_tag};
Background Field = 1;

Mesh.CharacteristicLengthMax = L_plate / 50;
Mesh 2;
```

---

## 3D boundary layers → prism elements

```geo
Field[1] = BoundaryLayer;
Field[1].SurfacesList = {wall_surface_tags};
Field[1].Size         = delta_y;
Field[1].Ratio        = 1.2;
Field[1].NbLayers     = 12;
Field[1].Quads        = 1;   // produces prism elements in 3D
```

3D BL meshing produces **prism (wedge) elements** near the wall and tetrahedra in the interior — the standard hybrid CFD mesh topology.

---

## Example file

See [`examples/08_boundary_layer.geo`](../examples/08_boundary_layer.geo) for a flat plate BL mesh with computed first cell height.


---

[← Previous](07-physical-groups.md) | [Course Home](../README.md) | [Next →](09-export.md)
