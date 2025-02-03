import os
import pandas as pd
import matplotlib.pyplot as plt
import scienceplots  # Ensuring "science" style is available
import numpy as np
import re  # For filename parsing
#TODO: check tov
# Use favorite plotting style
plt.style.use('science')
plt.rcParams.update({
    "text.usetex": True,
    "font.size": 24,
    "axes.labelsize": 28,
    "xtick.labelsize": 28,
    "ytick.labelsize": 28,
    "axes.titlesize": 32,
    "axes.linewidth": 3.5,  # Much thicker lines
    "xtick.major.size": 10,
    "xtick.minor.size": 5,
    "ytick.major.size": 10,
    "ytick.minor.size": 5,
    "lines.linewidth": 4.5,  # Make lines much thicker
})
figsize = (12, 8)

# Read all CSV files in the current directory except FB.csv
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f != "FB.csv"]
print(f"Found CSV files: {csv_files}")

# Define distinct colors for different d values using a colormap
color_map = plt.get_cmap("tab10")  # Use tab10 for highly distinguishable colors
d_colors = {}

# Create figure
plt.figure(figsize=figsize)

# Store labels for a single legend
legend_labels = {}

# --- Load FB_stars.csv if it exists ---
fb_plotted = False
if "FB_stars.csv" in os.listdir('.'):
    try:
        fb_data = pd.read_csv("FB_stars.csv")

        # Ensure we have the correct columns
        if 'M' in fb_data.columns and 'R' in fb_data.columns:
            # (1) NEW: Convert M to Msun (if needed). Currently dividing by 1 => no change.
            #          If your FB data is already in Msun, keep as is or adjust accordingly.
            fb_data['M'] /= 1.0  

            # (2) NEW: Filter out any rows where M < 1.1 Msun
            fb_data = fb_data[fb_data['M'] >= 1.2].copy()
            fb_data.reset_index(drop=True, inplace=True)

            # If no data remains after filtering, skip plotting
            if len(fb_data) == 0:
                print("FB_stars.csv has no rows with M >= 1.1 Msun. Skipping FB plot.")
            else:
                # (3) Find the index of maximum mass in the filtered data
                fb_max_idx = fb_data['M'].idxmax()

                # Extract data for solid and dashed parts
                R_fb_solid, M_fb_solid = fb_data['R'][:fb_max_idx+1], fb_data['M'][:fb_max_idx+1]
                R_fb_dashed, M_fb_dashed = fb_data['R'][fb_max_idx:], fb_data['M'][fb_max_idx:]

                # Plot FB curve:
                plt.plot(R_fb_solid, M_fb_solid, color="gray", linewidth=7, label="FB", zorder=1)
                plt.plot(R_fb_dashed, M_fb_dashed, linestyle='dashed', color="gray", linewidth=7, zorder=6)

                # Mark maximum mass with a big dot in gray
                plt.scatter(
                    fb_data['R'][fb_max_idx],
                    fb_data['M'][fb_max_idx],
                    s=250, color="gray", edgecolor='black', zorder=7
                )

                fb_plotted = True

    except Exception as e:
        print(f"Error processing FB_stars.csv: {e}")

# --- Process all other CSV files ---
for file in csv_files:
    try:
        data = pd.read_csv(file)
        print(f"Reading {file}, columns: {data.columns.tolist()}")

        if 'M' in data.columns and 'R' in data.columns:
            # Extract d value using regex
            match = re.search(r'd(\d+\.\d+)', file)
            if match:
                d_value = float(match.group(1))
                print(f"Extracted d_value: {d_value} from {file}")
            else:
                print(f"Skipping file (failed to extract d value): {file}")
                continue

            # Assign distinct color to each d_value
            if d_value not in d_colors:
                d_colors[d_value] = color_map(len(d_colors) % 10)  # Ensure distinct colors

            # Normalize M by 1.4 Msun
            data['M'] /= 1.4

            # Find the index of maximum mass
            max_idx = data['M'].idxmax()
            print(f"File: {file}, Max M Index: {max_idx}, Max M Value: {data['M'][max_idx]}")

            # Extract data for solid and dashed parts
            R_solid, M_solid = data['R'][:max_idx+1], data['M'][:max_idx+1]
            R_dashed, M_dashed = data['R'][max_idx:], data['M'][max_idx:]

            # Define colors (use a slightly darker one for "hybrid" if needed)
            base_color = d_colors[d_value]
            darker_color = tuple(np.clip(np.array(base_color) * 0.7, 0, 1))

            # Determine whether this file is "stars.csv" or "hybrid stars.csv"
            if "stars.csv" in file:
                line_color = base_color
            else:
                line_color = darker_color

            # Plot solid curve (before maximum mass)
            plt.plot(R_solid, M_solid, color=line_color, zorder=3)

            # Plot dashed curve (after maximum mass)
            plt.plot(R_dashed, M_dashed, linestyle='dashed', color=line_color, zorder=3)

            # Mark maximum mass with a big dot
            plt.scatter(
                data['R'][max_idx],
                data['M'][max_idx],
                s=200, color=line_color, edgecolor='black', zorder=4
            )

            # Store a single label per d value for the legend
            if d_value not in legend_labels:
                legend_labels[d_value] = line_color

    except Exception as e:
        print(f"Error processing file {file}: {e}")

# --- Plot customization ---
plt.xlabel(r"$R\ [\mathrm{km}]$")
plt.ylabel(r"$M\ [M_{\odot}]$")
plt.xlim(0, 20)
plt.grid(True)

# --- Create a single legend ---
legend_handles = [
    plt.Line2D([0], [0], color=color, lw=6, label=f"$\\eta_D={d_value}$")
    for d_value, color in legend_labels.items()
]
if fb_plotted:
    legend_handles.append(
        plt.Line2D([0], [0], color="gray", lw=7, label="FB")
    )

plt.legend(handles=legend_handles, loc="best", fontsize=22)

# --- Save and show the figure ---
plt.savefig("MR_curves.pdf", bbox_inches='tight')
plt.show()
