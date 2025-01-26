import os
import csv
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
# --------------------------------------------------------------------
# 1) TOTALLY UNNECESSARY PHYSICAL CONSTANTS (for your amusement only)
# --------------------------------------------------------------------
# Even though we used to brag about how to convert from MeV^-4 to code units,
# now we assume your input is ALREADY in TOV "code units" (dimensionless).
# So we do not actually need these constants in this script,
# but let's keep them anyway—like an old friend we can’t let go of.
#
# c0   = 299792458         # speed of light, m/s
# G    = 6.67408e-11       # gravitational constant, m^3 / (kg s^2)
# qe   = 1.6021766208e-19  # elementary charge in coulombs
# hbar = 1.054571817e-34   # reduced Planck constant, J*s
#
#
# But seriously, we’re not using them here, because you told us
# your file is *already* in those sweet dimensionless code units.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
###############################################################################
# USER SETTINGS
###############################################################################
FILENAME = "./inputCode/hsdd2.csv"  # EOS file in TOV code units
RMAX = 50.0                       # Maximum radius for TOV
DR = 0.001                        # Radial step
NUM_STARS = 50                    # Number of central pressures to sample

###############################################################################
# 1) Read an EOS CSV with multiple columns.
#    We assume the first column is "p", the second is "e", 
#    and any additional columns are "extra" columns in code units.
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

###############################################################################
# 2) EOS class with piecewise-linear interpolation in p for e, col2, etc.
###############################################################################
class EOSMulti:
    def __init__(self, data_dict, colnames):
        self.data_dict = data_dict
        self.colnames = colnames
        self.p_table = data_dict["p"]
        self.n = len(self.p_table)
        if self.n < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        self.ilast = 0  # bracket index for speed

    def get_value(self, colname, p):
        # clamp
        if p <= self.p_table[0]:
            return self.data_dict[colname][0]
        if p >= self.p_table[-1]:
            return self.data_dict[colname][-1]

        i = self.ilast
        # move left
        while i>0 and p<self.p_table[i]:
            i -= 1
        # move right
        while i<(self.n-1) and p>self.p_table[i+1]:
            i += 1

        p_i   = self.p_table[i]
        p_ip1 = self.p_table[i+1]
        c_i   = self.data_dict[colname][i]
        c_ip1 = self.data_dict[colname][i+1]

        frac = (p - p_i)/(p_ip1 - p_i)
        val  = c_i + frac*(c_ip1 - c_i)

        self.ilast = i
        return val

    def get_e_of_p(self, p):
        return self.get_value("e", p)

###############################################################################
# 3) TOV equations in dimensionless code units
###############################################################################
def tov_equations(y, r, eos_multi):
    M, p = y
    if p <= 0.0:
        return [0.0, 0.0]
    e_val = eos_multi.get_e_of_p(p)
    dMdr = 4.0 * np.pi * r*r * e_val

    denom = r*(r - 2.0*M)
    if abs(denom) < 1e-30:
        dPdr = 0.0
    else:
        dPdr = - ( (e_val + p)*( M + 4.0*np.pi*r**3 * p ) ) / denom

    return [dMdr, dPdr]

def solve_tov(central_p, eos_multi, r_max=RMAX, dr=DR):
    """
    Integrate TOV from r=0..r_max or p->0.
    Return (R, M) at the surface + the radial arrays if you like
    """
    r_vals = np.arange(0.0, r_max+dr, dr)
    y0 = [0.0, central_p]
    sol = odeint(tov_equations, y0, r_vals, args=(eos_multi,))
    M_sol = sol[:,0]
    p_sol = sol[:,1]

    idx_surface = np.where(p_sol<=0.0)[0]
    if len(idx_surface)>0:
        i_surf = idx_surface[0]
    else:
        i_surf = len(r_vals)-1

    R = r_vals[i_surf]
    M = M_sol[i_surf]

    return R, M

def solve_tov_rad(central_p, eos_multi, r_max=RMAX, dr=DR):
    """
    Integrate TOV from r=0..r_max or p->0.
    Return (R, M) at the surface + the radial arrays if you like
    """
    r_vals = np.arange(0.0, r_max+dr, dr)
    y0 = [0.0, central_p]
    sol = odeint(tov_equations, y0, r_vals, args=(eos_multi,))
    M_sol = sol[:,0]
    p_sol = sol[:,1]

    idx_surface = np.where(p_sol<=0.0)[0]
    if len(idx_surface)>0:
        i_surf = idx_surface[0]
    else:
        i_surf = len(r_vals)-1

    R = r_vals[i_surf]
    M = M_sol[i_surf]

    return r_vals, M_sol, p_sol, R, M

###############################################################################
# 4) MAIN => for each star solution, store 1 line: (p_c, R, M, e(pc), col2(pc), ...)
###############################################################################
def main():
    # Read the multi-column EOS
    data_dict, colnames = read_eos_csv_multi(FILENAME)
    eos = EOSMulti(data_dict, colnames)

    # Prepare an output folder MR
    out_folder = "MR"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # We'll create a single CSV with 1 line per star:
    # p_c, R, M, e(pc), plus other columns col2(pc)...
    base_name = os.path.splitext(os.path.basename(FILENAME))[0]
    out_csv = os.path.join(out_folder, f"{base_name}_stars.csv")
    out_pdf = os.path.join(out_folder, f"{base_name}.pdf")

    # We'll define a set of central pressures in log space
    p_min = max(data_dict["p"][0], 1e-15)
    p_max = data_dict["p"][-1]
    p_c_values = np.logspace(np.log10(p_min), np.log10(p_max), NUM_STARS)

    # Build CSV header:
    # We'll do: p_c, R, M, then for each col in colnames (except "p"), we store that col at pc
    # Because "p" is the independent variable, maybe skip it or rename it?
    # Let's skip "p" in the extras if you only want the other columns
    extra_cols = [c for c in colnames if c != "p"]
    header = ["p_c", "R", "M"] + [f"{c}(pc)" for c in extra_cols]

    R_list = []
    M_list = []

    with open(out_csv, "w", encoding="utf-8") as fcsv:
        fcsv.write(",".join(header) + "\n")

        for p_c in p_c_values:
            # Solve TOV
            R, M = solve_tov(p_c, eos)
            R_list.append(R)
            M_list.append(M)

            # Interpolate each extra col at pc
            # e.g. e(pc), n(pc), ...
            extras_at_pc = []
            for c in extra_cols:
                val_c = eos.get_value(c, p_c)
                extras_at_pc.append(val_c)

            # Write a single line: p_c, R, M, e(pc), n(pc), ...
            row_data = [p_c, R, M] + extras_at_pc
            row_str = ",".join(f"{x:.6e}" for x in row_data)
            fcsv.write(row_str + "\n")

            print(f"Star with p_c={p_c:.3e} => R={R:.4f}, M={M:.4f}")

    # Now we plot M(R) across all solutions
    plt.figure()
    plt.plot(R_list, M_list, "o-", label="TOV solutions")
    plt.xlabel("R (code units)")
    plt.ylabel("M (code units)")
    plt.title(f"M(R) from {base_name}")
    plt.grid(True)
    plt.legend()
    plt.savefig(out_pdf)
    plt.show()

    print(f"\nDone! Wrote {len(p_c_values)} lines to '{out_csv}'")
    print(f"Saved M(R) plot to '{out_pdf}'\n")


if __name__ == "__main__":
    main()
