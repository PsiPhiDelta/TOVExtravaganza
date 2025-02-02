import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def main():
    # Ask the user which column (1-indexed) corresponds to each variable.
    try:
        p_col = int(input("Enter the column number for P (pressure) [1-indexed]: ")) - 1
        e_col = int(input("Enter the column number for e (energy density) [1-indexed]: ")) - 1
        mu_col = int(input("Enter the column number for mu (chemical potential) [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input. Please enter valid integer values.")
        return

    # Get a list of all text files in the "inputCSC" folder.
    text_files = glob.glob(os.path.join("inputCSC", "*.txt"))
    if not text_files:
        print("No text files found in the 'inputCSC' folder!")
        return

    # Process each text file.
    for file in text_files:
        print(f"\nProcessing file: {file}")
        try:
            # Read the text file.
            # We use sep='\s+' to split columns on whitespace and skip comment lines starting with '#'.
            df = pd.read_csv(file, comment='#', sep='\s+')
            print("DataFrame shape:", df.shape)
            print("DataFrame columns:", df.columns.tolist())
        except Exception as ex:
            print(f"Error reading {file}: {ex}")
            continue

        # Check if the requested column indices exist.
        ncols = df.shape[1]
        if p_col >= ncols or e_col >= ncols or mu_col >= ncols:
            print(f"Error: One or more specified column numbers are out-of-bounds for file {file}.")
            print(f"This file has {ncols} columns.")
            continue

        try:
            # Extract the specified columns (after converting 1-based to 0-based indexing).
            P = df.iloc[:, p_col].values
            e = df.iloc[:, e_col].values
            mu = df.iloc[:, mu_col].values
        except Exception as ex:
            print(f"Error extracting columns from {file}: {ex}")
            continue

        # Sort the data by mu (the independent variable) for proper interpolation.
        sorted_indices = np.argsort(mu)
        mu_sorted = mu[sorted_indices]
        P_sorted = P[sorted_indices]
        e_sorted = e[sorted_indices]

        # Create linear interpolation functions for P vs μ and e vs μ.
        try:
            interp_P = interp1d(mu_sorted, P_sorted, kind='linear', fill_value="extrapolate")
            interp_e = interp1d(mu_sorted, e_sorted, kind='linear', fill_value="extrapolate")
        except Exception as ex:
            print(f"Error during interpolation for {file}: {ex}")
            continue

        # Generate a dense array of μ values for a smooth interpolated curve.
        mu_dense = np.linspace(np.min(mu_sorted), np.max(mu_sorted), 500)
        P_interp = interp_P(mu_dense)
        e_interp = interp_e(mu_dense)

        # Create a figure with two subplots.
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot P vs μ.
        axes[0].scatter(mu, P, color='blue', label="Data")
        axes[0].plot(mu_dense, P_interp, color='red', label="Linear Interpolation")
        axes[0].set_xlabel("Chemical Potential (μ)")
        axes[0].set_ylabel("Pressure (P)")
        axes[0].set_title("Pressure vs Chemical Potential")
        axes[0].legend()
        axes[0].grid(True)

        # Plot e vs μ.
        axes[1].scatter(mu, e, color='blue', label="Data")
        axes[1].plot(mu_dense, e_interp, color='red', label="Linear Interpolation")
        axes[1].set_xlabel("Chemical Potential (μ)")
        axes[1].set_ylabel("Energy Density (e)")
        axes[1].set_title("Energy Density vs Chemical Potential")
        axes[1].legend()
        axes[1].grid(True)

        fig.suptitle(f"Data and Interpolation from {os.path.basename(file)}")

        # Save the plot as a PNG file. The filename is derived from the text file name.
        output_filename = os.path.splitext(os.path.basename(file))[0] + "_plot.png"
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(output_filename)
        plt.close(fig)
        print(f"Plot saved as {output_filename}")

if __name__ == "__main__":
    main()
