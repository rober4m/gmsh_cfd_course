# Module 1 — `.geo` Syntax and the Kernel System

[← Course Home](../README.md) | [Next: Parametric Geometry →](02-parametric-geometry.md)

---

## The geometry entity hierarchy

Gmsh builds geometry bottom-up through four entity types, each identified by an integer tag. You cannot define a surface before the curves that bound it.

```
Point  →  Curve  →  Surface  →  Volume
(dim 0)   (dim 1)   (dim 2)     (dim 3)
```

### Points

```geo
lc = 0.1;  // characteristic length (mesh size hint)
Point(1) = {x, y, z, lc};
```

The fourth argument `lc` is the local target element size at that point. It is a hint — size fields (Module 6) override it and give you more control.

### Curves

```geo
Line(1)        = {start_tag, end_tag};
Circle(2)      = {start_tag, centre_tag, end_tag};  // arc, not full circle
Ellipse(3)     = {start, centre, major_axis_pt, end};
Spline(4)      = {p1, p2, p3, p4};      // Catmull-Rom through points
BSpline(5)     = {p1, p2, p3, p4};      // B-spline through control points
```

For a full circle, create two semicircular arcs and combine them into a curve loop.

### Curve loops

A curve loop closes a set of curves into a boundary for a surface. Curves must be **consistently oriented** — positive tag = traverse forward, negative tag = traverse in reverse.

```geo
Curve Loop(1) = {1, 2, 3, 4};    // all forward, forms closed CCW loop
Curve Loop(2) = {-4, -3, -2, -1}; // all reversed = CW (also valid)
```

The loop must be closed: the end point of each curve must equal the start point of the next.

### Surfaces

```geo
Plane Surface(1) = {1};        // flat surface bounded by loop 1
Plane Surface(2) = {1, 2};     // surface with a hole (loop 2 is the hole)
Surface(3)       = {3};        // general (curved) surface
```

For surfaces with holes, the outer loop is first and inner loops (holes) follow. The hole loops must be oriented **opposite** to the outer loop.

### Surface loops and volumes

```geo
Surface Loop(1) = {1, 2, 3, 4, 5, 6}; // must be closed/watertight
Volume(1) = {1};
```

The surface loop must enclose a watertight shell. Every surface must be oriented outward consistently — Gmsh will warn if normals are inconsistent.

---

## The two kernels

The kernel is the geometry engine. Choose it once at the top of your script — you cannot switch mid-file.

### Built-in kernel (default)

No declaration needed. Gmsh's original engine.

```geo
// No SetFactory call needed — built-in is the default
Point(1) = {0, 0, 0, 0.1};
```

- Tags are **manual** — you assign every integer yourself
- Boolean operations are limited and unreliable
- Suitable for simple 2D geometries and structured mesh setups

### OpenCASCADE kernel

```geo
SetFactory("OpenCASCADE");
```

- Full CAD-grade geometry engine
- **Robust boolean operations**: Union, Intersection, Difference, Fragments
- Can import **STEP and IGES** files directly
- After boolean operations, Gmsh **auto-assigns tags** — you must query them
- The right choice for almost all CFD work

---

## OpenCASCADE primitive shortcuts

OCC provides high-level primitives that the built-in kernel does not:

```geo
SetFactory("OpenCASCADE");

Box(1)      = {x0, y0, z0,  dx, dy, dz};
Sphere(2)   = {cx, cy, cz,  r};
Cylinder(3) = {x0, y0, z0,  dx, dy, dz,  r};   // axis + radius
Cone(4)     = {x0, y0, z0,  dx, dy, dz,  r1, r2, angle};
Torus(5)    = {cx, cy, cz,  r1, r2};            // major/minor radius
Disk(6)     = {cx, cy, cz,  r};                 // 2D disk
Rectangle(7)= {x0, y0, z0,  dx, dy};            // 2D rectangle
```

These create fully-tagged geometry in one line. Tags may be auto-assigned — use `Printf` or the GUI to inspect them.

---

## Boolean operations (OpenCASCADE only)

```geo
SetFactory("OpenCASCADE");

Box(1) = {-2, -2, -2, 4, 4, 4};   // fluid domain box
Sphere(2) = {0, 0, 0, 0.5};       // body

// Union: merge two volumes into one
BooleanUnion{ Volume{1}; Delete; }{ Volume{2}; Delete; }

// Difference: subtract sphere from box (hollow)
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }

// Fragments: split at intersections, keep both, shared faces are conformal
BooleanFragments{ Volume{1}; Delete; }{ Volume{2}; Delete; }
```

`BooleanFragments` is the most important operation for CFD. It produces a set of non-overlapping volumes that share conformal interfaces — essential for multi-region simulations (fluid + solid conjugate heat transfer, body-in-crossflow domains).

After any boolean operation, **entity tags may change**. Always check which tags survive:

```geo
// After BooleanFragments, list remaining volumes
Printf("Volumes: %g", #Volume[]);
```

Or use the GUI (Tools → Visibility) to inspect tags interactively.

---

## Orientation and the signed curve loop

The most common `.geo` bug is a misoriented curve loop. Here is how to avoid it:

1. Trace your boundary mentally — choose one direction (CCW or CW) and stick to it
2. If a curve runs against your direction, prefix its tag with `-`
3. Check closure: end point of curve `n` must equal start point of curve `n+1`

```geo
// A 2D channel domain: 4 corners, CCW winding
Point(1) = {0, 0, 0, lc};
Point(2) = {L, 0, 0, lc};
Point(3) = {L, H, 0, lc};
Point(4) = {0, H, 0, lc};

Line(1) = {1, 2};  // bottom (L→R)
Line(2) = {2, 3};  // right  (B→T)
Line(3) = {3, 4};  // top    (R→L)
Line(4) = {4, 1};  // left   (T→B)

Curve Loop(1) = {1, 2, 3, 4};   // closed CCW ✓
Plane Surface(1) = {1};
```

---

## Variable types and arithmetic

`.geo` has a simple scripting layer:

```geo
// Scalars
L = 2.0;
H = 0.4;
r = 0.05;
lc = H / 10;

// String (for Printf only)
name = "channel";

// Expressions
aspect = L / H;
area   = L * H;
diag   = Sqrt(L^2 + H^2);
Pi     = 3.14159265359;
circ   = 2 * Pi * r;

// Built-in functions
a = Abs(-3.5);
b = Floor(3.7);
c = Ceil(3.2);
d = Round(3.5);
e = Log(2.718);
f = Log10(100);
g = Exp(1);
h = Sin(Pi/6);
i = Cos(Pi/3);
j = Atan2(1, 1);
k = Min(a, b);
m = Max(a, b);
```

---

## Loops and conditionals

```geo
// For loop — inclusive on both ends
n = 8;
For i In {0:n}
  x = i * L / n;
  Point(100 + i) = {x, 0, 0, lc};
EndFor

// For loop with step
For i In {0:360:45}       // 0, 45, 90, ... 360 degrees
  angle = i * Pi / 180;
  // ...
EndFor

// While loop
i = 0;
While(i < 5)
  i++;
EndWhile

// If / ElseIf / Else
If(H > 0.5)
  Printf("Tall domain");
ElseIf(H > 0.2)
  Printf("Medium domain");
Else
  Printf("Short domain");
EndIf
```

---

## Printf for debugging

`Printf` is your primary debugging tool in `.geo` scripts:

```geo
Printf("L = %g, H = %g, aspect = %g", L, H, L/H);
Printf("Number of points: %g", #Point[]);
Printf("Number of surfaces: %g", #Surface[]);
```

Use it liberally to inspect variable values and entity counts, especially after boolean operations where tag numbers change.

---

## Kernel comparison

| Feature | Built-in | OpenCASCADE |
|---------|----------|-------------|
| Declaration | (none) | `SetFactory("OpenCASCADE")` |
| Boolean operations | Limited | Full: Union, Difference, Fragments |
| Tag assignment | Manual | Auto after booleans |
| STEP / IGES import | No | Yes |
| High-level primitives | No | Box, Sphere, Cylinder, Torus… |
| Fillet / chamfer | No | Yes (`Fillet`, `Chamfer`) |
| Recommended for CFD | Simple 2D only | Yes, all cases |

---

## Example file

See [`examples/01_channel_2d.geo`](../examples/01_channel_2d.geo) for a complete annotated 2D channel domain using the built-in kernel.

---

[← Course Home](../README.md) | [Next: Parametric Geometry →](02-parametric-geometry.md)
