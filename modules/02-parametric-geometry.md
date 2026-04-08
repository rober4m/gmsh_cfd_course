# Module 2 — Parametric Geometry

[← Module 1](01-geo-syntax-and-kernels.md) | [Course Home](../README.md) | [Next: Boolean Operations →](03-boolean-operations.md)

---

## Why parametric geometry matters for CFD

Hard-coding coordinates is fine for a one-off mesh. For CFD work you almost always need:

- **Design sweeps** — vary a diameter, angle, or length and remesh automatically
- **Mesh sensitivity studies** — change `lc` values and regenerate without editing dozens of coordinates
- **Template geometries** — one script that produces many configurations

The key is to express every coordinate as a function of a small set of top-level parameters. Change those parameters; the whole geometry updates.

---

## Structuring a parametric script

Organise every `.geo` file the same way:

```geo
// ─── 1. PARAMETERS ───────────────────────────────────────────────────────────
L   = 8.0;     // domain length  [m]
H   = 1.0;     // domain height  [m]
r   = 0.1;     // cylinder radius [m]
xc  = 2.0;     // cylinder x-centre [m]
yc  = H / 2;   // cylinder y-centre (centred)

// ─── 2. MESH SIZES ───────────────────────────────────────────────────────────
lc_far  = H / 5;
lc_wake = r / 2;
lc_cyl  = r / 8;

// ─── 3. DERIVED QUANTITIES ───────────────────────────────────────────────────
// Nothing hard-coded below this line — all coords are expressions

// ─── 4. KERNEL ───────────────────────────────────────────────────────────────
SetFactory("OpenCASCADE");

// ─── 5. GEOMETRY ─────────────────────────────────────────────────────────────
// ... points, lines, surfaces, volumes ...

// ─── 6. PHYSICAL GROUPS ──────────────────────────────────────────────────────
// ... boundary labels for solver ...

// ─── 7. MESH SETTINGS ────────────────────────────────────────────────────────
// ... fields, algorithms, element orders ...
```

This structure makes it immediately obvious which values drive the geometry and which are derived.

---

## A fully parametric 2D cylinder-in-channel

```geo
// ─── PARAMETERS ──────────────────────────────────────────────────────────────
L   = 10.0;    // channel length
H   = 2.0;     // channel height
r   = 0.2;     // cylinder radius
xc  = 2.5;     // cylinder centre x (1.25 diameters from inlet)
yc  = H / 2;   // centred vertically

lc_far = H / 6;
lc_cyl = r / 12;

SetFactory("OpenCASCADE");

// ─── OUTER DOMAIN ────────────────────────────────────────────────────────────
Rectangle(1) = {0, 0, 0, L, H};

// ─── CYLINDER ────────────────────────────────────────────────────────────────
Disk(2) = {xc, yc, 0, r};

// ─── SUBTRACT CYLINDER FROM DOMAIN ───────────────────────────────────────────
BooleanDifference{ Surface{1}; Delete; }{ Surface{2}; Delete; }
// Surface(1) now has a hole where the cylinder was

// ─── PHYSICAL GROUPS ─────────────────────────────────────────────────────────
// After BooleanDifference the surface tag is still 1 in this case,
// but boundary curve tags may have changed — inspect in GUI or use Printf.
Physical Surface("fluid") = {1};

// Boundary curves — check tags with GUI after boolean
// Typically: 1=bottom, 2=right(outlet), 3=top, 4=left(inlet), 5-8=cylinder
Physical Curve("inlet")    = {4};
Physical Curve("outlet")   = {2};
Physical Curve("walls")    = {1, 3};
Physical Curve("cylinder") = {5, 6, 7, 8};  // adjust tags after inspection

// ─── MESH ─────────────────────────────────────────────────────────────────────
Mesh.CharacteristicLengthMin = lc_cyl;
Mesh.CharacteristicLengthMax = lc_far;
Mesh 2;
```

Changing `r`, `xc`, or `L` regenerates the entire geometry. The physical group tag assignments may need updating after boolean operations if tag numbering shifts — this is covered in Module 7.

---

## Expressing geometry with angles and polar coordinates

For circular and annular geometries, polar coordinates reduce the chance of errors:

```geo
// Polar to Cartesian helper (inline expression)
r_hub = 0.3;
r_tip = 1.0;
n_blades = 5;
theta_pitch = 2 * Pi / n_blades;  // angular pitch between blades

// Hub and tip points at blade leading edge angle (30 degrees)
angle_le = 30 * Pi / 180;

Point(10) = {r_hub * Cos(angle_le), r_hub * Sin(angle_le), 0, lc_hub};
Point(11) = {r_tip * Cos(angle_le), r_tip * Sin(angle_le), 0, lc_tip};
```

---

## Loops for repeated geometry

Loops let you build arrays, rings, or grids of geometry without repeating code:

```geo
// Row of inlet holes (for a perforated plate)
n_holes = 6;
x_start = 0.1;
x_pitch = 0.15;
r_hole  = 0.02;
y_row   = 0.0;

For i In {0 : n_holes - 1}
  // Each hole needs a unique volume/surface tag
  // Use offset to avoid tag collisions
  tag = 100 + i;
  Disk(tag) = {x_start + i * x_pitch, y_row, 0, r_hole};
EndFor
```

For 3D arrays:

```geo
// 3D tube bundle
n_rows = 3;
n_cols = 4;
pitch_x = 0.05;
pitch_y = 0.05;
r_tube  = 0.015;

tag = 1;
For j In {0 : n_rows - 1}
  For i In {0 : n_cols - 1}
    Disk(tag) = {i * pitch_x, j * pitch_y, 0, r_tube};
    tag++;
  EndFor
EndFor
```

---

## Using `newp`, `newl`, `news`, `newv` for safe tag management

When building geometry in loops or with multiple sections, tag collisions are a common bug. Gmsh provides automatic tag counters:

```geo
p1 = newp;  Point(p1) = {0, 0, 0, lc};
p2 = newp;  Point(p2) = {1, 0, 0, lc};
p3 = newp;  Point(p3) = {1, 1, 0, lc};
p4 = newp;  Point(p4) = {0, 1, 0, lc};

l1 = newl;  Line(l1) = {p1, p2};
l2 = newl;  Line(l2) = {p2, p3};
l3 = newl;  Line(l3) = {p3, p4};
l4 = newl;  Line(l4) = {p4, p1};

ll = newll; Curve Loop(ll)    = {l1, l2, l3, l4};
s  = news;  Plane Surface(s)  = {ll};
```

`newp` returns the next available point tag, `newl` the next line tag, `newll` the next curve loop tag, `news` the next surface tag, `newv` the next volume tag. This is the recommended approach for any script that builds geometry programmatically.

---

## Extrusion for 3D geometry

`Extrude` is the most efficient way to create 3D geometry from a 2D profile:

```geo
SetFactory("OpenCASCADE");

// 2D inlet profile
Rectangle(1) = {0, 0, 0, W, H};

// Extrude along z to create 3D channel
// Returns a list: {surface_tag, volume_tag, lateral_surface_tags...}
out[] = Extrude{0, 0, depth}{ Surface{1}; };

// Access extruded entities
volume_tag  = out[1];
top_surface = out[0];   // the far-end cap

Printf("Volume tag: %g", volume_tag);
```

For structured layers (useful for quasi-2D CFD):

```geo
out[] = Extrude{0, 0, depth}{
  Surface{1};
  Layers{n_layers};   // number of element layers
  Recombine;          // recombine triangles into quads → then hexahedra
};
```

---

## Including external files

For large projects, split geometry into reusable components using `Include`:

```geo
// main.geo
L = 8.0;
H = 1.0;
r = 0.1;

Include "geometry/domain.geo";     // defines the outer box
Include "geometry/cylinder.geo";   // defines the body
Include "mesh_settings.geo";       // field definitions and mesh options
```

Variables defined before `Include` are visible inside the included file.

---

## Macro definitions

Macros let you define reusable geometry operations:

```geo
// Macro to create a rounded rectangle
Macro RoundedRect
  // Uses variables: rx0, ry0, rW, rH, rRad, rLc, rTag (base tag)
  // Creates a plane surface with tag rTag
  p1 = newp; Point(p1) = {rx0 + rRad, ry0,        0, rLc};
  p2 = newp; Point(p2) = {rx0 + rW - rRad, ry0,   0, rLc};
  p3 = newp; Point(p3) = {rx0 + rW, ry0 + rRad,   0, rLc};
  // ... arc centres and remaining corners ...
Return

// Call the macro
rx0 = 0; ry0 = 0; rW = 2; rH = 1; rRad = 0.1; rLc = 0.05; rTag = 10;
Call RoundedRect;
```

Macros in `.geo` are basic — for complex, reusable geometry the Python API (Module 10) is strongly preferred.

---

## Practical tips

- Always put `SetFactory("OpenCASCADE")` before any geometry calls if using OCC
- After boolean operations, use `Printf("Surfaces: %g", #Surface[])` to verify entity counts
- Test your parametric range before running long meshes — extreme aspect ratios crash Gmsh
- Keep `lc` values proportional to the geometry (`r / 10`, `H / 8`) so they scale when parameters change
- Use the GUI to verify geometry before meshing: Geometry → Elementary Entities → Show to see tags

---

## Example file

See [`examples/02_cylinder_parametric.geo`](../examples/02_cylinder_parametric.geo) for a complete annotated parametric cylinder-in-channel geometry.

---

[← Module 1](01-geo-syntax-and-kernels.md) | [Course Home](../README.md) | [Next: Boolean Operations →](03-boolean-operations.md)
