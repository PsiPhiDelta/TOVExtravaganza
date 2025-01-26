import os
import json
import numpy as np
import matplotlib.pyplot as plt

# We import from "tov.py" the same FILENAME, plus read_eos_csv_multi, EOSMulti, solve_tov, DR, RMAX
# so that we all share the same dimensionless TOV code units.
from tov import FILENAME, read_eos_csv_multi, EOSMulti, solve_tov_rad, DR, RMAX

def main():
    """
    Hello, friend!
    Howdy?

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

    # Step 2: create a 'radial' folder for storing metadata
    output_folder = "radial"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # We'll keep text-based metadata in 'metadata.txt'
    text_meta_path = os.path.join(output_folder, "metadata.txt")

    # We'll derive a JSON filename from the input's basename
    base_name = os.path.splitext(os.path.basename(FILENAME))[0]
    json_name = base_name + ".json"
    json_meta_path = os.path.join(output_folder, json_name)

    # Open the text metadata file
    fmeta_txt = open(text_meta_path, "w", encoding="utf-8")
    # cutesy preamble
    fmeta_txt.write("# Hello from radial.py!\n")
    fmeta_txt.write("# In this file, we store radial TOV solutions for multiple stars.\n")
    fmeta_txt.write("# Each star is marked by '# NEW STAR pc= ...' followed by lines:\n")
    fmeta_txt.write("#   r, M(r), p(r), plus all other columns colX(r)\n\n")

    # We'll gather data for a JSON structure
    json_data = {"stars": []}

    # Step 3: define a range of central pressures to sample
    p_arr = data_dict["p"]  # ascending array
    p_min = max(p_arr[0], 1e-6)  # or 1e-15, etc. 
    p_max = p_arr[-1]
    # We'll do 10 log-spaced points
    p_c_values = np.logspace(np.log10(p_min), np.log10(p_max), 10)

    # Step 4: define subfolders for plots
    plotting_root = "plotting"
    radial_plot_folder = os.path.join(plotting_root, "radial")
    mass_folder = os.path.join(radial_plot_folder, "Mass")
    pressure_folder = os.path.join(radial_plot_folder, "Pressure")

    # Make them if not existing
    for fld in [plotting_root, radial_plot_folder, mass_folder, pressure_folder]:
        if not os.path.exists(fld):
            os.makedirs(fld)

    # We'll figure out which columns are "extra" (i.e. not "p")
    # Because "p" is integrated from TOV, we'll store that directly.
    # For everything else, we do eos.get_value(col, p(r)).
    extra_columns = [c for c in colnames if c != "p"]

    # Step 5: Solve TOV for each star, record results in text & JSON, plus plots
    for idx, p_c in enumerate(p_c_values):
        # A) Solve TOV with p_c as the central pressure
        r_vals, m_vals, p_vals, R, M = solve_tov_rad(p_c, eos, r_max=RMAX, dr=DR)

        # B) Print final star info
        print(f"p_c= {p_c:.3e} => R= {R:.3f}, M= {M:.3f}  (still dimensionless, mind you)")

        # C) Write text metadata
        fmeta_txt.write(f"# NEW STAR pc= {p_c:.6e}\n")
        # We'll label columns for the user:
        col_label_str = "r, M(r), p(r)"
        for c in extra_columns:
            col_label_str += f", {c}(r)"
        fmeta_txt.write(f"# Columns: {col_label_str}\n")

        # We'll build the radial table => [ (r, M, p, {col: val, ...}), ... ]
        star_radial_list = []  # this will help build JSON

        # For each radial step
        for (rr, mm, pp) in zip(r_vals, m_vals, p_vals):
            # We'll create a dict that includes r, M, p, plus each extra column
            row_dict = {"r": rr, "M": mm, "p": pp}
            # Interpolate each extra col at p(r)
            for c in extra_columns:
                val_c = eos.get_value(c, pp)
                row_dict[c] = val_c

            star_radial_list.append(row_dict)

            # Write them all as a single line
            # We keep the same order: r, M, p, then extras
            row_str_list = [f"{rr:.6e}", f"{mm:.6e}", f"{pp:.6e}"]
            for c in extra_columns:
                row_str_list.append(f"{row_dict[c]:.6e}")
            line_str = ", ".join(row_str_list)
            fmeta_txt.write(line_str + "\n")

        fmeta_txt.write("\n")  # blank line

        # D) Build JSON star object
        star_obj = {
            "pc": p_c,
            "R": R,
            "M": M,
            "radial_data": []
        }
        # convert star_radial_list to the JSON-friendly format
        for row_dict in star_radial_list:
            star_obj["radial_data"].append(row_dict)

        json_data["stars"].append(star_obj)

        # E) Create plots:
        # (a) M(r) vs r
        plt.figure()
        plt.plot(r_vals, m_vals, label="M(r)")
        plt.xlabel("r (code units)")
        plt.ylabel("Mass M(r) (code units)")
        plt.title(f"pc={p_c:.3e}: M(r) vs r")
        plt.legend()
        mass_plot_file = os.path.join(mass_folder, f"mass_profile_{idx}.pdf")
        plt.savefig(mass_plot_file)
        plt.close()

        # (b) p(r) vs r
        plt.figure()
        plt.plot(r_vals, p_vals, label="p(r)")
        plt.xlabel("r (code units)")
        plt.ylabel("Pressure p(r) (code units)")
        plt.title(f"pc={p_c:.3e}: p(r) vs r")
        plt.legend()
        pressure_plot_file = os.path.join(pressure_folder, f"pressure_profile_{idx}.pdf")
        plt.savefig(pressure_plot_file)
        plt.close()

    # Step 6: close the text file
    fmeta_txt.close()

    # Step 7: dump the JSON
    with open(json_meta_path, "w", encoding="utf-8") as fjson:
        json.dump(json_data, fjson, indent=2)

    # Step 8: wave goodbye
    print("\nAll radial data for ALL stars is stashed in:")
    print(f"  {text_meta_path}  (human-friendly text)")
    print(f"  {json_meta_path}  (structured JSON)\n")
    print("Plots stored in:")
    print(f"  {mass_folder}       (mass profiles)")
    print(f"  {pressure_folder}   (pressure profiles)")
    print("Farewell and enjoy your radial extravaganza!\n")

if __name__ == "__main__":
    main()
