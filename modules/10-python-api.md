# Module 10 — Python API Automation

[← Previous](09-export.md) | [Course Home](../README.md) | [Next →](11-quality-optimization.md)

---

## Python API automation

The Gmsh Python API enables parametric pipelines, integration with numpy/scipy, batch meshing, and post-processing without the GUI.

---

## Installation

```bash
pip install gmsh
```

---

## Basic structure

```python
import gmsh

gmsh.initialize()
gmsh.model.add("my_model")

# geometry, fields, mesh settings here

gmsh.model.mesh.generate(2)
gmsh.write("output.msh")
gmsh.finalize()
```

---

## OCC geometry

```python
gmsh.model.add("channel")
gmsh.model.occ.addRectangle(0, 0, 0, L, H)      # returns tag
gmsh.model.occ.addDisk(xc, H/2, 0, r, r)
gmsh.model.occ.cut([(2,1)], [(2,2)], removeObject=True, removeTool=True)
gmsh.model.occ.synchronize()   # MUST call before querying or meshing
```

Entity tuples are `(dim, tag)`: `(0,t)` point, `(1,t)` curve, `(2,t)` surface, `(3,t)` volume.

---

## Querying entities after booleans

```python
surfaces = gmsh.model.getEntities(2)
for dim, tag in surfaces:
    xmin,ymin,zmin,xmax,ymax,zmax = gmsh.model.getBoundingBox(dim, tag)
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    print(f"Surface {tag}: centre ({cx:.3f}, {cy:.3f})")
```

Identify entities by their geometry (bounding box, centroid) rather than tag number — tags are not stable after boolean operations.

---

## Physical groups

```python
g = gmsh.model.addPhysicalGroup(2, [fluid_surface_tag])
gmsh.model.setPhysicalName(2, g, "fluid")

g2 = gmsh.model.addPhysicalGroup(1, [4])
gmsh.model.setPhysicalName(1, g2, "inlet")
```

---

## Mesh fields

```python
f1 = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(f1, "CurvesList", cyl_curves)
gmsh.model.mesh.field.setNumber(f1, "Sampling", 200)

f2 = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(f2, "InField", f1)
gmsh.model.mesh.field.setNumber(f2, "SizeMin", lc_cyl)
gmsh.model.mesh.field.setNumber(f2, "SizeMax", lc_far)
gmsh.model.mesh.field.setNumber(f2, "DistMin", r*0.5)
gmsh.model.mesh.field.setNumber(f2, "DistMax", r*5)
gmsh.model.mesh.field.setAsBackgroundMesh(f2)
```

---

## Parametric sweep

```python
import math

def build_channel(r=0.1, y_plus=1.0, U_ref=10.0, nu=1.5e-5):
    gmsh.initialize()
    gmsh.model.add(f"r{r:.3f}")

    L, H = 8.0, 1.0
    gmsh.model.occ.addRectangle(0, 0, 0, L, H)
    gmsh.model.occ.addDisk(2.0, H/2, 0, r, r)
    gmsh.model.occ.cut([(2,1)], [(2,2)], removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()

    # ... fields, physical groups ...

    gmsh.model.mesh.generate(2)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(f"channel_r{r:.3f}.msh")
    gmsh.finalize()

for radius in [0.05, 0.10, 0.15, 0.20]:
    build_channel(r=radius)
```

---

## Accessing mesh data

```python
import numpy as np
gmsh.model.mesh.generate(3)

node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
coords = np.array(node_coords).reshape(-1, 3)
print(f"Nodes: {len(node_tags)}, bounds x: {coords[:,0].min():.3f}–{coords[:,0].max():.3f}")

elem_types, elem_tags, _ = gmsh.model.mesh.getElements()
for et, etags in zip(elem_types, elem_tags):
    name,_,_,_,_,_ = gmsh.model.mesh.getElementProperties(et)
    print(f"  {name}: {len(etags)} elements")
```

---

## Opening GUI for debugging

```python
import sys
if "-nopopup" not in sys.argv:
    gmsh.fltk.run()
```

---

## Example file

See [`examples/10_python_api_pipe.py`](../examples/10_python_api_pipe.py) for a parametric 3D pipe with BL, fields, and multi-format export.


---

[← Previous](09-export.md) | [Course Home](../README.md) | [Next →](11-quality-optimization.md)
