# Module 2: Parametric Geometry

**Previous:** [Module 1 — `.geo` Syntax and Kernels](01_geo_syntax_kernels.md) | **Next:** [Module 3 — Boolean Operations](03_boolean_operations.md)

---

## Overview

Hard-coded coordinates make geometry fragile. A parametric script lets you change one number at the top and have the entire domain — geometry, mesh sizing, and boundary positions — update automatically. This is essential for design sweeps, mesh sensitivity studies, and reusable templates.

---

## 2.1 Variables and Expressions

`.geo` supports variables, arithmetic, and built-in math functions:

```geo
// Basic assignment
L = 4.0;
H = 1.0;
r = 0.1;

// Arithmetic
aspect = L / H;
area   = L * H;
diag   = Sqrt(L^2 + H^2);

// Built-in functions
Pi;               // 3.14159...
Sin(angle);
Cos(angle);
Atan2(y, x);
Sqrt(x);
Fabs(x);          // absolute value
Ceil(x);
Floor(x);
Log(x);           // natural log
Exp(x);
```

Variables are **global** and evaluated in order — you can reference a variable before it is used in a command, as long as it was assigned earlier in the file.

---

## 2.2 `DefineConstant` — External Parameters

`DefineConstant` declares a parameter with a default value that can be **overridden from the command line** or from Gmsh's GUI parameter panel. This is the professional way to parameterise a script.

```geo
// Define parameters with defaults
DefineConstant[
  L  = {4.0,  Name "Geometry/Channel length",    Min 1, Max 20, Step 0.5},
  H  = {1.0,  Name "Geometry/Channel height",    Min 0.1, Max 5},
  r  = {0.1,  Name "Geometry/Cylinder radius",   Min 0.01, Max 0.4},
  xc = {1.0,  Name "Geometry/Cylinder x centre", Min 0.5, Max 3},
  lc = {0.05, Name "Mesh/Base characteristic length"}
];
```

Override on the command line:

```bash
# Run with a different cylinder radius
gmsh cylinder_channel.geo -setnumber r 0.15 -2 -o mesh.msh

# Run a parameter sweep in bash
for r in 0.05 0.10 0.15 0.20; do
  gmsh cylinder_channel.geo -setnumber r $r -2 -o mesh_r${r}.msh
done
```

This makes the `.geo` file a self-documenting, GUI-controllable template. The `Name` string sets the label in Gmsh's parameter panel (the `/` creates sub-groups).

---

## 2.3 Loops: `For` and `While`

### `For` loops

```geo
// Create a row of evenly-spaced points
n  = 10;
dx = L / n;

For i In {0:n}
  Point(100 + i) = {i * dx, 0, 0, lc};
EndFor

// Connect them into lines
For i In {0:n-1}
  Line(200 + i) = {100 + i, 101 + i};
EndFor
```

The loop variable `i` runs from the first value to the second, inclusive, in steps of 1 (or a specified step):

```geo
For i In {0:10:2}   // 0, 2, 4, 6, 8, 10
  // ...
EndFor
```

### `While` loops

```geo
i = 0;
While(i < 5)
  // ...
  i++;
EndWhile
```

Loops are useful for building periodic geometry (turbine blade passages, heat exchanger arrays), radial point distributions, and structured surface patches.

---

## 2.4 Functions and Macros

You can define reusable **macros** (Gmsh's term for functions):

```geo
// Define a macro to create a circular arc from 4 points
// (full circle as two semicircles — Gmsh arcs must be < 180°)
Macro MakeCircle
  // Assumes: xc, yc, r, startTag, centreTag already set
  Point(centreTag)   = {xc, yc, 0, lc_near};
  Point(startTag)    = {xc + r, yc, 0, lc_near};
  Point(startTag+1)  = {xc,     yc + r, 0, lc_near};
  Point(startTag+2)  = {xc - r, yc,     0, lc_near};
  Point(startTag+3)  = {xc,     yc - r, 0, lc_near};
  Circle(startTag)   = {startTag,   centreTag, startTag+1};
  Circle(startTag+1) = {startTag+1, centreTag, startTag+2};
  Circle(startTag+2) = {startTag+2, centreTag, startTag+3};
  Circle(startTag+3) = {startTag+3, centreTag, startTag};
Return

// Call the macro
xc = 2.0; yc = 0.5; r = 0.15;
lc_near = r / 8;
startTag = 10; centreTag = 20;
Call MakeCircle;
```

For complex parametric geometry, the Python API (Module 10) is more powerful than macros — but for moderately complex `.geo` scripts, macros keep things clean.

---

## 2.5 Extrusion

Extrusion converts lower-dimensional entities into higher-dimensional ones and is the primary method for building 3D geometry from 2D profiles.

### Simple translation extrusion

```geo
SetFactory("OpenCASCADE");

// 2D profile
Rectangle(1) = {0, 0, 0, 1, 0.2};

// Extrude in z — returns new entities
Extrude {0, 0, 1} {
  Surface{1};
}
```

`Extrude` returns a list of new entity tags. To capture them:

```geo
// The return value is a list: {top_surface, volume, side_surfaces...}
out[] = Extrude {0, 0, L} {
  Surface{1};
};
// out[1] is the new volume
// out[0] is the top (extruded) surface
```

### Layered extrusion for structured hex mesh

Combine extrusion with `Layers` to produce structured hex elements (essential for 3D channel flows):

```geo
out[] = Extrude {0, 0, 1} {
  Surface{1};
  Layers{20};         // 20 layers in z
  Recombine;          // combine tris into quads → prisms become hexahedra
};
```

### Rotation extrusion

```geo
// Rotate a 2D profile around the z-axis to create a pipe
Extrude {{0, 0, 1}, {0, 0, 0}, Pi/2} {
  Surface{1};
}
```

---

## 2.6 Full Parametric Example: 2D Cylinder in a Channel

A complete parametric geometry for a classic CFD benchmark — flow past a cylinder:

```geo
// examples/2d_cylinder_flow/cylinder.geo
// Parametric 2D channel with circular cylinder obstacle

SetFactory("OpenCASCADE");

// ─── Parameters ───────────────────────────────────────────────
DefineConstant[
  L      = {8.0,  Name "Geometry/Channel length"},
  H      = {2.0,  Name "Geometry/Channel height"},
  xc     = {2.0,  Name "Geometry/Cylinder x"},
  yc     = {1.0,  Name "Geometry/Cylinder y"},
  r      = {0.2,  Name "Geometry/Cylinder radius"},
  lc_far = {0.2,  Name "Mesh/Far field size"},
  lc_cyl = {0.02, Name "Mesh/Cylinder surface size"}
];

// ─── Channel outer boundary ────────────────────────────────────
Rectangle(1) = {0, 0, 0, L, H};

// ─── Cylinder ─────────────────────────────────────────────────
Disk(2) = {xc, yc, 0, r, r};

// ─── Subtract cylinder from channel ───────────────────────────
BooleanDifference(3) = { Surface{1}; Delete; }{ Surface{2}; Delete; };

// ─── Physical groups ──────────────────────────────────────────
// After boolean op, query which curves are inlet/outlet/wall/cylinder
// (use Gmsh GUI to identify tags, or use Python API — see Module 10)
// Here we assume the tags created by OCC for a standard Rectangle:
//   curve 1 = bottom, 2 = right (outlet), 3 = top, 4 = left (inlet)
//   curves 5–8 = cylinder boundary (OCC numbers them after the boolean)

Physical Curve("inlet",    1) = {4};
Physical Curve("outlet",   2) = {2};
Physical Curve("walls",    3) = {1, 3};
Physical Curve("cylinder", 4) = {5, 6, 7, 8};
Physical Surface("fluid",  1) = {3};

// ─── Mesh size control ────────────────────────────────────────
// Assign lc on cylinder curves (overrides point lc)
// Full size field control covered in Module 6
Characteristic Length{ PointsOf{ Curve{5,6,7,8}; }} = lc_cyl;
Characteristic Length{ PointsOf{ Curve{1,2,3,4}; }} = lc_far;

Mesh 2;
Save "cylinder.msh";
```

Run with custom parameters:

```bash
gmsh cylinder.geo -setnumber r 0.25 -setnumber lc_cyl 0.01 -2 -o cylinder_fine.msh
```

---

## 2.7 Transformations

OCC supports geometric transformations on existing entities:

```geo
// Translate
Translate {dx, dy, dz} { Surface{1}; }

// Rotate around z-axis through origin
Rotate {{0,0,1}, {0,0,0}, Pi/4} { Surface{1}; }

// Mirror about the xz-plane (y=0)
Symmetry {0, 1, 0, 0} { Surface{1}; }

// Scale uniformly
Dilate {{0,0,0}, 2.0} { Surface{1}; }

// Duplicate and transform (keeps original)
out[] = Translate {3, 0, 0} { Duplicata{ Surface{1}; } };
```

The `Duplicata` keyword copies the entity before transforming — without it, the original is moved.

---

## Summary

- Use `DefineConstant` to expose parameters to the command line and GUI
- `For` loops build repeated geometry cleanly — arrays, periodic patterns, structured grids
- Macros (`Macro ... Return`) encapsulate reusable geometry operations
- `Extrude` with `Layers` and `Recombine` produces structured hex meshes from 2D profiles
- `Characteristic Length` on curves/surfaces overrides per-point `lc` values
- For complex parametric work, consider the Python API (Module 10) instead of macros

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 2

Build a parametric 2D converging-diverging nozzle:
- Throat width, inlet/outlet width, and length all `DefineConstant`
- Use a spline for the nozzle contour
- Verify the geometry can be re-run cleanly with at least three different parameter sets from the command line

---

**Previous:** [Module 1 — `.geo` Syntax and Kernels](01_geo_syntax_kernels.md) | **Next:** [Module 3 — Boolean Operations](03_boolean_operations.md)
