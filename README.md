# 🌀 TOV Extravaganza! 🌀

Welcome to **TOV Extravaganza**, your Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and exploring neutron star properties. **Oh boy oh boy!**

## 📂 Folder Structure

```
TOV-Extravaganza/
├── inputRaw/          # Your raw EOS CSV files
├── inputCode/         # Converted EOS CSV files in TOV "code units"
├── MR/                # Mass-Radius solutions and plots
├── plotting/
│   └── radial/
│       ├── Mass/      # PDF plots of Mass vs. Radius
│       └── Pressure/  # PDF plots of Pressure vs. Radius
├── radial.py          # Script to solve TOV for multiple stars
├── converter.py       # Core EOS converter to TOV "code units"
├── tov.py             # Core TOV solver for Mass-Radius analysis
├── README.md          # This README file
└── .gitignore         # Git ignore file
```

## 💻 Usage

### 1. Convert EOS Data

Sick of unit conversion? I was too. Run the `converter.py` script to convert your raw EOS data into TOV "code units":

```bash
python3 converter.py
```

*This script will prompt you to select your input file from the `inputRaw/` folder and ask a series of questions to determine the appropriate conversion factors. The converted files will be saved in the `inputCode/` directory with the same name as the input file.*

### 2. Perform Mass-Radius Analysis

Run the `tov.py` script to compute Mass-Radius relationships for a series of central pressures:

```bash
python3 tov.py
```

This script will:

- Read the EOS data from `inputCode/`.
- Solve the TOV equations for a specified number of stars.
- Store the results (central pressure, radius, mass, and interpolated properties) in the `MR/` folder as a CSV file.
- Generate a Mass-Radius plot and save it as a PDF in the same folder.

### 3. Solve the TOV Equations

Run the `radial.py` script to solve the TOV equations:

```bash
python3 radial.py
```

This script will:

- Read the converted EOS data from `inputCode/`.
- Solve the TOV equations for a range of central pressures.
- Store radial profiles in `radial/metadata.txt` and `radial/<inputfilename>.json`.
- Generate PDF plots in `plotting/radial/Mass/` and `plotting/radial/Pressure/`.

### 4. Understand the Python Scripts

- **`converter.py`**: Converts raw EOS data into TOV "code units." It asks you to:
  - Select a file from `inputRaw/`.
  - Specify pressure and energy density columns.
  - Choose a unit system for conversion.
  - Automatically rearrange columns in the output file for compatibility.

- **`tov.py`**: Computes Mass-Radius relationships for multiple stars. It:
  - Interpolates all columns at the central pressure of each star.
  - Writes the results (one row per star) into a CSV file.
  - Generates a Mass-Radius plot for easy visualization and a quick check.

- **`radial.py`**: Reads the converted EOS data, solves the TOV equations for various central pressures, interpolates data across all relevant columns, and outputs the results as human-readable files, structured JSON, and plots.

## 📊 Output Explained

### Metadata Files

- **`radial/metadata.txt`**: Human-readable radial profiles.
- **`radial/<inputfilename>.json`**: Structured JSON data for each star.

### Mass-Radius Data

- **`MR/<inputfilename>_stars.csv`**: Contains rows for each star with columns:
  - Central pressure (`p_c`), radius (`R`), mass (`M`), and interpolated values for all other columns in the EOS.

- **`MR/<inputfilename>.pdf`**: A Mass-Radius plot showing the relationship across all solutions.

### Plots

- **Mass Profiles**: `plotting/radial/Mass/` contains PDFs showing how mass accumulates with radius.
- **Pressure Profiles**: `plotting/radial/Pressure/` contains PDFs displaying pressure decline from core to crust.

## 🧰 Troubleshooting

### ⚠️ Common Errors

- **`ValueError: not enough values to unpack (expected 5, got 2)`**
  - *Solution*: Ensure `solve_tov` in `radial.py` or `tov.py` is receiving the correct EOS data and returning `r_vals, M_sol, p_sol, R, M`.

- **`ODEintWarning: Excess work done on this call`**
  - *Solution*: Tweak `DR` (radial step size) or check your EOS data for consistency.

## 🖋️ Contribution

Feel free to fork the repository, make your changes, and submit a pull request. We'll review it with a hearty "Oh boy oh boy, great job!"

## 📢 Contact

Have questions or suggestions? Reach out at [mohogholami@gmail.com](mailto:mohogholami@gmail.com).

## 🏦 License

This project is licensed under the MIT License. Feel free to use, modify, and share it with your fellow science enthusiasts!

---

**Oh boy oh boy!** Thanks for checking out **TOV Extravaganza**. May your neutron stars be massive and your plots ever clear! 🌟

