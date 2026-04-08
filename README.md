# Gmsh Scripting for CFD — Introduction to Intermediate Course

A structured course in Gmsh `.geo` scripting and Python API usage for computational fluid dynamics geometry and meshing. The course takes you from maintainable parametric scripts to production-ready meshes for OpenFOAM, Fluent, and SU2.

---

## Prerequisites

- Basic Gmsh GUI experience (you have meshed a simple shape before)
- Understanding of mesh element types (tri, quad, tet, hex, prism)
- Familiarity with CFD boundary condition concepts (inlet, outlet, wall, symmetry)
- At least one CFD solver installed (OpenFOAM recommended for examples)

## Tools Required

- [Gmsh 4.x](https://gmsh.info/) — version 4+ required for all API and field features
- Python 3.8+ with `gmsh` package: `pip install gmsh`
- A text editor — VSCode with the [Gmsh extension](https://marketplace.visualstudio.com/items?itemName=gcpmendez.gmsh-language-support) is recommended
- OpenFOAM (optional, for capstone validation)

---

## Course Structure

### Fundamentals

| Module | Topic | Description |
|--------|-------|-------------|
| [01](modules/01-geo-syntax-and-kernels.md) | `.geo` syntax & kernels | Entity hierarchy, built-in vs OpenCASCADE, curve loops |
| [02](modules/02-parametric-geometry.md) | Parametric geometry | Variables, expressions, loops, reusable scripts |
| [03](modules/03-boolean-operations.md) | Boolean operations | Union, difference, fragments, multi-region domains |

### Meshing

| Module | Topic | Description |
|--------|-------|-------------|
| [04](modules/04-structured-meshing.md) | Structured meshing | Transfinite curves, surfaces, and volumes |
| [05](modules/05-unstructured-meshing.md) | Unstructured meshing | Delaunay, Frontal-Delaunay, mesh algorithms |
| [06](modules/06-size-fields.md) | Size fields & refinement | Distance, Threshold, MathEval, Min/Max fields |

### CFD-Specific

| Module | Topic | Description |
|--------|-------|-------------|
| [07](modules/07-physical-groups.md) | Physical groups & BCs | Naming boundaries, solver-ready labelling |
| [08](modules/08-boundary-layers.md) | Boundary layer meshes | BoundaryLayer field, y⁺ sizing, fan/quad-dominant |
| [09](modules/09-export.md) | Export for solvers | OpenFOAM, Fluent (.msh), SU2, format options |

### Advanced

| Module | Topic | Description |
|--------|-------|-------------|
| [10](modules/10-python-api.md) | Python API automation | `gmsh.initialize`, parametric pipelines, batch meshing |
| [11](modules/11-quality-optimization.md) | Quality & optimization | Jacobian, skewness, Optimize/OptimizeNetgen |

### Project

| | Topic | Description |
|--|-------|-------------|
| [Capstone](modules/capstone.md) | Full CFD pipeline | Stenosed pipe: parametric 3D geometry → BL mesh → physical groups → export |

---

## Repository Layout

```
gmsh-cfd-course/
├── README.md                  ← you are here
├── modules/
│   ├── 01-geo-syntax-and-kernels.md
│   ├── 02-parametric-geometry.md
│   ├── 03-boolean-operations.md
│   ├── 04-structured-meshing.md
│   ├── 05-unstructured-meshing.md
│   ├── 06-size-fields.md
│   ├── 07-physical-groups.md
│   ├── 08-boundary-layers.md
│   ├── 09-export.md
│   ├── 10-python-api.md
│   ├── 11-quality-optimization.md
│   └── capstone.md
└── examples/
    ├── 01_channel_2d.geo
    ├── 02_cylinder_parametric.geo
    ├── 03_boolean_fragment.geo
    ├── 04_transfinite_channel.geo
    ├── 05_unstructured_airfoil.geo
    ├── 06_size_fields.geo
    ├── 07_physical_groups.geo
    ├── 08_boundary_layer.geo
    ├── 09_export_openfoam.geo
    ├── 10_python_api_pipe.py
    ├── 11_mesh_quality.py
    └── capstone_stenosed_pipe.py
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/gmsh-cfd-course.git
cd gmsh-cfd-course
gmsh examples/01_channel_2d.geo
```

Run Python examples:

```bash
pip install gmsh
python examples/10_python_api_pipe.py
```

---

## License

MIT — use freely for personal, academic, and commercial projects.
