# Module 10: Python API Automation

**Previous:** [Module 9 — Export for Solvers](09_export_for_solvers.md) | **Next:** [Module 11 — Mesh Quality and Optimization](11_quality_optimization.md)

---

## Overview

The Gmsh Python API exposes all of Gmsh's geometry and meshing functionality in a scriptable, programmable interface. It handles the one thing `.geo` scripts cannot do well: reliably recovering entity tags after boolean operations. For parametric studies, automated pipelines, and any geometry of moderate complexity, the Python API is the right tool.

---

## 10.1 API Basics

```python
import gmsh

gmsh.initialize()
gmsh.model.add("my_model")

# ... geometry and meshing commands ...

gmsh.finalize()
```

The API is organised into namespaces:

| Namespace | Purpose |
|-----------|---------|
| `gmsh.model.occ` | OCC geometry kernel (create, modify, boolean ops) |
| `gmsh.model.geo` | Built-in kernel |
| `gmsh.model.mesh` | Meshing, size fields, mesh options |
| `gmsh.model` | Entity queries, physical groups |
| `gmsh.option` | Get/set Gmsh options |
| `gmsh.write` | Save mesh to file |

---

## 10.2 Geometry Creation

All OCC primitives from `.geo` have Python equivalents:

```python
gmsh.model.occ.addBox(x0, y0, z0, dx, dy, dz, tag=-1)
gmsh.model.occ.addSphere(cx, cy, cz, r, tag=-1)
gmsh.model.occ.addCylinder(x0, y0, z0, dx, dy, dz, r, tag=-1)
gmsh.model.occ.addRectangle(x0, y0, z0, dx, dy, tag=-1)
gmsh.model.occ.addDisk(cx, cy, cz, rx, ry, tag=-1)

# tag=-1 means auto-assign (recommended)
```

After creating entities, always call `synchronize` before meshing or querying:

```python
gmsh.model.occ.synchronize()
```

---

## 10.3 Boolean Operations and Tag Recovery

This is where the Python API shines:

```python
import gmsh

gmsh.initialize()
gmsh.model.add("cht_pipe")

R_inner = 0.05
R_outer = 0.08
Len     = 0.5

# Create geometries
t_inner = gmsh.model.occ.addCylinder(0,0,0, 0,0,Len, R_inner)
t_outer = gmsh.model.occ.addCylinder(0,0,0, 0,0,Len, R_outer)

# BooleanFragments — returns (output_dimtags, output_dimtags_map)
out, parent_map = gmsh.model.occ.fragment(
    [(3, t_outer)],   # tool
    [(3, t_inner)]    # object
)
gmsh.model.occ.synchronize()

# out is a list of (dim, tag) tuples for all resulting entities
# Find volumes
volumes = [tag for dim, tag in out if dim == 3]
print("Resulting volumes:", volumes)

# Get bounding box of each volume to identify fluid vs solid
for vol in volumes:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(3, vol)
    print(f"  Volume {vol}: x=[{xmin:.3f},{xmax:.3f}], r_max={max(abs(xmax),abs(ymax)):.4f}")
```

---

## 10.4 Physical Groups in Python

```python
# Get all surfaces
surfs = gmsh.model.getEntities(dim=2)

# Find inlet (z=0 plane)
tol = 1e-3
inlet_tags = []
outlet_tags = []
wall_tags = []

for dim, tag in surfs:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
    if abs(zmax - zmin) < tol and abs(zmin) < tol:
        inlet_tags.append(tag)
    elif abs(zmax - zmin) < tol and abs(zmax - Len) < tol:
        outlet_tags.append(tag)
    else:
        wall_tags.append(tag)

gmsh.model.addPhysicalGroup(2, inlet_tags,  name="inlet")
gmsh.model.addPhysicalGroup(2, outlet_tags, name="outlet")
gmsh.model.addPhysicalGroup(2, wall_tags,   name="walls")
gmsh.model.addPhysicalGroup(3, volumes,     name="fluid")
```

---

## 10.5 Mesh Fields in Python

All `.geo` field types are available via `gmsh.model.mesh.field`:

```python
f_dist = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(f_dist, "CurvesList", [1, 2, 3, 4])
gmsh.model.mesh.field.setNumber(f_dist, "Sampling", 200)

f_thresh = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(f_thresh, "InField",  f_dist)
gmsh.model.mesh.field.setNumber(f_thresh, "SizeMin",  0.005)
gmsh.model.mesh.field.setNumber(f_thresh, "SizeMax",  0.1)
gmsh.model.mesh.field.setNumber(f_thresh, "DistMin",  0.02)
gmsh.model.mesh.field.setNumber(f_thresh, "DistMax",  0.3)

f_bl = gmsh.model.mesh.field.add("BoundaryLayer")
gmsh.model.mesh.field.setNumbers(f_bl, "CurvesList", wall_curve_tags)
gmsh.model.mesh.field.setNumber(f_bl, "Size",      first_cell_height)
gmsh.model.mesh.field.setNumber(f_bl, "Ratio",     1.2)
gmsh.model.mesh.field.setNumber(f_bl, "Thickness", 0.003)
gmsh.model.mesh.field.setNumber(f_bl, "Quads",     1)
gmsh.model.mesh.field.setAsBoundaryLayer(f_bl)

f_min = gmsh.model.mesh.field.add("Min")
gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", [f_thresh])
gmsh.model.mesh.field.setAsBackgroundMesh(f_min)

gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
```

---

## 10.6 Parametric Study Example

A reusable function to mesh a cylinder-in-channel case and sweep the cylinder radius:

```python
# examples/parametric_sweep/cylinder_sweep.py

import gmsh
import math
import os

def mesh_cylinder_channel(r, lc_cyl, output_dir="."):
    gmsh.initialize()
    gmsh.model.add(f"cylinder_r{r:.3f}")

    L, H = 8.0, 2.0
    xc, yc = 2.0, 1.0

    # Geometry
    ch  = gmsh.model.occ.addRectangle(0, 0, 0, L, H)
    cyl = gmsh.model.occ.addDisk(xc, yc, 0, r, r)

    out, _ = gmsh.model.occ.cut([(2, ch)], [(2, cyl)])
    gmsh.model.occ.synchronize()

    domain_tag = out[0][1]

    # Boundary detection
    curves = gmsh.model.getEntities(dim=1)
    inlet, outlet, walls, cylinder = [], [], [], []
    tol = 1e-3

    for _, tag in curves:
        xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, tag)
        cx_curve = (xmin + xmax) / 2
        cy_curve = (ymin + ymax) / 2
        dist_from_cyl = math.sqrt((cx_curve - xc)**2 + (cy_curve - yc)**2)

        if abs(xmax - xmin) < tol and abs(xmin) < tol:
            inlet.append(tag)
        elif abs(xmax - xmin) < tol and abs(xmax - L) < tol:
            outlet.append(tag)
        elif dist_from_cyl < r * 1.5:
            cylinder.append(tag)
        else:
            walls.append(tag)

    gmsh.model.addPhysicalGroup(1, inlet,    name="inlet")
    gmsh.model.addPhysicalGroup(1, outlet,   name="outlet")
    gmsh.model.addPhysicalGroup(1, walls,    name="walls")
    gmsh.model.addPhysicalGroup(1, cylinder, name="cylinder")
    gmsh.model.addPhysicalGroup(2, [domain_tag], name="fluid")

    # Size fields
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "CurvesList", cylinder)

    f_thresh = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_thresh, "InField",  f_dist)
    gmsh.model.mesh.field.setNumber(f_thresh, "SizeMin",  lc_cyl)
    gmsh.model.mesh.field.setNumber(f_thresh, "SizeMax",  0.1)
    gmsh.model.mesh.field.setNumber(f_thresh, "DistMin",  r * 0.1)
    gmsh.model.mesh.field.setNumber(f_thresh, "DistMax",  r * 3.0)
    gmsh.model.mesh.field.setAsBackgroundMesh(f_thresh)

    gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)

    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.optimize("Laplace2D")

    fname = os.path.join(output_dir, f"cylinder_r{r:.3f}.msh")
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(fname)
    gmsh.finalize()
    print(f"Saved: {fname}")
    return fname

if __name__ == "__main__":
    os.makedirs("sweep_meshes", exist_ok=True)
    for r in [0.10, 0.15, 0.20, 0.25, 0.30]:
        mesh_cylinder_channel(r=r, lc_cyl=r/20, output_dir="sweep_meshes")
```

---

## 10.7 Mesh Quality Statistics

```python
gmsh.model.mesh.generate(3)

# Get quality histogram
types, counts, _ = gmsh.model.mesh.getQualityHistogram("gamma", nbClasses=10)
print("Gamma quality histogram (0=bad, 1=perfect):")
for t, c in zip(types, counts):
    print(f"  {t:.2f}: {c} elements")

# Access individual element quality values
elem_types, elem_tags, _ = gmsh.model.mesh.getElements(dim=3)
quality = gmsh.model.mesh.getElementQualities(elem_tags[0], "gamma")
import statistics
print(f"Mean quality: {statistics.mean(quality):.3f}")
print(f"Min quality:  {min(quality):.3f}")
```

---

## Summary

- The Python API is essential for robust tag recovery after boolean operations
- Use bounding box queries (`getBoundingBox`) to identify surfaces by position
- All `.geo` field types and mesh commands are available via `gmsh.model.mesh.field`
- Wrap your mesh generation in a function to enable parameter sweeps
- Always call `gmsh.finalize()` — even after errors (use `try/finally`)

---

**Previous:** [Module 9 — Export for Solvers](09_export_for_solvers.md) | **Next:** [Module 11 — Mesh Quality and Optimization](11_quality_optimization.md)
