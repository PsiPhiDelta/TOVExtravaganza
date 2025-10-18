# TOV Extravaganza v1.1.0

**Release Date:** October 18, 2025

---

## 🎉 What's New

### Package Structure Refactor
- **Clean package layout** - All Python code now in `tovextravaganza/` folder following Python best practices
- **Cleaner root directory** - Only documentation and config files at root level
- **Standard imports** - Relative imports throughout the package

### New Console Command
- **`tovextravaganza`** - Shows comprehensive help and quick start guide
  - Lists all 6 available commands
  - Provides usage examples for both pip and source installations
  - Shows output structure
  - Includes citation information

### Enhanced User Experience
- **`tovx-demo`** - Download example EOS files without cloning the repository
  - Works from any directory
  - Downloads from GitHub automatically
- **Dual usage documentation** - README now shows both approaches:
  - Via pip: `tovx inputCode/hsdd2.csv`
  - From source: `python -m tovextravaganza.tov inputCode/hsdd2.csv`

### Better Documentation
- **Wizard-first approach** - Documentation prioritizes the easiest path for beginners
- **USAGE.md** - Complete guide for PyPI users
- **Updated README** - Clear instructions for both pip and source installations
- **Example outputs** - Shows both command styles everywhere

---

## 🚀 Installation

### Via PyPI (Recommended)
```bash
pip install tovextravaganza
tovextravaganza    # Shows quick start guide
```

### From Source
```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
pip install -e .
```

---

## 📦 Console Commands

After installation, 6 commands are available:

1. **tovextravaganza** - Show help and quick start guide
2. **tovx-demo** - Download example EOS files
3. **tovx** - Compute Mass-Radius + Tidal deformability
4. **tovx-radial** - Generate radial profiles
5. **tovx-converter** - Convert EOS units
6. **tovx-wizard** - Interactive guided workflow

---

## 🎯 Quick Start

```bash
# Install
pip install tovextravaganza

# Get examples
tovx-demo

# Run analysis
tovx inputCode/hsdd2.csv

# Or use wizard
tovx-wizard
```

---

## 🐛 Bug Fixes
- Fixed Unicode encoding errors in `demo.py` for Windows compatibility
- Fixed `SameFileError` when running `tovx-demo` from source directory
- Removed non-functional post-install command (modern pip doesn't support it)

---

## 📖 Citation

If you use TOV Extravaganza in your research, please cite:

**Software:**
```bibtex
@software{Gholami_TOVExtravaganza_2025,
  author = {Gholami, Hosein},
  title = {{TOVExtravaganza: Python toolkit for solving TOV equations}},
  url = {https://github.com/PsiPhiDelta/TOVExtravaganza},
  version = {1.1.2},
  year = {2025}
}
```

**Paper:**
```bibtex
@article{Gholami:2024csc,
  author = "Gholami, Hosein and Rather, Ishfaq Ahmad and Hofmann, Marco and Buballa, Michael and Schaffner-Bielich, J{\"u}rgen",
  title = "{Astrophysical constraints on color-superconducting phases in compact stars}",
  eprint = "2411.04064",
  archivePrefix = "arXiv",
  year = "2024"
}
```

---

## 🔗 Links

- **PyPI:** https://pypi.org/project/tovextravaganza/
- **GitHub:** https://github.com/PsiPhiDelta/TOVExtravaganza
- **Paper:** https://arxiv.org/abs/2411.04064
- **Author:** https://hoseingholami.com/

---

**Built with Python, NumPy, SciPy, and a healthy dose of enthusiasm for compact objects.**

