# Module 8: Boundary Layer Meshes

**Previous:** [Module 7 — Physical Groups and BCs](07_physical_groups_bcs.md) | **Next:** [Module 9 — Export for Solvers](09_export_for_solvers.md)

---

## Overview

Boundary layer meshing is the most critical step in wall-bounded CFD. It creates thin, highly-stretched prism or quad elements near walls to capture the steep velocity and temperature gradients in the viscous sublayer. This module covers y⁺ sizing theory, the Gmsh `BoundaryLayer` field, and practical workflow for both 2D and 3D cases.

---

## 8.1 First Cell Height from Target y⁺

The first cell height `y1` is determined by the dimensionless wall distance y⁺ and the local wall shear stress. The flat-plate correlation gives a practical estimate:

```
y1 = y⁺ × ν / u_τ

where:
  u_τ = sqrt(τ_w / ρ)        (friction velocity)
  τ_w ≈ 0.5 × ρ × U² × Cf   (wall shear stress, flat plate estimate)
  Cf  = 0.058 × Re_L^(-0.2)  (skin friction coefficient, turbulent)
  Re_L = U × L / ν           (Reynolds number based on reference length)
```

Target y⁺ values by turbulence model:

| Turbulence model | Target y⁺ | Reason |
|-----------------|-----------|--------|
| k-ε (standard)  | 30–300   | Wall functions — first cell in log layer |
| k-ω SST         | 1–5      | Low-Re formulation resolves sublayer |
| Spalart-Allmaras| 1–5      | Designed for y⁺ ~ 1 |
| LES / DNS       | ≈ 1      | Must resolve viscous sublayer |

Python helper for y⁺ estimation (also in `examples/`):

```python
# examples/yplus_calculator.py
import math

def first_cell_height(U, L, nu, rho=1.0, y_plus=1.0):
    Re_L = U * L / nu
    Cf   = 0.058 * Re_L**(-0.2)
    tau_w = 0.5 * rho * U**2 * Cf
    u_tau = math.sqrt(tau_w / rho)
    y1    = y_plus * nu / u_tau
    return y1

# Example: air flow over a 1m plate at 10 m/s
y1 = first_cell_height(U=10, L=1.0, nu=1.5e-5, rho=1.2, y_plus=1.0)
print(f"First cell height: {y1:.2e} m")   # ~6e-5 m
```

---

## 8.2 The `BoundaryLayer` Field

Gmsh's `BoundaryLayer` field generates prism (or quad in 2D) layers automatically from specified wall curves/surfaces:

```geo
// 2D example — boundary layer on cylinder surface
Field[1] = BoundaryLayer;
Field[1].CurvesList      = {5, 6, 7, 8};   // wall curves
Field[1].Size            = 5e-5;            // first layer height (y1)
Field[1].Ratio           = 1.2;             // growth ratio between layers
Field[1].Thickness       = 0.005;           // total BL thickness
Field[1].Quads           = 1;               // 1 = quads in 2D (0 = triangles)
Field[1].IntersectMetrics = 0;

BoundaryLayer Field = 1;
```

### Key parameters

| Parameter | Description | Typical value |
|-----------|-------------|---------------|
| `Size` | First cell height (= y1) | Computed from y⁺ formula |
| `Ratio` | Growth ratio per layer | 1.1–1.3 |
| `Thickness` | Total BL thickness | 10–30 × y1 or δ₉₉ estimate |
| `Quads` | 1 = quad layers (2D), prisms (3D) | 1 (always for CFD) |
| `NLayers` | Override layer count (optional) | Derived from Size/Ratio/Thickness |

### Controlling layer count

If you specify all three of `Size`, `Ratio`, and `Thickness`, Gmsh computes the layer count automatically. To manually set `n` layers:

```geo
// n layers: thickness = Size * (Ratio^n - 1) / (Ratio - 1)
// Or specify directly:
Field[1].NLayers   = 15;
Field[1].Size      = 1e-4;
Field[1].Ratio     = 1.15;
// Thickness auto-computed
```

---

## 8.3 3D Boundary Layers

In 3D, the `BoundaryLayer` field works on surfaces:

```geo
Field[1] = BoundaryLayer;
Field[1].SurfacesList    = {wall_surfs[]};  // list of wall surfaces
Field[1].Size            = 1e-4;
Field[1].Ratio           = 1.2;
Field[1].Thickness       = 0.003;
Field[1].Quads           = 1;              // 1 = prism layers

BoundaryLayer Field = 1;
```

The resulting mesh has prism elements near the wall and tetrahedra in the bulk. This hybrid mesh is standard for industrial RANS CFD.

---

## 8.4 Multiple Wall Regions

Apply different BL settings to different walls in the same mesh:

```geo
// Airfoil: fine BL on wing surface, coarser on farfield (if needed)
Field[1] = BoundaryLayer;
Field[1].CurvesList = {airfoil_curves[]};
Field[1].Size       = 5e-6;     // fine — y⁺ ~ 1 for k-ω SST
Field[1].Ratio      = 1.15;
Field[1].Thickness  = 0.002;
Field[1].Quads      = 1;

// Channel walls — different sizing
Field[2] = BoundaryLayer;
Field[2].CurvesList = {top_wall, bottom_wall};
Field[2].Size       = 2e-5;
Field[2].Ratio      = 1.2;
Field[2].Thickness  = 0.005;
Field[2].Quads      = 1;

// Combine with Min (for the background field)
Field[10] = Min;
Field[10].FieldsList = {1, 2, ...};   // other size fields too
Background Field = 10;
```

---

## 8.5 Checking BL Quality

After meshing, verify the boundary layer visually in Gmsh and numerically:

```bash
# In Gmsh GUI:
# Tools > Statistics — shows element count, quality histograms
# View > Mesh > 2D element quality (colourmap of Jacobian ratios)
```

Key quality checks for BL meshes:
- **First cell height**: matches target y1 ± 10%
- **Aspect ratio**: prism aspect ratio (height/width) should be < 1000 for stability
- **Growth ratio**: verify layers expand smoothly — sudden jumps cause solver issues
- **Layer count**: check total BL thickness covers the expected δ₉₉

In Python:
```python
# Use gmsh.model.mesh.getQualityStats() after meshing
# or export to VTK and check with ParaView filters
```

---

## Summary

- Compute first cell height from target y⁺ using the flat-plate correlation
- Use the `BoundaryLayer` field — specify `Size`, `Ratio`, and `Thickness`
- Always use `Quads = 1` in the BL field for CFD (prisms in 3D)
- Apply multiple `BoundaryLayer` fields for geometries with different wall regions
- Check aspect ratios and growth uniformity before exporting

---

**Previous:** [Module 7 — Physical Groups and BCs](07_physical_groups_bcs.md) | **Next:** [Module 9 — Export for Solvers](09_export_for_solvers.md)
