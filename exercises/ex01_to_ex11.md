# Exercises

One exercise per module. Solutions are in `solutions/`.

---

## Exercise 1 — `.geo` Syntax and Kernels

Build a 2D backward-facing step geometry using the OCC kernel:
- Inlet height `H_in = 1.0 m`, step height `H_step = 0.5 m`, downstream length `L = 6.0 m`
- All dimensions as variables at the top of the script
- Physical groups: `inlet`, `outlet`, `walls`

**Deliverable:** `ex01_bfs.geo`

---

## Exercise 2 — Parametric Geometry

Build a parametric 2D converging-diverging nozzle using `DefineConstant` for all dimensions. Use a `Spline` for the nozzle contours. Verify with three different parameter sets from the command line.

**Deliverable:** `ex02_nozzle.geo`

---

## Exercise 3 — Boolean Operations

Create a 3D wind tunnel domain (10×4×4 m) with a square prism obstacle (0.5×0.5×4 m at x=3). Use `BooleanDifference`. Assign all physical groups by bounding box.

**Deliverable:** `ex03_wind_tunnel.geo`

---

## Exercise 4 — Structured Meshing

Build a 2D structured quad mesh of the backward-facing step from Exercise 1. Apply wall-normal grading (ratio ≈ 1.15). Report total quad count and aspect ratio range.

**Deliverable:** `ex04_bfs_structured.geo`

---

## Exercise 5 — Unstructured Meshing

Generate an unstructured 3D mesh of a T-junction pipe (two inlets D=0.05 m, one outlet D=0.07 m). Compare Algorithm 1 vs 4 quality. Target ~200,000 cells.

**Deliverable:** `ex05_tjunction.geo`, quality comparison notes

---

## Exercise 6 — Size Fields and Refinement

Apply `Distance` + `Threshold` + `Box` (wake) + `Min` fields to the cylinder-in-channel geometry. Compare cell count and near-wall spacing against a uniform mesh.

**Deliverable:** `ex06_cylinder_fields.geo`, comparison table

---

## Exercise 7 — Physical Groups and BCs

Prepare the 3D wind tunnel for OpenFOAM and SU2 with appropriate naming conventions and a sample OpenFOAM `boundary` file snippet.

**Deliverable:** `ex07_wt_openfoam.geo`, `ex07_wt_su2.geo`, `boundary_snippet.txt`

---

## Exercise 8 — Boundary Layer Meshes

Apply a BL to the cylinder-in-channel for k-omega SST (y+ = 1). Compute first cell height analytically (show working in comments). 20 layers, ratio 1.15.

**Deliverable:** `ex08_cylinder_bl.geo`

---

## Exercise 9 — Export for Solvers

Export the Exercise 8 mesh to OpenFOAM, SU2, and VTK. Write a Bash script that generates all three formats from a single `.geo` file.

**Deliverable:** `ex09_export.sh`, sample `boundary` file

---

## Exercise 10 — Python API Automation

Rewrite the cylinder-in-channel mesh entirely in Python using the gmsh API. Use `getBoundingBox` for all physical group assignments. Parametric sweep over D in {0.10, 0.15, 0.20, 0.25} m.

**Deliverable:** `ex10_cylinder_api.py`

---

## Exercise 11 — Mesh Quality and Optimization

For the 3D pipe mesh: compute quality statistics, apply Netgen optimization, compare before/after. Implement pre-export checklist as a Python function.

**Deliverable:** `ex11_quality_check.py`
