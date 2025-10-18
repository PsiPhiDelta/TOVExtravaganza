# TOV Extravaganza v1.0.0 - Release Notes

**Release Date**: January 18, 2025  
**Version**: 1.0.0  
**Codename**: "Oh Boy Oh Boy!"

---

## 🎉 What's New in v1.0.0

### The Complete TOV Toolkit

TOV Extravaganza v1.0.0 is a **complete rewrite** of the neutron star physics toolkit, featuring:

✨ **Tidal Deformability** - Full Λ and k₂ calculations integrated into the core solver  
🧙‍♂️ **Interactive Wizard** - Beginner-friendly workflow that guides you through everything  
⚡ **Command-Line Tools** - Professional CLI for `tov.py`, `radial.py`, and `converter.py`  
📊 **Target-Specific Profiles** - Find stars by exact mass or radius  
🎯 **Publication-Ready Output** - Organized folders with beautiful multi-panel plots  
🏗️ **Object-Oriented Design** - Clean architecture with proper classes in `src/`  

---

## 🚀 Quick Start

### For Beginners (Easiest!)

```bash
python tov_wizard.py
```

Just answer a few questions and the wizard does everything!

### For Power Users

```bash
# Convert EOS
python converter.py inputRaw/your_eos.csv 2 3 1

# Compute M-R + Tidal
python tov.py inputCode/your_eos.csv

# Generate radial profiles for 1.4 M☉ star
python radial.py inputCode/your_eos.csv -M 1.4
```

---

## 🌟 Highlights

### 1. Tidal Deformability (NEW!)

Compute **dimensionless tidal deformability** (Λ) and **Love number** (k₂) for gravitational wave constraints:

```bash
python tov.py inputCode/hsdd2.csv
```

**Output**: `export/stars/csv/hsdd2.csv` with columns:
```
p_c, R, M_code, M_solar, Lambda, k2
```

Plus beautiful 3-panel plots showing M-R, Λ(M), and k₂(M)!

**Example Results (HS(DD2) EOS)**:
- Maximum Mass: ~2.4 M☉
- Λ @ 1.4 M☉: ~300 (consistent with GW170817!)
- Radius @ 1.4 M☉: ~13 km

### 2. Interactive Wizard (NEW!)

Perfect for students and first-time users:

```bash
python tov_wizard.py
```

The wizard will:
- 🔍 Auto-detect your EOS files
- ❓ Ask simple questions (no expertise needed!)
- 🎯 Run the full workflow for you
- 📊 Show you exactly where your results are
- 🎉 Celebrate your success!

### 3. Target-Specific Radial Profiles (NEW!)

Find stars by **exact mass or radius**:

```bash
# Profile for 1.4 M☉ star
python radial.py inputCode/hsdd2.csv -M 1.4

# Profile for 12 km radius star
python radial.py inputCode/hsdd2.csv -R 12.0

# Multiple profiles
python radial.py inputCode/hsdd2.csv -M 1.4 -M 1.8 -M 2.0
```

Each profile shows **M-R context** - see where your star lies on the curve!

### 4. Professional CLI Tools

All scripts now have proper command-line interfaces:

```bash
# tov.py - Full control
python tov.py input.csv -n 1000 --dr 0.0001 --quiet --no-show

# radial.py - Targeted profiles
python radial.py input.csv -M 1.4 -R 12 -o export/my_profiles

# converter.py - CLI mode
python converter.py hsdd2.csv 2 3 4 inputCode/hsdd2.csv
```

### 5. Organized Output Structure

Everything goes to clean folders:

```
export/
├── stars/
│   ├── csv/      → TOV + Tidal data (p_c, R, M, Lambda, k2)
│   └── plots/    → M-R curve, Lambda(M), k2(M)
└── radial_profiles/
    ├── json/     → Full radial data
    └── plots/    → M(r) and p(r) with M-R context
```

---

## 🐛 Critical Bug Fixes

### Division by Zero (FIXED!)

**Problem**: TOV integration would crash at `r*(r - 2M) = 0`  
**Solution**: Added `+1e-30` to denominator for numerical stability

### Zero-Mass Artifacts (FIXED!)

**Problem**: Unphysical (0,0) points appeared in M-R plots  
**Solution**: Filter out R=R_max and M<0.05 M☉ solutions

### Interpolation Extrapolation (FIXED!)

**Problem**: Dangerous extrapolation beyond EOS table bounds  
**Solution**: Clamp to boundary values instead

### ODE Accuracy (IMPROVED!)

Increased integration tolerances: `rtol=1e-12, atol=1e-14`

---

## 📚 Documentation

### Comprehensive README

The README now includes:
- ✅ Feature highlights
- ✅ Complete project structure
- ✅ Quick start (wizard + manual)
- ✅ Detailed usage for all 3 tools
- ✅ Physics explanations (TOV + tidal + k₂)
- ✅ Command reference tables
- ✅ Troubleshooting guide
- ✅ Citation information
- ✅ EOS database references

### Physics Explanations

Full mathematical treatment of:
- TOV equations (hydrostatic equilibrium)
- Tidal deformability (Λ = 2/3 k₂ C⁻⁵)
- Love number k₂ (complete differential equations)
- Geometric units and conversions

---

## 🎓 Citation

If you use TOV Extravaganza in your research, please cite:

**Software**:
```bibtex
@software{Gholami_TOVExtravaganza_Python_toolkit_2025,
  author = {Gholami, Hosein},
  title = {{TOVExtravaganza: Python toolkit for solving TOV equations}},
  url = {https://github.com/PsiPhiDelta/TOVExtravaganza},
  version = {1.0.0},
  year = {2025}
}
```

**Associated Paper**:
Gholami et al. (2024) - arXiv:2411.04064  
*Astrophysical constraints on color-superconducting phases in compact stars*

---

## 🛠️ Under the Hood

### Object-Oriented Architecture

- `src/eos.py` - EOS class
- `src/tov_solver.py` - TOVSolver + NeutronStar classes
- `src/tidal_calculator.py` - TidalCalculator class
- `src/output_handlers.py` - Output writers

### Backward Compatibility

Original scripts (`tov.py`, `radial.py`, `converter.py`) retain wrapper functions for compatibility.

### Testing

Validated against literature:
- DD2 EOS: M_max ≈ 2.42 M☉, Λ(1.4) ≈ 240
- HS(DD2) EOS: M_max ≈ 2.40 M☉, Λ(1.4) ≈ 300-320

---

## 📦 What's Included

- ✅ All Python scripts
- ✅ `src/` module folder
- ✅ Example EOS files (inputCode/)
- ✅ Comprehensive README
- ✅ This CHANGELOG
- ✅ MIT License
- ✅ CITATION.cff

---

## 🚧 Known Limitations

- Vector interaction causes speed of sound to approach c at high density (inconsistent with pQCD)
- EOS tables should be supplemented with pQCD matching for very high densities
- Current implementation is 1D (cold beta-equilibrated matter)

---

## 🔮 Future Plans

- 2D tables (finite temperature)
- 3D tables (arbitrary charge fraction)
- MUSES integration
- Additional EOS models
- GUI interface (maybe!)

---

## 🙏 Acknowledgments

Special thanks to:
- The astrophysics and gravitational wave communities
- Numerical relativity folks who make this possible
- CompOSE database maintainers
- Everyone who contributed feedback

**Oh boy oh boy!** May your neutron stars be massive and your convergence ever stable! 🌟

---

## 📧 Contact

**Author**: Hosein Gholami  
**Website**: https://hoseingholami.com/  
**Email**: mohogholami@gmail.com  
**GitHub**: https://github.com/PsiPhiDelta/TOVExtravaganza

Questions? Bugs? Feature requests? Open an issue!

---

*Built with Python, NumPy, SciPy, and a healthy dose of enthusiasm for compact objects.*

