# Module 3: Boolean Operations

**Previous:** [Module 2 — Parametric Geometry](02_parametric_geometry.md) | **Next:** [Module 4 — Structured Meshing](04_structured_meshing.md)

---

## Overview

Boolean operations are the primary method for building complex CFD geometries from simple primitives. With the OCC kernel, they are robust and deterministic. The key skill is not just running the operation — it is **recovering the correct entity tags afterwards** so you can assign physical groups and mesh settings.

---

## 3.1 The Four Boolean Operations

All boolean operations in Gmsh follow the same syntax:

```geo
BooleanOperation{ tool_entities; Delete; }{ object_entities; Delete; }
```

- `Delete` removes the input geometry after the operation (omit to keep it)
- The result is a new set of entities with auto-assigned tags

### Union

Merges two or more volumes/surfaces into one:

```geo
SetFactory("OpenCASCADE");
Box(1) = {0,0,0, 2,1,1};
Box(2) = {1,0,0, 2,1,1};   // overlapping box

BooleanUnion(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
// Volume 3 is the merged result
```

### Difference

Subtracts the tool from the object:

```geo
// Fluid domain with a solid body removed
Box(1)    = {-3,-3,-3, 6,6,6};    // outer domain
Sphere(2) = {0, 0, 0, 1};         // solid sphere to subtract

BooleanDifference(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
// Volume 3: box with spherical hole
```

### Intersection

Keeps only the overlapping region:

```geo
BooleanIntersection(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
```

### BooleanFragments — the CFD workhorse

`BooleanFragments` splits all input entities into non-overlapping pieces that share **conformal interfaces** — meaning the mesh on the shared boundary will match exactly on both sides. This is essential for:

- Multi-region domains (fluid + solid conjugate heat transfer)
- Overset/chimera-style geometries
- Any case where two regions must share a boundary

```geo
SetFactory("OpenCASCADE");

// Fluid box + solid cylinder (immersed body)
Box(1)      = {0, 0, 0, 4, 2, 2};
Cylinder(2) = {2, 1, 0, 0, 0, 2, 0.3};  // axis along z

// Fragment: splits both, creates shared interface surfaces
BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; };

// Now query the resulting volumes and surfaces
```

---

## 3.2 Tag Recovery After Boolean Operations

After any boolean operation, Gmsh **reassigns tags**. The entity tags in your script are no longer valid. You have three strategies for recovering them:

### Strategy 1: Gmsh GUI inspection

Run the script, open the GUI, and hover over surfaces/volumes to read their new tags. Quick for one-off work but not scriptable.

```bash
gmsh my_geometry.geo   # opens GUI — inspect tags visually
```

### Strategy 2: `Physical` groups by bounding box (OCC)

With OCC, you can use `Surface In BoundingBox` and `Volume In BoundingBox` to select entities by their spatial location rather than their tag:

```geo
// Select all surfaces with x near 0 (the inlet face)
inlet_surfs[] = Surface In BoundingBox {-0.01,-0.01,-0.01, 0.01, 2.01, 2.01};
Physical Surface("inlet") = {inlet_surfs[]};

// Select the fluid volume (larger bounding box)
fluid_vols[] = Volume In BoundingBox {-0.01,-0.01,-0.01, 4.01, 2.01, 2.01};
```

### Strategy 3: Python API (recommended)

The Python API provides full programmatic access to entity tags after boolean operations. Covered in Module 10 — for complex geometry this is the only reliable approach:

```python
import gmsh
gmsh.initialize()
gmsh.model.occ.addBox(0,0,0, 4,2,2)
gmsh.model.occ.addCylinder(2,1,0, 0,0,2, 0.3)
gmsh.model.occ.fragment([(3,1)], [(3,2)])   # fragment volumes
gmsh.model.occ.synchronize()

# Get all volumes
vols = gmsh.model.getEntities(dim=3)
# Get all surfaces on the inlet (x=0 plane)
inlet = gmsh.model.getEntitiesInBoundingBox(-0.01,-0.01,-0.01, 0.01,2.01,2.01, dim=2)
```

---

## 3.3 Multi-Region Example: Conjugate Heat Transfer Pipe

A pipe with fluid inside and a solid annular wall — a typical conjugate heat transfer setup:

```geo
// examples/3d_pipe_bend/cht_pipe.geo
SetFactory("OpenCASCADE");

DefineConstant[
  R_inner = {0.05, Name "Pipe/Inner radius"},
  R_outer = {0.08, Name "Pipe/Outer radius"},
  Len     = {1.0,  Name "Pipe/Length"}
];

// Inner fluid cylinder
Cylinder(1) = {0, 0, 0, 0, 0, Len, R_inner};

// Full pipe (fluid + wall)
Cylinder(2) = {0, 0, 0, 0, 0, Len, R_outer};

// Fragment creates:
//   - fluid region (inner cylinder)
//   - solid wall region (annulus = outer minus inner)
//   - conformal interface between them
BooleanFragments{ Volume{1,2}; Delete; }{}

// After fragment, inspect GUI to confirm tags
// Typically: Volume 1 = fluid, Volume 2 = solid wall
// Inner cylindrical surface = fluid-solid interface

// Bounding box selection for physical groups
inlet_f[]  = Surface In BoundingBox{-R_inner-0.01,-R_inner-0.01,-0.01, R_inner+0.01,R_inner+0.01,0.01};
outlet_f[] = Surface In BoundingBox{-R_inner-0.01,-R_inner-0.01,Len-0.01, R_inner+0.01,R_inner+0.01,Len+0.01};
inlet_s[]  = Surface In BoundingBox{-R_outer-0.01,-R_outer-0.01,-0.01, R_outer+0.01,R_outer+0.01,0.01};
outlet_s[] = Surface In BoundingBox{-R_outer-0.01,-R_outer-0.01,Len-0.01, R_outer+0.01,R_outer+0.01,Len+0.01};

Physical Surface("inlet_fluid")  = {inlet_f[]};
Physical Surface("outlet_fluid") = {outlet_f[]};
Physical Surface("inlet_solid")  = {inlet_s[]};
Physical Surface("outlet_solid") = {outlet_s[]};
Physical Volume("fluid") = {1};
Physical Volume("solid") = {2};

Mesh 3;
Save "cht_pipe.msh";
```

---

## 3.4 Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `BooleanFragments` produces empty result | Volumes don't overlap | Check coordinates; ensure at least partial overlap |
| Tags after boolean are unexpected | OCC renumbers all entities | Use bounding box selection or Python API |
| `Delete` left geometry behind | Mixed kernels or tag collision | Stick to one kernel; verify with GUI |
| Conformal interface not created | Used `BooleanDifference` instead of `BooleanFragments` | Use `BooleanFragments` for multi-region |
| Meshing fails on fragmented geometry | Surface loop not watertight | Check for missing faces with `Geometry > Check` in GUI |

---

## Summary

- Use `BooleanDifference` to carve a body out of a domain (single-fluid external flow)
- Use `BooleanFragments` for multi-region domains requiring conformal interfaces
- After boolean operations, use **bounding box selection** or the **Python API** to recover entity tags
- Never hard-code tags after boolean operations — they will change if the geometry changes

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 3

Create a 3D wind tunnel domain with a square prism obstacle:
- Domain: 10×4×4 m, prism: 0.5×0.5×4 m centred at x=3
- Use `BooleanDifference` to subtract the prism from the domain
- Assign physical groups using bounding box selection

---

**Previous:** [Module 2 — Parametric Geometry](02_parametric_geometry.md) | **Next:** [Module 4 — Structured Meshing](04_structured_meshing.md)
