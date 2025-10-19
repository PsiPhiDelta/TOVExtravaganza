# 🌟 TOV Extravaganza

**Python Toolkit for Neutron Star Physics: Solve TOV Equations, Calculate Tidal Deformability, and Explore Neutron Star Properties**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/tovextravaganza.svg)](https://badge.fury.io/py/tovextravaganza)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-2411.04064-b31b1b.svg)](https://arxiv.org/abs/2411.04064)
[![Downloads](https://pepy.tech/badge/tovextravaganza)](https://pepy.tech/project/tovextravaganza)

**TOV Extravaganza** is a comprehensive Python package for astrophysicists and researchers studying neutron stars, compact objects, and gravitational wave astronomy. Solve the Tolman-Oppenheimer-Volkoff (TOV) equations, compute tidal deformabilities for binary neutron star mergers, generate detailed radial profiles of neutron star interiors, and explore the Mass-Radius relationship for different equations of state (EoS).

---

## Features

- **Interactive Wizard** – Beginner-friendly guided workflow (just answer questions!)
- **Mass-Radius Calculations** – Solve TOV equations for multiple central pressures
- **Tidal Deformability** – Compute dimensionless tidal deformability (Λ) and Love number (k₂)
- **Batch Processing** 🚀 **NEW!** – Process multiple EOS files in parallel:
  - **Converter Batch**: Convert all raw EOS files with any columns preserved
  - **TOV Batch**: Compute M-R curves for multiple EOS simultaneously  
  - **Radial Batch**: Generate radial profiles for multiple EOS in parallel
- **Radial Profiles** – Generate detailed internal structure profiles with M-R context
- **Target-Specific Profiles** – Find stars by exact mass or radius values
- **EOS Converter** – Convert raw equation of state data into TOV code units (preserves all columns!)
- **Clean Output** – Organized export structure with CSV data and publication-ready plots

---


## 📂 Project Structure

```
TOVExtravaganza/
├── tovextravaganza/             # Main package
│   ├── core/                    # Core logic (reusable classes)
│   │   ├── eos.py               # EOS interpolation
│   │   ├── tov_solver.py        # TOV equation solver
│   │   ├── tidal_calculator.py  # Tidal deformability
│   │   └── output_handlers.py   # Output writers
│   ├── cli/                     # Command-line tools
│   │   ├── tov.py               # TOV solver CLI
│   │   ├── radial.py            # Radial profiler CLI
│   │   └── converter.py         # EOS converter CLI
│   └── utils/                   # Utilities
│       ├── wizard.py            # Interactive wizard
│       ├── demo.py              # Demo file downloader
│       └── help_command.py      # Help command
│
├── inputRaw/                    # Raw EOS data files
├── inputCode/                   # Converted EOS (code units)
│
├── export/                      # All output goes here!
│   ├── stars/                   # TOV + Tidal results
│   │   ├── csv/                 # M-R + Tidal data
│   │   └── plots/               # M-R curves, Λ(M), k₂(M)
│   └── radial_profiles/         # Internal structure
│       ├── json/                # Detailed radial data
│       └── plots/               # M(r) and p(r) plots
│
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Easiest!)

**Global Install:**
```bash
pip install tovextravaganza
```

**Or in a Virtual Environment (Recommended):**
```bash
python -m venv tovenv
source tovenv/bin/activate    # Linux/Mac, or tovenv\Scripts\activate on Windows
pip install tovextravaganza
```

> **⚠️ Important:** If using a venv, activate it before using any `tovx` commands!

This installs the package with console commands: `tovx`, `tovx-radial`, `tovx-converter`, `tovx-wizard`, `tovx-demo`, `tovextravaganza`

#### Option 2: Install from Source (For Development)

```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
pip install -e .
```

The `-e` flag installs in editable mode - any code changes take effect immediately without reinstalling.

### Workflow 1: Interactive Wizard (Easiest - Recommended!)

**Perfect for first-time users!** The wizard guides you through everything:

**If installed via pip:**
```bash
tovx-demo        # Get example files
tovx-wizard      # Run the wizard
```

**If using source/cloned repository:**
```bash
python -m tovextravaganza.tov_wizard
```

The wizard will:
- 🔍 Auto-detect your EOS files
- ❓ Ask simple questions (no expertise needed!)
- 🚀 Run everything for you
- 📊 Show you exactly where results are
- 🎉 Celebrate your success!

**Oh boy oh boy, so easy!**

### Workflow 2: Command-Line (For Power Users!)

**If installed via pip:**
```bash
tovx-demo                              # Get example files
tovx inputCode/hsdd2.csv              # Compute M-R + Tidal
tovx-radial inputCode/hsdd2.csv -M 1.4  # Radial profile for 1.4 M☉
tovx-converter                         # Convert EOS units
```

**If using source/cloned repository:**
```bash
python -m tovextravaganza.tov inputCode/hsdd2.csv
python -m tovextravaganza.radial inputCode/hsdd2.csv -M 1.4
python -m tovextravaganza.converter
```

**That's it!** Results appear in the `export/` folder.

---

## 📚 Complete Tutorial: DD2 Equation of State

This tutorial shows the **complete workflow** from raw EOS data to publication-quality results using the HS(DD2) equation of state as an example.

### Step 0: Get Example Files

First, download the demo EOS files:

```bash
# Via pip
tovx-demo

# From source
python -m tovextravaganza.utils.demo
```

This downloads example files including `hsdd2.csv` to both `inputRaw/` and `inputCode/` directories.

### Step 1: Convert Raw EOS to Code Units

**Input:** `inputRaw/hsdd2.csv` - Raw EOS in CGS units (g/cm³ and dyn/cm²)

**Goal:** Convert to dimensionless TOV code units

```bash
# Via pip
tovx-converter inputRaw/hsdd2.csv -o inputCode/hsdd2.csv

# From source
python -m tovextravaganza.cli.converter inputRaw/hsdd2.csv -o inputCode/hsdd2.csv
```

**What happens:**

The converter will analyze your file and ask:
```
Which column is PRESSURE? (1-based index): 2
Which column is ENERGY DENSITY? (1-based index): 1
Which unit system?
  1) MeV^-4
  2) MeV*fm^-3
  3) fm^-4
  4) CGS (g/cm^3, dyn/cm^2)
Select (1-4): 4
```

After confirmation, it converts the file and saves to `inputCode/hsdd2.csv`.

**Features:**
- Automatically preserves ALL additional columns (number density, chemical potential, etc.)
- Adds header comment showing conversion factors
- Reorders columns: pressure and energy first (converted), then rest (preserved)

### Step 2: Compute Mass-Radius Sequence & Tidal Deformability

**Goal:** Solve TOV equations for 200 neutron stars with different central pressures

```bash
# Via pip
tovx inputCode/hsdd2.csv -n 200

# From source
python -m tovextravaganza.cli.tov inputCode/hsdd2.csv -n 200
```

**Output:**
- **CSV:** `export/stars/csv/hsdd2.csv` containing:
  - Central pressure `p_c`
  - Radius `R` [km]
  - Mass `M_solar` [M☉]
  - Tidal deformability `Lambda` (dimensionless)
  - Love number `k2`
  - Any additional central columns from the EOS
- **Plots:** `export/stars/plots/hsdd2.pdf` (and `.png` if using `--save-png`)

**Example plot:**

![Mass-Radius Plot](export/stars/plots/hsdd2.png)

The plot shows three panels:
- **Left:** Mass-Radius relationship
- **Middle:** Tidal deformability Λ(M) with GW170817 constraint
- **Right:** Love number k₂(M)

### Step 3: Generate Internal Structure Profiles

**Goal:** Get detailed radial profiles showing the star's interior from center to surface

```bash
# Via pip
tovx-radial inputCode/hsdd2.csv -M 1.4

# From source
python -m tovextravaganza.cli.radial inputCode/hsdd2.csv -M 1.4
```

**What happens:**
1. Searches for the star closest to 1.4 M☉
2. Computes full radial profile: M(r), p(r), ε(r), n(r), etc.
3. Saves all data to HDF5 format
4. Generates plots with M-R context

**Output:**
- **Data:** `export/radial_profiles/json/hsdd2.h5` (HDF5 format - efficient binary)
- **Plots:** Two PDFs (and `.png` if using `--save-png`):

**Mass Profile:**

![Mass Profile](export/radial_profiles/plots/Mass/mass_profile_0.png)

**Pressure Profile:**

![Pressure Profile](export/radial_profiles/plots/Pressure/pressure_profile_0.png)

Each plot:
- **Left Panel:** Radial profile from center to surface
- **Right Panel:** Full M-R curve with ⭐ marking this star's position

---

## 🚀 Batch Processing Tutorial: Multiple EOS Files

Process **multiple EOS files in parallel** for high-throughput analysis.

### Scenario: Analyze 6 Quark Matter EOS Models

You have 6 raw EOS files in `inputRaw/Batch/` with different parameters (CSC and RGNJL series). Let's process them all efficiently.

### Step 1: Batch Convert to Code Units

Convert all 6 files simultaneously:

```bash
# Via pip
tovx-converter --batch inputRaw/Batch/ --pcol 2 --ecol 1 --system 3 --workers 6

# From source
python -m tovextravaganza.cli.converter --batch inputRaw/Batch/ --pcol 2 --ecol 1 --system 3 --workers 6
```

**Parameters:**
- `--pcol 2`: Pressure is in column 2
- `--ecol 1`: Energy density is in column 1  
- `--system 3`: Units are fm⁻⁴
- `--workers 6`: Use 6 parallel workers

**Result:** All files converted to `inputCode/Batch/` in ~2-5 seconds

### Step 2: Batch Compute M-R Curves

Compute M-R sequences for all 6 EOS files:

```bash
# Via pip
tovx --batch inputCode/Batch/ -n 1000 -o export/batch_all --workers 6

# From source
python -m tovextravaganza.cli.tov --batch inputCode/Batch/ -n 1000 -o export/batch_all --workers 6
```

**Output:**
- 6 CSV files with ~250-1000 stars each (R < 99 km filter)
- 6 sets of M-R, Λ(M), k₂(M) plots
- Completed in ~30-60 seconds (parallel processing!)

**Results Summary:**
```
CSC_v0.70d1.45   => M_max = 1.94 M☉
CSC_v0.80d1.50   => M_max = 2.08 M☉
CSC_v0.85d1.50   => M_max = 2.11 M☉
RGNJL_v0.70d1.45 => M_max = 2.06 M☉
RGNJL_v0.80d1.50 => M_max = 2.09 M☉
RGNJL_v0.85d1.50 => M_max = 2.19 M☉
```

### Step 3: Batch Radial Profiles at Maximum Mass

Generate internal structure profiles at M_max for all 6 EOS:

```bash
# Via pip
tovx-radial --batch inputCode/Batch/ --max-mass -o export/radial_maxmass --workers 6

# From source
python -m tovextravaganza.cli.radial --batch inputCode/Batch/ --max-mass -o export/radial_maxmass --workers 6
```

**What happens:**
1. Each EOS: Fast M_max search (50 coarse + 200 fine = 250 TOV solves)
2. Finds M_max with precision < 0.01 M☉
3. Computes full radial profile with all EOS columns
4. Generates M(r) and p(r) plots with M-R context
5. Saves to HDF5 format (efficient!)

**Output:**
- 6 HDF5 files in `export/radial_maxmass/*/json/*.h5`
- 12 plots (Mass and Pressure profiles for each EOS)
- **Total time: ~30 seconds** for all 6 files in parallel!

**Example result:** RGNJL v0.70 at M_max = 2.06 M☉, R = 12.44 km

---

## 🎨 Showcase

### Getting Started (First Time Users)

**Via pip (easiest):**
```bash
pip install tovextravaganza
tovx-demo        # Get example files
tovx-wizard      # Guided workflow
```

**From source:**
```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
pip install -e .
tovx-wizard
```

**That's it!** The wizard does everything for you!

---

## 🚀 Batch Processing Mode – Process Multiple Files in Parallel

**NEW!** All TOVExtravaganza tools now support batch processing to analyze multiple EOS files simultaneously using parallel workers.

### Overview

Process entire directories of EOS files with a single command:
- **Converter Batch**: Convert all raw EOS files to code units
- **TOV Batch**: Compute M-R curves for all EOS files
- **Radial Batch**: Generate radial profiles for all EOS files

### 1. Converter Batch – Convert Multiple EOS Files

Convert all raw EOS files in a directory with proper unit conversion.

**Interactive Mode** (prompts for columns and units if not provided):
```bash
# Via pip
tovx-converter --batch inputRaw/

# From source
python -m tovextravaganza.converter --batch inputRaw/
```

**Non-Interactive Mode** (all parameters specified):
```bash
# Via pip
tovx-converter --batch inputRaw/ --pcol 2 --ecol 1 --system 3  # fm^-4

# From source  
python -m tovextravaganza.converter --batch inputRaw/ --pcol 2 --ecol 3 --system 4 --workers 4
```

**Features:**
- 🎯 **Interactive prompts** when parameters not provided
- 📁 **Auto-creates** `inputCode/Batch/` for batch folders
- ⚙️ **Parallel processing** for multiple files
- ✅ Preserves ALL additional columns (mu, n, temperature, phase labels, etc.)
- ✅ Maintains header tags with "(code_units)" annotations
- ✅ Reorders columns: p & e first (converted), then rest (preserved)

**Example Output:**
```
======================================================================
BATCH CONVERTER MODE - oh boy oh boy!
======================================================================
Found 3 CSV files in inputRaw
Processing with 2 parallel workers

Processed 3 files in 0.60 seconds
  ✓ Successful: 3

csc.csv      => 1042 lines (MeV^-4 => code)
hsdd2.csv    =>  401 lines (CGS => code)
test.csv     =>  500 lines (Already code)
======================================================================
```

### 2. TOV Batch – Mass-Radius Sequences for Multiple EOS

Compute M-R curves and tidal deformability for all EOS files in parallel.

**Via pip:**
```bash
# Process all CSV files in a directory
tovx --batch inputCode/

# Specify number of workers and stars
tovx --batch inputCode/ --workers 4 -n 500
```

**From source:**
```bash
python -m tovextravaganza.tov --batch inputCode/ --workers 8 -n 200
```

**Example Output:**
```
======================================================================
BATCH PROCESSING MODE - oh boy oh boy!
======================================================================
Found 3 CSV files in inputCode
Processing with 24 parallel workers

Processed 3 files in 16.15 seconds
  ✓ Successful: 3

csc                  =>  149 solutions, Max M = 1.1186 Msun
hsdd2                =>  151 solutions, Max M = 2.4229 Msun
test                 =>  140 solutions, Max M = 1.8730 Msun
======================================================================
```

### 3. Radial Batch – Internal Profiles for Multiple EOS

Generate radial profiles for all EOS files in parallel.

**Via pip:**
```bash
# Process all files in a directory
tovx-radial --batch inputCode/

# Custom number of profiles and workers
tovx-radial --batch inputCode/ -n 10 --workers 4
```

**From source:**
```bash
python -m tovextravaganza.radial --batch inputCode/ -n 5 --workers 2
```

**Output Structure:**
```
export/radial_profiles/
├── csc/
│   ├── json/
│   └── plots/
├── hsdd2/
│   ├── json/
│   └── plots/
└── test/
    ├── json/
    └── plots/
```

### Performance Benefits

- **Parallel Processing**: Uses all CPU cores by default (configurable with `--workers`)
- **Time Savings**: ~45% faster with 2 workers, scales with more cores
- **Robust Error Handling**: Individual file failures don't stop the batch
- **Organized Output**: Each EOS gets its own folder (for radial profiles)

### Common Options

All batch modes support:
- `--batch <directory>`: Directory containing CSV files
- `--workers <N>`: Number of parallel workers (default: CPU count)
- `-o, --output <dir>`: Output directory
- `-n, --num-stars <N>`: Number of stars/profiles (TOV & radial)

### Complete Workflow Example

```bash
# Step 1: Convert all raw EOS files to code units
tovx-converter --batch inputRaw/ --system 2 --workers 4

# Step 2: Compute M-R sequences for all converted EOS
tovx --batch inputCode/ -n 200 --workers 8

# Step 3: Generate radial profiles for all EOS
tovx-radial --batch inputCode/ -n 10 --workers 8
```

---

## 📖 Usage Guide

### 1. tov.py – Mass-Radius & Tidal Deformability

**The main workhorse.** Solves TOV equations and computes tidal properties for a sequence of neutron stars.

#### Simple Usage

**Via pip:**
```bash
tovx inputCode/hsdd2.csv           # 200 stars (default)
tovx inputCode/test.csv -n 500     # 500 stars
```

**From source:**
```bash
python -m tovextravaganza.tov inputCode/hsdd2.csv
python -m tovextravaganza.tov inputCode/test.csv -n 500
```

#### Advanced Options

**Via pip:**
```bash
tovx inputCode/hsdd2.csv -n 1000 --dr 0.0001 --quiet --no-show
```

**From source:**
```bash
python -m tovextravaganza.tov inputCode/hsdd2.csv \
    -n 1000 \                               # Number of stars
    -o export/my_stars \                    # Custom output folder
    --dr 0.0001 \                           # Radial step size
    --rmax 50 \                             # Maximum radius
    --rmax-plot 15 \                        # 🌟 NEW! Zoom M-R plot to R ≤ 15 km (default: 20)
    --timeout 20 \                          # 🌟 NEW! Abort stars taking > 20s (default: 10s)
    --quiet \                               # Suppress progress messages
    --no-plot \                             # Skip plot generation
    --no-show                               # Don't display plot (still saves)
```

#### Output

**CSV:** `export/stars/csv/<eos_name>.csv`
```
p_c,R,M_code,M_solar,Lambda,k2
0.00010000,12.34,0.123,0.543,789.12,0.098
0.00015000,11.89,0.156,0.689,456.78,0.087
...
```

**Plots:** `export/stars/plots/<eos_name>.pdf`
- Mass-Radius relationship
- Λ vs M (tidal deformability)
- k₂ vs M (Love number)

#### Example Output

For HS(DD2) EOS:
- **Maximum Mass:** ~2.42 M☉
- **Λ @ 1.4 M☉:** ~705 (dimensionless)
- **Radius @ 1.4 M☉:** ~13.26 km

---

### 2. radial.py – Internal Structure Profiles

**Get detailed profiles** of mass, pressure, and energy density from center to surface.


#### Usage

**Via pip:**
```bash
# Generate profiles across pressure range
tovx-radial inputCode/hsdd2.csv           # 10 profiles (default)
tovx-radial inputCode/test.csv -n 20      # 20 profiles

# Generate profiles for specific mass/radius
tovx-radial inputCode/hsdd2.csv -M 1.4          # Star closest to 1.4 M☉
tovx-radial inputCode/hsdd2.csv -R 12.0         # Star closest to 12 km
tovx-radial inputCode/hsdd2.csv -M 1.4 -M 2.0   # Multiple masses
tovx-radial inputCode/hsdd2.csv -M 1.4 -R 12    # By mass AND radius

# 🌟 NEW! Generate profile at maximum mass
tovx-radial inputCode/hsdd2.csv --max-mass      # Finds M_max automatically (precision < 0.01 M☉)
```

**From source:**
```bash
# Generate profiles across pressure range
python -m tovextravaganza.radial inputCode/hsdd2.csv           # 10 profiles (default)
python -m tovextravaganza.radial inputCode/test.csv -n 20      # 20 profiles

# Generate profiles for specific mass/radius
python -m tovextravaganza.radial inputCode/hsdd2.csv -M 1.4          # Star closest to 1.4 M☉
python -m tovextravaganza.radial inputCode/hsdd2.csv -R 12.0         # Star closest to 12 km
python -m tovextravaganza.radial inputCode/hsdd2.csv -M 1.4 -M 2.0   # Multiple masses
python -m tovextravaganza.radial inputCode/hsdd2.csv -M 1.4 -R 12    # By mass AND radius

# 🌟 NEW! Generate profile at maximum mass
python -m tovextravaganza.radial inputCode/hsdd2.csv --max-mass      # Finds M_max automatically (precision < 0.01 M☉)
```

#### Advanced Options

**NEW features in v1.4.2+:**

```bash
# Control plot viewport (doesn't crop data)
tovx-radial inputCode/hsdd2.csv --rmax-plot 15   # M-R diagrams show only R ≤ 15 km

# Set timeout for stuck calculations
tovx-radial inputCode/hsdd2.csv --timeout 20     # Abort stars taking > 20s (default: 10s)

# Batch process all EOS files at M_max
tovx-radial --batch inputCode/Batch/ --max-mass  # Parallel M_max profiles
```

#### Output

**HDF5 (default):** `export/radial_profiles/json/<eos_name>.h5`  
- **10-100x smaller** than JSON (binary + compression)
- Fast read/write for large datasets
- Standard scientific format (Python, MATLAB, Julia, R)
- Requires: `pip install tovextravaganza[hdf5]` or `pip install h5py`

**Fallback JSON:** `export/radial_profiles/json/<eos_name>.json`  
- Used if h5py not installed
- Human-readable but large files
```json
{
  "stars": [
    {
      "p_c": 0.001,
      "R": 12.34,
      "M": 0.543,
      "radial_data": {
        "r": [0.0, 0.001, 0.002, ...],
        "M": [0.0, 0.0001, 0.0003, ...],
        "p": [0.001, 0.0009, 0.0008, ...],
        "e": [0.05, 0.049, 0.048, ...]
      }
    }
  ]
}
```

**Plots:** `export/radial_profiles/plots/`
- `Mass/mass_profile_N.pdf` – M(r) vs r
- `Pressure/pressure_profile_N.pdf` – p(r) vs r

---

### 3. converter.py – EOS Unit Converter

**Sick of unit conversion? I was too.** This tool converts raw EOS data into TOV code units.

#### Interactive Mode

**Via pip:**
```bash
tovx-converter
```

**From source:**
```bash
python -m tovextravaganza.converter
```

The script will guide you through:
1. Selecting input file from `inputRaw/`
2. Specifying if the file has a header
3. Identifying pressure and energy density columns
4. Choosing the unit system (MeV fm⁻³, CGS, etc.)

#### CLI Mode

**Via pip:**
```bash
tovx-converter <input_file> <pcol> <ecol> <system> [output_file]
```

**From source:**
```bash
python -m tovextravaganza.converter <input_file> <pcol> <ecol> <system> [output_file]
```

**Example:**
```bash
# Via pip
tovx-converter hsdd2.csv 2 3 4 inputCode/hsdd2.csv

# From source
python -m tovextravaganza.converter hsdd2.csv 2 3 4 inputCode/hsdd2.csv
```

**Parameters:**
- `<input_file>`: Filename in `inputRaw/` folder
- `<pcol>`: Pressure column (1-based index)
- `<ecol>`: Energy density column (1-based index)
- `<system>`: Unit system choice (0-4, see table below)
- `[output_file]`: Optional output path (default: `inputCode/<input_file>`)

**Output:** Converted file saved to `inputCode/` with columns rearranged as `[p, e, ...]`

#### Supported Unit Systems

| System | Pressure Units | Energy Density Units |
|--------|---------------|----------------------|
| 0 | Code units | Code units |
| 1 | MeV⁻⁴ | MeV⁻⁴ |
| 2 | MeV·fm⁻³ | MeV·fm⁻³ |
| 3 | fm⁻⁴ | fm⁻⁴ |
| 4 | CGS (dyn/cm²) | CGS (erg/cm³) |

---

## 📊 Understanding the Physics

### TOV Equations

The Tolman-Oppenheimer-Volkoff equations describe hydrostatic equilibrium in general relativity:

```
dM/dr = 4πr²ε(r)
dp/dr = -(ε + p)(M + 4πr³p) / (r(r - 2M))
```

Solved in dimensionless "code units" where G = c = M☉ = 1.

### Tidal Deformability

The dimensionless tidal deformability Λ characterizes how a neutron star deforms under tidal forces:

```
Λ = (2/3) k₂ (c²R/GM)⁵
```

where k₂ is the second Love number, obtained by solving a coupled ODE system with TOV.

#### Love Number k₂ Calculation

The tidal perturbation is governed by:

```
dy/dr = -(2/r)y - y² - y·F(r) + r²·Q(r)
dH/dr = y
```

where:
- `y(r) = r·dH/dr / H(r)` is the logarithmic derivative
- `H(r)` is the metric perturbation function
- `F(r) = (1 - 2M(r)/r)⁻¹ · [2M(r)/r² + 4πr(p(r) - ε(r))]`
- `Q(r) = (1 - 2M(r)/r)⁻¹ · [4π(5ε(r) + 9p(r) + (ε(r) + p(r))·(dε/dp)) - 6/r² - (2M(r)/r² + 4πr(p(r) - ε(r)))²]`

The Love number k₂ is then extracted at the surface (r = R):

```
k₂ = (8/5) C⁵ (1-2C)² [2C(y_R - 1) - y_R + 2] / {2C[4(y_R + 1)C⁴ + (6y_R - 4)C³ + (26 - 22y_R)C² + 3(5y_R - 8)C - 3y_R + 6] - 3(1-2C)²[2C(y_R - 1) - y_R + 2]ln(1-2C)}
```

where `C = GM/(c²R)` is the compactness and `y_R = y(R)`.


---

## 🎨 Example Showcase

### Mass-Radius Curves

Using HS(DD2) EOS, we compute 200 neutron star configurations:

```bash
python -m tovextravaganza.tov inputCode/hsdd2.csv
```

**Result:** The M-R curve shows:
- Stable branch reaching M_max ≈ 2.42 M☉
- Typical 1.4 M☉ star has R ≈ 13.26 km
- Tidal deformability Λ(1.4 M☉) ≈ 705

### Internal Structure

For a 1.4 M☉ star:

```bash
python -m tovextravaganza.radial inputCode/hsdd2.csv -n 10
```

**Result:** Radial profiles reveal:
- Central pressure: ~10¹⁵ g/cm³
- Pressure drops by ~6 orders of magnitude to surface
- Mass accumulates mostly in inner 10 km

---

## 🛠️ Technical Details

### Code Units

All calculations use **geometric units** where G = c = 1:

#### Internal (Code) Units:
- **Radius**: km
- **Mass**: km (geometric units, where **1 M☉ = 1.4766 km**)
- **Pressure**: dimensionless code units
- **Energy density**: dimensionless code units

#### Output Units (for display):
- **tov.py**: Converts M to M☉ in output CSV and plots
- **radial.py**: Shows M(r) in M☉, p(r) in MeV/fm³, r in km

#### Conversion Factors:
- **M [M☉] = M [km] / 1.4766**
- **p [MeV/fm³] = p [code] / 1.32379×10⁻⁶**
- **ε [MeV/fm³] = ε [code] / 1.32379×10⁻⁶**

### Numerical Methods

- **ODE Integration:** `scipy.integrate.odeint` with rtol=1e-12, atol=1e-14
- **EOS Interpolation:** Piecewise-linear
- **Division-by-zero handling:** Small epsilon added to denominator (1e-30)
- **Boundary conditions:** Start integration at r=1e-5 to avoid r=0 singularity

### Filtering

The code automatically filters out unphysical solutions:
- Stars that hit maximum radius (R = 100 km)
- Low-mass configurations (M < 0.05 M☉)

---

## 📝 File Formats

### Input EOS File (inputCode/)

CSV format, no header, columns: `p, e, ...`

```
0.00010000,0.00050000
0.00012000,0.00058000
...
```

### Output CSV (export/stars/csv/)

Header row with columns: `p_c, R, M_code, M_solar, Lambda, k2`

```
p_c,R,M_code,M_solar,Lambda,k2
0.00010000,12.34,0.123,0.543,789.12,0.098
...
```

### Output JSON (export/radial_profiles/json/)

Structured JSON with full radial arrays for each star.

---

## ⚙️ Command Reference

### tov.py

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `input` | positional | required | Input EOS file path |
| `-n, --num-stars` | int | 200 | Number of stars to compute |
| `-o, --output` | str | export/stars | Output folder |
| `--dr` | float | 0.0005 | Radial step size |
| `--rmax` | float | 100.0 | Maximum radius |
| `--quiet` | flag | False | Suppress output |
| `--no-plot` | flag | False | Skip all plots |
| `--no-show` | flag | False | Don't display plot window |

### radial.py

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `input` | positional | required | Input EOS file path |
| `-n, --num-stars` | int | 10 | Number of profiles |
| `-o, --output` | str | export/radial_profiles | Output folder |

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** `ValueError: not enough values to unpack`
- **Solution:** Check that your EOS file has at least 2 columns (p, e)

**Problem:** `ODEintWarning: Excess work done on this call`
- **Solution:** Reduce `--dr` or check for discontinuities in your EOS

**Problem:** All masses are zero
- **Solution:** Your EOS might be too soft or in wrong units. Run `converter.py` first.

**Problem:** UnicodeEncodeError in terminal output
- **Solution:** Set environment variable: `PYTHONIOENCODING=utf-8`




---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please maintain the code style and add tests where appropriate.

---

## 📚 References

### Key Papers

1. **Tolman (1939):** Static Solutions of Einstein's Field Equations
2. **Oppenheimer & Volkoff (1939):** On Massive Neutron Cores
3. **Damour & Nagar (2009):** Relativistic tidal properties of neutron stars
4. **Abbott et al. (2017):** GW170817: Observation of Gravitational Waves from a Binary Neutron Star Inspiral

### EOS Databases

- **CompOSE:** https://compose.obspm.fr/
- **stellarcollapse.org:** Comprehensive EOS tables
- **RG-NJL EoS Tables (Color-Superconducting Quark Matter):** https://github.com/marcohof/RG-NJL-EoS-tables

---

## 📸 Research Showcase

### Quark Matter Phase Transitions in Neutron Stars

**M-R curves from our research** on hybrid stars with color-superconducting quark matter:

![M-R Curves Showcase](export/all_mr_curves.png)

*Six EOS models showing quark matter phase transitions (CSC and RGNJL series). Solid lines: CSC models; Dashed lines: RGNJL models with hadronic cores. Maximum mass predictions: 1.94 - 2.19 M☉. From arXiv:2411.04064.*

### Internal Structure of Maximum Mass Stars

**Phase-resolved radial profiles at M_max** showing the internal structure from center to surface:

![Phase-Coded Radial Profiles at M_max](export/radial_plots/RGNJL_v0.70d1.45_radial_profiles.png)

*Maximum mass star (M_max = 2.06 M☉, R = 12.44 km) for RGNJL v0.70 EOS. Shows Hadronic → 2SC → CFL phase transitions from center to surface. Top-left: Mass profile M(r). Top-right: Pressure p(r) [MeV/fm³]. Bottom-left: Energy density ε(r) [MeV/fm³]. Bottom-right: Number density n(r) [fm⁻³]. Phase color-coding: Blue=Hadronic, Orange=2SC, Red=CFL.*

---

## 📧 Contact

**Author:** Hosein Gholami  
**Website:** [hoseingholami.com](https://hoseingholami.com/)  
**Email:** [mohogholami@gmail.com](mailto:mohogholami@gmail.com)  
**GitHub:** [TOVExtravaganza](https://github.com/yourusername/TOVExtravaganza)

Questions? Suggestions? Found a bug? Don't hesitate to reach out or open an issue!

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 📖 Citation

If you use **TOV Extravaganza** in your research, please cite this repository and our work on arXiv:

```bibtex
@software{Gholami_TOVExtravaganza_Python_toolkit_2025,
  author = {Gholami, Hosein},
  license = {MIT},
  month = jan,
  title = {{TOVExtravaganza: Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and exploring neutron star properties}},
  url = {https://github.com/PsiPhiDelta/TOVExtravaganza},
  version = {1.0.0},
  year = {2025}
}

@article{Gholami:2024csc,
  author = "Gholami, Hosein and Rather, Ishfaq Ahmad and Hofmann, Marco and Buballa, Michael and Schaffner-Bielich, J{\"u}rgen",
  title = "{Astrophysical constraints on color-superconducting phases in compact stars within the RG-consistent NJL model}",
  eprint = "2411.04064",
  archivePrefix = "arXiv",
  primaryClass = "hep-ph",
  month = "11",
  year = "2024"
}
```

**arXiv:** [2411.04064](https://arxiv.org/abs/2411.04064)

---

## 🎉 Acknowledgments

Thanks to the astrophysics and gravitational wave communities for making neutron star science accessible and exciting.

**Oh boy oh boy!** May your neutron stars be massive and your convergence ever stable! 🌟

---

*Built with Python, NumPy, SciPy, and a healthy dose of enthusiasm for compact objects.*


## 🔑 Keywords

`neutron-star` `neutron-stars` `tov` `tov-equation` `tov-equations` `tidal-deformability` `gravitational-waves` `astrophysics` `equation-of-state` `eos` `python-physics` `astronomy` `compact-objects` `GW170817` `nuclear-astrophysics` `nuclear-physics` `mass-radius` `love-number` `relativistic-stars` `color-superconductivity` `superconductivity` `csc` `cfl` `quark-matter` `dense-matter` `phase-transitions` `qcd` `binary-neutron-stars` `ligo` `virgo` `general-relativity` `stellar-structure` `computational-physics` `scientific-computing`

---