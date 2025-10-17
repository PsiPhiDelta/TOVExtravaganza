import os
import json
import numpy as np
import matplotlib.pyplot as plt

# We import from "tov.py" the same FILENAME, plus read_eos_csv_multi, EOSMulti, solve_tov, DR, RMAX
# so that we all share the same dimensionless TOV code units.
from tov import FILENAME, read_eos_csv_multi, EOSMulti, solve_tov_rad, DR, RMAX


class RadialProfiler:
    """
    Hello, friend! Howdy?
    
    This class does radial profiling in an object-oriented way
    while keeping all your favorite comedic comments!
    """
    
    def __init__(self, eos, output_folder="export/radial", plot_folder="export/plots/radial"):
        """
        Initialize the radial profiler.
        
        Parameters:
        -----------
        eos : EOSMulti
            Your beautiful EOS object
        output_folder : str
            Where to store text/JSON output
        plot_folder : str
            Where to store plots
        """
        self.eos = eos
        self.output_folder = output_folder
        self.plot_folder = plot_folder
        
        # Create folders
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        if not os.path.exists(os.path.join(plot_folder, "Mass")):
            os.makedirs(os.path.join(plot_folder, "Mass"))
        if not os.path.exists(os.path.join(plot_folder, "Pressure")):
            os.makedirs(os.path.join(plot_folder, "Pressure"))
    
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
    
    def generate_profiles(self, num_stars=10, p_min=None, p_max=None):
        """
        Generate radial profiles for multiple stars.
        oh boy oh boy, let's do a bunch of them!
        """
        # Default pressure range
        if p_min is None or p_max is None:
            p_table = self.eos.data_dict["p"]
            p_min = p_min or p_table[0]
            p_max = p_max or p_table[-1]
        
        central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), num_stars)
        
        profiles = []
        for i, p_c in enumerate(central_pressures):
            r_arr, M_arr, all_cols_data = self.compute_profile(p_c)
            
            # Only keep if we got a reasonable solution
            if len(r_arr) > 0 and M_arr[-1] > 0:
                profiles.append({
                    'p_c': p_c,
                    'r': r_arr,
                    'M': M_arr,
                    'data': all_cols_data
                })
                print(f"Star {i+1}/{num_stars}: p_c={p_c:.3e} => R={r_arr[-1]:.2f}, M={M_arr[-1]:.4f}")
        
        return profiles
    
    def save_profiles(self, profiles, basename):
        """
        Save profiles to text and JSON files.
        oh boy oh boy, let's write them out!
        """
        text_meta_path = os.path.join(self.output_folder, "metadata.txt")
        json_path = os.path.join(self.output_folder, f"{basename}.json")
        
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
    
    def plot_profiles(self, profiles):
        """
        Generate plots for M(r) and p(r).
        oh boy oh boy, let's make some beautiful plots!
        """
        mass_folder = os.path.join(self.plot_folder, "Mass")
        pressure_folder = os.path.join(self.plot_folder, "Pressure")
        
        for i, prof in enumerate(profiles):
            r_arr = prof['r']
            M_arr = prof['M']
            p_arr = prof['data']['p']
            
            # Plot M(r)
            plt.figure(figsize=(8, 6))
            plt.plot(r_arr, M_arr, 'b-', linewidth=2)
            plt.xlabel("r (code units)", fontsize=14)
            plt.ylabel("M(r) (code units)", fontsize=14)
            plt.title(f"Mass profile: p_c={prof['p_c']:.3e}", fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(mass_folder, f"mass_profile_{i}.pdf"))
            plt.close()
            
            # Plot p(r)
            plt.figure(figsize=(8, 6))
            plt.semilogy(r_arr, p_arr, 'r-', linewidth=2)
            plt.xlabel("r (code units)", fontsize=14)
            plt.ylabel("p(r) (code units, log)", fontsize=14)
            plt.title(f"Pressure profile: p_c={prof['p_c']:.3e}", fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(pressure_folder, f"pressure_profile_{i}.pdf"))
            plt.close()
        
        print(f"\nPlots saved to:")
        print(f"  {mass_folder}")
        print(f"  {pressure_folder}")


def main():
    """
    This script does the following:
      1) Reads the EXACT SAME EOS file as 'tov.py' (see 'FILENAME' in that script),
         using 'read_eos_csv_multi' to automatically get all columns in dimensionless code units.
      2) Builds an 'EOSMulti' object that can interpolate any column w.r.t. p.
      3) For a range of central pressures (p_c), we:
         - solve TOV => radial arrays {r, M(r), p(r)} in dimensionless code units
         - for each radial step, also interpolate *all other EOS columns* at p(r)
         - store everything in both:
           (a) 'radial/metadata.txt' (human-readable)
           (b) 'radial/<basename>.json' (structured)
      4) Also produce subfolders in 'plotting/radial/Mass' and 'plotting/radial/Pressure'
         for PDF plots of M(r) vs r and p(r) vs r.

    Since our file is ALREADY in dimensionless code units, we do not apply
    any conversions or black magic. We read them in, do TOV, store results. Done.
    """
    
    # Step 1: read all columns from the same file that 'tov.py' uses
    #   read_eos_csv_multi => (data_dict, colnames)
    #   data_dict["p"] is sorted ascending, colnames might be ["p","e","col2",...]
    data_dict, colnames = read_eos_csv_multi(FILENAME)
    # Build an EOSMulti object
    eos = EOSMulti(data_dict, colnames)
    
    # The first column must be 'p' in colnames[0], etc. 
    # We greet the user:
    npts = len(data_dict["p"])
    print(f"Wazzup! We read {npts} data points (and {len(colnames)} columns) from '{FILENAME}'. All in code units. Good job!")
    
    # Step 2: create our radial profiler object, oh boy oh boy!
    profiler = RadialProfiler(eos)
    
    # Step 3: choose how many stars to profile
    num_stars = 10
    print(f"\nWe'll generate radial profiles for {num_stars} stars across the pressure range.\n")
    
    # Generate profiles
    profiles = profiler.generate_profiles(num_stars=num_stars)
    
    if len(profiles) == 0:
        print("WARNING: no valid stars found. oh boy oh boy, check your EOS!")
        return
    
    # Step 4: save and plot
    basename = os.path.basename(FILENAME).replace(".csv", "")
    profiler.save_profiles(profiles, basename)
    profiler.plot_profiles(profiles)
    
    print("\nDone! oh boy oh boy!\n")


if __name__ == "__main__":
    main()
