# CI Matrix + Coverage + Status Badges (Conda)

This setup gives you:
- Matrix CI on Python **3.10 / 3.11 / 3.12**
- **pylint** + **pytest** with coverage
- **Codecov** coverage upload & badge
- **GitHub Actions** status badge
- **pre-commit** hooks
- `src/`-layout friendly config

## Badges

### CI Status (replace placeholders)
```
[![CI](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/actions/workflows/ci.yml)
```

### Coverage (Codecov)
```
[![codecov](https://codecov.io/gh/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/branch/main/graph/badge.svg)](https://codecov.io/gh/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>)
```

Place these near the top of your `README.md`.

## Local usage
```bash
conda env create -f environment.yml
conda activate redditbot

pre-commit install
pre-commit run -a

# Lint
pylint $(git ls-files '*.py')

# Tests + coverage
pytest --cov=src --cov-report=term-missing
```

## CI
- `.github/workflows/ci.yml` runs **lint** and **tests** across the Python matrix and uploads coverage to Codecov.
- For **private repos**, set `CODECOV_TOKEN` in GitHub → Settings → Secrets and variables → Actions.

## Notes
- `.pylintrc` appends `src/` to `sys.path` and relaxes some rules for `tests/`.
- `pytest.ini` sets `pythonpath = src` for clean imports.
