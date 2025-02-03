import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def main():
    # Scaling constant for plotting.
    # With this scale factor, if p or ε equals 1.323790e-06 then the plotted value will be 1.
    scale_factor = 1.323790e-06

    # ------------------------------
    # 1. Ask for inputCSC data columns (1-indexed)
    # ------------------------------
    try:
        print("Enter columns for inputCSC data:")
        p_col = int(input("  Enter the column number for P (pressure) [1-indexed]: ")) - 1
        e_col = int(input("  Enter the column number for ε (energy density) [1-indexed]: ")) - 1
        mu_col = int(input("  Enter the column number for μ (chemical potential) [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input for inputCSC columns. Please enter valid integer values.")
        return

    # ------------------------------
    # 2. Ask for inputH data columns (1-indexed)
    # ------------------------------
    try:
        print("\nEnter columns for inputH data:")
        p_h_col = int(input("  Enter the column number for p (pressure) [1-indexed]: ")) - 1
        e_h_col = int(input("  Enter the column number for ε (energy density) [1-indexed]: ")) - 1
        muB_h_col = int(input("  Enter the column number for μ_B (baryonic chemical potential) [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input for inputH columns. Please enter valid integer values.")
        return

    # ------------------------------
    # 3. Load and process inputH data from CSV files in "inputH"
    # ------------------------------
    csv_filesH = glob.glob(os.path.join("inputH", "*.csv"))
    inputH_exists = False  # Flag to indicate if inputH data is available
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
            print("\nCombined inputH DataFrame shape:", df_h_all.shape)
            print("Combined inputH DataFrame columns:", df_h_all.columns.tolist())
            ncols_h = df_h_all.shape[1]
            if p_h_col >= ncols_h or e_h_col >= ncols_h or muB_h_col >= ncols_h:
                print("Error: One or more specified column numbers for inputH data are out-of-bounds.")
            else:
                try:
                    p_h = df_h_all.iloc[:, p_h_col].values
                    e_h = df_h_all.iloc[:, e_h_col].values
                    muB_h = df_h_all.iloc[:, muB_h_col].values
                    # Convert μ_B to μ by dividing by 3.
                    mu_h = muB_h / 3.0
                    # Sort inputH data by μ.
                    sorted_indices_h = np.argsort(mu_h)
                    mu_h_sorted = mu_h[sorted_indices_h]
                    p_h_sorted = p_h[sorted_indices_h]
                    e_h_sorted = e_h[sorted_indices_h]
                    # Create interpolation functions for inputH data.
                    interp_p_h = interp1d(mu_h_sorted, p_h_sorted, kind='linear', fill_value="extrapolate")
                    interp_e_h = interp1d(mu_h_sorted, e_h_sorted, kind='linear', fill_value="extrapolate")
                    mu_h_dense = np.linspace(np.min(mu_h_sorted), np.max(mu_h_sorted), 500)
                    p_h_interp = interp_p_h(mu_h_dense)
                    e_h_interp = interp_e_h(mu_h_dense)
                    inputH_exists = True
                except Exception as ex:
                    print(f"Error processing inputH data: {ex}")
    else:
        print("No CSV files found in the 'inputH' folder!")

    # ------------------------------
    # 4. Process each CSV file from "inputCSC"
    # ------------------------------
    csv_files = glob.glob(os.path.join("inputCSC", "*.csv"))
    if not csv_files:
        print("No CSV files found in the 'inputCSC' folder!")
        return

    for file in csv_files:
        print(f"\nProcessing file: {file}")
        try:
            # Read the CSV file (skip lines starting with '#' if present)
            df = pd.read_csv(file, comment='#')
            print("DataFrame shape:", df.shape)
            print("DataFrame columns:", df.columns.tolist())
        except Exception as ex:
            print(f"Error reading {file}: {ex}")
            continue

        ncols = df.shape[1]
        if p_col >= ncols or e_col >= ncols or mu_col >= ncols:
            print(f"Error: One or more specified column numbers are out-of-bounds for file {file}.")
            print(f"This file has {ncols} columns.")
            continue

        try:
            # Extract the specified columns for inputCSC data.
            P = df.iloc[:, p_col].values
            e = df.iloc[:, e_col].values
            mu = df.iloc[:, mu_col].values
        except Exception as ex:
            print(f"Error extracting columns from {file}: {ex}")
            continue

        # Sort inputCSC data by μ.
        sorted_indices = np.argsort(mu)
        mu_sorted = mu[sorted_indices]
        P_sorted = P[sorted_indices]
        e_sorted = e[sorted_indices]

        # Create linear interpolation functions for inputCSC data.
        try:
            interp_P = interp1d(mu_sorted, P_sorted, kind='linear', fill_value="extrapolate")
            interp_e = interp1d(mu_sorted, e_sorted, kind='linear', fill_value="extrapolate")
        except Exception as ex:
            print(f"Error during interpolation for {file}: {ex}")
            continue

        mu_dense = np.linspace(np.min(mu_sorted), np.max(mu_sorted), 500)
        P_interp = interp_P(mu_dense)
        e_interp = interp_e(mu_dense)

        # ------------------------------
        # 5. Create the plots:
        #      (a) Pressure vs Chemical Potential (log y-axis)
        #      (b) Pressure vs Energy Density (log-log plot)
        # ------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # (a) Pressure vs Chemical Potential
        ax1.scatter(mu, P/scale_factor, color='blue', label="Data (inputCSC)")
        ax1.plot(mu_dense, P_interp/scale_factor, color='red', label="Linear Interpolation (inputCSC)")
        if inputH_exists:
            ax1.plot(mu_h_dense, p_h_interp/scale_factor, "k--", label="InputH (converted)")
        ax1.set_xlabel("Chemical Potential (μ)")
        ax1.set_ylabel("Pressure (P) (scaled)")
        ax1.set_title("Pressure vs Chemical Potential")
        ax1.set_yscale('log')
        ax1.set_ylim(16,2000)  # Force the pressure axis to start at 1
        ax1.set_xlim(300,600)  # Force the pressure axis to start at 1
        ax1.legend()
        ax1.grid(True)

        # (b) Pressure vs Energy Density (log-log plot)
        ax2.scatter(e/scale_factor, P/scale_factor, color='blue', label="Data (inputCSC)")
        ax2.plot(e_interp/scale_factor, P_interp/scale_factor, color='red', label="Linear Interpolation (inputCSC)")
        if inputH_exists:
            ax2.plot(e_h_interp/scale_factor, p_h_interp/scale_factor, "k--", label="InputH (converted)")
        ax2.set_xlabel("Energy Density (ε) (scaled)")
        ax2.set_ylabel("Pressure (P) (scaled)")
        ax2.set_title("Pressure vs Energy Density")
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlim(20,10000)  # Force the energy density axis to start at 1
        ax2.set_ylim(16,2000)  # Force the pressure axis to start at 1
        ax2.legend()
        ax2.grid(True)

        fig.suptitle(f"Data and Interpolations from {os.path.basename(file)}")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        output_filename = os.path.splitext(os.path.basename(file))[0] + "_plot.png"
        plt.savefig(output_filename)
        plt.close(fig)
        print(f"Plot saved as {output_filename}")

if __name__ == "__main__":
    main()
