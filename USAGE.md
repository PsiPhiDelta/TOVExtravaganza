# How to Use TOV Extravaganza After Installation

## Installation

```bash
pip install tovextravaganza
```

This installs **4 console commands** that you can run directly from your terminal!

---

## 🚀 Quick Usage

### Step 1: Get EOS Data

You need an EOS (Equation of State) file. You can:

**Option A: Use included example files**

The package includes 3 example EOS files:
- `test.csv` - Simple test EOS
- `hsdd2.csv` - HS(DD2) realistic EOS
- `csc.csv` - Color-superconducting quark matter EOS

Find them in your package installation or download from:
https://github.com/PsiPhiDelta/TOVExtravaganza/tree/main/inputCode

**Option B: Download from databases**
- CompOSE: https://compose.obspm.fr/
- RG-NJL: https://github.com/marcohof/RG-NJL-EoS-tables

**Option C: Convert your own data**
```bash
tovx-converter
```

---

### Step 2: Run Analysis

#### Option 1: Interactive Wizard (Easiest!)

```bash
tovx-wizard
```

Just answer the questions and it does everything for you!

#### Option 2: Direct Commands

```bash
# Compute Mass-Radius + Tidal properties
tovx path/to/your_eos.csv

# Generate radial profiles for 1.4 solar mass star
tovx-radial path/to/your_eos.csv -M 1.4

# Convert your raw EOS data
tovx-converter
```

---

## 📋 Detailed Examples

### Example 1: Compute M-R Relationship

```bash
# Basic usage (200 stars)
tovx hsdd2.csv

# High resolution (1000 stars)
tovx hsdd2.csv -n 1000

# Custom output folder
tovx hsdd2.csv -o my_results
```

**Output:**
- CSV: `export/stars/csv/hsdd2.csv` (p_c, R, M, Lambda, k2)
- Plot: `export/stars/plots/hsdd2.pdf` (M-R, Lambda, k2)

### Example 2: Get Internal Structure

```bash
# Profile for 1.4 solar mass star
tovx-radial hsdd2.csv -M 1.4

# Multiple masses
tovx-radial hsdd2.csv -M 1.4 -M 1.8 -M 2.0

# By radius
tovx-radial hsdd2.csv -R 12.0
```

**Output:**
- JSON: `export/radial_profiles/json/hsdd2.json`
- Plots: `export/radial_profiles/plots/Mass/` and `Pressure/`

### Example 3: Convert EOS

```bash
# Interactive mode
tovx-converter

# Or use python API
python -c "from converter import EOSConverter; converter = EOSConverter(); converter.interactive_convert()"
```

---

## 🐍 Python API Usage

You can also import and use the modules in your own scripts:

```python
from src.eos import EOS
from src.tov_solver import TOVSolver
from src.tidal_calculator import TidalCalculator

# Load EOS
eos = EOS('path/to/your_eos.csv')

# Solve TOV
solver = TOVSolver(eos)
star = solver.solve(central_pressure=0.001)

print(f"Mass: {star.M_solar:.3f} M☉")
print(f"Radius: {star.R:.2f} km")

# Compute tidal deformability
tidal = TidalCalculator(eos)
result = tidal.compute(central_pressure=0.001)

print(f"Lambda: {result['Lambda']:.1f}")
print(f"k2: {result['k2']:.3f}")
```

---

## 📂 Working Directory

The commands create output in your **current working directory**:

```
your_working_folder/
└── export/
    ├── stars/
    │   ├── csv/
    │   └── plots/
    └── radial_profiles/
        ├── json/
        └── plots/
```

**Tip:** Create a project folder first:
```bash
mkdir my_neutron_stars
cd my_neutron_stars
tovx path/to/eos.csv
```

---

## 🆘 Getting Example Data

### Method 1: Download from GitHub

```bash
wget https://raw.githubusercontent.com/PsiPhiDelta/TOVExtravaganza/main/inputCode/hsdd2.csv
tovx hsdd2.csv
```

### Method 2: Clone Repository

```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza/inputCode
tovx hsdd2.csv
```

### Method 3: Use Your Own Data

Convert your data first:
```bash
tovx-converter
# Follow the prompts to convert your raw EOS data
```

---

## ✅ Verify Installation

```bash
# Check commands are available
tovx --help
tovx-radial --help
tovx-converter --help

# Check Python imports work
python -c "from src.tov_solver import TOVSolver; print('✓ Import successful!')"

# Check version
pip show tovextravaganza
```

---

## 🎯 Common Workflows

### Workflow 1: Analyze Standard EOS

```bash
# Download example
wget https://raw.githubusercontent.com/PsiPhiDelta/TOVExtravaganza/main/inputCode/hsdd2.csv

# Compute everything
tovx hsdd2.csv

# Get 1.4 M☉ profile
tovx-radial hsdd2.csv -M 1.4
```

### Workflow 2: Convert Your Own EOS

```bash
# Interactive conversion
tovx-converter
# → Select your file
# → Choose columns and units
# → Get converted file

# Use converted file
tovx inputCode/your_eos.csv
```

### Workflow 3: Beginner Mode

```bash
# Just run the wizard!
tovx-wizard
```

---

## 💡 Tips

- **First time?** Use `tovx-wizard` - it guides you through everything!
- **Have your own EOS?** Use `tovx-converter` first to convert units
- **Need help?** Every command has `--help`:
  - `tovx --help`
  - `tovx-radial --help`
- **Want high accuracy?** Use `tovx file.csv -n 1000 --dr 0.0001`

---

## 📧 Need Help?

- **Documentation:** https://github.com/PsiPhiDelta/TOVExtravaganza
- **Issues:** https://github.com/PsiPhiDelta/TOVExtravaganza/issues
- **Email:** mohogholami@gmail.com
- **Website:** https://hoseingholami.com/

---

**Oh boy oh boy, happy computing!** 🌟

