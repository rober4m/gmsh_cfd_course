# Module 4: Structured Meshing

**Previous:** [Module 3 — Boolean Operations](03_boolean_operations.md) | **Next:** [Module 5 — Unstructured Meshing](05_unstructured_meshing.md)

---

## Overview

Structured meshes — where elements are arranged in regular rows and columns — are preferred in CFD for wall-bounded flows, boundary layer capture, and anywhere you need predictable element aspect ratios. In Gmsh, structured meshing is controlled via **transfinite** commands and the **Recombine** directive.

---

## 4.1 The Transfinite Approach

Gmsh's structured meshing works by specifying how many nodes lie on each curve, then projecting a structured grid onto surfaces and volumes:

1. `Transfinite Curve` — set node count (and grading) on each edge
2. `Transfinite Surface` — tell Gmsh to fill a surface with a structured grid
3. `Transfinite Volume` — extend to 3D
4. `Recombine Surface/Volume` — convert triangles to quads (and prisms to hexahedra)

All four sides of a `Transfinite Surface` must have compatible node counts: **opposite sides must have the same number of nodes**.

---

## 4.2 Transfinite Curves

```geo
// Uniform distribution — 20 nodes (= 19 elements)
Transfinite Curve{1} = 20;

// Geometric progression — cluster nodes at the start (ratio > 1)
// ratio > 1: denser at start; ratio < 1: denser at end
Transfinite Curve{2} = 40 Using Progression 1.15;

// Bump distribution — denser at both ends
Transfinite Curve{3} = 30 Using Bump 3.0;
```

For a boundary layer, you typically want a **Progression** ratio on the wall-normal curves, clustering nodes near the wall:

```geo
// Wall-normal direction: 40 nodes, growing away from wall
Transfinite Curve{wall_normal_curve} = 40 Using Progression 1.2;
```

The first cell height can be estimated from the target y⁺ (covered in detail in Module 8).

---

## 4.3 Transfinite Surfaces

A transfinite surface must be bounded by **exactly 3 or 4 curves**, and opposite pairs must have the same node count.

```geo
SetFactory("OpenCASCADE");

// Simple 2D channel
Rectangle(1) = {0, 0, 0, 4, 1};

// The rectangle has 4 curves — query them
// Typically: 1=bottom, 2=right, 3=top, 4=left (verify in GUI)

// 80 nodes along length, 20 along height
Transfinite Curve{1, 3} = 80;   // bottom and top (same count — opposite sides)
Transfinite Curve{2, 4} = 20;   // right and left (same count — opposite sides)

// Make the surface structured
Transfinite Surface{1};

// Convert triangular elements to quads
Recombine Surface{1};
```

Without `Recombine`, Gmsh produces a structured triangular mesh. With it, you get pure quads — generally preferred for CFD.

---

## 4.4 Graded Channel Example

A 2D channel with wall-normal clustering — the standard setup for channel flow DNS/LES:

```geo
// examples/2d_channel/channel_structured.geo
SetFactory("OpenCASCADE");

DefineConstant[
  L     = {4.0,  Name "Channel length"},
  H     = {1.0,  Name "Channel height"},
  Nx    = {100,  Name "Nodes along length"},
  Ny    = {40,   Name "Nodes along height"},
  ratio = {1.15, Name "Wall-normal grading ratio"}
];

Rectangle(1) = {0, 0, 0, L, H};

// Identify curves (OCC Rectangle: 1=bottom, 2=right, 3=top, 4=left)
Transfinite Curve{1, 3} = Nx;
Transfinite Curve{4}    = Ny Using Progression ratio;    // left: cluster near y=0
Transfinite Curve{2}    = Ny Using Progression 1/ratio;  // right: cluster near y=0 (mirrored)

Transfinite Surface{1};
Recombine Surface{1};

Physical Curve("inlet",  1) = {4};
Physical Curve("outlet", 2) = {2};
Physical Curve("bottom", 3) = {1};
Physical Curve("top",    4) = {3};
Physical Surface("fluid",1) = {1};

Mesh 2;
Save "channel_structured.msh";
```

---

## 4.5 O-Grid / C-Grid Topology for Cylinders

For flow around a cylinder, a structured mesh requires an **O-grid** topology — a ring of quads surrounding the cylinder. This is built manually by creating intermediate surfaces.

```geo
SetFactory("OpenCASCADE");

r     = 0.5;    // cylinder radius
r_far = 2.0;    // outer O-grid radius
n_cyl = 60;     // nodes around cylinder (must divide evenly)
n_rad = 30;     // nodes in radial direction
ratio = 1.12;   // clustering ratio toward cylinder

// Inner cylinder circle
Circle(1) = {0, 0, 0, r};        // full circle via OCC

// Outer circle
Circle(2) = {0, 0, 0, r_far};

// Connect them with 4 radial lines (splitting circles into arcs)
// ... (see examples/2d_cylinder_flow/cylinder_ogrid.geo for full script)

// Radial curves: cluster toward cylinder (Progression < 1 clusters at end)
Transfinite Curve{radial_curves[]} = n_rad Using Progression ratio;
// Circumferential curves: uniform
Transfinite Curve{circ_curves[]}   = n_cyl / 4;  // per quarter
```

The full O-grid example is in `examples/2d_cylinder_flow/cylinder_ogrid.geo`.

---

## 4.6 3D Structured Meshing: Extrusion

The most common 3D structured mesh is a 2D structured surface extruded in one direction:

```geo
SetFactory("OpenCASCADE");

// Build a 2D structured quad mesh first
Rectangle(1) = {0, 0, 0, 1, 0.2};
Transfinite Curve{1, 3} = 50;
Transfinite Curve{2, 4} = 20 Using Progression 1.2;
Transfinite Surface{1};
Recombine Surface{1};

// Extrude with structured layers → hex mesh
out[] = Extrude{0, 0, 0.5} {
  Surface{1};
  Layers{25};     // 25 layers in z
  Recombine;      // quads → hexahedra
};

Physical Volume("fluid") = {out[1]};
Mesh 3;
```

The `Recombine` inside `Extrude` converts the prism layer elements into pure hexahedra. A purely hex mesh is preferred in many CFD solvers (lower numerical diffusion, better convergence).

---

## 4.7 Transfinite Volumes

For fully 3D structured meshing without extrusion:

```geo
// 6-faced brick volume
Transfinite Volume{1} = {p1, p2, p3, p4, p5, p6, p7, p8};
// Corner points listed in a specific order — see Gmsh docs for convention
Recombine Volume{1};
```

This is less common than extrusion-based workflows. The Python API (Module 10) makes 3D structured meshing easier to manage.

---

## Summary

- `Transfinite Curve` sets node count and grading on each edge
- Opposite edges of a structured surface **must have the same node count**
- `Recombine Surface` + `Recombine Volume` converts to quads and hexahedra
- For cylinders and airfoils, **O-grid topology** enables structured circumferential meshing
- 3D structured meshes are most cleanly built by extruding a 2D structured surface

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 4

Build a 2D structured mesh of a backward-facing step:
- Use the geometry from Exercise 1
- Apply Transfinite constraints with wall-normal grading on both walls
- Export a pure-quad mesh
- Count total cells and report the aspect ratio range

---

**Previous:** [Module 3 — Boolean Operations](03_boolean_operations.md) | **Next:** [Module 5 — Unstructured Meshing](05_unstructured_meshing.md)
