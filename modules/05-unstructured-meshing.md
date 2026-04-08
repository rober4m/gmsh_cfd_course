# Module 05 — Unstructured Meshing

[← Previous](04-structured-meshing.md) | [Course Home](../README.md) | [Next →](06-size-fields.md)

---

## Unstructured meshing

Unstructured meshes are Gmsh's default output — triangles in 2D, tetrahedra in 3D. They handle complex geometry automatically with minimal user input.

---

## Mesh algorithms

```geo
Mesh.Algorithm   = 6;   // 2D: Frontal-Delaunay (best quality, default)
Mesh.Algorithm3D = 10;  // 3D: HXT parallel Delaunay (fast, large meshes)
```

Common 2D choices: 5 (Delaunay, fast), 6 (Frontal-Delaunay, best quality), 8 (Frontal for Quads), 11 (Quasi-structured Quads).
Common 3D choices: 1 (TetGen Delaunay), 4 (Netgen Frontal, best quality), 10 (HXT, fastest).

---

## Global size control

```geo
Mesh.CharacteristicLengthMin = 0.001;
Mesh.CharacteristicLengthMax = 0.1;
Mesh 2;
```

For spatially varying control, use size fields (Module 6).

---

## Element order

```geo
Mesh 2;
Mesh.ElementOrder = 2;   // quadratic elements (mid-edge nodes)
```

Order-2 elements significantly improve accuracy for the same node count. Most CFD solvers support up to order 2.

---

## Curvature-based refinement

```geo
Mesh.CharacteristicLengthFromCurvature = 1;
Mesh.MinimumCirclePoints = 12;  // min elements per 2pi curvature
```

Automatically refines near curved boundaries — useful for imported CAD with fillets and arcs.

---

## Optimization

```geo
Mesh 3;
Optimize "Netgen";   // swap + smooth tetrahedra (3D, best quality)
Optimize "";         // Laplacian smoothing (fast follow-up)
```

---

## Quad-dominant meshes

```geo
Recombine Surface{:};   // recombine all surfaces
Mesh.RecombineAll = 1;
Mesh.Algorithm = 11;    // Quasi-structured Quads
Mesh 2;
```

---

## Example file

See [`examples/05_unstructured_airfoil.geo`](../examples/05_unstructured_airfoil.geo) for an unstructured mesh around a NACA 0012 airfoil.


---

[← Previous](04-structured-meshing.md) | [Course Home](../README.md) | [Next →](06-size-fields.md)
