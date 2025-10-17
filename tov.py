#!/usr/bin/env python3
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------
# 1) TOTALLY UNNECESSARY PHYSICAL CONSTANTS (for your amusement only)
# --------------------------------------------------------------------
# Even though we used to brag about how to convert from MeV^-4 to code units,
# now we assume your input is ALREADY in TOV "code units" (dimensionless).
# So we do not actually need these constants in this script,
# but let's keep them anyway—like an old friend we can't let go of.
#
# c0   = 299792458         # speed of light, m/s
# G    = 6.67408e-11       # gravitational constant, m^3 / (kg s^2)
# qe   = 1.6021766208e-19  # elementary charge in coulombs
# hbar = 1.054571817e-34   # reduced Planck constant, J*s
#
#
# But seriously, we're not using them here, because you told us
# your file is *already* in those sweet dimensionless code units.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Now we use the fancy object-oriented modules from src/!
from src.eos import EOS
from src.tov_solver import TOVSolver
from src.output_handlers import MassRadiusWriter

# Use this constant to convert from code units to solar masses:
Msun_in_code = 1.4766  # 1 Msun = 1.4766 (G=c=1) length units

###############################################################################
# USER SETTINGS
###############################################################################
FILENAME = "./inputCode/test.csv"  # EOS file in TOV code units
RMAX = 100.0                       # Maximum radius for TOV
DR = 0.001                        # Radial step
NUM_STARS = 500                    # Number of central pressures to sample

###############################################################################
# BACKWARD COMPATIBILITY FUNCTIONS
# These let radial.py still work with the old function calls
###############################################################################
def read_eos_csv_multi(filename):
    """
    Read EOS from CSV:
      - skip comment lines (#) and empty lines
      - if the first non-comment row is textual, treat as header
      - store columns in data_dict = {colname: np.array([...])}
      - assume first column is "p", second is "e" if no explicit header
      - sort by ascending p
    Returns: data_dict, colnames
    """
    raw_data = []
    header = None

    with open(filename, "r") as fin:
        reader = csv.reader(fin)
        for row in reader:
            if (not row) or row[0].startswith("#"):
                continue
            # check if we have a header yet
            if header is None:
                # try parsing first 2 columns as float
                try:
                    float(row[0]), float(row[1])
                    # no exception => numeric => no header
                    raw_data.append(row)
                except ValueError:
                    # not numeric => treat as header
                    header = row
            else:
                raw_data.append(row)

    # if no header found, create a default
    if header is None:
        ncols = len(raw_data[0])
        header = []
        header.append("p")
        header.append("e")
        for i in range(2, ncols):
            header.append(f"col{i}")

    # parse data into float arrays
    columns = [[] for _ in header]
    for row in raw_data:
        if len(row) < 2:
            continue
        valid = True
        vals = []
        for i in range(len(header)):
            try:
                vals.append(float(row[i]))
            except (IndexError, ValueError):
                valid = False
                break
        if valid:
            for i in range(len(header)):
                columns[i].append(vals[i])

    data_dict = {}
    for h, colvals in zip(header, columns):
        data_dict[h] = np.array(colvals, dtype=float)

    # Sort by ascending p
    if "p" not in data_dict:
        raise ValueError("No 'p' column found! (First column must be named 'p' or given by default.)")

    sort_idx = np.argsort(data_dict["p"])
    for k in data_dict.keys():
        data_dict[k] = data_dict[k][sort_idx]

    return data_dict, header


class EOSMulti:
    """
    Backward compatibility wrapper for radial.py
    This just wraps the new EOS class from src/
    """
    def __init__(self, data_dict, colnames):
        self.data_dict = data_dict
        self.colnames = colnames
        self.p_table = data_dict["p"]
        self.n = len(self.p_table)
        if self.n < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        self.ilast = 0  # bracket index for speed
        
        # Create the real EOS object from src/
        self._eos = EOS(data_dict, colnames)

    def get_value(self, colname, p):
        return self._eos.get_value(colname, p)

    def get_e_of_p(self, p):
        return self._eos.get_energy_density(p)
    
    def interp(self, colname, p):
        """For radial.py compatibility"""
        return self._eos.get_value(colname, p)


def solve_tov(central_p, eos_multi, r_max=RMAX, dr=DR):
    """Legacy function for backward compatibility"""
    solver = TOVSolver(eos_multi._eos, r_max, dr)
    star = solver.solve(central_p)
    return star.radius, star.mass_code


def solve_tov_rad(central_p, eos_multi, r_max=RMAX, dr=DR):
    """Legacy function for backward compatibility with radial.py"""
    solver = TOVSolver(eos_multi._eos, r_max, dr)
    star, r_vals, M_vals, p_vals = solver.solve(central_p, return_profile=True)
    
    # Return in the old format that radial.py expects
    return r_vals, M_vals, p_vals, star.radius, star.mass_code


###############################################################################
# 4) MAIN => for each star solution, store 1 line: (p_c, R, M, e(pc), col2(pc), ...)
###############################################################################
def main():
    """
    Main function - now using fancy OO modules from src/
    but keeping all the comedic style you know and love!
    """
    # Read the multi-column EOS using our fancy new EOS class
    eos = EOS.from_file(FILENAME)
    
    print(f"Loaded EOS from {FILENAME}")
    print(f"  {eos.n_points} data points")
    print(f"  Columns: {', '.join(eos.colnames)}")
    
    # Create our solver object - now from src/!
    solver = TOVSolver(eos, r_max=RMAX, dr=DR)

    # Prepare an output folder MR
    out_folder = "export/MR"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # We'll create a single CSV with 1 line per star:
    # p_c, R, M, e(pc), plus other columns col2(pc)...
    base_name = os.path.splitext(os.path.basename(FILENAME))[0]
    
    # Generate the sequence of stars using our fancy solver
    print(f"\nSolving TOV for {NUM_STARS} central pressures...")
    
    # Get pressure range
    p_range = eos.get_pressure_range()
    p_min = max(p_range[0], 1e-15)
    p_max = p_range[1]
    central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), NUM_STARS)
    
    # Solve for each pressure
    stars = []
    for p_c in central_pressures:
        try:
            star = solver.solve(p_c)
            stars.append(star)
            M_solar = star.mass_solar
            print(f"Star with p_c={p_c:.3e} => R={star.radius:.4f}, M={M_solar:.4f}")
        except Exception as e:
            print(f"Failed at p_c={p_c:.3e}: {e}")
    
    # Use our fancy writer from src/
    writer = MassRadiusWriter(output_folder=out_folder)
    csv_path, pdf_path = writer.write_stars(stars, base_name)
    
    # Print some stats
    valid_stars = [s for s in stars if s.mass_solar > 0.01]
    if valid_stars:
        max_star = max(valid_stars, key=lambda s: s.mass_solar)
        print(f"\nValid solutions: {len(valid_stars)}/{len(stars)}")
        print(f"Maximum mass: {max_star.mass_solar:.4f} Msun at R={max_star.radius:.4f} km")
        
        # Find star near 1.4 solar masses
        near_14 = min(valid_stars, key=lambda s: abs(s.mass_solar - 1.4))
        print(f"Near 1.4 Msun: M={near_14.mass_solar:.4f} Msun, R={near_14.radius:.4f} km")

    print(f"\nWrote {len(stars)} stars to: {csv_path}")
    print(f"Saved M-R plot to: {pdf_path}")
    print("\nDone!\n")


if __name__ == "__main__":
    main()
