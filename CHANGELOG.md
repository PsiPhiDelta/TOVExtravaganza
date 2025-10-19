# Changelog

All notable changes to TOV Extravaganza.

---

## [1.5.1] - 2025-10-19

### Updated
- **README Documentation** 📚
  - Complete comprehensive DD2 tutorial (raw → conversion → TOV → radial → max mass)
  - Batch processing tutorial with step-by-step guide
  - Detailed explanation of all new features and flags
  - Full dβ/dr tidal perturbation equation now documented
  - Phase-color-coded showcase plots added
  - Improved organization and clarity throughout

- **Phase-Coded M-R Plot** 🎨
  - Better color distinction between Hadronic (blue) and 2SC (orange) phases
  - Clean legend showing phase colors and series line styles
  - High-quality showcase plot included in README

---

## [1.5.0] - 2025-10-19

### Added
- **HDF5 Storage Format** 💾 – Efficient binary storage for radial profiles
  - 10-100x smaller files than JSON (with gzip compression)
  - Fast read/write for large datasets with 10,000+ radial points
  - Standard scientific format (Python, MATLAB, Julia, R compatible)
  - Automatic fallback to JSON if h5py not installed
  - Install with: `pip install tovextravaganza[hdf5]`
  
- **Maximum Mass Profile** 🎯 – New `--max-mass` flag for radial profiles
  - Automatically finds M_max with precision < 0.01 M☉
  - Fast adaptive search (50 coarse + 200 fine points)
  - Only computes full radial profile once at M_max
  - Works in both single-file and batch modes
  - Example: `tovx-radial --batch inputCode/Batch/ --max-mass`

- **Timeout Protection** ⏱️ – Prevent hanging on problematic configurations
  - Default: 10 seconds per star (configurable with `--timeout`)
  - Gracefully skips stuck calculations and continues
  - Works in TOV solver, radial profiles, and batch modes
  - Example: `tovx --batch inputCode/ --timeout 20`

- **Plot Viewport Control** 📊 – New `--rmax-plot` parameter
  - Zoom M-R plots to specific radius range (default: 20 km)
  - Only changes axis limits, doesn't crop data
  - Applies to all M-R diagrams in TOV and radial plots
  - Example: `tovx inputCode/hsdd2.csv --rmax-plot 15`

- **Phase-Coded Radial Plots** 🎨 – Beautiful visualization of internal structure
  - Color-coded by phase (Hadronic=blue, 2SC=orange, CFL=red)
  - Shows M(r), p(r), ε(r), n(r) from center to surface
  - High-resolution PNG output (200 DPI) for publications
  - Physical units: pressure & energy in MeV/fm³, number density in fm⁻³

- **Utility Modules**
  - `tovextravaganza.utils.timeout` – Cross-platform timeout decorator
  - `tovextravaganza.utils.read_radial_hdf5` – HDF5 data reader with examples

### Improved
- **Energy-Based String Interpolation** 🔬 – Critical fix for phase transitions
  - String columns (phase labels) now use energy density for nearest-neighbor search
  - Correctly handles first-order phase transitions where pressure plateaus
  - More robust than pressure-based approach for discontinuous transitions
  - Applies to ALL string columns, not just "phase"

- **Radial Profile Performance** ⚡ – Massive speed improvements
  - M-R curve calculation: Only computes M & R (not full profiles)
  - M_max search: Fast TOV solve (250 points in seconds, not minutes)
  - Full column interpolation: Only when generating actual profiles
  - ~100x faster for large EOS tables (20,000 points)

- **All EOS Column Tracking** 📋 – Complete data preservation
  - TOV solver: Tracks all columns at central pressure
  - Radial profiles: Interpolates all columns at each radial point
  - Supports mixed numeric and string columns
  - Dynamic CSV headers based on available columns

- **Windows Compatibility** 🪟 – Fixed Unicode encoding issues
  - Replaced M☉ symbols with "Msun" in terminal output
  - All print statements now work on Windows CMD/PowerShell
  - No more UnicodeEncodeError crashes

### Changed
- **Default timeout**: Now 10 seconds (was 60s in initial implementation)
- **Optional dependency**: h5py now in `[hdf5]` and `[all]` extras

---

## [1.4.2] - 2025-10-19

### Fixed
- **Critical M-R Curve Bug** – Reverted problematic surface detection changes from v1.4.0
  - Surface detection restored to `p <= 0.0` (instead of `p <= eos.p_table[0]`)
  - TOV solver `dpdr` formula reverted to stable version
  - Integration starting point restored to `r=0.0`
  - DD2 EOS now correctly gives maximum mass ~2.42 M☉ (was broken at ~2.10 M☉)
  - All M-R curves now match reference implementations

### Improved
- **Interactive Batch Converter** – Batch mode now prompts for missing parameters
  - Automatically prompts for pressure column if not provided
  - Automatically prompts for energy column if not provided
  - Automatically prompts for unit system if not provided
  - Auto-creates `inputCode/Batch/` subfolder when processing batch directories
  - Works in both interactive and non-interactive modes
  
- **Tidal Deformability Accuracy** – Improved but still under active development
  - Lambda values within ~6% of reference for DD2 EOS
  - Further improvements planned for future releases

### Added
- Batch EOS test files for validation (RGgen v0.70, v0.80, v0.85)
- Comparison scripts for validating against reference implementations

---

## [1.4.0] - 2025-10-19

### Added
- **Central Column Values in TOV Output** 🎯 – Track ALL EOS columns at central pressure!
  - Automatically includes central values for all additional EOS columns (mu, n, temperature, phase, etc.)
  - Supports both numeric (interpolated) and string columns (nearest value)
  - Dynamic CSV headers: `central_<column_name>` for each additional column
  - Example: EOS with muB and phase_index → output includes `central_muB` and `central_phase_index`
  
- **Batch Processing for Unit Converter** 🚀 – Convert multiple EOS files in parallel!
  - `tovx-converter --batch inputRaw/` processes all files in parallel
  - Preserves ALL additional columns (strings, floats, whatever!)
  - Configurable unit systems and column mappings
  - Example: 3 files (1943 lines) converted in 0.60 seconds

### Improved
- Enhanced EOS reader with better commented header detection
- Automatic header normalization (pressure/epsilon → p/e)
- Support for mixed-type columns (numeric + string)
- Column name cleanup (removes "(code_units)" suffixes)

---

## [1.3.1] - 2025-10-19

### Added
- **Batch Processing for Radial Profiles** 🚀 – Parallel processing now available for radial profiles too!
  - `tovx-radial --batch inputCode/` processes all files in parallel
  - Organized output structure: each EOS gets its own subfolder
  - Same performance benefits and error handling as TOV batch mode
  - Example: 3 files with profiles processed in 38s with 2 workers

### Improved
- Better error handling in TOV batch processing
- Check for empty results before writing output
- Race condition prevention with `exist_ok=True` for folder creation

---

## [1.3.0] - 2025-10-19

### Added
- **Batch Processing Mode** 🚀 – Process multiple EOS files in parallel!
  - New `--batch` flag to process all CSV files in a directory
  - Configurable parallel workers with `--workers` flag (defaults to CPU count)
  - Comprehensive summary with success/failure statistics for each file
  - Significant performance improvements: ~45% faster with 2 workers, scales with more cores
  - Graceful error handling: individual file failures don't stop the batch
- Updated CLI help with batch processing examples
- Documentation in README with usage examples and performance benefits

### Performance
- Parallel processing using Python's multiprocessing module
- Automatic CPU core detection and utilization
- Example: 3 files processed in 4.7s (parallel) vs 6.8s (sequential)

---

## [1.2.0] - 2025-10-18

### Changed
- **Package reorganization**: Restructured into `core/`, `cli/`, `utils/` subdirectories
  - `core/` - Reusable business logic classes (EOS, TOVSolver, TidalCalculator, etc.)
  - `cli/` - Command-line interface tools (tov, radial, converter)
  - `utils/` - Utility scripts (wizard, demo, help_command)
- Cleaner, more professional package structure following Python best practices

### Improved
- Search accuracy now guarantees 0.01 M☉ error (was 0.05 M☉)
- Radius search accuracy 0.01 km (was 0.1 km)
- Better M > M_max error handling (returns None instead of silently using wrong value)

### Added
- Dashed lines for unstable branch in radial profile M-R diagrams
- M_max display in radial profile plot titles
- DEVELOPMENT.md guide for contributors
- Consolidated documentation (4 .md files instead of 8)

---

## [1.1.2] - 2025-10-18

### Added
- Version number display in `tovextravaganza` help command
- Accuracy guarantee for radial profile search (< 0.05 M☉ for mass, < 0.1 km for radius)
- Dashed line for unstable branch in radial profile M-R plots
- DEVELOPMENT.md guide for contributors

### Fixed
- Updated all help messages to show correct `tovx` and `python -m` syntax
- Proper error handling when user requests M > M_max
- Wizard now uses correct module paths

### Optimized
- Radial profile search ~2.5x faster (2-step algorithm, stable branch only)

---

## [1.1.1] - 2025-10-18

### Fixed
- Wizard module paths (use `python -m tovextravaganza.MODULE`)
- Documentation examples for source installation

---

## [1.1.0] - 2025-10-18

### Changed
- **Package refactor**: All code moved to `tovextravaganza/` folder
- Clean package structure following Python best practices

### Added
- `tovextravaganza` help command
- `tovx-demo` command to download example files
- Dual usage documentation (pip + source)
- GitHub Actions for CI/CD
- Venv activation warnings

---

## [1.0.0] - 2025-10-18

### Added
- Tidal deformability calculations (Λ, k₂)
- Command-line interfaces for all tools
- Interactive wizard (`tovx-wizard`)
- Unified `export/` output structure
- Object-oriented architecture

### Fixed
- Division by zero in TOV integration
- Zero-mass solutions filtered from output
- Dangerous EOS extrapolation → boundary clamping
- Phase index rounding (use `round()` not `int()`)
- Plot axis labels
- Unicode encoding errors

### Documentation
- Comprehensive README with physics, examples, citations
- PyPI package configuration
- Installation and publishing guides

---

**Format**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
