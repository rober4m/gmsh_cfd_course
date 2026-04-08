# Module 11 — Mesh Quality and Optimization

[← Previous](10-python-api.md) | [Course Home](../README.md) | [Next →](capstone.md)

---

## Mesh quality and optimization

Mesh quality directly affects solver convergence, accuracy, and stability. Poor elements — skewed, flat, or with negative Jacobians — can cause divergence.

---

## Key quality metrics

| Metric | Good range | Effect if poor |
|--------|-----------|----------------|
| Aspect ratio | < 20 (BL: up to 1000 OK) | Ill-conditioned system |
| Skewness | < 0.85 | Gradient accuracy loss |
| Scaled Jacobian | > 0.1 (negative = invalid) | Invalid elements |
| Non-orthogonality | < 70° | Discretisation error |

---

## Quality visualization in GUI

1. **Tools → Statistics** — element counts and quality histogram
2. **Plugin → AnalyseMeshQuality** — colour elements by ICN (1 = perfect, 0 = degenerate)

```geo
Plugin(AnalyseMeshQuality).ICNMeasure = 1;
Plugin(AnalyseMeshQuality).Run;
```

---

## Optimization passes

```geo
Mesh 3;
Optimize "Netgen";   // swap + smooth tets (3D, best quality)
Optimize "";         // Laplacian smoothing (fast follow-up)
```

For high-order elements:

```geo
Mesh 3;
SetOrder 2;
Optimize "HighOrder";         // moves mid-nodes for Jacobian
Optimize "HighOrderElastic";  // elastic analogy — better, slower
```

---

## Python quality check

```python
import numpy as np
import gmsh

gmsh.initialize()
gmsh.open("case.geo")
gmsh.model.mesh.generate(3)
gmsh.model.mesh.optimize("Netgen")
gmsh.model.mesh.optimize("")

gmsh.plugin.setNumber("AnalyseMeshQuality", "ICNMeasure", 1)
gmsh.plugin.run("AnalyseMeshQuality")

view_tag = gmsh.view.getTags()[-1]
_, _, data, _, _ = gmsh.view.getListData(view_tag)
qualities = np.array([v for d in data for v in d])
print(f"ICN min:  {qualities.min():.4f}")
print(f"ICN mean: {qualities.mean():.4f}")
print(f"Bad elements (ICN < 0.1): {(qualities < 0.1).sum()}")

gmsh.write("optimized.msh")
gmsh.finalize()
```

---

## Diagnosing and fixing bad elements

| Cause | Fix |
|-------|-----|
| Very small feature | Increase `CharacteristicLengthMin` or simplify geometry |
| Sharp angle (< 20°) | Fillet geometry, or refine locally |
| Thin gap | Reduce mesh size or widen geometry |
| Bad BL fan | Adjust `FanPointsList` or fan geometry |
| Conflicting fields | Check `Min` field is combining all refinement fields |

---

## OpenFOAM quality check

After `gmshToFoam`:

```bash
checkMesh -allTopology -allGeometry
```

Key thresholds: max non-orthogonality < 70° (ideally < 40°), max skewness < 4 (ideally < 0.85).

---

## Example file

See [`examples/11_mesh_quality.py`](../examples/11_mesh_quality.py) for an automated quality check and optimization pipeline.


---

[← Previous](10-python-api.md) | [Course Home](../README.md) | [Next →](capstone.md)
