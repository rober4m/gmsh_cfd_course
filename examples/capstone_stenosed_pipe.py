"""
Capstone — Parametric stenosed pipe: full CFD meshing pipeline
==============================================================
Builds a 3D pipe with a cosine-shaped stenosis, applies boundary
layers, size fields near the stenosis, assigns physical groups,
and exports to OpenFOAM MSH2 and SU2.

Usage:
    python capstone_stenosed_pipe.py
    python capstone_stenosed_pipe.py --severity 0.5 --yplus 1.0
    python capstone_stenosed_pipe.py --gui
"""

import gmsh
import math
import numpy as np
import sys
import argparse


def build_stenosed_pipe(
    R=0.005,        # pipe radius [m]
    L=0.10,         # pipe length [m]
    severity=0.50,  # stenosis: 0=none, 0.75=75% area reduction
    x_sten=None,    # stenosis centre (default: L/3)
    w_sten=None,    # stenosis half-width (default: R*3)
    y_plus=1.0,
    U_ref=0.1,
    nu=4e-6,        # blood viscosity ~4 cSt
    gui=False,
):
    if x_sten is None:
        x_sten = L / 3
    if w_sten is None:
        w_sten = R * 3

    gmsh.initialize()
    gmsh.model.add(f"stenosed_pipe_s{int(severity*100):03d}")

    # ── GEOMETRY: revolve a 2D profile ───────────────────────
    # Build r(x) profile: pipe with cosine stenosis bump
    # r(x) = R - severity*R * 0.5*(1 + cos(pi*(x-x_sten)/w_sten))
    # for |x - x_sten| <= w_sten

    n_axial = 80        # axial sample points for spline
    n_extra = 20        # extra points through stenosis

    # Build sorted x positions with extra resolution near stenosis
    x_uniform = np.linspace(0, L, n_axial)
    x_sten_region = np.linspace(x_sten - w_sten, x_sten + w_sten, n_extra)
    x_all = np.unique(np.concatenate([x_uniform, x_sten_region]))
    x_all = x_all[(x_all >= 0) & (x_all <= L)]

    def r_profile(x):
        if abs(x - x_sten) <= w_sten:
            bump = 0.5 * (1 + math.cos(math.pi * (x - x_sten) / w_sten))
            return R - severity * R * bump
        return R

    # Create profile points (in the x-r plane, z=0)
    pt_tags = []
    for x in x_all:
        r = r_profile(x)
        tag = gmsh.model.occ.addPoint(x, r, 0)
        pt_tags.append(tag)

    # Centreline points (r=0)
    p_inlet_centre  = gmsh.model.occ.addPoint(0, 0, 0)
    p_outlet_centre = gmsh.model.occ.addPoint(L, 0, 0)

    # Profile spline
    spline_tag = gmsh.model.occ.addSpline(pt_tags)

    # Close the profile with inlet/outlet lines and centreline
    l_inlet    = gmsh.model.occ.addLine(p_inlet_centre, pt_tags[0])
    l_outlet   = gmsh.model.occ.addLine(pt_tags[-1], p_outlet_centre)
    l_axis     = gmsh.model.occ.addLine(p_outlet_centre, p_inlet_centre)

    loop = gmsh.model.occ.addCurveLoop([l_inlet, spline_tag, l_outlet, l_axis])
    profile_surf = gmsh.model.occ.addPlaneSurface([loop])

    # Revolve 360 degrees around x-axis
    out = gmsh.model.occ.revolve(
        [(2, profile_surf)], 0, 0, 0, 1, 0, 0, 2 * math.pi
    )
    gmsh.model.occ.synchronize()

    volumes = gmsh.model.getEntities(3)
    vol_tag = volumes[0][1]

    # ── IDENTIFY SURFACES ────────────────────────────────────
    surfaces = gmsh.model.getEntities(2)
    inlet_tags = []
    outlet_tags = []
    wall_tags = []

    for dim, tag in surfaces:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        cx = (xmin + xmax) / 2
        if abs(xmin - 0) < R * 0.1 and abs(xmax - 0) < R * 0.1:
            inlet_tags.append(tag)
        elif abs(xmin - L) < R * 0.1 and abs(xmax - L) < R * 0.1:
            outlet_tags.append(tag)
        elif xmax - xmin > L * 0.05:
            wall_tags.append(tag)

    print(f"inlet surfaces: {inlet_tags}")
    print(f"outlet surfaces: {outlet_tags}")
    print(f"wall surfaces: {wall_tags}")

    # ── PHYSICAL GROUPS ──────────────────────────────────────
    all_surfs = [t for _, t in surfaces]
    if not inlet_tags:
        inlet_tags = all_surfs[:1]
    if not outlet_tags:
        outlet_tags = all_surfs[1:2]
    if not wall_tags:
        wall_tags = all_surfs[2:]

    g = gmsh.model.addPhysicalGroup(2, inlet_tags)
    gmsh.model.setPhysicalName(2, g, "inlet")
    g = gmsh.model.addPhysicalGroup(2, outlet_tags)
    gmsh.model.setPhysicalName(2, g, "outlet")
    g = gmsh.model.addPhysicalGroup(2, wall_tags)
    gmsh.model.setPhysicalName(2, g, "wall")
    g = gmsh.model.addPhysicalGroup(3, [vol_tag])
    gmsh.model.setPhysicalName(3, g, "fluid")

    # ── FIRST CELL HEIGHT ────────────────────────────────────
    Re = U_ref * 2 * R / nu
    Cf = 0.058 * Re ** (-0.2) if Re > 1e3 else 16 / Re
    u_tau = U_ref * math.sqrt(max(Cf / 2, 1e-10))
    delta_y = y_plus * nu / max(u_tau, 1e-12)
    delta_y = max(delta_y, R * 1e-4)  # safety floor
    print(f"Re={Re:.0f}, delta_y={delta_y:.2e} m")

    # ── BOUNDARY LAYER FIELD ─────────────────────────────────
    f_bl = gmsh.model.mesh.field.add("BoundaryLayer")
    gmsh.model.mesh.field.setNumbers(f_bl, "SurfacesList", wall_tags)
    gmsh.model.mesh.field.setNumber(f_bl, "Size", delta_y)
    gmsh.model.mesh.field.setNumber(f_bl, "Ratio", 1.2)
    gmsh.model.mesh.field.setNumber(f_bl, "NbLayers", 10)
    gmsh.model.mesh.field.setNumber(f_bl, "Quads", 1)

    # ── STENOSIS REFINEMENT FIELD ─────────────────────────────
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "SurfacesList", wall_tags)
    gmsh.model.mesh.field.setNumber(f_dist, "Sampling", 50)

    f_thr = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_thr, "InField", f_dist)
    gmsh.model.mesh.field.setNumber(f_thr, "SizeMin", R / 8)
    gmsh.model.mesh.field.setNumber(f_thr, "SizeMax", R / 1.5)
    gmsh.model.mesh.field.setNumber(f_thr, "DistMin", R * 0.1)
    gmsh.model.mesh.field.setNumber(f_thr, "DistMax", R * 2)

    f_min = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", [f_thr])
    gmsh.model.mesh.field.setAsBackgroundMesh(f_min)

    # Note: BoundaryLayer field also set as background
    gmsh.model.mesh.field.setAsBackgroundMesh(f_bl)

    # ── MESH ─────────────────────────────────────────────────
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", R / 2)
    gmsh.option.setNumber("Mesh.Algorithm3D", 4)  # Netgen frontal

    print("Generating mesh...")
    gmsh.model.mesh.generate(3)
    print("Optimizing...")
    gmsh.model.mesh.optimize("Netgen")
    gmsh.model.mesh.optimize("")

    # ── QUALITY CHECK ────────────────────────────────────────
    gmsh.plugin.setNumber("AnalyseMeshQuality", "ICNMeasure", 1)
    gmsh.plugin.run("AnalyseMeshQuality")

    node_tags, _, _ = gmsh.model.mesh.getNodes()
    print(f"\n── Mesh statistics ──────────────────────────────")
    print(f"  Nodes: {len(node_tags)}")

    etypes, etags, _ = gmsh.model.mesh.getElements(dim=3)
    total_3d = sum(len(t) for t in etags)
    print(f"  3D elements: {total_3d}")
    print(f"  delta_y: {delta_y:.2e} m  (y+ target = {y_plus})")
    print("─────────────────────────────────────────────────")

    # ── EXPORT ───────────────────────────────────────────────
    sev_str = f"s{int(severity*100):03d}"
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(f"capstone_stenosed_pipe_{sev_str}.msh")
    gmsh.write(f"capstone_stenosed_pipe_{sev_str}.su2")
    print(f"Written: capstone_stenosed_pipe_{sev_str}.msh/.su2")

    if gui and "-nopopup" not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius",   type=float, default=0.005)
    parser.add_argument("--length",   type=float, default=0.10)
    parser.add_argument("--severity", type=float, default=0.50)
    parser.add_argument("--yplus",    type=float, default=1.0)
    parser.add_argument("--gui",      action="store_true")
    args = parser.parse_args()

    build_stenosed_pipe(
        R=args.radius, L=args.length,
        severity=args.severity, y_plus=args.yplus,
        gui=args.gui,
    )
