# Module 07 — Physical Groups and Boundary Conditions

[← Previous](06-size-fields.md) | [Course Home](../README.md) | [Next →](08-boundary-layers.md)

---

## Physical groups

Physical groups are **mandatory** for CFD-ready meshes. They name boundaries and regions so solvers can apply the right boundary conditions.

---

## Syntax

```geo
// 2D
Physical Curve("inlet")   = {4};
Physical Curve("outlet")  = {2};
Physical Curve("walls")   = {1, 3};
Physical Surface("fluid") = {1};

// 3D
Physical Surface("inlet")   = {10};
Physical Surface("outlet")  = {11};
Physical Surface("wall")    = {12, 13, 14};
Physical Volume("fluid")    = {1};
Physical Volume("solid")    = {2};
```

---

## Naming conventions

### OpenFOAM

```geo
Physical Surface("inlet")       = {inlet_tags};
Physical Surface("outlet")      = {outlet_tags};
Physical Surface("wall")        = {wall_tags};
Physical Surface("symmetry")    = {sym_tags};
Physical Surface("frontAndBack") = {z_faces};   // for 2D extruded meshes
Physical Volume("fluid")        = {vol_tag};
```

Names are **case-sensitive**. `Inlet` and `inlet` are different patches.

### Fluent

```geo
Physical Surface("velocity-inlet")   = {...};
Physical Surface("pressure-outlet")  = {...};
Physical Surface("wall")             = {...};
Physical Surface("symmetry")         = {...};
Physical Volume("fluid")             = {...};
```

### SU2

Any names you choose — you reference them in the SU2 config file:

```
MARKER_INLET= ( inlet, 300.0, 100000.0, 1.0, 0.0, 0.0 )
MARKER_OUTLET= ( outlet, 97000.0 )
MARKER_EULER= ( wall )
```

---

## Finding tags after booleans

After boolean operations, use `Printf` to list surviving tags:

```geo
Printf("Surfaces: %g", #Surface[]);
For i In {1:#Surface[]}
  Printf("  tag: %g", Surface[i-1]);
EndFor
```

Or in the GUI: **Tools → Visibility → Surface** to see all tags with highlighting.

---

## 2D extruded mesh for OpenFOAM

OpenFOAM requires 3D meshes even for 2D cases. Extrude one cell in z:

```geo
depth = 0.001;
out[] = Extrude{0, 0, depth}{
  Surface{1}; Layers{1}; Recombine;
};
Physical Surface("frontAndBack") = {1, out[0]};  // → empty BC in OF
Physical Volume("fluid")         = {out[1]};
// side surfaces → inlet, outlet, walls
```

Set type to `empty` in `constant/polyMesh/boundary` after `gmshToFoam`.

---

## Save only physical group entities

```geo
Mesh.SaveAll = 0;   // default — only export entities in physical groups
```

---

## Example file

See [`examples/07_physical_groups.geo`](../examples/07_physical_groups.geo) for a 3D pipe with all boundaries named.


---

[← Previous](06-size-fields.md) | [Course Home](../README.md) | [Next →](08-boundary-layers.md)
