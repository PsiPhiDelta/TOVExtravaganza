# Development Guide

## Setting Up for Development

If you want to modify the code and test your changes:

### 1. Clone the Repository

```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create venv
python -m venv dev_venv

# Activate it
source dev_venv/bin/activate      # Linux/Mac
dev_venv\Scripts\activate          # Windows
```

### 3. Install in Editable/Development Mode

```bash
pip install -e .
```

**What `-e` does:**
- Installs the package in "editable" mode
- Changes to the code are **immediately reflected** - no need to reinstall!
- All `tovx` commands will use your modified code

### 4. Make Your Changes

Edit any file in `tovextravaganza/`:
- `tovextravaganza/tov.py` - TOV solver
- `tovextravaganza/radial.py` - Radial profiles
- `tovextravaganza/tidal_calculator.py` - Tidal calculations
- etc.

### 5. Test Your Changes

```bash
# Test immediately - no reinstall needed!
tovx inputCode/hsdd2.csv
tovx-radial inputCode/hsdd2.csv -M 1.4
```

Your changes are live! 🚀

---

## Development Workflow

### Running Tests

```bash
# Test TOV solver
tovx inputCode/hsdd2.csv -n 50

# Test radial profiler
tovx-radial inputCode/csc.csv -M 1.0

# Test converter
tovx-converter
```

### Checking for Issues

Look out for:
- ODE integration warnings
- Division by zero errors
- Unphysical results (R=100 km, M=0)
- Unit conversion errors

### Git Workflow

```bash
# Create a feature branch
git checkout -b my-feature

# Make changes and commit
git add tovextravaganza/tov.py
git commit -m "Fix: improved numerical stability"

# Push to your fork
git push origin my-feature
```

---

## Project Structure

```
TOVExtravaganza/
├── tovextravaganza/           # Main package
│   ├── __init__.py            # Package initialization
│   ├── tov.py                 # TOV solver (CLI entry point)
│   ├── radial.py              # Radial profiler (CLI entry point)
│   ├── converter.py           # EOS converter (CLI entry point)
│   ├── tov_wizard.py          # Interactive wizard
│   ├── demo.py                # Demo file downloader
│   ├── help_command.py        # Help command
│   ├── eos.py                 # EOS class (interpolation)
│   ├── tov_solver.py          # TOV solver core logic
│   ├── tidal_calculator.py    # Tidal deformability
│   └── output_handlers.py     # CSV/plot writers
├── inputCode/                 # Example EOS files (code units)
├── inputRaw/                  # Example raw EOS files
├── setup.py                   # Package configuration
├── pyproject.toml             # Modern Python packaging
└── README.md                  # Documentation
```

---

## Key Classes

### EOS (`tovextravaganza/eos.py`)
- Loads and interpolates EOS data
- Methods: `get_energy_density(p)`, `get_all_columns(p)`

### TOVSolver (`tovextravaganza/tov_solver.py`)
- Solves TOV equations
- Returns `NeutronStar` objects with M, R, profiles

### TidalCalculator (`tovextravaganza/tidal_calculator.py`)
- Computes tidal deformability (Λ, k₂)
- Integrates coupled TOV-tidal equations

### RadialProfiler (`tovextravaganza/radial.py`)
- Generates detailed radial profiles
- Finds stars by target M or R

---

## Adding New Features

### Example: Add a new EOS table format

1. Modify `tovextravaganza/eos.py`:
```python
def load_new_format(self, filename):
    # Your loading logic
    pass
```

2. Test immediately:
```bash
python -m tovextravaganza.tov my_new_eos.csv
```

3. No reinstall needed with `pip install -e .`!

---

## Common Issues

### Changes not reflected?
- Make sure you installed with `-e` flag
- Restart Python if testing interactively
- Check you're in the right venv

### Import errors?
- Verify all relative imports use `.` prefix
- Example: `from .eos import EOS` (not `from eos import EOS`)

### Package not found?
- Activate your venv: `source dev_venv/bin/activate`
- Verify install: `pip list | grep tovextravaganza`

---

## Contact

Questions? Improvements?
- **GitHub Issues:** https://github.com/PsiPhiDelta/TOVExtravaganza/issues
- **Email:** mohogholami@gmail.com
- **Website:** https://hoseingholami.com/

---

**Happy developing! Oh boy oh boy, let's make science better!** 🚀

