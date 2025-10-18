# Changelog

All notable changes to TOV Extravaganza will be documented in this file.

## [1.0.0] - 2025-01-18

### 🎉 Major Release - Complete Refactor & New Features

This is the first major release of TOV Extravaganza, featuring a complete rewrite with object-oriented architecture, CLI tools, and comprehensive documentation.

### ✨ New Features

#### Core Functionality
- **Tidal Deformability Calculations** - Compute dimensionless tidal deformability (Λ) and Love number (k₂) for all stars
- **Interactive Wizard** (`tov_wizard.py`) - Beginner-friendly guided workflow with step-by-step instructions
- **Command-Line Interfaces** - All tools now have proper CLI with argparse
  - `tov.py` - Full-featured CLI for Mass-Radius + Tidal calculations
  - `radial.py` - CLI for radial profile generation with target mass/radius selection
  - `converter.py` - Both interactive and CLI modes for EOS conversion

#### Radial Profile Enhancements
- **Target-Specific Profiles** - Find stars by exact mass (`-M`) or radius (`-R`) values
- **M-R Context Plots** - Each radial profile now shows where the star lies on the M-R curve
- **Multiple Target Selection** - Generate profiles for multiple masses/radii in one run

#### Output Organization
- **Unified Export Structure** - All output goes to organized `export/` folder
  - `export/stars/` - TOV + Tidal results (csv/ and plots/)
  - `export/radial_profiles/` - Internal structure data (json/ and plots/)
- **Publication-Ready Plots** - Multi-panel plots with M-R, Λ(M), and k₂(M)
- **Filtering** - Automatic removal of unphysical solutions (R_max, low mass)

#### Code Architecture
- **Object-Oriented Design** - Complete refactor with proper classes
  - `src/eos.py` - EOS class for data loading and interpolation
  - `src/tov_solver.py` - TOVSolver and NeutronStar classes
  - `src/tidal_calculator.py` - TidalCalculator class
  - `src/output_handlers.py` - MassRadiusWriter and TidalWriter classes
- **Backward Compatibility** - Wrapper functions maintain compatibility with existing scripts

### 🐛 Bug Fixes

#### Critical Fixes
- **Division by Zero** - Fixed TOV integration crashes by adding epsilon (1e-30) to denominator
- **Zero-Mass Solutions** - Filtered out (0,0) points from M-R plots
- **Interpolation Safety** - Replaced dangerous extrapolation with boundary value clamping
- **Phase Index Rounding** - Use `round()` instead of `int()` to prevent truncation errors

#### Numerical Improvements
- **ODE Integration Accuracy** - Increased tolerances (rtol=1e-12, atol=1e-14)
- **Error Handling** - Added warnings capture for ODE integration issues
- **Radial Step Refinement** - Adjusted default DR to 0.0005 for smoother results
- **Tidal Initial Conditions** - Corrected H initial condition for small r

#### Display & Output
- **Plot Labels** - Fixed Y-axis label from "code units" to "solar masses"
- **Unicode Compatibility** - Replaced M☉ with Msun in print statements to avoid encoding errors
- **Pressure Warnings** - Added warnings when pressure clipping occurs
- **Default Values** - Changed NUM_STARS from 500 to 200 for faster execution

### 📚 Documentation

- **Comprehensive README** - Professional documentation with:
  - Complete feature list and project structure
  - Quick start guide with wizard and manual workflows
  - Detailed usage examples for all three tools
  - Physics explanations (TOV equations, tidal deformability, k₂ calculation)
  - Command reference tables
  - Troubleshooting guide
  - EOS database references (CompOSE, stellarcollapse.org, RG-NJL)
  - Citation information (software + arXiv paper)

- **Inline Documentation** - All code retains original comedic comments ("oh boy oh boy!")

### 🎨 Showcase Examples

- Added example outputs with HS(DD2) EOS showing:
  - M_max ≈ 2.4 M☉
  - Λ(1.4 M☉) ≈ 300
  - R(1.4 M☉) ≈ 13 km

### 🔧 Technical Details

- **Unit System Documentation** - Clarified geometric units (G=c=1)
- **Conversion Factors** - Documented all unit conversions
- **Numerical Methods** - Documented ODE settings and interpolation schemes
- **Filtering Logic** - Explained physical solution criteria

### 🙏 Acknowledgments

- Added citation to Gholami et al. (2024) arXiv:2411.04064
- Added website link (hoseingholami.com)
- Added RG-NJL EoS database reference

---

## [Pre-1.0.0] - Historical Development

### Previous Work
- Initial TOV solver implementation
- Basic EOS conversion tools
- Mass-Radius relationship calculations
- Radial profile generation
- Maxwell construction for hybrid stars

---

**Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

