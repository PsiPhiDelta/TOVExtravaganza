"""
Tidal Deformability Calculator Module
Computes tidal Love numbers and deformability for neutron stars
"""
import numpy as np
import warnings
from scipy.integrate import odeint
from .tov_solver import TOVSolver


class TidalCalculator:
    """
    Calculator for tidal deformability and Love numbers.
    """
    
    def __init__(self, tov_solver):
        """
        Initialize tidal calculator.
        
        Parameters:
        -----------
        tov_solver : TOVSolver
            TOV solver instance (uses same EOS and parameters)
        """
        self.tov_solver = tov_solver
        self.eos = tov_solver.eos
        self.r_max = tov_solver.r_max
        self.dr = tov_solver.dr
        self.rtol = tov_solver.rtol
        self.atol = tov_solver.atol
    
    def _tov_tidal_equations(self, y, r):
        """
        Combined TOV + tidal perturbation equations.
        
        Parameters:
        -----------
        y : array
            [M, p, H] where H = r*beta
        r : float
            Radial coordinate
            
        Returns:
        --------
        array
            [dM/dr, dp/dr, dH/dr]
        """
        M, p, H = y
        
        if p <= 0.0:
            return [0.0, 0.0, 0.0]
        
        e = self.eos.get_energy_density(p)
        
        # TOV equations
        dMdr = 4.0 * np.pi * r * r * e
        denom = r * (r - 2.0 * M) + 1e-30
        dpdr = -((e + p) * (M + 4.0 * np.pi * r**3 * p)) / denom
        
        # Tidal perturbation equation
        if r < 1e-8:
            # Near center: H ~ 2r^2, so dH/dr ~ 4r
            dHdr = 4.0 * r
        else:
            m_over_r = M / (r + 1e-30)
            
            # Sound speed squared: cs2 = dp/de
            dp_small = max(1e-8 * abs(p), 1e-20)
            p_plus = min(p + dp_small, self.eos.p_table[-1])
            p_minus = max(p - dp_small, self.eos.p_table[0])
            e_plus = self.eos.get_energy_density(p_plus)
            e_minus = self.eos.get_energy_density(p_minus)
            de = e_plus - e_minus
            dp = p_plus - p_minus
            
            if abs(de) > 1e-30:
                cs2 = dp / de
            else:
                cs2 = 1.0
            
            cs2 = np.clip(cs2, 0.01, 1.0)
            
            y_val = H / r
            F1 = 1.0 - 2.0 * m_over_r
            
            # Tidal ODE coefficients
            A = (1.0 - 4.0 * np.pi * r**2 * (e - p)) / F1
            B = (4.0 * np.pi * r * (5.0 * e + 9.0 * p + (e + p) / cs2)) / F1
            B += (-6.0 / (r * F1))
            B += (2.0 * m_over_r / (r * F1))**2
            B += (2.0 * m_over_r / (r**2 * F1)) * (1.0 + 4.0 * np.pi * r**2 * (e - p))
            
            dHdr = y_val * A + H * B / r
        
        return [dMdr, dpdr, dHdr]
    
    def compute(self, central_p):
        """
        Compute tidal deformability for a given central pressure.
        
        Parameters:
        -----------
        central_p : float
            Central pressure in code units
            
        Returns:
        --------
        dict
            {'R': radius, 'M_code': mass_code, 'M_solar': mass_solar,
             'Lambda': tidal_deformability, 'k2': love_number,
             'compactness': C}
        """
        # Start from small r > 0 to avoid H=0 trap
        r_start = 1e-5
        r_vals = np.arange(r_start, self.r_max + self.dr, self.dr)
        
        # Initial conditions at r_start
        y0 = [0.0, central_p, 2.0 * r_start**2]
        
        # Integrate with error handling
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                sol = odeint(self._tov_tidal_equations, y0, r_vals,
                           args=(), rtol=self.rtol, atol=self.atol)
                if w:
                    for warning in w:
                        print(f"  Tidal Warning (p_c={central_p:.3e}): {warning.message}")
            except Exception as e:
                print(f"  ERROR: Tidal integration failed for p_c={central_p:.3e}: {e}")
                return None
        
        M_sol = sol[:, 0]
        p_sol = sol[:, 1]
        H_sol = sol[:, 2]
        
        # Find surface
        idx_surface = np.where(p_sol <= 0.0)[0]
        if len(idx_surface) > 0:
            i_surf = idx_surface[0]
        else:
            i_surf = len(r_vals) - 1
        
        R = r_vals[i_surf]
        M_code = M_sol[i_surf]
        M_solar = M_code / TOVSolver.MSUN_CODE
        H_R = H_sol[i_surf]
        
        # Compute compactness
        C = M_code / R
        
        # Avoid unphysical cases
        if R < 1e-5 or M_code < 1e-10 or C >= 0.5:
            return {
                'R': R, 'M_code': M_code, 'M_solar': M_solar,
                'Lambda': 0.0, 'k2': 0.0, 'compactness': C
            }
        
        # Compute Love number k2
        y_R = H_R / R
        
        C2 = C * C
        C3 = C2 * C
        C4 = C3 * C
        C5 = C4 * C
        
        # k2 formula from Hinderer et al.
        num = (8.0 / 5.0) * C5 * (1.0 - 2.0 * C)**2
        num *= (2.0 + 2.0 * C * (y_R - 1.0) - y_R)
        
        denom = (2.0 * C * (6.0 - 3.0 * y_R + 3.0 * C * (5.0 * y_R - 8.0)) +
                 4.0 * C3 * (13.0 - 11.0 * y_R + C * (3.0 * y_R - 2.0) + 
                            2.0 * C2 * (1.0 + y_R)) +
                 3.0 * (1.0 - 2.0 * C)**2 * (2.0 - y_R + 2.0 * C * (y_R - 1.0)) * 
                 np.log(1.0 - 2.0 * C))
        
        if abs(denom) < 1e-30:
            k2 = 0.0
        else:
            k2 = num / denom
        
        # Dimensionless tidal deformability
        if C > 0:
            Lambda = (2.0 / 3.0) * k2 / C5
        else:
            Lambda = 0.0
        
        return {
            'R': R,
            'M_code': M_code,
            'M_solar': M_solar,
            'Lambda': Lambda,
            'k2': k2,
            'compactness': C,
            'y_R': y_R
        }
    
    def compute_sequence(self, num_stars=100, p_min=None, p_max=None):
        """
        Compute tidal deformability for a sequence of stars.
        
        Parameters:
        -----------
        num_stars : int
            Number of stars to compute
        p_min, p_max : float
            Pressure range (uses EOS range if None)
            
        Returns:
        --------
        list of dict
            List of tidal results
        """
        if p_min is None or p_max is None:
            p_range = self.eos.get_pressure_range()
            p_min = p_min or max(p_range[0], 1e-15)
            p_max = p_max or p_range[1]
        
        p_c_values = np.logspace(np.log10(p_min), np.log10(p_max), num_stars)
        
        results = []
        for p_c in p_c_values:
            result = self.compute(p_c)
            if result is not None:
                result['p_c'] = p_c
                results.append(result)
        
        return results

