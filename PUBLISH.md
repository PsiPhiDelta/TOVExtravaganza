# Publishing TOV Extravaganza to PyPI

## Prerequisites

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Build the Package

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Build Distribution

```bash
python -m build
```

This creates:
- `dist/tovextravaganza-1.0.0.tar.gz` (source distribution)
- `dist/tovextravaganza-1.0.0-py3-none-any.whl` (wheel)

## Test on TestPyPI (Optional but Recommended)

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 2. Test Installation

```bash
pip install --index-url https://test.pypi.org/simple/ tovextravaganza
```

## Publish to PyPI

### 1. Upload to PyPI

```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password.

### 2. Verify on PyPI

Visit: https://pypi.org/project/tovextravaganza/

## Using API Token (Recommended)

### 1. Create API Token

- Go to https://pypi.org/manage/account/token/
- Create a new token
- Scope: "Entire account" or specific to "tovextravaganza"

### 2. Configure `.pypirc`

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

### 3. Upload with Token

```bash
twine upload dist/*
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add `PYPI_API_TOKEN` to repository secrets:
- Go to GitHub repo → Settings → Secrets → New repository secret

## After Publishing

### Update Installation Instructions

In README.md, add:

```markdown
## Installation

```bash
pip install tovextravaganza
```
\```

### Announce the Release

- Create GitHub Release (already done!)
- Share on social media
- Update documentation
- Send to mailing lists

## Version Updates

For future releases:

1. Update version in:
   - `setup.py`
   - `pyproject.toml`
   - `src/__init__.py` (if you add one)

2. Update `CHANGELOG.md`

3. Create git tag:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

4. Rebuild and republish:
   ```bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Error: File already exists

You cannot overwrite a version on PyPI. Increment the version number.

### Error: Invalid authentication

Check your PyPI token or credentials in `~/.pypirc`.

### Warning: Long description failed

Validate your README:
```bash
twine check dist/*
```

## Resources

- PyPI: https://pypi.org/
- Python Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/

