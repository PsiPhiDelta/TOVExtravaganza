import glob
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def plot_etaV_etaD(folder_path):
    # Lists to store extracted eta_V and eta_D values for each phase category
    eta_V_2sc = []
    eta_D_2sc = []
    eta_V_cfl = []
    eta_D_cfl = []

    # Regex to match filenames like: RGgen_v0.00d0.90_hybrid.csv
    pattern = re.compile(r'RGgen_v([0-9.]+)d([0-9.]+)_hybrid\.csv')

    # Find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        # Extract eta_V and eta_D from the filename
        match = pattern.search(filename)
        if not match:
            print(f"Filename not in expected format: {filename}")
            continue
        
        try:
            eta_V = float(match.group(1))
            eta_D = float(match.group(2))
        except ValueError:
            print(f"Could not convert extracted values to float from file: {filename}")
            continue
        
        # Read the CSV file to check the 'phase_index' column
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue
        
        # Ensure the phase_index column exists
        if "phase_index" not in df.columns:
            print(f"No 'phase_index' column found in {filename}. Skipping.")
            continue
        
        # Check if any row has phase_index == 1
        if (df["phase_index"] == 1).any():
            # 2SC match
            eta_V_2sc.append(eta_V)
            eta_D_2sc.append(eta_D)
        else:
            # CFL
            eta_V_cfl.append(eta_V)
            eta_D_cfl.append(eta_D)

    # --- Load data from text file and store in separate lists ---
    text_file = "eta_v_eta_d_mass_2.txt"  # Adjust path if necessary
    eta_V_mass = []
    eta_D_mass = []

    try:
        with open(text_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                # Expect each line to have at least two columns: eta_V and eta_D
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        v = float(parts[0])
                        d = float(parts[1])
                        eta_V_mass.append(v)
                        eta_D_mass.append(d)
                    except ValueError:
                        # If a line can't be converted, skip it
                        print(f"Skipping malformed line in {text_file}: {line}")
    except FileNotFoundError:
        print(f"Could not find the text file: {text_file}. Make sure it's in the correct folder.")

    # Create scatter plot
    plt.figure(figsize=(5,5))
    
    # Plot 2SC points in blue
    plt.scatter(eta_V_2sc, eta_D_2sc, 
                color='blue', alpha=0.7, edgecolors='k', label='2SC match')

    # Plot CFL points in red
    plt.scatter(eta_V_cfl, eta_D_cfl, 
                color='red', alpha=0.7, edgecolors='k', label='CFL match')

    # Plot points from the text file in green
    plt.plot(eta_V_mass, eta_D_mass, 
                color='green', alpha=0.7)

    plt.xlabel(r'$\eta_V$')
    plt.ylabel(r'$\eta_D$')
    plt.xlim(0., 1.5)
    plt.ylim(0.9, 1.8)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save figure as PDF
    plt.savefig("etaV_vs_etaD.pdf", format='pdf', dpi=300)
    
    # Show the plot
    plt.show()

# Example usage:
if __name__ == "__main__":
    folder = "./allMatches/"
    plot_etaV_etaD(folder)
