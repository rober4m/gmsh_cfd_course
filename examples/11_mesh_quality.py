"""
Module 11 — Mesh quality check and optimization pipeline
=========================================================
Opens a mesh or .geo file, runs optimization passes, computes
ICN quality metrics, and prints a statistics report.

Usage:
    python 11_mesh_quality.py mesh.msh
    python 11_mesh_quality.py case.geo --dim 3
"""

import gmsh
import numpy as np
import sys
import argparse


def check_quality(filepath, dim=3, optimize=True, gui=False):
    gmsh.initialize()

    if filepath.endswith(".geo"):
        gmsh.open(filepath)
        gmsh.model.mesh.generate(dim)
    else:
        gmsh.open(filepath)

    if optimize:
        print("Optimizing...")
        if dim == 3:
            gmsh.model.mesh.optimize("Netgen")
        gmsh.model.mesh.optimize("")

    # Run quality plugin
    gmsh.plugin.setNumber("AnalyseMeshQuality", "ICNMeasure", 1)
    gmsh.plugin.run("AnalyseMeshQuality")

    # Get quality data
    view_tags = gmsh.view.getTags()
    if not view_tags:
        print("No quality view generated.")
        gmsh.finalize()
        return

    view_tag = view_tags[-1]
    try:
        _, _, data, _, _ = gmsh.view.getListData(view_tag)
        qualities = np.array([v for d in data for v in d])

        print("\n── Mesh quality report ──────────────────────────")
        print(f"  ICN min:               {qualities.min():.4f}")
        print(f"  ICN max:               {qualities.max():.4f}")
        print(f"  ICN mean:              {qualities.mean():.4f}")
        print(f"  ICN std:               {qualities.std():.4f}")
        print(f"  Elements ICN < 0.1:    {(qualities < 0.1).sum()}")
        print(f"  Elements ICN < 0.3:    {(qualities < 0.3).sum()}")
        print(f"  Elements ICN >= 0.5:   {(qualities >= 0.5).sum()}")
        print(f"  Total elements:        {len(qualities)}")
        print("─────────────────────────────────────────────────")
    except Exception as e:
        print(f"Could not retrieve quality data: {e}")

    # Node count
    node_tags, _, _ = gmsh.model.mesh.getNodes()
    print(f"  Total nodes:           {len(node_tags)}")

    # Element counts by type
    elem_types, elem_tags, _ = gmsh.model.mesh.getElements()
    for et, etags in zip(elem_types, elem_tags):
        name, edim, _, _, _, _ = gmsh.model.mesh.getElementProperties(et)
        if edim == dim:
            print(f"  {name}: {len(etags)}")

    # Write optimized mesh
    out = filepath.replace(".msh", "_opt.msh").replace(".geo", "_opt.msh")
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)
    print(f"\nWritten: {out}")

    if gui and "-nopopup" not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("--dim",      type=int, default=3)
    parser.add_argument("--no-opt",   action="store_true")
    parser.add_argument("--gui",      action="store_true")
    args = parser.parse_args()

    check_quality(args.filepath, dim=args.dim,
                  optimize=not args.no_opt, gui=args.gui)
