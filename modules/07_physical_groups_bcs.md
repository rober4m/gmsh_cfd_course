# Module 7: Physical Groups and Boundary Conditions

**Previous:** [Module 6 — Size Fields and Refinement](06_size_fields_refinement.md) | **Next:** [Module 8 — Boundary Layer Meshes](08_boundary_layer_meshes.md)

---

## Overview

Physical groups are how Gmsh communicates boundary and region information to CFD solvers. Without them, your mesh file contains only unlabelled elements — the solver has no way to know which faces are inlets, walls, or outlets. This module covers correct physical group assignment and solver-specific naming conventions.

---

## 7.1 What Physical Groups Do

When Gmsh exports a mesh, it only includes entities that belong to a physical group. Entities not assigned to a physical group are **not written to the mesh file** (except in some formats). This has two implications:

1. Every boundary that the solver needs must be in a physical group
2. Every volume/surface that contains fluid (or solid) must be in a physical group

```geo
// Syntax
Physical Curve("name", tag) = {curve_tags};     // 2D boundary
Physical Surface("name", tag) = {surf_tags};    // 3D boundary
Physical Surface("name", tag) = {surf_tags};    // 2D domain
Physical Volume("name", tag) = {vol_tags};      // 3D domain
```

The `tag` (integer) is optional but important for some solvers. If omitted, Gmsh auto-assigns one.

---

## 7.2 Naming Conventions by Solver

### OpenFOAM

OpenFOAM reads boundary names directly from the mesh. The names you set in Gmsh become `boundary` patch names in OpenFOAM's `constant/polyMesh/boundary` file.

```geo
// OpenFOAM naming — no spaces, no special characters
Physical Surface("inlet")    = {1};
Physical Surface("outlet")   = {2};
Physical Surface("topWall")  = {3};
Physical Surface("botWall")  = {4};
Physical Surface("frontBack") = {5, 6};   // 2D simulation: empty patches
Physical Volume("internalMesh") = {1};    // required — names the cell zone
```

OpenFOAM conventions:
- Patch names are case-sensitive
- The volume group name is used as the cell zone identifier
- For 2D simulations: front and back patches must be named and set to type `empty` in `boundary`

### ANSYS Fluent

Fluent reads the integer tag of each physical group. Names are used as zone labels in the interface.

```geo
// Fluent — tags matter as much as names
Physical Surface("velocity-inlet",   4) = {inlet_surfs[]};
Physical Surface("pressure-outlet",  5) = {outlet_surfs[]};
Physical Surface("wall",             3) = {wall_surfs[]};
Physical Volume("fluid",             2) = {1};
```

Fluent zone types are assigned in the GUI or journal file after import — the mesh only carries the name and tag.

### SU2

SU2 uses marker names from the mesh file directly in its config:

```geo
Physical Surface("INLET")   = {1};
Physical Surface("OUTLET")  = {2};
Physical Surface("WALL")    = {3};
Physical Volume("FLUID")    = {1};
```

In `su2_config.cfg`:
```
MARKER_INLET= ( INLET, 300.0, 1e5, 1.0, 0.0, 0.0 )
MARKER_OUTLET= ( OUTLET, 1e5 )
MARKER_HEATFLUX= ( WALL, 0.0 )
```

---

## 7.3 Bounding Box Selection

For complex geometries after boolean operations, bounding box selection is the most reliable way to assign physical groups without knowing exact entity tags:

```geo
// All surfaces with x coordinate between -0.001 and 0.001 (inlet face at x=0)
inlet[] = Surface In BoundingBox{-0.001, -1.001, -1.001,  0.001, 1.001, 1.001};
Physical Surface("inlet") = {inlet[]};

// All surfaces on the outer domain boundary (large bounding box)
outer[] = Surface In BoundingBox{-5.001,-5.001,-0.001, 5.001,5.001,0.001};
// Subtract known interior surfaces
Physical Surface("farfield") = {outer[]};
```

Use tight tolerances (0.001 × typical cell size) to avoid accidentally capturing interior surfaces.

---

## 7.4 Verifying Physical Groups

Before exporting, verify your physical groups cover all boundaries:

```bash
# Check the .msh file for physical names
grep "PhysicalName" mesh.msh | head -30

# In Gmsh GUI: Tools > Options > Mesh > Visibility
# Enable "physical group labels" to see names on screen
```

A common mistake is forgetting to assign the **volume** to a physical group — the mesh exports with zero cells.

---

## 7.5 Multi-Region Physical Groups

For conjugate heat transfer or multi-phase cases with separate mesh regions:

```geo
// After BooleanFragments producing volumes 1 (fluid) and 2 (solid)
Physical Volume("fluid") = {1};
Physical Volume("solid") = {2};

// The shared interface — assign to both sides (solver-dependent naming)
interface[] = Surface In BoundingBox{...};
Physical Surface("fluid_to_solid") = {interface[]};
```

In OpenFOAM, the interface becomes a `mappedWall` or `cyclicAMI` patch type depending on the case setup.

---

## Summary

- Every boundary and domain volume must be in a physical group — entities without one are not exported
- Naming conventions differ by solver — match them carefully to avoid remapping in the solver
- Use bounding box selection after boolean operations to robustly capture surfaces by location
- Always verify: does the volume group exist? Do all boundary faces have names?

---

**Previous:** [Module 6 — Size Fields and Refinement](06_size_fields_refinement.md) | **Next:** [Module 8 — Boundary Layer Meshes](08_boundary_layer_meshes.md)
