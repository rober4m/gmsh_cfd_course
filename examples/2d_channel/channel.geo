// examples/2d_channel/channel.geo
// Parametric 2D rectangular channel

SetFactory("OpenCASCADE");

DefineConstant[
  L  = {4.0, Name "Geometry/Length"},
  H  = {1.0, Name "Geometry/Height"},
  Nx = {80,  Name "Mesh/Nodes along length"},
  Ny = {20,  Name "Mesh/Nodes along height"}
];

Rectangle(1) = {0, 0, 0, L, H};

// OCC Rectangle curves: 1=bottom, 2=right, 3=top, 4=left
Transfinite Curve{1, 3} = Nx;
Transfinite Curve{2, 4} = Ny;
Transfinite Surface{1};
Recombine Surface{1};

Physical Curve("inlet",  1) = {4};
Physical Curve("outlet", 2) = {2};
Physical Curve("walls",  3) = {1, 3};
Physical Surface("fluid",1) = {1};

Mesh 2;
Save "channel.msh";
