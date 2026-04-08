# Capstone Project — Full CFD Meshing Pipeline

[← Module 11](11-quality-optimization.md) | [Course Home](../README.md)

---

## Project overview

Build a fully parametric, production-ready mesh for a 3D stenosed pipe — a pipe with a partial blockage — and export it for OpenFOAM and SU2. This geometry is a standard benchmark case for cardiovascular CFD and internal flow studies.

The entire pipeline runs from a single Python script with command-line parameters.

---

## Geometry definition

```
         ┌─────────────────────────────────────┐
inlet →  │  ╔═══════════╗       ╔═══════════╗  │  → outlet
         │  ║ stenosis  ║       ║           ║  │
         │  ╚═══════════╝       ╚═══════════╝  │
         └─────────────────────────────────────┘
           smooth cosine-shaped narrowing at x=L/3
```

**Parameters:**
- `R` — pipe radius [m]
- `L` — pipe length [m]
- `s` — stenosis severity (0 = no stenosis, 0.75 = 75% area reduction)
- `x_sten` — stenosis axial centre location
- `w_sten` — stenosis axial width (half-width of cosine profile)
- `y_plus` — target y⁺ for wall boundary layer

---

## Full pipeline script

See [`examples/capstone_stenosed_pipe.py`](../examples/capstone_stenosed_pipe.py) for the complete annotated implementation. The script:

1. Accepts command-line arguments for all geometric parameters
2. Builds the stenosed pipe using OpenCASCADE revolution
3. Computes the first cell height for the target y⁺
4. Applies a `BoundaryLayer` field on all wall surfaces
5. Applies a `Threshold` size field for refinement near the stenosis
6. Assigns physical groups: `inlet`, `outlet`, `wall`, `fluid`
7. Generates the 3D mesh with Netgen optimization
8. Exports to both OpenFOAM MSH2 and SU2 formats
9. Runs a quality check and prints statistics

---

## Running the capstone

```bash
# Default parameters
python examples/capstone_stenosed_pipe.py

# Custom stenosis severity and y+
python examples/capstone_stenosed_pipe.py --severity 0.5 --yplus 1.0 --radius 0.005 --length 0.1

# Open GUI for inspection
python examples/capstone_stenosed_pipe.py --gui
```

---

## Expected outputs

After running:

```
capstone_stenosed_pipe_s050.msh   (OpenFOAM MSH2)
capstone_stenosed_pipe_s050.su2   (SU2)
```

Quality stats printed to console:
```
--- Mesh statistics ---
Total nodes:    ~120,000
Total elements: ~650,000 (tets + prisms)
ICN min:   0.312
ICN mean:  0.847
Bad elements (ICN < 0.1): 0
First cell height: 4.2e-06 m (target y+ = 1.0)
```

---

## OpenFOAM setup

After converting with `gmshToFoam`:

```bash
# In your OpenFOAM case directory
gmshToFoam capstone_stenosed_pipe_s050.msh
checkMesh

# Set boundary types in constant/polyMesh/boundary:
# inlet  → patch
# outlet → patch
# wall   → wall
```

Recommended initial case setup:
- Solver: `simpleFoam` (steady) or `pimpleFoam` (transient)
- Turbulence model: k-ω SST with low-Re corrections (requires y⁺ ≤ 1)
- Re = U_mean × 2R / ν ≈ 500–2000 (laminar to transitional range)

---

## Mesh sensitivity study

Use the parametric script to run a mesh sensitivity study:

```python
# Run 3 mesh resolutions
for refinement in [0.5, 1.0, 2.0]:
    subprocess.run([
        "python", "examples/capstone_stenosed_pipe.py",
        "--refinement", str(refinement)
    ])
```

Compare pressure drop and wall shear stress distributions across the three meshes to verify grid independence.

---

## Extension challenges

Once you have the base case working, try these extensions:

1. **Pulsatile inlet**: add a cosine-shaped velocity inlet profile using `codedFixedValue` in OpenFOAM
2. **Multiple stenoses**: parameterise the script to place N stenoses at arbitrary axial positions
3. **Patient-specific geometry**: replace the synthetic stenosis with a STEP file from medical imaging segmentation (Module 3 — STEP import)
4. **Conjugate heat transfer**: add a pipe wall solid region using `BooleanFragments` and set up a CHT case in OpenFOAM
5. **Mesh adaptation**: use the quality script (Module 11) to identify high-Jacobian regions and refine them iteratively

---

## Key concepts applied in this capstone

| Module | Concept | Where used |
|--------|---------|------------|
| 01 | OpenCASCADE kernel | `SetFactory("OpenCASCADE")` |
| 02 | Parametric geometry | All coordinates from parameters |
| 03 | Boolean operations | `BooleanFragments` for multi-region option |
| 05 | Unstructured meshing | Tetrahedral interior |
| 06 | Size fields | `Threshold` field near stenosis |
| 07 | Physical groups | All 4 boundaries named |
| 08 | Boundary layers | `BoundaryLayer` field on wall |
| 09 | Export | MSH2 + SU2 dual export |
| 10 | Python API | Full pipeline in one script |
| 11 | Quality & optimization | Netgen pass + ICN check |

---

[← Module 11](11-quality-optimization.md) | [Course Home](../README.md)
