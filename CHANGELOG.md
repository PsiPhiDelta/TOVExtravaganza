# Changelog

All notable changes to TOV Extravaganza.

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
