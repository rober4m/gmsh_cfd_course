"""
Module 10 — Python API: parametric 3D pipe with boundary layers
================================================================
Builds a stenosed pipe geometry, applies a BoundaryLayer field,
assigns physical groups, meshes, optimises, and exports to both
OpenFOAM MSH2 and SU2 formats.

Usage:
    python 10_python_api_pipe.py
    python 10_python_api_pipe.py --gui          # open Gmsh GUI
    python 10_python_api_pipe.py --radius 0.01  # change radius
"""

import gmsh
import math
import sys
import argparse


def build_pipe(R=0.025, L=0.1, y_plus=1.0, U_ref=1.0, nu=1e-6, gui=False):
    """Build and mesh a 3D pipe with boundary layers."""

    gmsh.initialize()
    gmsh.model.add("pipe")

    # ── GEOMETRY ─────────────────────────────────────────────
    gmsh.model.occ.addCylinder(0, 0, 0, L, 0, 0, R)
    gmsh.model.occ.synchronize()

    # ── IDENTIFY SURFACES ────────────────────────────────────
    surfaces = gmsh.model.getEntities(2)
    inlet_tag = outlet_tag = wall_tag = None

    for dim, tag in surfaces:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        cx = (xmin + xmax) / 2
        if abs(cx) < 1e-10:
            inlet_tag = tag
        elif abs(cx - L) < 1e-10:
            outlet_tag = tag
        else:
            wall_tag = tag

    print(f"inlet={inlet_tag}, outlet={outlet_tag}, wall={wall_tag}")

    # ── PHYSICAL GROUPS ──────────────────────────────────────
    g = gmsh.model.addPhysicalGroup(2, [inlet_tag])
    gmsh.model.setPhysicalName(2, g, "inlet")

    g = gmsh.model.addPhysicalGroup(2, [outlet_tag])
    gmsh.model.setPhysicalName(2, g, "outlet")

    g = gmsh.model.addPhysicalGroup(2, [wall_tag])
    gmsh.model.setPhysicalName(2, g, "wall")

    g = gmsh.model.addPhysicalGroup(3, [1])
    gmsh.model.setPhysicalName(3, g, "fluid")

    # ── FIRST CELL HEIGHT ────────────────────────────────────
    Re = U_ref * 2 * R / nu
    Cf = 0.058 * Re ** (-0.2)
    u_tau = U_ref * math.sqrt(Cf / 2)
    delta_y = y_plus * nu / u_tau
    print(f"Re={Re:.0f}, u_tau={u_tau:.4f} m/s, delta_y={delta_y:.2e} m")

    # ── BOUNDARY LAYER FIELD ─────────────────────────────────
    f1 = gmsh.model.mesh.field.add("BoundaryLayer")
    gmsh.model.mesh.field.setNumbers(f1, "SurfacesList", [wall_tag])
    gmsh.model.mesh.field.setNumber(f1, "Size", delta_y)
    gmsh.model.mesh.field.setNumber(f1, "Ratio", 1.2)
    gmsh.model.mesh.field.setNumber(f1, "NbLayers", 12)
    gmsh.model.mesh.field.setNumber(f1, "Quads", 1)
    gmsh.model.mesh.field.setAsBackgroundMesh(f1)

    # ── MESH OPTIONS ─────────────────────────────────────────
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", R / 3)
    gmsh.option.setNumber("Mesh.Algorithm3D", 4)  # Netgen

    # ── GENERATE AND OPTIMIZE ────────────────────────────────
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.optimize("Netgen")
    gmsh.model.mesh.optimize("")

    # ── EXPORT ───────────────────────────────────────────────
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write("pipe_openfoam.msh")
    gmsh.write("pipe.su2")
    print("Written: pipe_openfoam.msh, pipe.su2")

    # ── GUI ──────────────────────────────────────────────────
    if gui and "-nopopup" not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=float, default=0.025)
    parser.add_argument("--length", type=float, default=0.1)
    parser.add_argument("--yplus",  type=float, default=1.0)
    parser.add_argument("--gui",    action="store_true")
    args = parser.parse_args()

    build_pipe(R=args.radius, L=args.length, y_plus=args.yplus, gui=args.gui)
