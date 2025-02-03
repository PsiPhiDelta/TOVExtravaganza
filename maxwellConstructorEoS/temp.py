import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Ask user for the column numbers (1-indexed) for p, ε, and n.
    try:
        print("Enter columns for inputH data:")
        p_col = int(input("  Enter the column number for p (pressure) [1-indexed]: ")) - 1
        e_col = int(input("  Enter the column number for ε (energy density) [1-indexed]: ")) - 1
        n_col = int(input("  Enter the column number for n (number density) [1-indexed]: ")) - 1
    except ValueError:
        print("Invalid input. Please enter valid integer values.")
        return

    # Get a list of all CSV files in the "inputH" folder.
    csv_files = glob.glob(os.path.join("inputH", "*.csv"))
    if not csv_files:
        print("No CSV files found in the 'inputH' folder!")
        return

    # Process each CSV file.
    for file in csv_files:
        print(f"\nProcessing file: {file}")
        try:
            df = pd.read_csv(file, comment='#')
        except Exception as ex:
            print(f"Error reading {file}: {ex}")
            continue

        # Check if the file has enough columns.
        if df.shape[1] <= max(p_col, e_col, n_col):
            print(f"File {file} does not have enough columns.")
            continue

        try:
            # Extract the raw data for p, ε, and n.
            p = df.iloc[:, p_col].values
            e = df.iloc[:, e_col].values
            n = df.iloc[:, n_col].values
        except Exception as ex:
            print(f"Error extracting columns from {file}: {ex}")
            continue

        # Calculate μ using the formula: (p + ε) / n.
        # (Assuming n is nonzero for valid rows.)
        with np.errstate(divide='ignore', invalid='ignore'):
            mu = (p + e) / n

        # Create a scatter plot (log-log) of p vs. the calculated μ.
        plt.figure(figsize=(8, 6))
        plt.scatter(mu, p, c='blue', label="Data")
        plt.xlabel("Calculated μ = (p + ε) / n")
        plt.ylabel("Pressure (p)")
        plt.xscale('log')
        plt.yscale('log')
        plt.title(f"Log-Log Scatter Plot of p vs. Calculated μ\n{os.path.basename(file)}")
        plt.legend()
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()

        # Save the plot.
        output_filename = os.path.splitext(os.path.basename(file))[0] + "_scatter_plot.png"
        plt.savefig(output_filename)
        plt.close()
        print(f"Plot saved as {output_filename}")

if __name__ == "__main__":
    main()
