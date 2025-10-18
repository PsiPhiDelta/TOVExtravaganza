import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt

# We import from "tov" for backward compatibility
from .tov import read_eos_csv_multi, EOSMulti, solve_tov_rad, DR, RMAX

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
    
    def __init__(self, eos, output_folder="export/radial_profiles"):
        """
        Initialize the radial profiler.
        
        Parameters:
        -----------
        eos : EOSMulti
            Your beautiful EOS object
        output_folder : str
            Base output folder (will create json/ and plots/ subfolders)
        """
        self.eos = eos
        self.output_folder = output_folder
        self.json_folder = os.path.join(output_folder, "json")
        self.plot_folder = os.path.join(output_folder, "plots")
        
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
        r_arr, M_arr, p_arr, R, M = solve_tov_rad(p_c, self.eos, RMAX, DR)
        
        # Interpolate all other EOS columns at each p(r)
        all_cols_data = {}
        for col in self.eos.colnames:
            if col == "p":
                all_cols_data["p"] = p_arr
            else:
                all_cols_data[col] = np.array([self.eos.interp(col, p_val) for p_val in p_arr])
        
        return r_arr, M_arr, all_cols_data
    
    def compute_full_mr_curve(self, num_points=100):
        """
        Compute full M-R curve for visualization.
        oh boy oh boy, more stars!
        Filters out unphysical stars (R >= 99 km or M < 0.05 Msun).
        """
        p_table = self.eos.data_dict["p"]
        p_min = p_table[0]
        p_max = p_table[-1]
        
        central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), num_points)
        
        R_list = []
        M_list = []
        
        for p_c in central_pressures:
            r_arr, M_arr, _ = self.compute_profile(p_c)
            
            # Apply same filter: R < 99 km and M > 0.05 Msun
            R_final = r_arr[-1] if len(r_arr) > 0 else 0
            M_final = M_arr[-1] / MSUN_TO_KM if len(M_arr) > 0 else 0
            
            if len(r_arr) > 0 and M_arr[-1] > 0 and R_final < 99.0 and M_final > 0.05:
                R_list.append(R_final)
                M_list.append(M_final)
        
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
        p_table = self.eos.data_dict["p"]
        p_min = p_table[0]
        p_max = p_table[-1]
        
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
            print(f"WARNING: Target M={target_mass_Msun:.3f} M☉ exceeds M_max={M_max:.3f} M☉")
            target_mass_Msun = M_max * 0.99  # Use close to M_max instead
        
        # Step 2: Fine search in stable branch only
        p_min_stable = p_stable[0]
        p_max_stable = p_stable[-1]
        
        fine_pressures = np.logspace(np.log10(p_min_stable), np.log10(p_max_stable), 50)
        
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
        
        if best_profile:
            R_final = best_profile['r'][-1]
            M_final = best_profile['M'][-1] / MSUN_TO_KM
            print(f"Found star closest to M={target_mass_Msun:.3f} M☉: M={M_final:.4f} M☉, R={R_final:.2f} km (M_max={M_max:.3f} M☉)")
        
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
        p_table = self.eos.data_dict["p"]
        p_min = p_table[0]
        p_max = p_table[-1]
        
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
        
        fine_pressures = np.logspace(np.log10(p_min_stable), np.log10(p_max_stable), 50)
        
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
        
        if best_profile:
            R_final = best_profile['r'][-1]
            M_final = best_profile['M'][-1] / MSUN_TO_KM
            print(f"Found star closest to R={target_radius_km:.2f} km: R={R_final:.2f} km, M={M_final:.4f} M☉ (M_max={M_max:.3f} M☉)")
        
        return best_profile
    
    def generate_profiles(self, num_stars=10, p_min=None, p_max=None):
        """
        Generate radial profiles for multiple stars.
        oh boy oh boy, let's do a bunch of them!
        Filters out unphysical stars (R >= 99 km or M < 0.05 Msun).
        """
        # Default pressure range
        if p_min is None or p_max is None:
            p_table = self.eos.data_dict["p"]
            p_min = p_min or p_table[0]
            p_max = p_max or p_table[-1]
        
        central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), num_stars)
        
        profiles = []
        skipped = 0
        for i, p_c in enumerate(central_pressures):
            r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
            
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
                print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => R={R_final:.2f} km, M={M_final:.4f} M☉")
            else:
                skipped += 1
                print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => SKIPPED (R={R_final:.2f} km, M={M_final:.4f} M☉)")
        
        if skipped > 0:
            print(f"\nFiltered: kept {len(profiles)}/{num_stars} physical solutions (R < 99 km, M > 0.05 M☉)")
        
        return profiles
    
    def save_profiles(self, profiles, basename):
        """
        Save profiles to text and JSON files.
        oh boy oh boy, let's write them out!
        """
        text_meta_path = os.path.join(self.json_folder, "metadata.txt")
        json_path = os.path.join(self.json_folder, f"{basename}.json")
        
        # Write text metadata
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
        
        # Write JSON
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
                star_dict['columns'][col] = arr.tolist()
            json_data.append(star_dict)
        
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\nRadial data saved to:")
        print(f"  {text_meta_path}")
        print(f"  {json_path}")
    
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
            M_all = np.array([prof['M'][-1] / MSUN_TO_KM for prof in profiles])  # Convert to M☉
        
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
            ax1.set_ylabel("M(r) [M☉]", fontsize=12)
            ax1.set_title(f"Mass profile: p_c={p_c_MeV:.3e} MeV/fm³", fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Right: M-R diagram with this star marked
            ax2.plot(R_all, M_all, 'k-', linewidth=1.5, alpha=0.5, label='M-R curve')
            ax2.plot(R_final, M_final, 'r*', markersize=20, label=f'This star: R={R_final:.2f} km, M={M_final:.3f} M☉')
            ax2.set_xlabel("R [km]", fontsize=12)
            ax2.set_ylabel("M [M☉]", fontsize=12)
            ax2.set_title("Mass-Radius Relation", fontsize=12)
            ax2.grid(True, alpha=0.3)
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
            ax2.plot(R_all, M_all, 'k-', linewidth=1.5, alpha=0.5, label='M-R curve')
            ax2.plot(R_final, M_final, 'r*', markersize=20, label=f'This star: R={R_final:.2f} km, M={M_final:.3f} M☉')
            ax2.set_xlabel("R [km]", fontsize=12)
            ax2.set_ylabel("M [M☉]", fontsize=12)
            ax2.set_title("Mass-Radius Relation", fontsize=12)
            ax2.grid(True, alpha=0.3)
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
  python radial.py inputCode/hsdd2.csv -M 1.4          # Star closest to 1.4 M☉
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
                          help='Generate profile for star closest to this mass [M☉]. Can be used multiple times.')
        parser.add_argument('-R', '--radius', type=float, action='append',
                          help='Generate profile for star closest to this radius [km]. Can be used multiple times.')
        parser.add_argument('--save-png', action='store_true',
                          help='Also save PNG versions of plots (for README/web, default: PDF only)')
        
        args = parser.parse_args()
        
        if args.input is None:
            parser.print_help()
            sys.exit(0)
    
    # Step 1: read all columns from the EOS file
    data_dict, colnames = read_eos_csv_multi(args.input)
    eos = EOSMulti(data_dict, colnames)
    
    # Greet the user with comedic style!
    npts = len(data_dict["p"])
    print(f"We read {npts} data points (and {len(colnames)} columns) from '{args.input}'. All in code units. Good job!")
    
    # Step 2: create our radial profiler object, oh boy oh boy!
    profiler = RadialProfiler(eos, output_folder=args.output)
    
    # Step 3: generate radial profiles
    profiles = []
    
    # Check if user specified specific mass or radius values
    if args.mass or args.radius:
        print("\nFinding stars with specific M or R values...\n")
        
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
