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
    
    def _tov_tidal_equations(self, y, r, segment=None):
        """
        Combined TOV + tidal perturbation equations.
        Second-order formulation: integrates H and beta = dH/dr.
        
        Parameters:
        -----------
        y : array
            [M, p, H, beta]
        r : float
            Radial coordinate
        segment : int or None
            Index of the single-phase EOS segment currently being integrated.
            Only meaningful for a hybrid EOS; None is correct for a single-phase
            table.  Note that this function is only ever the *smooth* part of
            the problem: the delta-function piece of de/dp at a first-order
            transition is applied separately, by _apply_transition_jump().
            
        Returns:
        --------
        array
            [dM/dr, dp/dr, dH/dr, d(beta)/dr]
        """
        M, p, H, beta = y
        
        if p <= 0.0:
            return [0.0, 0.0, 0.0, 0.0]
        
        e = self.eos.get_energy_density(p, segment=segment)
        
        # TOV equations (match form in tov_solver.py)
        dMdr = 4.0 * np.pi * r * r * e
        
        if r < 1e-10:
            dpdr = 0.0
        else:
            tmp = 1.0 - 2.0 * M / r
            dpdr = -((e + p) * (M / (r * r) + 4.0 * np.pi * r * p)) / tmp
        
        # Tidal: dH/dr = beta
        dHdr = beta
        
        # Tidal: d(beta)/dr - exact match to their code
        # f = de/dp = 1/cs2 (use precomputed fdedp, matches their getF())
        f = self.eos.get_fdedp(p, segment=segment)
        f = max(1.0, f)  # Only lower bound, NO upper clip!
        
        F1 = 1.0 - 2.0 * M / r
        
        # Their exact d(beta)/dr formula:
        term1 = (2.0 / F1) * H * (
            -2.0 * np.pi * (5.0 * e + 9.0 * p + f * (e + p)) +
            3.0 / (r * r) +
            (2.0 / F1) * (M / (r * r) + 4.0 * np.pi * r * p)**2
        )
        
        term2 = (2.0 * beta / r / F1) * (
            -1.0 + M / r + 2.0 * np.pi * r * r * (e - p)
        )
        
        dbetadr = term1 + term2
        
        return [dMdr, dpdr, dHdr, dbetadr]
    
    @staticmethod
    def _apply_transition_jump(state, r_d, delta_e):
        """
        Apply the matching condition for y = r H'/H across a first-order phase
        transition, integrating outward.
        
            y(r_d^+) = y(r_d^-) - 4 pi r_d^3 Delta_eps / (m(r_d) + 4 pi r_d^3 p(r_d))
        
        (Damour & Nagar 2009; Postnikov, Prakash & Lattimer 2010;
        Takatsy & Kovacs 2020.)
        
        This term cannot be carried by the ODE right-hand side.  In a Maxwell
        construction eps jumps at *constant* P, so de/dp is a delta function:
        its integral across the transition is finite and non-zero, but the jump
        has no width for the stepper to resolve.  H is continuous across the
        transition and beta = dH/dr is not, so the shift is applied to beta.
        
        Parameters:
        -----------
        state : array
            [M, p, H, beta] at r_d, on the high-pressure side
        r_d : float
            Radius at which p(r_d) = P_tr
        delta_e : float
            eps(high-pressure branch) - eps(low-pressure branch) > 0
            
        Returns:
        --------
        array
            [M, p, H, beta] at r_d on the low-pressure side
        """
        M_d, p_d, H_d, beta_d = state
        denom = M_d + 4.0 * np.pi * r_d**3 * p_d
        if abs(H_d) < 1e-300 or abs(denom) < 1e-300:
            return np.array([M_d, p_d, H_d, beta_d])

        y_minus = r_d * beta_d / H_d
        y_plus = y_minus - 4.0 * np.pi * r_d**3 * delta_e / denom
        beta_plus = y_plus * H_d / r_d
        return np.array([M_d, p_d, H_d, beta_plus])

    def _integrate_with_jumps(self, r_vals, y0, central_p):
        """
        Integrate the coupled TOV + tidal system across a hybrid EOS, applying
        the y-matching condition at every first-order transition the star
        crosses.
        
        Pressure falls monotonically outward, so the integration walks down one
        EOS segment at a time.  At each crossing we locate r_d (where
        p(r_d) = P_tr), step exactly onto it, shift beta, and resume on the
        next branch down.
        """
        n = len(r_vals)
        out = np.empty((n, 4))
        state = np.asarray(y0, dtype=float)
        seg = self.eos.segment_for_pressure(central_p)
        i = 0
        r_anchor = float(r_vals[0])

        while i < n:
            grid = r_vals[i:]
            prepend = r_anchor < grid[0]
            t = np.concatenate(([r_anchor], grid)) if prepend else grid
            sub = odeint(self._tov_tidal_equations, state, t, args=(seg,),
                         rtol=1e-8, atol=1e-10)
            if prepend:
                sub = sub[1:]

            if seg == 0:
                out[i:] = sub
                break

            transition = self.eos.transitions[seg - 1]
            p_tr = transition["p_tr"]
            below = np.where(sub[:, 1] < p_tr)[0]
            if len(below) == 0:
                # Transition never reached (star surfaces first)
                out[i:] = sub
                break

            j = int(below[0])
            out[i:i + j] = sub[:j]

            # Bracket the crossing.  j == 0 would mean we are already below P_tr
            # at the anchor, in which case there is nothing left to match.
            if j == 0:
                seg -= 1
                continue

            r_lo = float(grid[j - 1])
            r_hi = float(grid[j])
            p_lo = float(sub[j - 1, 1])
            p_hi = float(sub[j, 1])

            # Linear interpolation for r_d, kept strictly inside the bracket so
            # the resumed integration always has a positive first step.
            if p_lo != p_hi:
                r_d = r_lo + (p_lo - p_tr) * (r_hi - r_lo) / (p_lo - p_hi)
            else:
                r_d = 0.5 * (r_lo + r_hi)
            eps_r = 1e-12 * max(1.0, abs(r_hi))
            r_d = min(max(r_d, r_lo + eps_r), r_hi - eps_r)

            # Step precisely onto r_d, still on the high-pressure branch
            state_d = odeint(self._tov_tidal_equations, sub[j - 1], [r_lo, r_d],
                             args=(seg,), rtol=1e-8, atol=1e-10)[-1]

            state = self._apply_transition_jump(state_d, r_d, transition["delta_e"])
            r_anchor = r_d
            i += j
            seg -= 1

        return out

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
        # Use dr=0.001 for tidal (their rstep value)
        r_start = 1e-5
        dr_tidal = 0.001
        r_vals = np.arange(r_start, self.r_max + dr_tidal, dr_tidal)
        
        # Initial conditions at r_start: [M, p, H, beta]
        # H ~ r^2, beta = dH/dr ~ 2r near center
        y0 = [0.0, central_p, r_start**2, 2.0 * r_start]
        
        # Integrate with error handling
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                if self.eos.transitions:
                    sol = self._integrate_with_jumps(r_vals, y0, central_p)
                else:
                    sol = odeint(self._tov_tidal_equations, y0, r_vals,
                               args=(), rtol=1e-8, atol=1e-10)
                if w:
                    for warning in w:
                        print(f"  Tidal Warning (p_c={central_p:.3e}): {warning.message}")
            except Exception as e:
                print(f"  ERROR: Tidal integration failed for p_c={central_p:.3e}: {e}")
                return None
        
        M_sol = sol[:, 0]
        p_sol = sol[:, 1]
        H_sol = sol[:, 2]
        beta_sol = sol[:, 3]
        
        # Find surface (where p drops to minimum EOS pressure)
        # Stop at pressure[0] to avoid extrapolating outside EOS table
        p_min = self.eos.p_table[0]
        idx_surface = np.where(p_sol <= p_min)[0]
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
        # Use beta from integration (exact, not numerical derivative)
        beta_R = beta_sol[i_surf]
        
        # y = r * beta / H (matches their solver exactly)
        y_R = R * beta_R / (H_R + 1e-30)
        
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
        
        # Get all EOS column values at central pressure, on the branch the core
        # is actually on (matters only for a hybrid EOS whose central pressure
        # sits exactly on a transition plateau).
        central_values = self.eos.get_all_values_at_pressure(
            central_p, segment=self.eos.segment_for_pressure(central_p))
        
        result = {
            'R': R,
            'M_code': M_code,
            'M_solar': M_solar,
            'Lambda': Lambda,
            'k2': k2,
            'compactness': C,
            'y_R': y_R
        }
        
        # Add central values with 'central_' prefix
        for col, val in central_values.items():
            result[f'central_{col}'] = val
        
        return result
    
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

