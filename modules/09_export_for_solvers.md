# Module 9: Export for Solvers

**Previous:** [Module 8 — Boundary Layer Meshes](08_boundary_layer_meshes.md) | **Next:** [Module 10 — Python API Automation](10_python_api_automation.md)

---

## Overview

Gmsh can export to many formats, but each solver has specific requirements around format version, element ordering, boundary naming, and how physical groups map to boundary condition types. Getting export right is the last mile before running the simulation.

---

## 9.1 Gmsh Native Format (.msh)

The `.msh` format is Gmsh's native format and supports all mesh features. Use **version 2.2** for maximum solver compatibility:

```geo
Mesh.MshFileVersion = 2.2;   // most solvers read v2.2; some don't support v4
Mesh 3;
Save "mesh.msh";
```

Or from the command line:

```bash
gmsh my.geo -3 -format msh2 -o mesh.msh
```

### .msh format versions

| Version | Notes |
|---------|-------|
| 2.2 | Best compatibility — OpenFOAM, Fluent, SU2 all support it |
| 4.1 | Default in Gmsh 4.x — not all third-party tools read it |

Always explicitly set `Mesh.MshFileVersion = 2.2` unless you have a reason to use v4.

---

## 9.2 OpenFOAM Export

OpenFOAM does **not** read `.msh` files directly — you must convert using `gmshToFoam`:

```bash
# In your OpenFOAM case directory
gmsh my.geo -3 -format msh2 -o mesh.msh
gmshToFoam mesh.msh

# Check the mesh
checkMesh
```

After conversion, edit `constant/polyMesh/boundary` to set correct patch types:

```
inlet
{
    type            patch;       // for velocity-inlet
    nFaces          240;
    startFace       ...;
}
outlet
{
    type            patch;       // for pressure-outlet
    ...
}
walls
{
    type            wall;        // IMPORTANT: must be 'wall' not 'patch' for wall functions
    ...
}
frontBack
{
    type            empty;       // 2D simulation — must be empty
    ...
}
```

Common OpenFOAM issues after `gmshToFoam`:
- **Mixed element error**: ensure mesh has only tets + prisms (no pyramids) — use `Mesh.Algorithm3D = 1`
- **Wrong patch types**: always edit `boundary` to set `wall` type explicitly
- **Empty patches missing**: 2D sims require `empty` type patches — create them with `extrudeMesh` or manually

### 2D OpenFOAM workflow

OpenFOAM's 2D meshes need a one-cell-thick 3D mesh. Generate in Gmsh:

```bash
# Generate the 2D mesh
gmsh channel_2d.geo -2 -format msh2 -o channel_2d.msh

# Convert and extrude one cell in z
gmshToFoam channel_2d.msh
# Then use extrudeMesh to create the 3D single-layer mesh
# OR: use Extrude with Layers{1} in Gmsh before meshing
```

---

## 9.3 ANSYS Fluent Export

Export directly to `.msh` (Fluent format — not the same as Gmsh `.msh`):

```bash
gmsh my.geo -3 -format msh -o fluent_mesh.msh
```

Or from within the script:

```geo
Mesh.MshFileVersion = 2.2;
Mesh 3;
// Fluent uses its own msh format — use the GUI File > Export > Fluent
// or command line: gmsh -3 -format msh my.geo
```

In Fluent after import:
- Zone types are assigned in `Boundary Conditions` panel
- Physical group names become zone labels
- Physical group integer tags become zone IDs

### Fluent element type compatibility

| Gmsh element | Fluent equivalent |
|-------------|------------------|
| Tetrahedron | Tet |
| Hexahedron  | Hex |
| Prism (wedge)| Wedge |
| Pyramid     | Pyramid |
| Triangle    | Tri (2D) |
| Quad        | Quad (2D) |

All are supported. Mixed meshes (tet + prism) import correctly.

---

## 9.4 SU2 Export

SU2 uses its own `.su2` format. Export directly:

```bash
gmsh my.geo -3 -format su2 -o mesh.su2
```

Or from the GUI: `File > Export` → select `.su2` format.

The `.su2` format embeds boundary marker names from physical groups. These must match exactly what is referenced in your SU2 config file:

```
# su2_config.cfg
MESH_FILENAME= mesh.su2
MARKER_INLET= ( INLET, ... )
MARKER_OUTLET= ( OUTLET, ... )
MARKER_HEATFLUX= ( WALL, 0.0 )
```

Note: SU2 is case-sensitive — `inlet` ≠ `INLET`.

---

## 9.5 Format Quick Reference

| Solver | Format flag | Extension | Notes |
|--------|-------------|-----------|-------|
| OpenFOAM | `msh2` | `.msh` | Then run `gmshToFoam`; edit `boundary` |
| Fluent | `msh` | `.msh` | Direct import via Fluent mesh import |
| SU2 | `su2` | `.su2` | Marker names must match config |
| CGNS | `cgns` | `.cgns` | Good for high-order meshes |
| VTK | `vtk` | `.vtk` | Visualisation / ParaView |
| Medit | `mesh` | `.mesh` | Used by some finite-element solvers |

---

## 9.6 Batch Conversion Script

```bash
#!/bin/bash
# convert_mesh.sh — convert Gmsh .geo to multiple formats

GEO="stenosis.geo"
BASE="stenosis"

# Generate mesh once
gmsh $GEO -3 -format msh2 -o ${BASE}.msh

# OpenFOAM case
mkdir -p foam_case/constant/polyMesh
cp ${BASE}.msh foam_case/
cd foam_case && gmshToFoam ${BASE}.msh && checkMesh && cd ..

# SU2
gmsh $GEO -3 -format su2 -o ${BASE}.su2

# VTK for inspection
gmsh $GEO -3 -format vtk -o ${BASE}.vtk

echo "Done. Files: ${BASE}.msh, ${BASE}.su2, ${BASE}.vtk"
```

---

## Summary

- Use `Mesh.MshFileVersion = 2.2` for maximum solver compatibility
- OpenFOAM: export as `msh2`, convert with `gmshToFoam`, always edit `boundary` to set `wall` and `empty` types
- Fluent: export as `msh` (Fluent format); boundary types are assigned inside Fluent
- SU2: export as `su2`; physical group names must exactly match the config file
- Check mesh before exporting: `Mesh.Optimize = 1` and `checkMesh` (OpenFOAM) catch most problems

---

**Previous:** [Module 8 — Boundary Layer Meshes](08_boundary_layer_meshes.md) | **Next:** [Module 10 — Python API Automation](10_python_api_automation.md)
