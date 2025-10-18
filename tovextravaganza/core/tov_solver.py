"""
TOV Solver Module
Solves Tolman-Oppenheimer-Volkoff equations for neutron star structure
"""
import numpy as np
import warnings
from scipy.integrate import odeint
from .eos import EOS


class TOVSolver:
    """
    Solver for the Tolman-Oppenheimer-Volkoff equations.
    """
    
    # Physical constants
    MSUN_CODE = 1.4766  # 1 Msun in code units (km)
    
    def __init__(self, eos, r_max=100.0, dr=0.0005, rtol=1e-12, atol=1e-14):
        """
        Initialize TOV solver.
        
        Parameters:
        -----------
        eos : EOS
            Equation of state object
        r_max : float
            Maximum radius for integration (km)
        dr : float
            Radial step size (km)
        rtol, atol : float
            ODE integration tolerances
        """
        self.eos = eos
        self.r_max = r_max
        self.dr = dr
        self.rtol = rtol
        self.atol = atol
    
    def _tov_equations(self, y, r):
        """
        TOV differential equations in dimensionless code units.
        
        Parameters:
        -----------
        y : array
            [M, p] - mass and pressure
        r : float
            Radial coordinate
            
        Returns:
        --------
        array
            [dM/dr, dp/dr]
        """
        M, p = y
        
        if p <= 0.0:
            return [0.0, 0.0]
        
        e = self.eos.get_energy_density(p)
        dMdr = 4.0 * np.pi * r * r * e
        
        # Add small epsilon to prevent division by zero
        denom = r * (r - 2.0 * M) + 1e-30
        dpdr = -((e + p) * (M + 4.0 * np.pi * r**3 * p)) / denom
        
        return [dMdr, dpdr]
    
    def solve(self, central_p, return_profile=False):
        """
        Solve TOV equations for given central pressure.
        
        Parameters:
        -----------
        central_p : float
            Central pressure in code units
        return_profile : bool
            If True, return full radial profile
            
        Returns:
        --------
        If return_profile=False:
            NeutronStar object
        If return_profile=True:
            (NeutronStar, r_vals, M_vals, p_vals)
        """
        r_vals = np.arange(0.0, self.r_max + self.dr, self.dr)
        y0 = [0.0, central_p]
        
        # Integrate with error handling
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                sol = odeint(self._tov_equations, y0, r_vals,
                           rtol=self.rtol, atol=self.atol)
                if w:
                    for warning in w:
                        print(f"  ODE Warning (p_c={central_p:.3e}): {warning.message}")
            except Exception as e:
                print(f"  ERROR: ODE failed for p_c={central_p:.3e}: {e}")
                raise
        
        M_vals = sol[:, 0]
        p_vals = sol[:, 1]
        
        # Find surface (where p -> 0)
        idx_surface = np.where(p_vals <= 0.0)[0]
        if len(idx_surface) > 0:
            i_surf = idx_surface[0]
        else:
            i_surf = len(r_vals) - 1
        
        R = r_vals[i_surf]
        M_code = M_vals[i_surf]
        M_solar = M_code / self.MSUN_CODE
        
        star = NeutronStar(
            central_pressure=central_p,
            radius=R,
            mass_code=M_code,
            mass_solar=M_solar,
            eos=self.eos
        )
        
        if return_profile:
            return star, r_vals[:i_surf+1], M_vals[:i_surf+1], p_vals[:i_surf+1]
        else:
            return star
    
    def solve_sequence(self, num_stars=500, p_min=None, p_max=None):
        """
        Solve for a sequence of stars with different central pressures.
        
        Parameters:
        -----------
        num_stars : int
            Number of stars to compute
        p_min, p_max : float
            Pressure range (uses EOS range if None)
            
        Returns:
        --------
        list of NeutronStar objects
        """
        if p_min is None or p_max is None:
            p_range = self.eos.get_pressure_range()
            p_min = p_min or max(p_range[0], 1e-15)
            p_max = p_max or p_range[1]
        
        p_c_values = np.logspace(np.log10(p_min), np.log10(p_max), num_stars)
        
        stars = []
        for p_c in p_c_values:
            try:
                star = self.solve(p_c)
                stars.append(star)
            except Exception as e:
                print(f"Failed to solve for p_c={p_c:.3e}: {e}")
        
        return stars


class NeutronStar:
    """
    Represents a neutron star solution.
    """
    
    def __init__(self, central_pressure, radius, mass_code, mass_solar, eos):
        """
        Initialize neutron star.
        
        Parameters:
        -----------
        central_pressure : float
            Central pressure (code units)
        radius : float
            Radius (km)
        mass_code : float
            Mass in code units (km)
        mass_solar : float
            Mass in solar masses
        eos : EOS
            Equation of state used
        """
        self.central_pressure = central_pressure
        self.radius = radius
        self.mass_code = mass_code
        self.mass_solar = mass_solar
        self.eos = eos
        self._extra_properties = {}
    
    @property
    def compactness(self):
        """Compactness C = M/R"""
        return self.mass_code / self.radius if self.radius > 0 else 0.0
    
    def interpolate_eos_at_center(self):
        """
        Interpolate all EOS columns at the central pressure.
        
        Returns:
        --------
        dict
            {column_name: value}
        """
        result = {}
        for col in self.eos.colnames:
            if col != "p":
                result[col] = self.eos.get_value(col, self.central_pressure)
        return result
    
    def is_valid(self, min_mass=0.01):
        """Check if this is a valid physical solution."""
        return self.mass_solar > min_mass and self.radius > 0
    
    def __repr__(self):
        return (f"NeutronStar(M={self.mass_solar:.4f} Msun, "
                f"R={self.radius:.4f} km, p_c={self.central_pressure:.3e})")

