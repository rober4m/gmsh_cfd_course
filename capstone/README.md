# Capstone Project: Full CFD Meshing Pipeline — 3D Stenosis

**Previous:** [Module 11 — Mesh Quality and Optimization](../modules/11_quality_optimization.md)

---

## Project Overview

Build a complete, production-quality CFD mesh of a pipe with a stenosis (partial blockage) — a geometry used in cardiovascular CFD to study blood flow through arterial narrowing. The entire pipeline runs from a single Python script with command-line parameters.

---

## Learning Objectives

By completing this project, you will demonstrate:

- Parametric OCC geometry construction via the Python API
- Boundary layer sizing from a specified y⁺ target
- Size field composition (Distance + Threshold + wake refinement)
- Robust physical group assignment using bounding box queries
- Mesh quality checking with an automated pass/fail gate
- Export to OpenFOAM and SU2 formats

---

## Geometry Description

A circular pipe with a cosine-profiled stenosis in the middle section:

```
         Inlet          Stenosis          Outlet
    ─────────────── ─────╱──────╲──────── ───────────────
    |               |   |        |   |               |
    |   R_pipe      |   R_throat |   |   R_pipe      |
    |               |            |               |
    ─────────────── ───────────────── ───────────────────
    0             L_in    L_in+L_s  L_in+L_s+L_out
```

**Parameters (all via `DefineConstant` or CLI args):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `R_pipe` | 0.01 m | Pipe radius (full section) |
| `R_throat` | 0.006 m | Minimum radius at stenosis throat |
| `L_in` | 0.05 m | Inlet straight length |
| `L_stenosis` | 0.02 m | Stenosis section length |
| `L_out` | 0.08 m | Outlet straight length |
| `y_plus` | 1.0 | Target y⁺ (default: resolve sublayer) |
| `U_mean` | 0.1 m/s | Mean inlet velocity (for y⁺ estimate) |
| `nu` | 3.5e-6 m²/s | Blood kinematic viscosity |

---

## Deliverables

### 1. `stenosis.py` — Full Python API meshing script

Structure:

```python
# stenosis.py
import gmsh, math, sys, os

def compute_y1(U, L, nu, y_plus):
    """Compute first cell height from y+ target."""
    ...

def build_stenosis(R_pipe, R_throat, L_in, L_s, L_out, y_plus, U_mean, nu):
    """Build geometry, mesh, assign groups, return mesh stats."""
    ...

def check_quality(min_gamma_threshold=0.1):
    """Raise if any element fails quality gate."""
    ...

def export(base_name):
    """Export to .msh (v2.2) and .su2."""
    ...

if __name__ == "__main__":
    # Parse CLI args, call build_stenosis, check_quality, export
    ...
```

### 2. `stenosis.msh` — OpenFOAM-ready mesh (msh2 format)

### 3. `stenosis.su2` — SU2-ready mesh

### 4. `quality_report.txt` — Output of quality check function including:
- Total element count (tets + prisms)
- BL layer count and first cell height achieved
- Min / mean gamma
- Pass/fail status

### 5. `README_run.md` — Instructions to reproduce the mesh

---

## Evaluation Criteria

| Criterion | Check |
|-----------|-------|
| Geometry is watertight | No open surfaces |
| All physical groups present | inlet, outlet, wall, fluid |
| BL first cell achieves target y1 ± 20% | Measure in ParaView |
| Min gamma > 0.1 | Quality gate passes |
| Script runs cleanly with different R_throat values | Test R_throat = 0.004, 0.006, 0.008 |
| Export opens in OpenFOAM without `checkMesh` errors | Non-orthogonality < 85° |

---

## Hints

- Build the stenosis profile as a 2D spline in the rz-plane, then revolve with `Extrude` rotation
- Use `BooleanFragments` if you split the geometry into inlet/stenosis/outlet sections for zonal refinement
- The stenosis throat is the highest-velocity region — add a `Cylinder` size field there
- First cell height at Re ~ 100–1000 (cardiovascular) will be ~1–10 µm — check for aspect ratio issues in the BL

---

## Extension Challenges

1. Add a **secondary stenosis** 0.03 m downstream and mesh the intervening recirculation zone with a wake box field
2. Build a **parametric sweep** over stenosis severity (R_throat / R_pipe from 0.3 to 0.9) and plot cell count vs severity
3. Generate a **2D axisymmetric** version for OpenFOAM's `axisymmetric` solver (wedge mesh, 5° sector)

---

Good luck — and remember, a mesh that doesn't converge is just a geometry file you haven't debugged yet.
