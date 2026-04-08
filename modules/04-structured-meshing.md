# Module 04 — Structured Meshing

[← Previous](03-boolean-operations.md) | [Course Home](../README.md) | [Next →](05-unstructured-meshing.md)

---

## Structured meshing with Transfinite

Structured meshes (hexahedra in 3D, quads in 2D) have lower numerical diffusion than unstructured tet meshes. Gmsh generates them via Transfinite commands.

---

## Transfinite Curve

Distributes nodes along an edge with a specified progression:

```geo
Transfinite Curve{1} = 20;                          // 20 nodes, uniform
Transfinite Curve{2} = 20 Using Progression 1.2;   // geometric, bunching toward end
Transfinite Curve{3} = 20 Using Bump 3.0;          // bunching toward both ends
```

Negative curve tag reverses the bunching direction.

---

## Transfinite Surface and Volume

```geo
Transfinite Surface{1};          // must specify 3 or 4 corner points
Recombine Surface{1};            // triangles → quads

Transfinite Volume{1};
Recombine Volume{1};             // tetrahedra → hexahedra
```

Always call `Recombine` after `Transfinite` to get quads/hexahedra.

---

## Complete 2D structured channel

```geo
L = 4.0; H = 1.0; Nx = 80; Ny = 30; growth = 1.15;
SetFactory("OpenCASCADE");

Point(1) = {0, 0, 0}; Point(2) = {L, 0, 0};
Point(3) = {L, H, 0}; Point(4) = {0, H, 0};
Line(1)={1,2}; Line(2)={2,3}; Line(3)={3,4}; Line(4)={4,1};
Curve Loop(1) = {1,2,3,4};
Plane Surface(1) = {1};

Transfinite Curve{1, 3} = Nx;
Transfinite Curve{2}    = Ny Using Progression growth;
Transfinite Curve{-4}   = Ny Using Progression growth;

Transfinite Surface{1} = {1, 2, 3, 4};
Recombine Surface{1};

Physical Curve("inlet")  = {4};
Physical Curve("outlet") = {2};
Physical Curve("bottom") = {1};
Physical Curve("top")    = {3};
Physical Surface("fluid") = {1};
Mesh 2;
```

---

## 3D structured pipe: O-grid topology

For circular cross-sections, an O-grid (inner square block + 4 surrounding blocks) gives the most uniform hex mesh. The inner square avoids the singularity at the pipe centreline.

Key steps:
1. Define inner square points at `r * 0.4` from centre
2. Define perimeter points on the circle
3. Connect with arcs and radial lines
4. Create 5 transfinite surfaces (4 outer + 1 inner)
5. Extrude with `Layers{Nz}; Recombine;`

---

## Tips

- Use Progression 1.1–1.25 for wall-normal BL clustering — higher values create over-stretched cells
- Specify corners explicitly in `Transfinite Surface{s} = {c1,c2,c3,c4}` to control bunching direction
- The `Alternating` keyword flips the diagonal in alternating cells — needed for some solvers

---

## Example file

See [`examples/04_transfinite_channel.geo`](../examples/04_transfinite_channel.geo) for a fully structured 2D channel with wall-normal bunching.


---

[← Previous](03-boolean-operations.md) | [Course Home](../README.md) | [Next →](05-unstructured-meshing.md)
