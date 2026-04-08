# Module 03 — Boolean Operations

[← Previous](02-parametric-geometry.md) | [Course Home](../README.md) | [Next →](04-structured-meshing.md)

---

## Boolean operations in Gmsh (OpenCASCADE)

Boolean operations require the OpenCASCADE kernel. They are the standard way to carve fluid domains, create multi-region setups, and prepare CAD geometry for meshing.

---

## BooleanDifference

Subtracts one volume from another. The most common CFD use: subtract a body from a domain box.

```geo
SetFactory("OpenCASCADE");
Box(1) = {-5, -2, -2, 10, 4, 4};
Sphere(2) = {0, 0, 0, 0.5};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
```

`Delete` removes the original volumes after the operation. Omit it to keep them.

---

## BooleanUnion

Merges two volumes into one:

```geo
Box(1) = {0, 0, 0, 1, 1, 1};
Box(2) = {0.8, 0, 0, 1, 1, 1};
BooleanUnion{ Volume{1}; Delete; }{ Volume{2}; Delete; }
```

---

## BooleanFragments — the CFD workhorse

Splits all input volumes at their intersections and produces conformally shared faces between adjacent regions. Essential for conjugate heat transfer and multi-region simulations.

```geo
SetFactory("OpenCASCADE");
Box(1) = {-3, -2, -2, 6, 4, 4};
Sphere(2) = {0, 0, 0, 0.5};
BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; }
// Result: fluid volume (with spherical cavity) + solid sphere, sharing the sphere surface conformally
```

---

## Querying tags after boolean operations

Tags change after boolean operations. Always query surviving entities:

```geo
Printf("Volumes: %g", #Volume[]);
For i In {1 : #Volume[]}
  Printf("  tag: %g", Volume[i-1]);
EndFor
```

In the Python API:

```python
gmsh.model.occ.synchronize()
volumes = gmsh.model.getEntities(3)
for dim, tag in volumes:
    bb = gmsh.model.getBoundingBox(dim, tag)
    print(f"Volume {tag}: bbox {bb}")
```

---

## Importing CAD files

```geo
SetFactory("OpenCASCADE");
Merge "geometry/blade.step";
Coherence;   // remove duplicate entities and merge coincident points
HealShapes;  // attempt repair of gaps and overlapping surfaces
```

After import, use the GUI (Tools → Visibility) to identify surface and volume tags, then assign physical groups.

---

## Common pitfalls

- **Empty result from BooleanDifference**: check operand order — first argument is kept, second is subtracted
- **Tag drift**: never hard-code tags below a boolean operation; always query
- **Non-watertight CAD**: use `HealShapes` and `Coherence` after STEP import
- **Missing Delete**: original volumes persist alongside boolean result, causing duplicate geometry

---

## Example file

See [`examples/03_boolean_fragment.geo`](../examples/03_boolean_fragment.geo) for a fluid-solid domain with a conformal interface.


---

[← Previous](02-parametric-geometry.md) | [Course Home](../README.md) | [Next →](04-structured-meshing.md)
