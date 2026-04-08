# Module 6: Size Fields and Refinement

**Previous:** [Module 5 — Unstructured Meshing](05_unstructured_meshing.md) | **Next:** [Module 7 — Physical Groups and BCs](07_physical_groups_bcs.md)

---

## Overview

Size fields are the professional way to control element size across a domain. Rather than relying on the `lc` hint on individual points, size fields let you specify exactly how mesh size varies in space — near walls, in wakes, around features, and in the far field. They are composable: you build complex refinement by combining simple fields.

---

## 6.1 The Field System

A field is a scalar function defined over the domain. The final element size at any point is determined by evaluating all active fields and taking the minimum. Fields are defined with:

```geo
Field[tag] = Type;
Field[tag].Parameter = value;
Background Field = tag;   // or Min field if combining multiple
```

Always set `Mesh.CharacteristicLengthExtendFromBoundary = 0` when using fields — otherwise point-based `lc` values override your fields.

---

## 6.2 Key Field Types

### Distance field

Computes the distance from any point in the domain to specified curves or surfaces:

```geo
Field[1] = Distance;
Field[1].CurvesList = {5, 6, 7, 8};   // cylinder boundary curves
Field[1].Sampling   = 100;             // resolution for distance computation
```

### Threshold field

Maps the distance field to an element size using a linear ramp between two distance thresholds:

```geo
Field[2] = Threshold;
Field[2].InField      = 1;       // input: Distance field above
Field[2].SizeMin      = 0.005;   // size at distance <= DistMin
Field[2].SizeMax      = 0.1;     // size at distance >= DistMax
Field[2].DistMin      = 0.02;    // inner radius of ramp
Field[2].DistMax      = 0.3;     // outer radius of ramp
```

Between `DistMin` and `DistMax`, size varies linearly. Outside `DistMax`, size is `SizeMax`.

### Min field

Takes the minimum of multiple fields — the standard way to combine refinement zones:

```geo
Field[10] = Min;
Field[10].FieldsList = {2, 4, 6};   // take minimum of fields 2, 4, and 6
Background Field = 10;
```

### MathEval field

Arbitrary mathematical expression for size as a function of x, y, z:

```geo
Field[3] = MathEval;
Field[3].F = "0.02 + 0.1 * Sqrt(x^2 + (y-0.5)^2)";   // radially graded
```

### Box field

Uniform refinement inside an axis-aligned box:

```geo
Field[4] = Box;
Field[4].VIn   = 0.01;    // size inside box
Field[4].VOut  = 0.1;     // size outside box
Field[4].XMin  = 0.5;  Field[4].XMax = 4.0;
Field[4].YMin  = 0.3;  Field[4].YMax = 0.7;
Field[4].ZMin  = 0.0;  Field[4].ZMax = 1.0;
```

### Cylinder field

Refinement inside a cylinder:

```geo
Field[5] = Cylinder;
Field[5].VIn  = 0.005;
Field[5].VOut = 0.1;
Field[5].Radius = 0.5;
Field[5].XAxis = 1; Field[5].YAxis = 0; Field[5].ZAxis = 0;
Field[5].XCenter = 2; Field[5].YCenter = 0; Field[5].ZCenter = 0;
```

---

## 6.3 Wake Refinement: Practical Example

Refining the wake behind a bluff body — one of the most common CFD mesh requirements:

```geo
// Cylinder surface: curves 5,6,7,8 (after BooleanDifference)
// Wake extends downstream in +x direction

// Step 1: Distance from cylinder
Field[1] = Distance;
Field[1].CurvesList = {5, 6, 7, 8};
Field[1].Sampling   = 200;

// Step 2: Near-cylinder refinement
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = 0.005;  // on cylinder surface
Field[2].SizeMax = 0.08;   // far field
Field[2].DistMin = 0.01;
Field[2].DistMax = 0.5;

// Step 3: Wake box refinement
Field[3] = Box;
Field[3].VIn  = 0.015;    // refined wake
Field[3].VOut = 1e10;     // don't affect outside (Min field handles this)
Field[3].XMin = 0.5;  Field[3].XMax = 6.0;   // downstream extent
Field[3].YMin = 0.7;  Field[3].YMax = 1.3;   // narrow wake region
Field[3].ZMin = -1;   Field[3].ZMax = 1;

// Step 4: Combine — take minimum everywhere
Field[10] = Min;
Field[10].FieldsList = {2, 3};
Background Field = 10;

// Step 5: Lock — prevent point lc from overriding
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthMin = 0.003;
Mesh.CharacteristicLengthMax = 0.15;
```

---

## 6.4 Anisotropic Size Fields

For boundary layer-like refinement without the `BoundaryLayer` field (e.g., when you need directional control):

```geo
Field[1] = MathEvalAniso;
Field[1].m11 = "0.001";          // size in x direction
Field[1].m22 = "0.001 + 0.1*y";  // size in y grows away from wall
Field[1].m33 = "0.05";           // size in z
Field[1].m12 = "0";
Field[1].m13 = "0";
Field[1].m23 = "0";
```

Full anisotropic control is more commonly done via the Mmg/BAMG remeshers — but for simple wall-normal gradation, the `BoundaryLayer` field (Module 8) is the right tool.

---

## 6.5 Combining Size Fields: Full Example

```geo
// Airfoil in a far-field domain
// Refinement: LE/TE, surface, wake, far field

// 1. Distance from airfoil surface
Field[1] = Distance;
Field[1].CurvesList = {airfoil_curves[]};
Field[1].Sampling   = 500;

// 2. Surface refinement (tight near airfoil)
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = 0.001;   // on airfoil
Field[2].SizeMax = 0.05;    // far field
Field[2].DistMin = 0.005;
Field[2].DistMax = 0.5;

// 3. Leading edge — extra tight
Field[3] = Cylinder;
Field[3].VIn  = 0.0005;
Field[3].VOut = 1e10;
Field[3].Radius  = 0.02;
Field[3].XCenter = le_x;  Field[3].YCenter = le_y;  Field[3].ZCenter = 0;

// 4. Wake box
Field[4] = Box;
Field[4].VIn  = 0.003;
Field[4].VOut = 1e10;
Field[4].XMin = te_x;    Field[4].XMax = te_x + 3.0;
Field[4].YMin = -0.15;   Field[4].YMax = 0.15;
Field[4].ZMin = -1;      Field[4].ZMax = 1;

// 5. Combine all
Field[20] = Min;
Field[20].FieldsList = {2, 3, 4};
Background Field = 20;

Mesh.CharacteristicLengthExtendFromBoundary = 0;
```

---

## Summary

- `Distance` → `Threshold` → `Min` is the standard composition pattern
- `Box` and `Cylinder` fields add targeted refinement zones without affecting the rest of the domain
- `MathEval` handles any custom function of (x, y, z)
- Always set `CharacteristicLengthExtendFromBoundary = 0` when using background fields
- Set global `CharacteristicLengthMin` and `CharacteristicLengthMax` as safety bounds

---

## Exercise

> See [exercises/ex01_to_ex11.md](../exercises/ex01_to_ex11.md) — Exercise 6

For the cylinder-in-channel geometry from Module 2:
- Apply a `Distance` + `Threshold` field on the cylinder
- Add a `Box` field for the wake (2D behind cylinder)
- Combine with `Min` field
- Compare total cell count and y-nearest-wall distance against a uniform `lc` mesh

---

**Previous:** [Module 5 — Unstructured Meshing](05_unstructured_meshing.md) | **Next:** [Module 7 — Physical Groups and BCs](07_physical_groups_bcs.md)
