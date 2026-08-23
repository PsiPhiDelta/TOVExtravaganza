# Changelog

All notable changes to TOV Extravaganza.

---

## [1.6.0] - 2026-08-23

### Added
- **Hybrid EOS support (first-order phase transitions)** ⚛️
  - `EOS` now splits a table into single-phase **segments** at each first-order
    transition. `get_value()`, `get_energy_density()`, `get_fdedp()`,
    `get_string_value()` and `get_all_values_at_pressure()` take an optional
    `segment=` argument and clamp at segment edges, so a caller always gets the
    branch it asked for.
  - New `EOS.transitions`, `EOS.segments`, `EOS.n_segments()`,
    `EOS.segment_for_pressure()` and `EOS.segment_pressure_range()`.
  - New `EOS(..., transition_pressures=[...])` to declare transition pressures
    explicitly instead of relying on auto-detection — the robust option when you
    built the Maxwell construction yourself and already know `P_tr`.
  - `TOVSolver` and `TidalCalculator` track which phase they are in as they
    integrate outward, stepping down one segment at each crossing.
- **Regression tests** under `tests/`, plus a hybrid fixture
  (`tests/data/hybrid_dd2_csc.csv`, DD2 ↔ toy CSC quark by Maxwell
  construction) and the script that generates it. Runs under pytest or
  standalone: `python3 tests/test_hybrid_eos.py`.

### Fixed
- **Missing `y` matching condition at a first-order transition (tidal)**
  - `H` and `beta` were integrated continuously in `r`. In a Maxwell
    construction `eps` jumps at *constant* `P`, so `de/dp` is a delta function
    with no width for the stepper to resolve; the discontinuity has to enter as
    an explicit matching condition on `y = r H'/H`:

        y(r_d^+) = y(r_d^-) - 4 pi r_d^3 Delta_eps / (m(r_d) + 4 pi r_d^3 p(r_d))

    (Damour & Nagar 2009; Postnikov, Prakash & Lattimer 2010;
    Takatsy & Kovacs 2020.) Implemented in
    `TidalCalculator._apply_transition_jump()`, driven by
    `_integrate_with_jumps()`, which locates `r_d`, steps exactly onto it,
    shifts `beta`, and resumes on the branch below.
  - Omitting it biases `Lambda` **low** for hybrid stars — up to ~9% on the test
    fixture, growing with quark-core size.
- **`de/dp` contaminated across the transition**
  - `_precompute_fdedp()` took centered differences straddling the plateau,
    dividing a finite `de` by a vanishing `dp`. On the test fixture that put
    `de/dp` = 44 and 8395 on the two plateau rows (neighbours ≈3.5 and ≈3.8),
    which linear interpolation then smeared over the adjacent intervals — a
    spurious, table-resolution-dependent contribution. Differences are now taken
    strictly within one phase. The two ends of the *table* keep the original
    convention, so single-phase results are unchanged.
- **Non-deterministic loading of a Maxwell plateau**
  - `np.argsort` defaults to quicksort, which is not stable, so the two rows
    sharing one pressure were ordered arbitrarily — the same physics in a
    slightly longer table could load with the phases swapped. Now sorted with
    `kind="stable"`, and every plateau is additionally forced into
    ascending-energy order, so the result no longer depends on how the file
    happened to be written.
- **Silent failure on a near-degenerate plateau**
  - A plateau written with a tiny but nonzero pressure step (`dp/p = 1e-12`, as
    a finite-precision table round-trip produces) previously returned
    `M = 0, Lambda = 0` without an error. Now handled like an exact plateau.

### Changed
- **Transition auto-detection is relative-thresholded**
  - Requires both `dp/p <= 1e-6` and `de/e > 1e-3` (`EOS.TRANSITION_REL_DP` /
    `TRANSITION_REL_DE`, overridable per instance). An *absolute* `dp` threshold
    fires on ordinary outer-crust table steps, where `dp` is small only because
    the pressure itself is. All EOS files shipped with the package detect zero
    transitions; the smallest legitimate `dp/p` among them is 9e-5.

### Unchanged
- Single-phase results are **byte-identical** to 1.5.3 (`hsdd2.csv`, `csc.csv`,
  `test.csv`, all six `Batch/` files). DD2 reference: `M_max` 2.4228 Msun,
  `R(1.4)` 13.2347 km, `Lambda(1.4)` ~703-710 depending on sampling.
  Note `Lambda ~ M^-6`, so interpolate a sequence in `log Lambda` and use >= 200
  central pressures.

---

## [1.5.3] - 2026-03-24

### Fixed
- **Converter Unit Labeling**
  - Corrected user-facing unit representation from `MeV^-4` to `MeV^4` in converter menus, help text, and printed descriptions.
  - Conversion factors and numeric behavior remain unchanged.

### Improved
- **Converter Messaging Cleanup**
  - Replaced remaining `TODO`/placeholder text for the `fm^-4` path with explicit formula and finalized messaging.
  - Clarified the displayed `fm^-4` conversion factor expression.

---

## [1.5.2] - 2025-10-20

### Added
- **Batch EOS Files in Demo** 🎁
  - `tovx-demo` now downloads all 6 batch EOS files (CSC + RGNJL series)
  - Includes both raw (`inputRaw/batch/`) and code-unit (`inputCode/Batch/`) versions
  - Perfect for testing batch processing tutorials
  - All files included in PyPI package (~200KB total)

### Updated
- **Demo Command** enhanced to copy/download batch files automatically
- **Package Data** now includes `inputRaw/batch/` and `inputCode/Batch/` subdirectories
- Demo messages updated to mention batch files and batch processing examples

### Note
- **Post-install messages**: Modern `pip` doesn't show post-install messages anymore
- Run `tovextravaganza` command after installation to see quick start guide and version info

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
