"""
y+ / first cell height calculator for CFD boundary layer meshing.
Usage: python yplus_calculator.py
"""
import math

def first_cell_height(U, L, nu, rho=1.0, y_plus=1.0):
    """
    Compute first cell height from flat-plate correlation.
    
    Parameters
    ----------
    U      : float  Reference velocity [m/s]
    L      : float  Reference length [m]
    nu     : float  Kinematic viscosity [m^2/s]
    rho    : float  Density [kg/m^3]
    y_plus : float  Target y+
    
    Returns
    -------
    y1     : float  First cell height [m]
    """
    Re_L  = U * L / nu
    Cf    = 0.058 * Re_L**(-0.2)
    tau_w = 0.5 * rho * U**2 * Cf
    u_tau = math.sqrt(tau_w / rho)
    y1    = y_plus * nu / u_tau
    return y1, u_tau, Re_L, Cf

def n_layers(y1, ratio, thickness):
    """Compute number of BL layers given sizing parameters."""
    if ratio == 1.0:
        return int(thickness / y1)
    return int(math.log(1 + thickness * (ratio - 1) / y1) / math.log(ratio)) + 1

if __name__ == "__main__":
    cases = [
        {"label": "Air over flat plate (U=10, L=1m)", "U": 10, "L": 1.0, "nu": 1.5e-5, "rho": 1.2},
        {"label": "Blood in artery (U=0.1, D=0.02m)", "U": 0.1, "L": 0.02, "nu": 3.5e-6, "rho": 1060},
        {"label": "Water pipe flow (U=2, D=0.05m)",   "U": 2.0, "L": 0.05, "nu": 1.0e-6, "rho": 998},
    ]
    for c in cases:
        y1, u_tau, Re, Cf = first_cell_height(c["U"], c["L"], c["nu"], c["rho"], y_plus=1.0)
        n = n_layers(y1, ratio=1.2, thickness=50*y1)
        print(f"\n{c['label']}")
        print(f"  Re = {Re:.2e},  Cf = {Cf:.4f},  u_tau = {u_tau:.4f} m/s")
        print(f"  y1 (y+=1) = {y1:.2e} m")
        print(f"  Suggested: {n} layers, ratio 1.2, total thickness {50*y1:.2e} m")
