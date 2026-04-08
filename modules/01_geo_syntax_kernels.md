# Module 1: `.geo` Syntax and the Kernel System

**Previous:** [Course README](../README.md) | **Next:** [Module 2 — Parametric Geometry](02_parametric_geometry.md)

---

## Overview

Every Gmsh script is built on a four-level entity hierarchy. Understanding that hierarchy — and choosing the right geometry kernel — is the foundation everything else rests on.

---

## 1.1 The Geometry Entity Hierarchy

Gmsh represents geometry through four **entity types**, each identified by a positive integer **tag**. You must build bottom-up: a curve requires points, a surface requires curves, a volume requires surfaces.

```
Points  (dim 0)  →  Curves  (dim 1)  →  Surfaces  (dim 2)  →  Volumes  (dim 3)
```

| Entity | Command | Key arguments |
|--------|---------|---------------|
| Point | `Point(t) = {x, y, z, lc};` | coordinates + characteristic length |
| Line | `Line(t) = {start, end};` | point tags |
| Circle arc | `Circle(t) = {start, centre, end};` | point tags, arc < 180° |
| Spline | `Spline(t) = {p1, p2, ..., pn};` | ordered point tags |
| Curve Loop | `Curve Loop(t) = {c1, c2, ...};` | signed curve tags, must close |
| Plane Surface | `Plane Surface(t) = {loop1, loop2, ...};` | first loop = outer, rest = holes |
| Surface | `Surface(t) = {loop};` | for non-planar surfaces |
| Surface Loop | `Surface Loop(t) = {s1, s2, ...};` | must be watertight |
| Volume | `Volume(t) = {shell};` | surface loop tag |

The fourth argument to `Point` — `lc` — is a **local characteristic length**: a hint to the mesher about target element size at that point. It is the simplest mesh-size control available, but size fields (Module 6) give far more power and should be preferred for CFD work.

---

## 1.2 The Two Kernels

Gmsh has two geometry kernels. You choose one at the top of your script — you cannot mix them.

### Built-in kernel (default)

No declaration required. Gmsh's original geometry engine.

```geo
// Built-in is the default — no declaration needed
Point(1) = {0, 0, 0, 0.1};
```

Characteristics:
- Tags are fully manual — you assign every integer yourself
- Boolean operations exist but are unreliable for complex geometry
- No STEP/IGES import
- Good for: simple 2D structured geometries, learning the tag system

### OpenCASCADE kernel (OCC)

Activated with a single line at the top of the script.

```geo
SetFactory("OpenCASCADE");
Point(1) = {0, 0, 0, 0.1};
```

Characteristics:
- Full CAD-grade geometry engine (same kernel used by FreeCAD, Salome)
- Robust boolean operations: `BooleanUnion`, `BooleanDifference`, `BooleanIntersection`, `BooleanFragments`
- Direct import of STEP and IGES files via `Merge "file.step";`
- After boolean operations, Gmsh **auto-assigns tags** — you must query them
- Supports fillets and chamfers
- **Recommended for all CFD work**

### Side-by-side comparison

| Feature | Built-in | OpenCASCADE |
|---------|----------|-------------|
| Activation | (none) | `SetFactory("OpenCASCADE")` |
| Tag assignment | Manual | Auto after booleans |
| Boolean operations | Limited | Full |
| STEP/IGES import | No | Yes |
| Fillet / chamfer | No | Yes |
| Best for CFD | Simple 2D only | Yes — all cases |

---

## 1.3 Building a 2D Domain

A complete 2D rectangular channel — the most common starting geometry in CFD:

```geo
// examples/2d_channel/channel.geo

SetFactory("OpenCASCADE");

// Parameters
L  = 4.0;   // channel length
H  = 1.0;   // channel height
lc = 0.1;   // characteristic length

// Four corner points
Point(1) = {0, 0, 0, lc};
Point(2) = {L, 0, 0, lc};
Point(3) = {L, H, 0, lc};
Point(4) = {0, H, 0, lc};

// Four edges
Line(1) = {1, 2};   // bottom wall
Line(2) = {2, 3};   // outlet
Line(3) = {3, 4};   // top wall
Line(4) = {4, 1};   // inlet

// Close into a loop and create the surface
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// Assign physical groups (required for solvers — see Module 7)
Physical Curve("inlet",  10) = {4};
Physical Curve("outlet", 11) = {2};
Physical Curve("walls",  12) = {1, 3};
Physical Surface("fluid", 1) = {1};

// Generate 2D mesh and save
Mesh 2;
Save "channel.msh";
```

Run it:

```bash
gmsh channel.geo -2 -o channel.msh
```

---

## 1.4 The Signed Curve Loop

The **most common beginner bug** in Gmsh is an incorrectly oriented `Curve Loop`. The loop must be closed and consistently oriented (all CCW or all CW when viewed from outside). Gmsh uses the **sign** of the tag to indicate direction:

- Positive tag → traverse the curve forward (in the direction it was defined)
- Negative tag → traverse the curve in reverse

```geo
Line(1) = {1, 2};   // defined left → right
Line(2) = {2, 3};   // defined bottom → top
Line(3) = {3, 4};   // defined right → left
Line(4) = {4, 1};   // defined top → bottom

// Correct — consistent CCW loop
Curve Loop(1) = {1, 2, 3, 4};

// Also correct — consistent CW loop
Curve Loop(1) = {-4, -3, -2, -1};

// WRONG — loop is not closed (Gmsh will error or produce bad surface)
Curve Loop(1) = {1, 2, -3, 4};
```

### Surfaces with holes

When creating a domain with an embedded body (e.g., a cylinder in a channel), the outer boundary is the **first** argument to `Plane Surface` and inner boundaries (holes) follow:

```geo
Curve Loop(1) = {1, 2, 3, 4};       // outer channel boundary (CCW)
Curve Loop(2) = {10, 11, 12, 13};   // cylinder boundary (must be CW — opposite to outer)
Plane Surface(1) = {1, 2};          // surface with hole
```

The inner loop must be oriented **opposite** to the outer loop. If the outer is CCW, the hole must be CW. When using OCC, `BooleanFragments` handles this automatically (see Module 3).

---

## 1.5 OCC Primitive Shortcuts

With the OCC kernel, you can create standard shapes directly without building point-by-point:

```geo
SetFactory("OpenCASCADE");

// 3D primitives
Box(1)     = {x0, y0, z0, dx, dy, dz};
Sphere(2)  = {cx, cy, cz, r};
Cylinder(3) = {x0, y0, z0, dx, dy, dz, r};  // axis vector + radius
Cone(4)    = {x0, y0, z0, dx, dy, dz, r1, r2, angle};
Torus(5)   = {cx, cy, cz, r1, r2};

// 2D primitives
Rectangle(1) = {x0, y0, z0, dx, dy};
Disk(2)      = {cx, cy, cz, rx, ry};  // ellipse if rx ≠ ry
```

These are the building blocks of most CFD geometries — combine them with boolean operations (Module 3) to build complex domains quickly.

---

## 1.6 Comments and Script Organisation

`.geo` supports C-style comments:

```geo
// Single-line comment

/* Multi-line
   comment */
```

For maintainable scripts, a recommended structure is:

```geo
// =============================================================
// channel_flow.geo
// 2D channel with cylinder — parametric
// =============================================================

SetFactory("OpenCASCADE");

// --- Parameters ---
L = 8.0;
H = 2.0;
r = 0.2;
// ...

// --- Geometry ---
// ...

// --- Mesh settings ---
// ...

// --- Physical groups ---
// ...
```

---

## Summary

- The entity hierarchy is **Points → Curves → Surfaces → Volumes**, always built bottom-up
- Use the **OCC kernel** (`SetFactory("OpenCASCADE")`) for all CFD work
- The `lc` argument on `Point` sets local mesh size — but prefer size fields for real control
- `Curve Loop` must be **closed and consistently oriented** — sign flips reverse a curve
- For domains with holes: outer loop first, inner loops (opposite orientation) follow

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 1

Build a 2D backward-facing step geometry using the OCC kernel:
- Inlet height: 1.0 m, step height: 0.5 m, downstream length: 6.0 m
- All dimensions parametric (variables at top of script)
- Physical groups: `inlet`, `outlet`, `walls` assigned correctly

---

**Previous:** [Course README](../README.md) | **Next:** [Module 2 — Parametric Geometry](02_parametric_geometry.md)
