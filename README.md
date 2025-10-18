# 🌟 TOV Extravaganza

Welcome to **TOV Extravaganza**, your Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and exploring neutron star properties. **Oh boy oh boy!**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Solve TOV equations, compute tidal deformabilities, generate radial profiles, and explore the Mass-Radius relationship of neutron stars, all with a streamlined command-line interface.

---

## ✨ Features

- **Interactive Wizard** 🧙‍♂️ – Beginner-friendly guided workflow (just answer questions!)
- **Mass-Radius Calculations** – Solve TOV equations for multiple central pressures
- **Tidal Deformability** – Compute dimensionless tidal deformability (Λ) and Love number (k₂)
- **Radial Profiles** – Generate detailed internal structure profiles with M-R context
- **Target-Specific Profiles** – Find stars by exact mass or radius values
- **EOS Converter** – Convert raw equation of state data into TOV code units (CLI + interactive)
- **Clean Output** – Organized export structure with CSV data and publication-ready plots

---

## 📂 Project Structure

```
TOVExtravaganza/
├── tovextravaganza/             # Core package (all Python modules)
│   ├── eos.py                   # EOS class for interpolation
│   ├── tov_solver.py            # TOV equation solver
│   ├── tidal_calculator.py      # Tidal deformability calculator
│   └── output_handlers.py       # CSV and plot output handlers
│
├── inputRaw/                    # Raw EOS data files
├── inputCode/                   # Converted EOS in TOV code units
│
├── export/                      # All output goes here!
│   ├── stars/                   # TOV + Tidal results
│   │   ├── csv/                 # p_c, R, M, Lambda, k2 data
│   │   └── plots/               # M-R curves, Lambda(M), k2(M)
│   └── radial_profiles/         # Internal structure data
│       ├── json/                # Detailed radial profiles
│       └── plots/               # M(r) and p(r) plots
│
├── tov.py                       # Main TOV + Tidal solver (CLI)
├── radial.py                    # Radial profile generator (CLI)
├── converter.py                 # EOS unit converter (CLI + interactive)
├── tov_wizard.py                # 🧙‍♂️ Interactive wizard (beginner-friendly!)
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

**Why `-e` (editable mode)?**
- ✅ Changes to code are **immediately reflected** - no reinstall needed!
- ✅ Perfect for development and testing
- ✅ Runs `tovx` commands from your local modified files

> **⚠️ Important:** Regular `pip install tovextravaganza` installs a copy from PyPI. If you want to modify the code, you MUST use `pip install -e .` from the cloned repo!

#### Option 3: Manual (No Installation)

```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
pip install -r requirements.txt
```

Run scripts directly with `python -m tovextravaganza.tov`, etc.

> **Note:** Without `pip install -e .`, the `tovx` commands won't be available - you must use `python -m tovextravaganza.MODULE` syntax.

### Workflow 1: Interactive Wizard 🧙‍♂️ (Easiest - Recommended!)

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

### Mass-Radius Relationship

For advanced users, run the TOV solver directly:

**Via pip:**
```bash
tovx inputCode/hsdd2.csv
```

**From source:**
```bash
python -m tovextravaganza.tov inputCode/hsdd2.csv
```

Creates:
- **M-R Curve**: Mass vs. Radius for the entire EoS
- **Tidal Properties**: Λ(M) and k₂(M) relationships
- **Key Results**: Maximum mass (~2.4 M☉ for HS(DD2) EoS), R @ 1.4 M☉ (~13 km)

![Mass-Radius Plot](export/stars/plots/hsdd2.png)

### Internal Structure Profiles

Running `radial.py` reveals the **internal structure** from center to surface:

**Example Output:**
```bash
python -m tovextravaganza.radial inputCode/hsdd2.csv -M 1.4 -M 2.0
```

Each profile shows:
- **Left Panel**: M(r) or p(r) radial profile from center to surface
- **Right Panel**: Full M-R curve with a ⭐ showing where this star lies

**Mass Profile Example:**

![Mass Profile](export/radial_profiles/plots/Mass/mass_profile_0.png)

**Pressure Profile Example:**

![Pressure Profile](export/radial_profiles/plots/Pressure/pressure_profile_0.png)


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
- **Maximum Mass:** ~2.4 M☉
- **Λ @ 1.4 M☉:** ~300 (dimensionless)
- **Radius @ 1.4 M☉:** ~13 km

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
```

#### Output

**JSON:** `export/radial_profiles/json/<eos_name>.json`
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
| 1 | MeV fm⁻³ | MeV fm⁻³ |
| 2 | fm⁻⁴ | fm⁻⁴ |
| 3 | MeV⁴ | MeV⁴ |
| 4 | CGS (dyn/cm²) | CGS (g/cm³) |

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
- Stable branch reaching M_max ≈ 2.4 M☉
- Typical 1.4 M☉ star has R ≈ 13 km
- Tidal deformability Λ(1.4 M☉) ≈ 300

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

