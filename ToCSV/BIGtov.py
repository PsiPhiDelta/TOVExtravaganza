#!/usr/bin/env python3
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

###############################################################################
# USER SETTINGS
###############################################################################
RMAX = 30.0            # Maximum radius for TOV integration (code units)
DR = 0.005             # Radial step size for Runge–Kutta
NUM_STARS = 300        # Number of central pressures to sample

# Use this constant to convert from code units to solar masses:
Msun_in_code = 1.4766  # 1 Msun = 1.4766 (G=c=1) length units

###############################################################################
# 1) Read an EOS CSV with multiple columns.
#    We assume the first column is "p", the second is "e", 
#    and any additional columns are extra columns in code units.
###############################################################################
def read_eos_csv_multi(filename):
    """
    Read EOS from CSV:
      - Skips comment lines (starting with "#") and empty lines.
      - If the first non-comment row is non-numeric, it is treated as a header.
      - Stores columns in a dictionary: {column_name: np.array([...])}.
      - If no header is present, the first two columns are named "p" and "e",
        with any additional columns named "col2", "col3", etc.
      - The data is sorted in ascending order of pressure.
    Returns: (data_dict, header)
    """
    raw_data = []
    header = None

    with open(filename, "r") as fin:
        reader = csv.reader(fin)
        for row in reader:
            if (not row) or row[0].startswith("#"):
                continue
            # If header not determined, try to see if first row is header.
            if header is None:
                try:
                    float(row[0]), float(row[1])
                    # No exception: row is numeric, so no header.
                    raw_data.append(row)
                except ValueError:
                    # First row is textual => treat as header.
                    header = row
            else:
                raw_data.append(row)

    # If no header was found, create a default header.
    if header is None:
        ncols = len(raw_data[0])
        header = ["p", "e"]
        for i in range(2, ncols):
            header.append(f"col{i}")

    # Parse raw data into float arrays.
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

    # Sort by ascending pressure.
    if "p" not in data_dict:
        raise ValueError("No 'p' column found! (The first column must be 'p' or given by default.)")
    sort_idx = np.argsort(data_dict["p"])
    for k in data_dict.keys():
        data_dict[k] = data_dict[k][sort_idx]

    return data_dict, header

###############################################################################
# 2) EOS class with piecewise-linear interpolation for each column.
###############################################################################
class EOSMulti:
    def __init__(self, data_dict, colnames):
        self.data_dict = data_dict
        self.colnames = colnames
        self.p_table = data_dict["p"]
        self.n = len(self.p_table)
        if self.n < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        self.ilast = 0  # For faster look-ups (bracketing index)

    def get_value(self, colname, p):
        # Clamp to the table endpoints.
        if p <= self.p_table[0]:
            return self.data_dict[colname][0]
        if p >= self.p_table[-1]:
            return self.data_dict[colname][-1]

        i = self.ilast
        # Adjust index downward if needed.
        while i > 0 and p < self.p_table[i]:
            i -= 1
        # Adjust index upward if needed.
        while i < (self.n - 1) and p > self.p_table[i + 1]:
            i += 1

        p_i   = self.p_table[i]
        p_ip1 = self.p_table[i + 1]
        c_i   = self.data_dict[colname][i]
        c_ip1 = self.data_dict[colname][i + 1]

        frac = (p - p_i) / (p_ip1 - p_i)
        val  = c_i + frac * (c_ip1 - c_i)

        self.ilast = i
        return val

    def get_e_of_p(self, p):
        return self.get_value("e", p)

###############################################################################
# 3) TOV equations in dimensionless code units.
###############################################################################
def tov_equations(y, r, eos_multi):
    """
    TOV equations:
      y[0] = M(r)  (mass enclosed within radius r)
      y[1] = p(r)  (pressure at radius r)
    """
    M, p = y
    if p <= 0.0:
        return [0.0, 0.0]
    e_val = eos_multi.get_e_of_p(p)
    dMdr = 4.0 * np.pi * r**2 * e_val

    denom = r * (r - 2.0 * M)
    if abs(denom) < 1e-30:
        dPdr = 0.0
    else:
        dPdr = -((e_val + p) * (M + 4.0 * np.pi * r**3 * p)) / denom
    return [dMdr, dPdr]

###############################################################################
# 4) Fourth-order Runge–Kutta step.
###############################################################################
def runge_kutta_step(func, y, r, h, eos_multi):
    k1 = np.array(func(y, r, eos_multi))
    k2 = np.array(func(y + 0.5 * h * k1, r + 0.5 * h, eos_multi))
    k3 = np.array(func(y + 0.5 * h * k2, r + 0.5 * h, eos_multi))
    k4 = np.array(func(y + h * k3, r + h, eos_multi))
    return y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

###############################################################################
# 5) Solve TOV using Runge–Kutta integration.
###############################################################################
def solve_tov(central_p, eos_multi, r_max=RMAX, dr=DR):
    """
    Integrate the TOV equations using a fixed-step Runge–Kutta method.
    Integration proceeds until r_max is reached or the pressure drops to zero.
    Returns (R, M) where R is the radius at the surface (p > 0) and M is the 
    enclosed mass at that radius, both in code units.
    """
    r = 0.0
    y = np.array([0.0, central_p])
    # Store the last state with positive pressure.
    last_r = r
    last_M = y[0]

    while r < r_max and y[1] > 0:
        last_r = r
        last_M = y[0]
        y = runge_kutta_step(tov_equations, y, r, dr, eos_multi)
        r += dr

    return last_r, last_M

###############################################################################
# 6) Process one EOS file: read the EOS, solve TOV for multiple central pressures,
#    write a star CSV file, and generate an M(R) plot.
###############################################################################
def process_eos_file(infile, out_folder="MR"):
    # Read the multi-column EOS.
    data_dict, colnames = read_eos_csv_multi(infile)
    eos = EOSMulti(data_dict, colnames)

    # Create output folder if it doesn't exist.
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    base_name = os.path.splitext(os.path.basename(infile))[0]
    out_csv = os.path.join(out_folder, f"{base_name}_stars.csv")
    out_pdf = os.path.join(out_folder, f"{base_name}.pdf")

    # Define a set of central pressures (log-spaced).
    p_min = max(data_dict["p"][0], 1e-15)
    p_max = data_dict["p"][-1]
    p_c_values = np.logspace(np.log10(p_min), np.log10(p_max), NUM_STARS)

    # Extra columns besides 'p'
    extra_cols = [c for c in colnames if c != "p"]
    # We will record mass in solar masses. So rename header to show that:
    header = ["p_c", "R(code units)", "M(Msun)"] + [f"{c}(pc)" for c in extra_cols]

    R_list = []
    M_list = []

    with open(out_csv, "w", encoding="utf-8") as fcsv:
        fcsv.write(",".join(header) + "\n")

        for p_c in p_c_values:
            # Solve TOV using the custom Runge–Kutta integrator.
            R_code, M_code = solve_tov(p_c, eos, RMAX, DR)

            # Convert M from code units to solar masses:
            M_solar = M_code / Msun_in_code

            R_list.append(R_code)
            M_list.append(M_solar)

            # Interpolate each extra column at p_c.
            extras_at_pc = []
            for c in extra_cols:
                val_c = eos.get_value(c, p_c)
                extras_at_pc.append(val_c)

            # Write a single CSV line: p_c, R(code units), M(Msun), extras...
            row_data = [p_c, R_code, M_solar] + extras_at_pc
            row_str = ",".join(f"{x:.6e}" for x in row_data)
            fcsv.write(row_str + "\n")

            print(f"File={base_name}, p_c={p_c:.3e} => R={R_code:.4f} (code units), "
                  f"M={M_solar:.4f} (Msun)")

    # Plot M(R) across all solutions, with R in code units, M in Msun.
    plt.figure()
    plt.plot(R_list, M_list, "o-", label="TOV solutions")
    plt.xlabel("R (code units)")
    plt.ylabel("M (Msun)")  # Now in solar masses
    plt.title(f"M(R) from {base_name}")
    plt.grid(True)
    plt.legend()
    plt.savefig(out_pdf)
    plt.close()  # Close the figure to avoid display

    print(f"Done with {base_name}: Wrote {len(p_c_values)} lines to '{out_csv}' "
          f"and plot to '{out_pdf}'\n")

###############################################################################
# 7) MAIN: Ask user for a folder and process each CSV file.
###############################################################################
def main():
    folder_in = input("Enter the folder containing your EOS CSV files: ").strip()
    if not os.path.isdir(folder_in):
        print(f"'{folder_in}' is not a valid directory! Exiting.")
        return

    # Gather all CSV files in the folder.
    files = sorted(
        f for f in os.listdir(folder_in)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(folder_in, f))
    )

    if not files:
        print(f"No CSV files found in '{folder_in}'. Exiting.")
        return

    print("\nProcessing the following files:")
    for fn in files:
        print("  ", fn)

    out_folder = "MR"
    print(f"\nStar solutions and plots will be written to the '{out_folder}/' folder.\n")

    count_files = 0
    for csv_file in files:
        csv_path = os.path.join(folder_in, csv_file)
        process_eos_file(csv_path, out_folder=out_folder)
        count_files += 1

    print(f"\nAll done! Processed {count_files} file(s). Enjoy your TOV solutions!\n")

if __name__ == "__main__":
    main()
