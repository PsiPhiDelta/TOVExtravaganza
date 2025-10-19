import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from pathlib import Path
import time
try:
    import h5py
    HAS_HDF5 = True
except ImportError:
    HAS_HDF5 = False

# Import the new EOS class and TOV solver
from ..core.eos import EOS
from ..core.tov_solver import TOVSolver
from .tov import DR, RMAX
from ..utils.timeout import timeout, TimeoutError

###############################################################################
# UNIT SYSTEM EXPLANATION
###############################################################################
# The TOV solver uses geometric units (G = c = 1):
#   - Radius r: kilometers [km]
#   - Mass M(r): kilometers [km] (1 solar mass = 1.4766 km)
#   - Pressure p: dimensionless code units
#   - Energy density e: dimensionless code units
#   - Central pressure p_c: dimensionless code units
#
# To convert M from km to solar masses: M_Msun = M_km / 1.4766
# To convert p from code units to MeV/fm³: p_MeV = p_code / 1.32379e-06

###############################################################################
# CONVERSION FACTORS
###############################################################################
MSUN_TO_KM = 1.4766  # 1 solar mass in km
CODE_TO_MEVFM3 = 1.0 / 1.32379e-06  # code units to MeV/fm³

###############################################################################
# DEFAULT SETTINGS
###############################################################################
DEFAULT_NUM_STARS = 10
DEFAULT_OUTPUT = "export/radial_profiles"


class RadialProfiler:
    """
    Hello, friend! Howdy?
    
    This class does radial profiling in an object-oriented way
    while keeping all your favorite comedic comments!
    """
    
    def __init__(self, eos, output_folder="export/radial_profiles", rmax_plot=20.0, timeout_value=10.0):
        """
        Initialize the radial profiler.
        
        Parameters:
        -----------
        eos : EOS
            Your beautiful EOS object
        output_folder : str
            Base output folder (will create json/ and plots/ subfolders)
        rmax_plot : float
            Maximum radius for M-R plot axis (default: 20.0 km)
        timeout_value : float
            Timeout for each star calculation in seconds (default: 10.0, 0 = no timeout)
        """
        self.eos = eos
        self.output_folder = output_folder
        self.json_folder = os.path.join(output_folder, "json")
        self.plot_folder = os.path.join(output_folder, "plots")
        self.rmax_plot = rmax_plot
        self.timeout_value = timeout_value
        
        # Create folders
        if not os.path.exists(self.json_folder):
            os.makedirs(self.json_folder)
        if not os.path.exists(os.path.join(self.plot_folder, "Mass")):
            os.makedirs(os.path.join(self.plot_folder, "Mass"))
        if not os.path.exists(os.path.join(self.plot_folder, "Pressure")):
            os.makedirs(os.path.join(self.plot_folder, "Pressure"))
    
    def compute_profile(self, p_c):
        """
        Solve TOV for a given central pressure and return radial profile.
        oh boy oh boy, this is where the magic happens!
        """
        # Solve TOV using the new EOS class
        solver = TOVSolver(self.eos, r_max=RMAX, dr=DR)
        star, r_arr, M_arr, p_arr = solver.solve(p_c, return_profile=True)
        
        # Interpolate all EOS columns (numeric and string) at each p(r)
        all_cols_data = {}
        for i, p_val in enumerate(p_arr):
            # Get all column values at this pressure
            col_values = self.eos.get_all_values_at_pressure(p_val)
            for col_name, col_val in col_values.items():
                if col_name not in all_cols_data:
                    all_cols_data[col_name] = []
                all_cols_data[col_name].append(col_val)
        
        # Convert lists to arrays (numeric) or keep as lists (strings)
        for col_name in all_cols_data:
            try:
                all_cols_data[col_name] = np.array(all_cols_data[col_name], dtype=float)
            except (ValueError, TypeError):
                # Keep as list for string columns
                pass
        
        # Always include p array
        all_cols_data["p"] = p_arr
        
        return r_arr, M_arr, all_cols_data
    
    def compute_full_mr_curve(self, num_points=100):
        """
        Compute full M-R curve for visualization (fast, no full profiles).
        oh boy oh boy, more stars!
        Filters out unphysical stars (R >= 99 km or M < 0.05 Msun).
        """
        # Use fast TOV solver (no full profiles, just M and R)
        solver = TOVSolver(self.eos, r_max=RMAX, dr=DR)
        
        p_range = self.eos.get_pressure_range()
        p_min = max(p_range[0], 1e-15)
        p_max = p_range[1]
        
        central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), num_points)
        
        R_list = []
        M_list = []
        
        for p_c in central_pressures:
            try:
                star = solver.solve(p_c)
                R_final = star.radius
                M_final = star.mass_solar
                
                # Apply same filter: R < 99 km and M > 0.05 Msun
                if R_final < 99.0 and M_final > 0.05:
                    R_list.append(R_final)
                    M_list.append(M_final)
            except:
                pass
        
        return np.array(R_list), np.array(M_list)
    
    def find_star_by_mass(self, target_mass_Msun):
        """
        Find the central pressure that gives a star closest to target mass.
        oh boy oh boy, let's find it!
        
        Parameters:
        -----------
        target_mass_Msun : float
            Target mass in solar masses
            
        Returns:
        --------
        dict : Profile for the closest star
        """
        p_range = self.eos.get_pressure_range()
        p_min = max(p_range[0], 1e-15)
        p_max = p_range[1]
        
        # Step 1: Quick coarse search to find stable branch (up to M_max)
        # Use fewer samples for initial scan
        coarse_pressures = np.logspace(np.log10(p_min), np.log10(p_max), 30)
        M_values = []
        p_stable = []
        
        M_max = 0
        for p_c in coarse_pressures:
            r_arr, M_arr, _ = self.compute_profile(p_c)
            R_final = r_arr[-1] if len(r_arr) > 0 else 0
            M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
            
            # Only consider physical stars in stable branch
            if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                M_values.append(M_final)
                p_stable.append(p_c)
                if M_final > M_max:
                    M_max = M_final
                elif M_final < 0.95 * M_max:  # Entered unstable branch
                    break
        
        if len(M_values) == 0:
            print(f"WARNING: No stable stars found!")
            return None
        
        # Check if target is beyond M_max
        if target_mass_Msun > M_max:
            print(f"ERROR: Target M={target_mass_Msun:.3f} Msun exceeds M_max={M_max:.3f} Msun")
            print(f"       Stable stars only exist up to M_max. Please choose M < {M_max:.3f} Msun")
            return None
        
        # Step 2: Fine search in stable branch only
        p_min_stable = p_stable[0]
        p_max_stable = p_stable[-1]
        
        fine_pressures = np.logspace(np.log10(p_min_stable), np.log10(p_max_stable), 100)
        
        best_p_c = None
        best_diff = float('inf')
        best_profile = None
        
        for p_c in fine_pressures:
            r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
            
            R_final = r_arr[-1] if len(r_arr) > 0 else 0
            M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
            
            # Only consider physical stars
            if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                diff = abs(M_final - target_mass_Msun)
                if diff < best_diff:
                    best_diff = diff
                    best_p_c = p_c
                    best_profile = {
                        'p_c': p_c,
                        'r': r_arr,
                        'M': M_arr,
                        'data': all_cols_data
                    }
        
        # Step 3: Adaptive refinement to guarantee accuracy < 0.01 Msun
        if best_profile and best_diff > 0.01:
            print(f"  Refining search (initial error: {best_diff:.4f} Msun)...")
            # Narrow search around best_p_c
            p_low = best_p_c * 0.9
            p_high = best_p_c * 1.1
            refine_pressures = np.logspace(np.log10(p_low), np.log10(p_high), 100)
            
            for p_c in refine_pressures:
                r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
                R_final = r_arr[-1] if len(r_arr) > 0 else 0
                M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
                
                if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                    diff = abs(M_final - target_mass_Msun)
                    if diff < best_diff:
                        best_diff = diff
                        best_p_c = p_c
                        best_profile = {
                            'p_c': p_c,
                            'r': r_arr,
                            'M': M_arr,
                            'data': all_cols_data
                        }
        
        if best_profile:
            R_final = best_profile['r'][-1]
            M_final = best_profile['M'][-1] / MSUN_TO_KM
            error = abs(M_final - target_mass_Msun)
            if error > 0.01:
                print(f"WARNING: Could not find star within 0.01 Msun (error: {error:.4f} Msun)")
            print(f"Found star closest to M={target_mass_Msun:.3f} Msun: M={M_final:.4f} Msun, R={R_final:.2f} km (error: {error:.4f} Msun, M_max={M_max:.3f} Msun)")
        
        return best_profile
    
    def find_maximum_mass_star(self, precision=0.001):
        """
        Find the star with maximum mass (M_max) with specified precision.
        oh boy oh boy, let's find the max mass star!
        
        Uses a fast search (only computing M and R, not full profiles) followed by
        a single full profile computation at the M_max configuration.
        
        Parameters:
        -----------
        precision : float
            Target precision in solar masses (default: 0.001 Msun)
            
        Returns:
        --------
        dict : Profile for the maximum mass star
        """
        print(f"\nSearching for maximum mass star (precision: {precision:.4f} Msun)...")
        
        # Use fast TOV solver (no full profile) for the search
        solver = TOVSolver(self.eos, r_max=RMAX, dr=DR)
        
        # Step 1: Coarse search to find approximate M_max
        p_range = self.eos.get_pressure_range()
        p_min = max(p_range[0], 1e-15)
        p_max = p_range[1]
        
        coarse_pressures = np.logspace(np.log10(p_min), np.log10(p_max), 50)
        M_values = []
        p_stable = []
        
        for p_c in coarse_pressures:
            try:
                star = solver.solve(p_c)
                R_final = star.radius
                M_final = star.mass_solar
                
                if R_final < 99.0 and M_final > 0.05:
                    M_values.append(M_final)
                    p_stable.append(p_c)
            except:
                pass
        
        if not M_values:
            print("ERROR: No valid stars found!")
            return None
        
        # Find approximate maximum
        M_max_idx = np.argmax(M_values)
        M_max_approx = M_values[M_max_idx]
        p_max_approx = p_stable[M_max_idx]
        
        print(f"  Coarse search (50 points): M_max ~{M_max_approx:.4f} Msun at p_c={p_max_approx:.3e}")
        
        # Step 2: Fine search around maximum (fast, no full profiles)
        p_low = p_stable[max(0, M_max_idx - 3)]
        p_high = p_stable[min(len(p_stable) - 1, M_max_idx + 3)]
        
        fine_pressures = np.logspace(np.log10(p_low), np.log10(p_high), 200)
        
        max_M = 0
        best_p_c = None
        
        for p_c in fine_pressures:
            try:
                star = solver.solve(p_c)
                R_final = star.radius
                M_final = star.mass_solar
                
                if R_final < 99.0 and M_final > 0.05:
                    if M_final > max_M:
                        max_M = M_final
                        best_p_c = p_c
            except:
                pass
        
        print(f"  Fine search (200 points): M_max = {max_M:.4f} Msun at p_c={best_p_c:.3e}")
        
        # Step 3: Compute FULL radial profile only for the M_max configuration
        if best_p_c:
            print(f"  Computing full radial profile at M_max...")
            r_arr, M_arr, all_cols_data = self.compute_profile(best_p_c)
            R_final = r_arr[-1]
            M_final = M_arr[-1] / MSUN_TO_KM
            
            best_profile = {
                'p_c': best_p_c,
                'r': r_arr,
                'M': M_arr,
                'data': all_cols_data
            }
            
            print(f"✓ Found M_max = {M_final:.4f} Msun, R = {R_final:.2f} km")
        
        return best_profile
    
    def find_star_by_radius(self, target_radius_km):
        """
        Find the central pressure that gives a star closest to target radius.
        oh boy oh boy, let's find it!
        
        Parameters:
        -----------
        target_radius_km : float
            Target radius in km
            
        Returns:
        --------
        dict : Profile for the closest star
        """
        p_range = self.eos.get_pressure_range()
        p_min = max(p_range[0], 1e-15)
        p_max = p_range[1]
        
        # Step 1: Quick coarse search to find stable branch (up to M_max)
        coarse_pressures = np.logspace(np.log10(p_min), np.log10(p_max), 30)
        M_values = []
        p_stable = []
        
        M_max = 0
        for p_c in coarse_pressures:
            r_arr, M_arr, _ = self.compute_profile(p_c)
            R_final = r_arr[-1] if len(r_arr) > 0 else 0
            M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
            
            # Only consider physical stars in stable branch
            if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                M_values.append(M_final)
                p_stable.append(p_c)
                if M_final > M_max:
                    M_max = M_final
                elif M_final < 0.95 * M_max:  # Entered unstable branch
                    break
        
        if len(M_values) == 0:
            print(f"WARNING: No stable stars found!")
            return None
        
        # Step 2: Fine search in stable branch only
        p_min_stable = p_stable[0]
        p_max_stable = p_stable[-1]
        
        fine_pressures = np.logspace(np.log10(p_min_stable), np.log10(p_max_stable), 100)
        
        best_p_c = None
        best_diff = float('inf')
        best_profile = None
        
        for p_c in fine_pressures:
            r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
            
            R_final = r_arr[-1] if len(r_arr) > 0 else 0
            M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
            
            # Only consider physical stars
            if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                diff = abs(R_final - target_radius_km)
                if diff < best_diff:
                    best_diff = diff
                    best_p_c = p_c
                    best_profile = {
                        'p_c': p_c,
                        'r': r_arr,
                        'M': M_arr,
                        'data': all_cols_data
                    }
        
        # Step 3: Adaptive refinement to guarantee accuracy < 0.01 km
        if best_profile and best_diff > 0.01:
            print(f"  Refining search (initial error: {best_diff:.4f} km)...")
            # Narrow search around best_p_c
            p_low = best_p_c * 0.9
            p_high = best_p_c * 1.1
            refine_pressures = np.logspace(np.log10(p_low), np.log10(p_high), 100)
            
            for p_c in refine_pressures:
                r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
                R_final = r_arr[-1] if len(r_arr) > 0 else 0
                M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
                
                if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                    diff = abs(R_final - target_radius_km)
                    if diff < best_diff:
                        best_diff = diff
                        best_p_c = p_c
                        best_profile = {
                            'p_c': p_c,
                            'r': r_arr,
                            'M': M_arr,
                            'data': all_cols_data
                        }
        
        if best_profile:
            R_final = best_profile['r'][-1]
            M_final = best_profile['M'][-1] / MSUN_TO_KM
            error = abs(R_final - target_radius_km)
            if error > 0.01:
                print(f"WARNING: Could not find star within 0.01 km (error: {error:.4f} km)")
            print(f"Found star closest to R={target_radius_km:.2f} km: R={R_final:.2f} km, M={M_final:.4f} Msun (error: {error:.4f} km, M_max={M_max:.3f} Msun)")
        
        return best_profile
    
    def generate_profiles(self, num_stars=10, p_min=None, p_max=None):
        """
        Generate radial profiles for multiple stars.
        oh boy oh boy, let's do a bunch of them!
        Filters out unphysical stars (R >= 99 km or M < 0.05 Msun).
        """
        # Default pressure range
        if p_min is None or p_max is None:
            p_range = self.eos.get_pressure_range()
            p_min = p_min or max(p_range[0], 1e-15)
            p_max = p_max or p_range[1]
        
        central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), num_stars)
        
        # Create timeout-wrapped compute function if timeout is enabled
        if self.timeout_value and self.timeout_value > 0:
            @timeout(self.timeout_value)
            def compute_with_timeout(p_c):
                return self.compute_profile(p_c)
        else:
            def compute_with_timeout(p_c):
                return self.compute_profile(p_c)
        
        profiles = []
        skipped = 0
        for i, p_c in enumerate(central_pressures):
            try:
                r_arr, M_arr, all_cols_data = compute_with_timeout(p_c)
                
                # Apply same filter as tov.py: R < 99 km and M > 0.05 Msun
                R_final = r_arr[-1] if len(r_arr) > 0 else 0
                M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
                
                if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                    profiles.append({
                        'p_c': p_c,
                        'r': r_arr,
                        'M': M_arr,
                        'data': all_cols_data
                    })
                    print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => R={R_final:.2f} km, M={M_final:.4f} Msun")
                else:
                    skipped += 1
                    print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => SKIPPED (R={R_final:.2f} km, M={M_final:.4f} Msun)")
            except TimeoutError:
                skipped += 1
                print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => TIMEOUT after {self.timeout_value}s")
        
        if skipped > 0:
            print(f"\nFiltered: kept {len(profiles)}/{num_stars} physical solutions (R < 99 km, M > 0.05 Msun)")
        
        return profiles
    
    def save_profiles(self, profiles, basename):
        """
        Save profiles to text metadata and HDF5/JSON files.
        oh boy oh boy, let's write them out efficiently!
        """
        text_meta_path = os.path.join(self.json_folder, "metadata.txt")
        
        # Write text metadata (human-readable summary)
        with open(text_meta_path, "w") as f:
            f.write("# Radial profiles for TOV stars in dimensionless code units\n")
            f.write(f"# Number of stars: {len(profiles)}\n")
            f.write(f"# Columns: p, e, and all other EOS columns\n\n")
            
            for i, prof in enumerate(profiles):
                f.write(f"\n=== Star {i} ===\n")
                f.write(f"p_c = {prof['p_c']:.6e}\n")
                f.write(f"R = {prof['r'][-1]:.4f} (code units)\n")
                f.write(f"M = {prof['M'][-1]:.4f} (code units)\n")
                f.write(f"Number of radial points: {len(prof['r'])}\n")
        
        # Save data in HDF5 format (efficient binary format)
        if HAS_HDF5:
            hdf5_path = os.path.join(self.json_folder, f"{basename}.h5")
            with h5py.File(hdf5_path, 'w') as hf:
                for i, prof in enumerate(profiles):
                    # Create a group for each star
                    grp = hf.create_group(f'profile_{i}')
                    
                    # Store scalar metadata
                    grp.attrs['p_c'] = prof['p_c']
                    grp.attrs['R'] = prof['r'][-1]
                    grp.attrs['M'] = prof['M'][-1]
                    grp.attrs['radial_points'] = len(prof['r'])
                    
                    # Store radial arrays
                    grp.create_dataset('r', data=prof['r'], compression='gzip')
                    grp.create_dataset('M_r', data=prof['M'], compression='gzip')
                    
                    # Store all EOS columns
                    col_grp = grp.create_group('columns')
                    for col, arr in prof['data'].items():
                        if isinstance(arr, np.ndarray):
                            col_grp.create_dataset(col, data=arr, compression='gzip')
                        elif isinstance(arr, list):
                            # String columns - store as variable-length strings
                            str_dtype = h5py.string_dtype(encoding='utf-8')
                            col_grp.create_dataset(col, data=arr, dtype=str_dtype, compression='gzip')
            
            print(f"\nRadial data saved to:")
            print(f"  {text_meta_path}")
            print(f"  {hdf5_path} (HDF5 format - efficient binary)")
        else:
            # Fallback to JSON if HDF5 not available
            json_path = os.path.join(self.json_folder, f"{basename}.json")
            json_data = []
            for prof in profiles:
                star_dict = {
                    'p_c': float(prof['p_c']),
                    'R': float(prof['r'][-1]),
                    'M': float(prof['M'][-1]),
                    'radial_points': len(prof['r']),
                    'r': prof['r'].tolist(),
                    'M_r': prof['M'].tolist(),
                    'columns': {}
                }
                for col, arr in prof['data'].items():
                    if hasattr(arr, 'tolist'):
                        star_dict['columns'][col] = arr.tolist()
                    else:
                        star_dict['columns'][col] = arr
                json_data.append(star_dict)
            
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=2)
            
            print(f"\nRadial data saved to:")
            print(f"  {text_meta_path}")
            print(f"  {json_path} (JSON format - install h5py for efficient HDF5)")
    
    def plot_profiles(self, profiles, mr_curve=None, save_png=False):
        """
        Generate plots for M(r) and p(r) with M-R diagram on the right.
        oh boy oh boy, let's make some beautiful plots!
        
        Parameters:
        -----------
        profiles : list
            List of profile dictionaries
        mr_curve : tuple or None
            If provided, (R_array, M_array) for the full M-R curve
            If None, will use only the profiled stars
        save_png : bool
            If True, also save PNG versions (for README showcase)
        """
        mass_folder = os.path.join(self.plot_folder, "Mass")
        pressure_folder = os.path.join(self.plot_folder, "Pressure")
        
        # Use provided M-R curve or extract from profiles
        if mr_curve is not None:
            R_all, M_all = mr_curve
        else:
            R_all = np.array([prof['r'][-1] for prof in profiles])
            M_all = np.array([prof['M'][-1] / MSUN_TO_KM for prof in profiles])  # Convert to Msun
        
        # Find M_max to separate stable/unstable branches
        M_max_idx = np.argmax(M_all)
        M_max = M_all[M_max_idx]
        
        # Split into stable and unstable branches (use ALL data, not filtered by rmax_plot)
        R_stable = R_all[:M_max_idx+1]
        M_stable = M_all[:M_max_idx+1]
        R_unstable = R_all[M_max_idx:]
        M_unstable = M_all[M_max_idx:]
        
        for i, prof in enumerate(profiles):
            r_arr = prof['r']
            M_arr = prof['M']
            p_arr = prof['data']['p']
            
            # Convert M to solar masses and p to MeV/fm³
            M_Msun = M_arr / MSUN_TO_KM
            p_MeV = p_arr * CODE_TO_MEVFM3
            p_c_MeV = prof['p_c'] * CODE_TO_MEVFM3
            
            # Current star's final R and M
            R_final = r_arr[-1]
            M_final = M_Msun[-1]
            
            # Plot M(r) with M-R diagram
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Left: M(r) profile
            ax1.plot(r_arr, M_Msun, 'b-', linewidth=2)
            ax1.set_xlabel("r [km]", fontsize=12)
            ax1.set_ylabel("M(r) [Msun]", fontsize=12)
            ax1.set_title(f"Mass profile: p_c={p_c_MeV:.3e} MeV/fm³", fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Right: M-R diagram with this star marked
            # Plot stable branch (solid) and unstable branch (dashed)
            ax2.plot(R_stable, M_stable, 'k-', linewidth=1.5, alpha=0.7, label='Stable branch')
            if len(R_unstable) > 1:
                ax2.plot(R_unstable, M_unstable, 'k--', linewidth=1.5, alpha=0.5, label='Unstable branch')
            ax2.plot(R_final, M_final, 'r*', markersize=20, label=f'This star: R={R_final:.2f} km, M={M_final:.3f} Msun')
            ax2.set_xlabel("R [km]", fontsize=12)
            ax2.set_ylabel("M [Msun]", fontsize=12)
            ax2.set_title(f"Mass-Radius Relation (M_max={M_max:.3f} Msun)", fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, self.rmax_plot)
            ax2.legend(fontsize=10)
            
            plt.tight_layout()
            mass_pdf = os.path.join(mass_folder, f"mass_profile_{i}.pdf")
            plt.savefig(mass_pdf)
            if save_png:
                mass_png = os.path.join(mass_folder, f"mass_profile_{i}.png")
                plt.savefig(mass_png, dpi=150)
            plt.close()
            
            # Plot p(r) with M-R diagram
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Left: p(r) profile - LINEAR scale, in MeV/fm³
            ax1.plot(r_arr, p_MeV, 'r-', linewidth=2)
            ax1.set_xlabel("r [km]", fontsize=12)
            ax1.set_ylabel("p(r) [MeV/fm³]", fontsize=12)
            ax1.set_title(f"Pressure profile: p_c={p_c_MeV:.3e} MeV/fm³", fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Right: M-R diagram with this star marked
            # Plot stable branch (solid) and unstable branch (dashed)
            ax2.plot(R_stable, M_stable, 'k-', linewidth=1.5, alpha=0.7, label='Stable branch')
            if len(R_unstable) > 1:
                ax2.plot(R_unstable, M_unstable, 'k--', linewidth=1.5, alpha=0.5, label='Unstable branch')
            ax2.plot(R_final, M_final, 'r*', markersize=20, label=f'This star: R={R_final:.2f} km, M={M_final:.3f} Msun')
            ax2.set_xlabel("R [km]", fontsize=12)
            ax2.set_ylabel("M [Msun]", fontsize=12)
            ax2.set_title(f"Mass-Radius Relation (M_max={M_max:.3f} Msun)", fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, self.rmax_plot)
            ax2.legend(fontsize=10)
            
            plt.tight_layout()
            pressure_pdf = os.path.join(pressure_folder, f"pressure_profile_{i}.pdf")
            plt.savefig(pressure_pdf)
            if save_png:
                pressure_png = os.path.join(pressure_folder, f"pressure_profile_{i}.png")
                plt.savefig(pressure_png, dpi=150)
            plt.close()
        
        print(f"\nPlots saved to:")
        print(f"  {mass_folder}")
        print(f"  {pressure_folder}")


###############################################################################
# BATCH PROCESSING FUNCTIONS FOR PARALLEL EXECUTION
###############################################################################
def process_single_file_radial(file_args):
    """
    Process a single EOS file for radial profiles (designed for parallel execution).
    
    Parameters:
    -----------
    file_args : tuple
        (input_file, args_dict) where args_dict contains all processing parameters
        
    Returns:
    --------
    dict with status, filename, and results or error message
    """
    input_file, args_dict = file_args
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    try:
        # Read EOS
        eos = EOS.from_file(input_file)
        
        # Create output folder for this EOS
        eos_output = os.path.join(args_dict['output'], base_name)
        profiler = RadialProfiler(eos, output_folder=eos_output, rmax_plot=args_dict.get('rmax_plot', 20.0), timeout_value=args_dict.get('timeout', 10.0))
        
        # Generate profiles based on mode
        profiles = []
        
        if args_dict.get('max_mass') or args_dict.get('target_masses') or args_dict.get('target_radii'):
            # Target mode
            # Find maximum mass star
            if args_dict.get('max_mass'):
                prof = profiler.find_maximum_mass_star(precision=0.001)
                if prof:
                    profiles.append(prof)
            
            # Find stars by mass
            if args_dict.get('target_masses'):
                for target_M in args_dict['target_masses']:
                    prof = profiler.find_star_by_mass(target_M)
                    if prof:
                        profiles.append(prof)
            
            # Find stars by radius
            if args_dict.get('target_radii'):
                for target_R in args_dict['target_radii']:
                    prof = profiler.find_star_by_radius(target_R)
                    if prof:
                        profiles.append(prof)
        else:
            # Default mode: sample across pressure range
            profiles = profiler.generate_profiles(num_stars=args_dict['num_stars'])
        
        if not profiles:
            return {
                'status': 'error',
                'filename': base_name,
                'error': 'No valid profiles generated'
            }
        
        # Compute M-R curve for plots
        mr_curve = profiler.compute_full_mr_curve(num_points=200)
        
        # Save results
        try:
            profiler.save_profiles(profiles, base_name)
            profiler.plot_profiles(profiles, mr_curve=mr_curve, save_png=args_dict.get('save_png', False))
        except Exception as e:
            return {
                'status': 'error',
                'filename': base_name,
                'error': f'Failed to save output: {str(e)}'
            }
        
        return {
            'status': 'success',
            'filename': base_name,
            'num_profiles': len(profiles),
            'output_folder': eos_output
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'filename': base_name,
            'error': str(e)
        }


def process_batch_radial(args):
    """
    Process all EOS files in a directory in parallel for radial profiles.
    
    Parameters:
    -----------
    args : argparse.Namespace
        Command-line arguments
    """
    input_dir = Path(args.batch)
    
    # Find all CSV files
    csv_files = list(input_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in directory: {input_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"BATCH RADIAL PROFILES MODE - oh boy oh boy!")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV files in {input_dir}")
    print(f"Processing with {args.workers} parallel workers")
    print(f"Output directory: {args.output}")
    print(f"Profiles per file: {args.num_stars if not args.max_mass and not args.target_mass and not args.target_radius else 'target-based'}")
    print(f"{'='*70}\n")
    
    # Prepare arguments for each file
    args_dict = {
        'output': args.output,
        'num_stars': args.num_stars,
        'max_mass': args.max_mass,
        'target_masses': args.target_mass if hasattr(args, 'target_mass') else None,
        'target_radii': args.target_radius if hasattr(args, 'target_radius') else None,
        'save_png': args.save_png,
        'rmax_plot': args.rmax_plot,
        'timeout': args.timeout
    }
    
    file_args_list = [(str(f), args_dict) for f in csv_files]
    
    # Process files in parallel
    start_time = time.time()
    
    if args.workers == 1:
        # Sequential processing
        results = [process_single_file_radial(fa) for fa in file_args_list]
    else:
        # Parallel processing
        with Pool(processes=args.workers) as pool:
            results = pool.map(process_single_file_radial, file_args_list)
    
    elapsed = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"BATCH RADIAL PROFILES COMPLETE!")
    print(f"{'='*70}")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print(f"\nProcessed {len(results)} files in {elapsed:.2f} seconds")
    print(f"  ✓ Successful: {len(successful)}")
    print(f"  ✗ Failed: {len(failed)}")
    
    if successful:
        print(f"\n{'='*70}")
        print("SUCCESSFUL FILES:")
        print(f"{'='*70}")
        for r in successful:
            print(f"  {r['filename']:20s} => {r['num_profiles']:4d} profiles")
    
    if failed:
        print(f"\n{'='*70}")
        print("FAILED FILES:")
        print(f"{'='*70}")
        for r in failed:
            print(f"  {r['filename']:20s} => Error: {r['error']}")
    
    print(f"\n{'='*70}")
    print(f"All results saved to: {args.output}")
    print(f"{'='*70}\n")


def main(args=None):
    """
    This script does the following:
      1) Reads EOS file in dimensionless code units
      2) Builds an 'EOSMulti' object that can interpolate any column w.r.t. p.
      3) For a range of central pressures (p_c), we:
         - solve TOV => radial arrays {r, M(r), p(r)} in dimensionless code units
         - for each radial step, also interpolate *all other EOS columns* at p(r)
         - store everything in both:
           (a) 'export/radial_profiles/json/metadata.txt' (human-readable)
           (b) 'export/radial_profiles/json/<basename>.json' (structured)
      4) Also produce subfolders in 'export/radial_profiles/plots/Mass' and 'Pressure'
         for PDF plots of M(r) vs r and p(r) vs r.

    Since our file is ALREADY in dimensionless code units, we do not apply
    any conversions or black magic. We read them in, do TOV, store results. Done.
    """
    
    # Parse CLI arguments
    if args is None:
        import sys
        parser = argparse.ArgumentParser(
            description="""Radial Profile Generator
            
Get the INTERNAL STRUCTURE of neutron stars!
Shows M(r), p(r), e(r) from center to surface.""",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python radial.py inputCode/hsdd2.csv                 # 10 stars (default)
  python radial.py inputCode/test.csv -n 20            # 20 radial profiles
  python radial.py inputCode/hsdd2.csv -M 1.4          # Star closest to 1.4 Msun
  python radial.py inputCode/hsdd2.csv -R 12.0         # Star closest to 12 km
  python radial.py inputCode/hsdd2.csv -M 1.4 -M 2.0   # Multiple masses
  python radial.py inputCode/hsdd2.csv -M 1.4 -R 12    # By mass AND radius

Output: export/radial_profiles/json/ (JSON data)
        export/radial_profiles/plots/ (M(r) and p(r) plots with M-R context)
            """
        )
        parser.add_argument('input', nargs='?',
                          help='Input EOS file')
        parser.add_argument('-n', '--num-stars', type=int, default=DEFAULT_NUM_STARS,
                          help=f'Number of stars to profile (default: {DEFAULT_NUM_STARS})')
        parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                          help=f'Output folder (default: {DEFAULT_OUTPUT})')
        parser.add_argument('-M', '--mass', type=float, action='append',
                          help='Generate profile for star closest to this mass [Msun]. Can be used multiple times.')
        parser.add_argument('-R', '--radius', type=float, action='append',
                          help='Generate profile for star closest to this radius [km]. Can be used multiple times.')
        parser.add_argument('--max-mass', action='store_true',
                          help='Generate profile at maximum mass (M_max) with precision < 0.001 Msun')
        parser.add_argument('--save-png', action='store_true',
                          help='Also save PNG versions of plots (for README/web, default: PDF only)')
        parser.add_argument('--rmax-plot', type=float, default=20.0,
                          help='Maximum radius for M-R plot axis (default: 20 km, does not affect data)')
        parser.add_argument('--timeout', type=float, default=10.0,
                          help='Timeout for each star calculation in seconds (default: 10, 0 = no timeout)')
        
        # Batch processing options
        parser.add_argument('-b', '--batch', type=str,
                          help='Batch mode: process all CSV files in the specified directory in parallel')
        parser.add_argument('-w', '--workers', type=int, default=cpu_count(),
                          help=f'Number of parallel workers for batch mode (default: {cpu_count()} = CPU count)')
        
        args = parser.parse_args()
        
        # Check if batch mode is requested
        if args.batch:
            # Batch mode: process all files in directory
            # Rename mass/radius arguments for consistency
            args.target_mass = args.mass
            args.target_radius = args.radius
            process_batch_radial(args)
            return
        
        if args.input is None:
            parser.print_help()
            sys.exit(0)
    
    # Step 1: read all columns from the EOS file
    eos = EOS.from_file(args.input)
    
    # Greet the user with comedic style!
    npts = len(eos.p_table)
    num_cols = len(eos.colnames) + len(eos.string_dict)
    print(f"We read {npts} data points (and {num_cols} columns) from '{args.input}'. All in code units. Good job!")
    
    # Step 2: create our radial profiler object, oh boy oh boy!
    profiler = RadialProfiler(eos, output_folder=args.output, rmax_plot=args.rmax_plot, timeout_value=args.timeout)
    
    # Step 3: generate radial profiles
    profiles = []
    
    # Check if user specified specific mass or radius values
    if args.max_mass or args.mass or args.radius:
        print("\nFinding stars with specific M or R values...\n")
        
        # Find maximum mass star
        if args.max_mass:
            prof = profiler.find_maximum_mass_star(precision=0.01)
            if prof:
                profiles.append(prof)
        
        # Find stars by mass
        if args.mass:
            for target_M in args.mass:
                prof = profiler.find_star_by_mass(target_M)
                if prof:
                    profiles.append(prof)
        
        # Find stars by radius
        if args.radius:
            for target_R in args.radius:
                prof = profiler.find_star_by_radius(target_R)
                if prof:
                    profiles.append(prof)
    else:
        # Default: generate profiles across pressure range
        print(f"\nWe'll generate radial profiles for {args.num_stars} stars across the pressure range.\n")
        profiles = profiler.generate_profiles(num_stars=args.num_stars)
    
    if len(profiles) == 0:
        print("WARNING: no valid stars found. oh boy oh boy, check your EOS!")
        return
    
    # Step 4: compute full M-R curve for context plots
    print("\nComputing full M-R curve for visualization...")
    mr_curve = profiler.compute_full_mr_curve(num_points=100)
    print(f"  Computed {len(mr_curve[0])} M-R points")
    
    # Step 5: save and plot
    basename = os.path.basename(args.input).replace(".csv", "")
    profiler.save_profiles(profiles, basename)
    profiler.plot_profiles(profiles, mr_curve=mr_curve, save_png=args.save_png)
    
    if args.save_png:
        print("\n✓ Also saved PNG versions for README/web display")
    
    print("\nDone! oh boy oh boy!\n")


if __name__ == "__main__":
    main()
