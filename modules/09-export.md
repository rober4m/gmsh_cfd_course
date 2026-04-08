# Module 09 — Export for CFD Solvers

[← Previous](08-boundary-layers.md) | [Course Home](../README.md) | [Next →](10-python-api.md)

---

## Export for CFD solvers

Gmsh exports to over 30 formats. For CFD: OpenFOAM (via MSH2 + gmshToFoam), Fluent MSH2, and SU2 are the primary targets.

---

## OpenFOAM

### Step 1: export MSH2

```bash
gmsh case.geo -3 -format msh2 -o mesh.msh
```

Or in the `.geo` file:

```geo
Mesh 3;
Mesh.MshFileVersion = 2.2;
Save "mesh.msh";
```

MSH4 format (the default) is **not** compatible with `gmshToFoam`. Always use MSH2 for OpenFOAM.

### Step 2: convert

```bash
cd my_openfoam_case
gmshToFoam mesh.msh
checkMesh
```

### Step 3: set boundary types

Edit `constant/polyMesh/boundary` to assign correct types (`patch`, `wall`, `symmetry`, `empty`).

### Requirements

- Physical Volumes **must** be defined — `gmshToFoam` uses them to identify the fluid domain
- All boundary faces must be in a Physical Surface — any unassigned face becomes `defaultFaces`

---

## Fluent

```geo
Mesh 3;
Mesh.MshFileVersion = 2.2;
Save "fluent_mesh.msh";
```

Fluent auto-assigns BC types from patch names:

```geo
Physical Surface("velocity-inlet")  = {...};
Physical Surface("pressure-outlet") = {...};
Physical Surface("wall")            = {...};
Physical Surface("symmetry")        = {...};
Physical Volume("fluid")            = {...};
```

---

## SU2

```bash
gmsh case.geo -3 -o mesh.su2
```

Reference marker names in `SU2.cfg`:

```
MARKER_INLET=  ( inlet, 300.0, 100000.0, 1.0, 0.0, 0.0 )
MARKER_OUTLET= ( outlet, 97000.0 )
MARKER_EULER=  ( wall )
```

---

## Python API multi-format export

```python
gmsh.model.mesh.generate(3)
gmsh.model.mesh.optimize("Netgen")

gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("mesh_openfoam.msh")  # MSH2 for gmshToFoam

gmsh.write("mesh.su2")           # SU2
gmsh.write("mesh.cgns")          # CGNS for Fluent/Star-CCM+
```

---

## Format reference

| Target | Format | Version | Command |
|--------|--------|---------|---------|
| OpenFOAM | MSH | 2.2 | `gmsh -format msh2` |
| Fluent | MSH | 2.2 | same as above |
| SU2 | SU2 | auto | `-o mesh.su2` |
| Star-CCM+ | CGNS | — | `-o mesh.cgns` |
| ParaView | VTK | — | `-o mesh.vtk` |

---

## Common issues

- `gmshToFoam` fails: missing Physical Volume, or wrong MSH version
- Patches missing in SU2: physical group not defined before `Save`
- High-order elements: `gmshToFoam` only handles order 1 — run `SetOrder 1` before export

---

## Example file

See [`examples/09_export_openfoam.geo`](../examples/09_export_openfoam.geo) for a pipe exported in all three formats.


---

[← Previous](08-boundary-layers.md) | [Course Home](../README.md) | [Next →](10-python-api.md)
