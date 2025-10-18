# Installation Guide

## Installation from PyPI (Coming Soon)

Once published to PyPI, you can install TOV Extravaganza with:

```bash
pip install tovextravaganza
```

## Installation from Source

### 1. Clone the Repository

```bash
git clone https://github.com/PsiPhiDelta/TOVExtravaganza.git
cd TOVExtravaganza
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install the Package

#### Development Mode (Recommended for Contributors)

```bash
pip install -e .
```

This installs the package in editable mode, so changes to the source code are immediately reflected.

#### Standard Installation

```bash
pip install .
```

### 4. Verify Installation

```bash
# Check that command-line tools are available
tov --help
tov-radial --help
tov-converter --help
tov-wizard
```

## Requirements

- Python >= 3.7
- NumPy >= 1.19.0
- SciPy >= 1.5.0
- Matplotlib >= 3.3.0

## Optional Dependencies

For development:

```bash
pip install -e ".[dev]"
```

This installs additional tools like `pytest` for testing.

## Uninstallation

```bash
pip uninstall tovextravaganza
```

## Troubleshooting

### ImportError: No module named 'tovextravaganza'

Make sure you've installed the package:
```bash
pip install -e .
```

### Command not found: tov

The console scripts may not be in your PATH. Try:
```bash
python -m tov --help
```

Or reinstall with:
```bash
pip install --force-reinstall -e .
```

### Permission Denied

On Linux/Mac, you may need to use:
```bash
sudo pip install .
```

Or install in user mode:
```bash
pip install --user .
```

