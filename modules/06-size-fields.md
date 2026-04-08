# Module 06 — Size Fields and Refinement

[← Previous](05-unstructured-meshing.md) | [Course Home](../README.md) | [Next →](07-physical-groups.md)

---

## Size fields

Size fields give spatial control over element size — far more powerful than point-level `lc` values. Gmsh takes the minimum of all active fields at each location.

---

## The field workflow

```geo
Field[1] = Distance;        // compute distance from entities
Field[1].CurvesList = {5};  // measure from curve 5
Field[1].Sampling = 200;

Field[2] = Threshold;       // map distance to size
Field[2].InField  = 1;
Field[2].SizeMin  = lc_min;
Field[2].SizeMax  = lc_max;
Field[2].DistMin  = d_min;
Field[2].DistMax  = d_max;

Field[3] = Min;
Field[3].FieldsList = {2, other_field};

Background Field = 3;
```

---

## Distance field

```geo
Field[1] = Distance;
Field[1].PointsList   = {5, 6};
Field[1].CurvesList   = {3, 4};
Field[1].SurfacesList = {1};      // 3D only
Field[1].Sampling = 100;
```

---

## Threshold field

Maps distance to element size with a smooth ramp between DistMin and DistMax:

```geo
Field[2] = Threshold;
Field[2].InField  = 1;
Field[2].SizeMin  = 0.002;
Field[2].SizeMax  = 0.05;
Field[2].DistMin  = 0.005;
Field[2].DistMax  = 0.1;
Field[2].StopAtDistMax = 1;
```

---

## Box field

Applies a specific size within a rectangular region — good for wake refinement:

```geo
Field[3] = Box;
Field[3].XMin = 1.0;  Field[3].XMax = 4.0;
Field[3].YMin = -0.5; Field[3].YMax = 0.5;
Field[3].VIn  = 0.01;
Field[3].VOut = 0.1;
```

---

## MathEval field

Arbitrary mathematical expression for size:

```geo
Field[5] = MathEval;
Field[5].F = "0.005 + 0.02 * Sqrt(x^2 + y^2 + z^2)";
```

Supports `x`, `y`, `z`, `Sin`, `Cos`, `Sqrt`, `Exp`, `Abs`, `Min`, `Max`, `Pi`.

---

## Cylinder field

Refinement within a cylindrical region:

```geo
Field[4] = Cylinder;
Field[4].XAxis = 1.0; Field[4].YAxis = 0.0; Field[4].ZAxis = 0.0;
Field[4].XCenter = 0.0; Field[4].YCenter = 0.0; Field[4].ZCenter = 0.0;
Field[4].Radius = 0.2;
Field[4].VIn = 0.005; Field[4].VOut = 0.05;
```

---

## Tips

- Always set `Background Field` — without it, all fields are ignored
- Set `Mesh.CharacteristicLengthFromPoints = 0` to let fields fully override point `lc` values
- Use `Min` field to combine multiple refinement zones — they compose cleanly
- `Sampling` on Distance fields must be high enough for curved boundaries: use at least 100 per curve

---

## Example file

See [`examples/06_size_fields.geo`](../examples/06_size_fields.geo) for a cylinder wake with surface refinement and wake box.


---

[← Previous](05-unstructured-meshing.md) | [Course Home](../README.md) | [Next →](07-physical-groups.md)
