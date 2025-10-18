# TOV Extravaganza v1.0.0

**Release Date:** January 18, 2025

---

## Overview

TOV Extravaganza v1.0.0 is a Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and computing neutron star properties, including tidal deformability for gravitational wave astronomy.

---

## Key Features

### Tidal Deformability Calculations
- Computes dimensionless tidal deformability (Λ) and Love number (k₂)
- Integrated with TOV solver for seamless workflow
- Generates publication-ready plots: M-R curves, Λ(M), k₂(M)

### Command-Line Interface
- `tov.py` - Mass-Radius relationships with tidal properties
- `radial.py` - Detailed radial profiles with target mass/radius selection
- `converter.py` - EOS unit conversion (interactive and CLI modes)

### Interactive Wizard
- Beginner-friendly guided workflow
- Automatic file detection and validation
- Step-by-step instructions

### Object-Oriented Architecture
- Modular design with `src/` package structure
- Clean separation of concerns: EOS handling, TOV integration, tidal calculations, output management
- Backward-compatible with existing workflows

---

## Installation & Usage

### Quick Start

```bash
# Interactive mode (recommended for first-time users)
python tov_wizard.py

# Command-line mode
python converter.py inputRaw/your_eos.csv 2 3 1
python tov.py inputCode/your_eos.csv
python radial.py inputCode/your_eos.csv -M 1.4
```

### Output Structure

```
export/
├── stars/
│   ├── csv/      # TOV + Tidal data (p_c, R, M, Lambda, k2)
│   └── plots/    # M-R, Lambda(M), k2(M) plots
└── radial_profiles/
    ├── json/     # Detailed radial data
    └── plots/    # M(r) and p(r) with M-R context
```

---

## Technical Details

### Validation

Results validated against literature for standard equations of state:
- DD2 EOS: M_max ≈ 2.42 M☉, Λ(1.4) ≈ 240
- HS(DD2) EOS: M_max ≈ 2.40 M☉, Λ(1.4) ≈ 300-320

### Numerical Methods

- ODE integration: `scipy.integrate.odeint` with rtol=1e-12, atol=1e-14
- EOS interpolation: Piecewise-linear
- Units: Geometric units (G = c = 1) with km for length, M☉ for mass

### Bug Fixes

- Fixed division-by-zero in TOV integration at r(r-2M) = 0
- Implemented boundary clamping to prevent EOS table extrapolation
- Added filtering for unphysical solutions (R = R_max, M < 0.05 M☉)
- Improved numerical stability with epsilon regularization

---

## Citation

If you use this software in your research, please cite:

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

---

## Documentation

Complete documentation available in `README.md`, including:
- Physics background (TOV equations, tidal deformability, Love number k₂)
- Command reference
- EOS database references
- Troubleshooting guide

---

## Contact

**Author:** Hosein Gholami  
**Website:** https://hoseingholami.com/  
**Email:** mohogholami@gmail.com  
**Repository:** https://github.com/PsiPhiDelta/TOVExtravaganza

---

## License

MIT License - See `LICENSE` file for details.
