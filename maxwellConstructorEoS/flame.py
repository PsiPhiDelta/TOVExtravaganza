import glob
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def plot_etaV_etaD(folder_path):
    # Lists to store the eta_V and eta_D values (for files passing the filter)
    eta_V_all = []
    eta_D_all = []

    # Regex to match filenames like: RGgen_v0.00d0.90_hybrid_stars.csv
    pattern = re.compile(r'RGgen_v([0-9.]+)d([0-9.]+)_hybrid_stars\.csv')

    # Find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        # Extract eta_V and eta_D from the filename
        match = pattern.search(filename)
        if not match:
            # Skip files that don't match the naming pattern
            continue
        
        try:
            eta_V = float(match.group(1))
            eta_D = float(match.group(2))
        except ValueError:
            print(f"Could not convert extracted values to float from file: {filename}")
            continue
        
        # Read the CSV file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue
        
        # Check if 'M(Msun)' column exists
        if "M(Msun)" not in df.columns:
            print(f"No 'M(Msun)' column found in {filename}. Skipping.")
            continue
        
        # Filter by maximum of 'M(Msun)' > 2.08
        if df["M(Msun)"].max() > 2.08:
            # Keep this point
            eta_V_all.append(eta_V)
            eta_D_all.append(eta_D)

    # Create scatter plot of the points that passed the filter
    plt.figure(figsize=(7,5))
    
    plt.scatter(eta_V_all, eta_D_all, 
                color='blue', alpha=0.7, edgecolors='k')
    
    plt.xlabel(r'$\eta_V$')
    plt.ylabel(r'$\eta_D$')
    plt.title('Scatter Plot of $\eta_D$ vs. $\eta_V$ (Max M > 2.08)')
    plt.xlim(0., 1.5)
    plt.ylim(0.9, 1.8)
    plt.grid(True)
    plt.tight_layout()

    # Save figure as PDF
    plt.savefig("etaV_vs_etaD_filter_maxMgt2p08.pdf", format='pdf', dpi=300)
    
    # Show the plot
    plt.show()

# Example usage:
if __name__ == "__main__":
    folder = "./massRadiusMatches/"
    plot_etaV_etaD(folder)
