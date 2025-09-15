import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Use your favourite plotting style
import scienceplots  # ensures the "science" style is available
from matplotlib.ticker import MaxNLocator

plt.style.use('science')
plt.rcParams.update({
    "text.usetex": True,
    "font.size": 21,
    "axes.labelsize": 24,
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "axes.titlesize": 27,
    "axes.linewidth": 1.5,
    "xtick.major.size": 7.5,
    "xtick.minor.size": 3.5,
    "ytick.major.size": 7.5,
    "ytick.minor.size": 7.5,
})
figsize = (12, 8)


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def main():
    # === Parameters ===
    # Scale factor: a raw value equal to 1.323790e-06 becomes 1 in scaled units.
    scale_factor = 1.323790e-06
    tol = 1  # tolerance for intersection (scaled units)
    N_points = 500  # number of points in hybrid grid
    n_sat = 0.15  # nuclear saturation density in fm^{-3}

    # === 1. Get columns for inputCSC data (1-indexed) ===
    try:
        print("Enter columns for inputCSC data:")
        p_col = int(input("  Enter the column number for P (pressure) [1-indexed]: ")) - 1
        e_col = int(input("  Enter the column number for \\(\\epsilon\\) (energy density) [1-indexed]: ")) - 1
        mu_col = int(input("  Enter the column number for \\(\\mu\\) (chemical potential) [1-indexed]: ")) - 1
        # New: Ask for phase index column
        phase_col = int(input("  Enter the column number for phase index [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input for inputCSC columns. Please enter valid integer values.")
        return

    # === 2. Get columns for inputH data (1-indexed) ===
    try:
        print("\nEnter columns for inputH data:")
        p_h_col = int(input("  Enter the column number for p (pressure) [1-indexed]: ")) - 1
        e_h_col = int(input("  Enter the column number for \\(\\epsilon\\) (energy density) [1-indexed]: ")) - 1
        muB_h_col = int(input("  Enter the column number for \\(\\mu_B\\) (baryonic chemical potential) [1-indexed]: ")) - 1
        n_h_col = int(input("  Enter the column number for n (density) [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input for inputH columns. Please enter valid integer values.")
        return

    # === 3. Load and process inputH data from CSV files in "inputH" ===
    csv_filesH = glob.glob(os.path.join("inputH", "*.csv"))
    inputH_exists = False
    if csv_filesH:
        df_list_h = []
        for file in csv_filesH:
            try:
                df_h = pd.read_csv(file, comment='#')
                df_list_h.append(df_h)
            except Exception as ex:
                print(f"Error reading {file} from inputH: {ex}")
        if df_list_h:
            df_h_all = pd.concat(df_list_h, ignore_index=True)
            ncols_h = df_h_all.shape[1]
            if p_h_col >= ncols_h or e_h_col >= ncols_h or muB_h_col >= ncols_h or n_h_col >= ncols_h:
                print("Error: One or more specified column numbers for inputH data are out-of-bounds.")
            else:
                try:
                    # Extract raw inputH columns.
                    p_h_raw = df_h_all.iloc[:, p_h_col].values
                    e_h_raw = df_h_all.iloc[:, e_h_col].values
                    muB_h = df_h_all.iloc[:, muB_h_col].values
                    n_h_raw = df_h_all.iloc[:, n_h_col].values
                    # Convert \\(\\mu_B\\) to \\(\\mu\\).
                    mu_h_raw = muB_h / 3.0
                    # Scale the inputH pressure and energy density data.
                    p_h_scaled = p_h_raw / scale_factor
                    e_h_scaled = e_h_raw / scale_factor
                    # (Density is not scaled.)
                    # Sort the inputH data by \\(\\mu\\).
                    sort_idx_h = np.argsort(mu_h_raw)
                    mu_h_sorted = mu_h_raw[sort_idx_h]
                    p_h_sorted = p_h_scaled[sort_idx_h]
                    e_h_sorted = e_h_scaled[sort_idx_h]
                    n_h_sorted = n_h_raw[sort_idx_h]
                    # Create interpolation functions for inputH data.
                    interp_p_h = interp1d(mu_h_sorted, p_h_sorted, kind='linear', bounds_error=False, fill_value=(p_h_sorted[0], p_h_sorted[-1]))
                    interp_e_h = interp1d(mu_h_sorted, e_h_sorted, kind='linear', bounds_error=False, fill_value=(e_h_sorted[0], e_h_sorted[-1]))
                    interp_n_h = interp1d(mu_h_sorted, n_h_sorted, kind='linear', bounds_error=False, fill_value=(n_h_sorted[0], n_h_sorted[-1]))
                    mu_h_dense = np.linspace(np.min(mu_h_sorted), np.max(mu_h_sorted), 500)
                    p_h_interp = interp_p_h(mu_h_dense)
                    e_h_interp = interp_e_h(mu_h_dense)
                    n_h_interp = interp_n_h(mu_h_dense)
                    inputH_exists = True
                except Exception as ex:
                    print(f"Error processing inputH data: {ex}")
    else:
        print("No CSV files found in the 'inputH' folder!")

    # === 4. Process each CSV file from "inputCSC" ===
    csv_files = glob.glob(os.path.join("inputCSC", "*.csv"))
    if not csv_files:
        print("No CSV files found in the 'inputCSC' folder!")
        return

    # Create folder "hybrid" if it doesn't exist.
    hybrid_folder = "hybrid"
    make_folder(hybrid_folder)
    master_list = []

    for file in csv_files:
        print(f"\nProcessing file: {file}")
        try:
            df = pd.read_csv(file, comment='#')
        except Exception as ex:
            print(f"Error reading {file}: {ex}")
            continue

        ncols = df.shape[1]
        if p_col >= ncols or e_col >= ncols or mu_col >= ncols or phase_col >= ncols:
            print(f"Error: One or more specified column numbers are out-of-bounds for file {file}.")
            continue

        try:
            # Extract raw inputCSC columns.
            P_raw = df.iloc[:, p_col].values
            e_raw = df.iloc[:, e_col].values
            mu_raw = df.iloc[:, mu_col].values
            # New: Extract phase index column.
            phase_raw = df.iloc[:, phase_col].values
        except Exception as ex:
            print(f"Error extracting columns from {file}: {ex}")
            continue

        # Scale the inputCSC data.
        P_scaled = P_raw / scale_factor
        e_scaled = e_raw / scale_factor

        # Sort inputCSC data by \\(\\mu\\).
        sort_idx = np.argsort(mu_raw)
        mu_sorted = mu_raw[sort_idx]
        P_sorted = P_scaled[sort_idx]
        e_sorted = e_scaled[sort_idx]
        phase_sorted = phase_raw[sort_idx]  # sorted phase index

        # Create interpolation functions for inputCSC data.
        try:
            interp_P = interp1d(mu_sorted, P_sorted, kind='linear', bounds_error=False, fill_value=(P_sorted[0], P_sorted[-1]))
            interp_e = interp1d(mu_sorted, e_sorted, kind='linear', bounds_error=False, fill_value=(e_sorted[0], e_sorted[-1]))
            # New: Create an interpolation for phase index using nearest-neighbor.
            interp_phase = interp1d(mu_sorted, phase_sorted, kind='nearest', bounds_error=False, fill_value=(phase_sorted[0], phase_sorted[-1]))
        except Exception as ex:
            print(f"Error during interpolation for {file}: {ex}")
            continue

        mu_dense = np.linspace(np.min(mu_sorted), np.max(mu_sorted), 500)
        P_interp = interp_P(mu_dense)
        e_interp = interp_e(mu_dense)
        phase_interp = interp_phase(mu_dense)  # interpolated phase index

        # Clip pressure values below 0.1.
        P_interp_clipped = np.clip(P_interp, 0.1, None)
        n_clipped_csc = np.sum(P_interp < 0.1)
        if n_clipped_csc > 0:
            print(f"  WARNING: Clipped {n_clipped_csc} CSC pressure values below 0.1 (min P = {np.min(P_interp):.6e})")
        
        if inputH_exists:
            p_h_interp_clipped = np.clip(p_h_interp, 0.1, None)
            n_clipped_h = np.sum(p_h_interp < 0.1)
            if n_clipped_h > 0:
                print(f"  WARNING: Clipped {n_clipped_h} hadronic pressure values below 0.1 (min P = {np.min(p_h_interp):.6e})")

        # --- Determine the overlapping \\(\\mu\\) range ---
        if inputH_exists:
            mu_common_min = max(np.min(mu_dense), np.min(mu_h_dense))
            mu_common_max = min(np.max(mu_dense), np.max(mu_h_dense))
        else:
            mu_common_min = np.min(mu_dense)
            mu_common_max = np.max(mu_dense)

        if mu_common_max <= mu_common_min:
            print("No overlapping \\(\\mu\\) range between inputCSC and inputH data; skipping file.")
            continue

        # --- Compute the intersection point using sign changes ---
        valid_intersection = False
        if inputH_exists:
            common_mu = np.linspace(mu_common_min, mu_common_max, 5000)
            P_interp_csci = interp_P(common_mu)
            P_interp_h_common = interp_p_h(common_mu)
            diff = P_interp_csci - P_interp_h_common

            # Detect sign changes in diff.
            sign_diff = np.sign(diff)
            sign_changes = np.where(np.diff(sign_diff) != 0)[0]
            num_intersections = len(sign_changes)
            print(f"File: {os.path.basename(file)}")
            print(f"  Overlapping \\(\\mu\\) range: {mu_common_min:.4f} to {mu_common_max:.4f}")
            print(f"  Number of intersections found: {num_intersections}")

            # Instead of taking the last intersection, search for the first intersection candidate
            # that yields a hadronic density above 0.5 n_sat.
            mu_int = None
            n_int = None
            if num_intersections > 0:
                valid_candidate_found = False
                for idx in sign_changes:
                    mu1, mu2 = common_mu[idx], common_mu[idx+1]
                    f1, f2 = diff[idx], diff[idx+1]
                    if f2 - f1 == 0:
                        mu_int_candidate = common_mu[idx]
                    else:
                        mu_int_candidate = mu1 - f1 * (mu2 - mu1) / (f2 - f1)
                    n_int_candidate = interp_n_h(mu_int_candidate)
                    print(f"  Candidate intersection at mu = {mu_int_candidate:.4f} gives n = {n_int_candidate:.6f}")
                    if n_int_candidate > 0.5 * n_sat:
                        mu_int = mu_int_candidate
                        n_int = n_int_candidate
                        valid_candidate_found = True
                        break
                if valid_candidate_found:
                    P_int = interp_P(mu_int)
                    print(f"  Using intersection at mu = {mu_int:.4f}, P = {P_int:.6f}, n = {n_int:.6f}")
                    if np.abs(interp_P(mu_int) - interp_p_h(mu_int)) < tol and interp_P(mu_int) > 0.1:
                        valid_intersection = True
                        print(f"  --> Intersection accepted at \\(\\mu\\) = {mu_int:.4f}")
                    else:
                        print("  --> Intersection found but does not meet the criteria.")
                else:
                    print("  --> No intersection candidate found with n > 0.5 n_sat")
            else:
                print("  --> No valid intersection found.")
        else:
            print("  --> No hadronic data (inputH) found; skipping hybrid construction.")
            valid_intersection = False

        # === Plot (with or without the hybrid) ===
        eos_name = os.path.splitext(os.path.basename(file))[0]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot CSC data (blue) and hadronic data (gray dashed).
        ax1.plot(mu_dense, P_interp_clipped, color='blue', label=eos_name, linewidth=3, zorder=2)
        if inputH_exists:
            ax1.plot(mu_h_dense, p_h_interp_clipped, color="gray", linewidth=3,
                     linestyle="--", label="FB", zorder=3)
            if valid_intersection:
                # Here we show both the quark chemical potential (mu_q) and the corresponding
                # baryonic chemical potential (mu_B = 3*mu_q) in the legend.
                ax1.plot(mu_int, P_int, 'ro', markersize=10,
                         label=f"$n$ = {n_int/n_sat:.2f} $n_0$, "
                               f"$\\mu_q$ = {mu_int:.0f} MeV, $\\mu_B$ = {mu_int*3:.0f} MeV",
                         zorder=4)

        ax1.set_xlabel("$\\mu_q$ [MeV]")
        ax1.set_ylabel("$P$ [MeV/fm$^3$]")
        ax1.set_yscale('log')
        ax1.set_ylim(bottom=1)
        ax1.legend()
        ax1.grid(True)

        ax2.plot(e_interp, P_interp_clipped, color='blue', linewidth=3, label=eos_name, zorder=2)
        if inputH_exists:
            ax2.plot(e_h_interp, p_h_interp_clipped, color="gray", linestyle="--",
                     linewidth=3, label="FB", zorder=3)
        ax2.set_xlabel("$\\epsilon$ [MeV/fm$^3$]")
        ax2.set_ylabel("$P$ [MeV/fm$^3$]")
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlim(100,3000)
        ax2.set_ylim(bottom=1)
        ax2.legend()
        ax2.grid(True)

        # --- If there is a valid intersection, build and plot the hybrid EoS ---
        if valid_intersection:
            # Use a small offset near mu_int for branch selection.
            offset = 0.01 * (mu_common_max - mu_common_min)
            mu_left_test = mu_int - offset if (mu_int - offset) > mu_common_min else mu_common_min
            mu_right_test = mu_int + offset if (mu_int + offset) < mu_common_max else mu_common_max

            P_left_CSC = interp_P(mu_left_test)
            P_left_H = interp_p_h(mu_left_test) if inputH_exists else -np.inf
            left_branch = "CSC" if P_left_CSC >= P_left_H else "H"

            P_right_CSC = interp_P(mu_right_test)
            P_right_H = interp_p_h(mu_right_test) if inputH_exists else -np.inf
            right_branch = "CSC" if P_right_CSC >= P_right_H else "H"

            print(f"  Left branch (near mu = {mu_left_test:.4f}): {left_branch}")
            print(f"  Right branch (near mu = {mu_right_test:.4f}): {right_branch}")

            # Only accept the matching if the left branch is hadronic (H) and the right branch is CSC.
            if left_branch != "H" or right_branch != "CSC":
                print("  --> Intersection rejected: left branch must be hadronic (H) and right branch must be CSC.")
                valid_intersection = False

            if valid_intersection:
                if left_branch == "CSC":
                    branch_left_min = np.min(mu_sorted)
                else:
                    branch_left_min = np.min(mu_h_sorted)
                if right_branch == "CSC":
                    branch_right_max = np.max(mu_sorted)
                else:
                    branch_right_max = np.max(mu_h_sorted)

                hybrid_mu = np.linspace(branch_left_min, branch_right_max, N_points)
                hybrid_P_scaled = np.empty_like(hybrid_mu)
                hybrid_e_scaled = np.empty_like(hybrid_mu)
                # New: Create an array for the phase index.
                hybrid_phase = np.empty_like(hybrid_mu, dtype=int)

                for i, mu_val in enumerate(hybrid_mu):
                    if mu_val < mu_int:
                        if left_branch == "CSC":
                            hybrid_P_scaled[i] = interp_P(mu_val)
                            hybrid_e_scaled[i] = interp_e(mu_val)
                            hybrid_phase[i] = round(interp_phase(mu_val))
                        else:
                            hybrid_P_scaled[i] = interp_p_h(mu_val)
                            hybrid_e_scaled[i] = interp_e_h(mu_val)
                            hybrid_phase[i] = 0  # Hadronic branch gets phase index 0.
                    else:
                        if right_branch == "CSC":
                            hybrid_P_scaled[i] = interp_P(mu_val)
                            hybrid_e_scaled[i] = interp_e(mu_val)
                            hybrid_phase[i] = round(interp_phase(mu_val))
                        else:
                            hybrid_P_scaled[i] = interp_p_h(mu_val)
                            hybrid_e_scaled[i] = interp_e_h(mu_val)
                            hybrid_phase[i] = 0  # Hadronic branch gets phase index 0.

                hybrid_P = hybrid_P_scaled * scale_factor
                hybrid_e = hybrid_e_scaled * scale_factor
                hybrid_muB = hybrid_mu * 3

                # Include the hybrid phase index in the output DataFrame.
                df_hybrid = pd.DataFrame({
                    "pressure": hybrid_P,
                    "epsilon": hybrid_e,
                    "muB": hybrid_muB,
                    "phase_index": hybrid_phase
                })
                hybrid_filename = os.path.join(hybrid_folder, eos_name + "_hybrid.csv")
                df_hybrid.to_csv(hybrid_filename, index=False)
                print(f"Hybrid EoS saved as: {hybrid_filename}")
                master_list.append({"eos": eos_name, "file": hybrid_filename})

                try:
                    hybrid_mu_loaded = hybrid_muB / 3.0
                    hybrid_P_loaded = hybrid_P_scaled
                    hybrid_e_loaded = hybrid_e_scaled

                    ax1.plot(hybrid_mu_loaded, hybrid_P_loaded, color="red", linewidth=1.5,
                             alpha=0.8, zorder=5, label="Hybrid")
                    ax2.plot(hybrid_e_loaded, hybrid_P_loaded, color="red", linewidth=1.5,
                             alpha=0.8, zorder=5, label="Hybrid")
                    print(f"Hybrid branch plotted for {eos_name}")
                except Exception as ex:
                    print(f"Error plotting hybrid data: {ex}")

                ax1.legend()
                ax2.legend()

        plot_filename = os.path.join(hybrid_folder, eos_name + ".pdf")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(plot_filename)
        plt.close(fig)
        print(f"Plot saved as {plot_filename}")

    if master_list:
        df_master = pd.DataFrame(master_list)
        master_csv = os.path.join(hybrid_folder, "hybrid_master.csv")
        df_master.to_csv(master_csv, index=False)
        print(f"Master CSV file created: {master_csv}")


if __name__ == "__main__":
    main()
