# Module 11: Mesh Quality and Optimization

**Previous:** [Module 10 — Python API Automation](10_python_api_automation.md) | **Next:** [Capstone Project](../capstone/README.md)

---

## Overview

A mesh that looks reasonable in the GUI can still cause solver divergence if it contains a small number of highly distorted elements. This module covers quality metrics, built-in optimization, and a pre-export checklist.

---

## 11.1 Quality Metrics

| Metric | Range | Meaning | CFD threshold |
|--------|-------|---------|---------------|
| **Gamma** (γ) | 0–1 | Inscribed/circumscribed sphere ratio | > 0.3 (> 0.5 preferred) |
| **Scaled Jacobian** | −1 to 1 | Determinant ratio at quadrature points | > 0.1 (negative = invalid) |
| **Aspect ratio** | 1–∞ | Max edge / min edge | < 100 bulk; < 10,000 BL prisms |
| **Skewness** | 0–1 | Angular deviation from ideal | < 0.85 (0 = perfect, 1 = degenerate) |
| **Orthogonality** | 0–1 | Face-centre-to-neighbour angle | > 0.1 (OpenFOAM checkMesh) |

For CFD specifically, **scaled Jacobian < 0** (negative Jacobian) indicates an inverted element — the solver will immediately diverge. This is the most critical check.

---

## 11.2 Built-in Optimization

```geo
// In .geo script — apply after meshing
Mesh.Optimize = 1;           // Laplacian smoothing (fast, mild)
Mesh.OptimizeNetgen = 1;     // Netgen optimizer (3D only, stronger)
Mesh.SmoothingSteps = 5;     // smoothing iterations

// Per-surface/volume optimization
Optimize Mesh "Laplace2D";   // 2D surfaces
Optimize Mesh "Relocate3D";  // 3D node relocation
Optimize Mesh "Netgen";      // Netgen 3D (requires Gmsh built with Netgen)
```

In Python:

```python
gmsh.model.mesh.generate(3)
gmsh.model.mesh.optimize("Laplace2D")      # fast pass
gmsh.model.mesh.optimize("Netgen")         # stronger (3D)
gmsh.model.mesh.optimize("HighOrder")      # for quadratic meshes only
```

Apply optimization in order: Laplacian first (fast, improves average quality), then Netgen (slower, fixes problem elements).

---

## 11.3 Checking Quality in Python

```python
import gmsh

gmsh.initialize()
# ... generate mesh ...

# Get gamma quality for all 3D elements
elem_types, elem_tags, _ = gmsh.model.mesh.getElements(dim=3)
if elem_tags:
    all_tags = [t for group in elem_tags for t in group]
    quality  = gmsh.model.mesh.getElementQualities(all_tags, "gamma")

    bad  = sum(1 for q in quality if q < 0.1)
    inv  = sum(1 for q in quality if q < 0)
    total = len(quality)

    print(f"Total 3D elements : {total}")
    print(f"Invalid (gamma<0) : {inv}  ({100*inv/total:.2f}%)")
    print(f"Poor    (gamma<0.1): {bad}  ({100*bad/total:.2f}%)")
    print(f"Mean gamma         : {sum(quality)/total:.3f}")
    print(f"Min gamma          : {min(quality):.4f}")

    if inv > 0:
        raise ValueError("Mesh contains inverted elements — do not export")

gmsh.finalize()
```

---

## 11.4 OpenFOAM `checkMesh` Integration

After converting with `gmshToFoam`, always run `checkMesh`:

```bash
checkMesh 2>&1 | tee checkMesh.log

# Key lines to check:
grep -E "Max (skewness|non-orthogonality|aspect ratio)|FAILED|OK" checkMesh.log
```

| `checkMesh` metric | Acceptable | Warning | Action needed |
|--------------------|-----------|---------|---------------|
| Max non-orthogonality | < 70° | 70–85° | Reduce time step, use `limitedLinear` |
| Max skewness | < 4 | 4–20 | Remesh problem region |
| Max aspect ratio | < 1000 | 1000–10000 | OK in BL if well-structured |
| Negative volumes | 0 | — | Remesh — will diverge |

---

## 11.5 Pre-Export Checklist

Before exporting a mesh for CFD:

```
Geometry
  [ ] All boolean operations completed and synchronised
  [ ] No duplicate or overlapping surfaces
  [ ] Domain is watertight (closed surface loop for 3D)

Physical groups
  [ ] All boundary surfaces are in a physical group
  [ ] Volume(s) are in a physical group
  [ ] Naming matches solver conventions

Mesh
  [ ] No inverted elements (Jacobian > 0 everywhere)
  [ ] Minimum gamma > 0.2 (bulk), BL prisms may be lower
  [ ] BL first cell height matches target y1
  [ ] BL growth ratio uniform (no abrupt jumps)
  [ ] Total cell count appropriate for available compute

Export
  [ ] MshFileVersion = 2.2 (for OpenFOAM / Fluent)
  [ ] Physical groups exported (not just geometry)
  [ ] Verify with: gmsh -check mesh.msh
```

---

## 11.6 Debugging Common Mesh Failures

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Solver diverges immediately | Inverted elements | Check Jacobian; re-optimise or refine |
| `checkMesh` fails orthogonality | Coarse mesh with sharp features | Add size field near edges/corners |
| BL layers not generated | Wrong surface tags in BL field | Verify tags in GUI; use Python API |
| Huge element size jump at BL edge | Missing transition field | Add Threshold field on top of BL |
| `gmshToFoam` crashes | Pyramid elements in mesh | Use `Mesh.Algorithm3D = 1`; avoid `Recombine` on 3D |
| Physical group missing from .msh | Entity not added to group | Check with `grep PhysicalName mesh.msh` |

---

## Summary

- Check **scaled Jacobian** — any negative value means an inverted element and immediate solver failure
- Apply `Mesh.Optimize = 1` and `Mesh.OptimizeNetgen = 1` always
- Use the Python API to query quality statistics and gate export
- Run `checkMesh` (OpenFOAM) as an independent quality gate after conversion
- The pre-export checklist is the last line of defence before a simulation

---

**Previous:** [Module 10 — Python API Automation](10_python_api_automation.md) | **Next:** [Capstone Project](../capstone/README.md)
