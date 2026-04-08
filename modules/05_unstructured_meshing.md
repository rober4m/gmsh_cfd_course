# Module 5: Unstructured Meshing

**Previous:** [Module 4 — Structured Meshing](04_structured_meshing.md) | **Next:** [Module 6 — Size Fields and Refinement](06_size_fields_refinement.md)

---

## Overview

Unstructured meshes fill complex 3D domains automatically without requiring you to define a mapping topology. They are the default for most industrial CFD — especially external aerodynamics, turbomachinery, and any geometry too complex for manual structured blocking.

---

## 5.1 Mesh Algorithm Selection

Gmsh offers multiple algorithms for both 2D and 3D meshing. The algorithm is set per-dimension using `Mesh.Algorithm` and `Mesh.Algorithm3D`.

### 2D algorithms

```geo
Mesh.Algorithm = 6;   // Frontal-Delaunay (default, good general-purpose)
Mesh.Algorithm = 5;   // Delaunay
Mesh.Algorithm = 8;   // Frontal-Delaunay for quads (with Recombine)
Mesh.Algorithm = 9;   // Packing of parallelograms (experimental, high-quality quads)
Mesh.Algorithm = 11;  // Mesh Adapt (anisotropic)
```

For most 2D CFD work: **algorithm 6** (default) is a good starting point. For high-quality quad-dominant meshes: **algorithm 8** or **9**.

### 3D algorithms

```geo
Mesh.Algorithm3D = 1;   // Delaunay (fast, good for large meshes)
Mesh.Algorithm3D = 4;   // Frontal (Netgen — good quality, slower)
Mesh.Algorithm3D = 7;   // MMG3D (anisotropic, for adapted meshes)
Mesh.Algorithm3D = 10;  // HXT (parallel Delaunay — fastest for large meshes)
```

For most 3D CFD work: **algorithm 1** (Delaunay) is fast and reliable. For better quality near curved surfaces: **algorithm 4** (Frontal/Netgen).

---

## 5.2 General Mesh Options

```geo
// Mesh order (1 = linear, 2 = quadratic)
Mesh.ElementOrder = 1;

// Optimisation passes
Mesh.Optimize = 1;           // Laplacian smoothing after generation
Mesh.OptimizeNetgen = 1;     // Netgen optimiser (3D only, better quality)

// Minimum and maximum element sizes (global limits)
Mesh.CharacteristicLengthMin = 0.005;
Mesh.CharacteristicLengthMax = 0.5;

// Factor applied to all characteristic lengths
Mesh.CharacteristicLengthFactor = 1.0;

// Prevent Gmsh from extending lc to empty regions
Mesh.CharacteristicLengthExtendFromBoundary = 0;
```

Setting `CharacteristicLengthExtendFromBoundary = 0` is important when using size fields (Module 6) — otherwise Gmsh propagates boundary `lc` values into the volume, overriding your fields.

---

## 5.3 Mixed-Element Meshes

For most CFD, you want prism layers near walls and tetrahedra in the bulk — this is handled automatically by the boundary layer field (Module 8). Without explicit boundary layers, a pure tetrahedral mesh is generated.

To produce a quad-dominant 2D mesh:

```geo
Mesh.Algorithm  = 8;     // Frontal-Delaunay for quads
Mesh.RecombineAll = 1;   // Apply Recombine to all surfaces automatically
```

Or selectively:

```geo
Recombine Surface{1, 2, 5};   // only specific surfaces
```

---

## 5.4 Mesh Smoothing and Refinement

### Smoothing

After generation, Gmsh can smooth the mesh to improve element quality:

```geo
Mesh.Optimize = 1;           // basic Laplacian smoother
Mesh.OptimizeNetgen = 1;     // Netgen-based smoother (3D, better quality)
Mesh.SmoothingSteps = 10;    // number of smoothing iterations
```

### Refinement by splitting

```geo
RefineMesh;   // splits all elements once (doubles resolution globally)
```

This is a blunt instrument — use size fields (Module 6) for targeted refinement.

---

## 5.5 Example: Unstructured 3D Pipe Flow Mesh

```geo
// examples/3d_pipe_bend/pipe_unstructured.geo
SetFactory("OpenCASCADE");

DefineConstant[
  R   = {0.05, Name "Pipe radius"},
  Len = {0.5,  Name "Pipe length"},
  lc  = {0.01, Name "Mesh size"}
];

Cylinder(1) = {0, 0, 0, 0, 0, Len, R};

// Physical groups
inlet[]  = Surface In BoundingBox{-R-0.001,-R-0.001,-0.001, R+0.001,R+0.001,0.001};
outlet[] = Surface In BoundingBox{-R-0.001,-R-0.001,Len-0.001, R+0.001,R+0.001,Len+0.001};
wall[]   = Surface In BoundingBox{-R-0.001,-R-0.001,-0.001, R+0.001,R+0.001,Len+0.001};
// Remove inlet/outlet from wall list
wall_only[] = {};  // handled more cleanly via Python API (Module 10)

Physical Surface("inlet",  1) = {inlet[]};
Physical Surface("outlet", 2) = {outlet[]};
Physical Volume("fluid",   1) = {1};

// Mesh settings
Mesh.Algorithm3D = 1;
Mesh.Optimize    = 1;
Mesh.CharacteristicLengthMax = lc * 3;
Mesh.CharacteristicLengthMin = lc / 2;

Mesh 3;
Save "pipe_unstructured.msh";
```

---

## Summary

- Algorithm 6 (2D Frontal-Delaunay) and Algorithm 1 (3D Delaunay) are reliable defaults
- Set `CharacteristicLengthExtendFromBoundary = 0` when using size fields
- `Mesh.Optimize = 1` and `Mesh.OptimizeNetgen = 1` improve quality with minimal cost
- Use `Recombine` for quad-dominant 2D meshes; the boundary layer field handles near-wall elements in 3D
- Pure unstructured tet meshes are fast to generate but have higher numerical diffusion — supplement with size fields and BL layers

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 5

Generate an unstructured 3D mesh of a T-junction pipe:
- Two inlet pipes (D=0.05 m) meeting a single outlet pipe (D=0.07 m)
- Apply algorithm 4 and compare mesh quality metrics vs algorithm 1
- Use `Mesh.CharacteristicLengthMax` to achieve ~200,000 cells

---

**Previous:** [Module 4 — Structured Meshing](04_structured_meshing.md) | **Next:** [Module 6 — Size Fields and Refinement](06_size_fields_refinement.md)
