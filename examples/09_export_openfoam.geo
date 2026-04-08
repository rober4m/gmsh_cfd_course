// ============================================================
// Module 09 — Export 3D pipe for OpenFOAM, Fluent, SU2
// ============================================================
// Generates a simple pipe mesh and exports in MSH2 format.
// Run gmshToFoam on the output for OpenFOAM.
//
// Usage: gmsh 09_export_openfoam.geo -3
// ============================================================

SetFactory("OpenCASCADE");
r = 0.025; L = 0.1;
Cylinder(1) = {0, 0, 0,  L, 0, 0,  r};
Physical Surface("inlet")  = {2};
Physical Surface("outlet") = {3};
Physical Surface("wall")   = {4};
Physical Volume("fluid")   = {1};
Mesh.CharacteristicLengthMax = r / 4;
Mesh.Algorithm3D = 4;
Mesh 3;
Optimize "Netgen";
Mesh.MshFileVersion = 2.2;
Save "pipe_openfoam.msh";
// Also export SU2
Save "pipe.su2";
Printf("Exported: pipe_openfoam.msh and pipe.su2");
