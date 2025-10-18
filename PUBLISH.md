# Publishing Guide (For Maintainers)

Quick guide for publishing new versions to PyPI.

---

## Prerequisites

1. Install tools: `pip install build twine`
2. Get PyPI API token: https://pypi.org/manage/account/token/

---

## Publishing Workflow

### 1. Update Version

Edit 3 files:
- `setup.py` → `version='1.x.x'`
- `pyproject.toml` → `version = "1.x.x"`
- `tovextravaganza/__init__.py` → `__version__ = "1.x.x"`

### 2. Update Changelog

Add entry to `CHANGELOG.md`

### 3. Commit and Tag

```bash
git add .
git commit -m "Release v1.x.x: brief description"
git tag -a v1.x.x -m "Release v1.x.x"
git push origin main
git push origin v1.x.x
```

### 4. Build Package

```bash
rm -rf dist/ build/ *.egg-info
python -m build
```

### 5. Upload to PyPI

```bash
twine upload dist/*
```

Use API token when prompted:
- Username: `__token__`
- Password: `pypi-YOUR_TOKEN_HERE`

### 6. Create GitHub Release

1. Go to https://github.com/PsiPhiDelta/TOVExtravaganza/releases/new
2. Choose tag: `v1.x.x`
3. Copy changelog entry as description
4. Publish release

---

## API Token Setup

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

Then `twine upload dist/*` won't prompt for credentials.

---

## Quick Reference

```bash
# Version bump → Commit → Tag → Build → Upload → GitHub Release
```

That's it! Oh boy oh boy, publishing complete! 🚀
