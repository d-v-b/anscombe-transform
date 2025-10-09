# Installation

## From PyPI

The recommended way to install the Anscombe Transform codec is via pip:

```bash
pip install anscombe-transform
```

## From Source

For development or to get the latest unreleased features:

```bash
git clone https://github.com/datajoint/anscombe-transform.git
cd anscombe-transform
pip install -e .
```

## Requirements

- Python >= 3.11
- zarr >= 3.1.2
- scikit-learn
- numpy

## Optional Dependencies

For running tests and examples:

```bash
pip install anscombe-transform[test]
```

This includes:
- pytest
- pytest-cov
- nbmake (for testing notebooks)
- scipy
- imageio
- matplotlib

## Verifying Installation

You can verify the installation by running:

```python
import anscombe_transform
print(anscombe_transform.__version__)
```

Or run the test suite:

```bash
pytest tests/
```

## Development Installation

For contributors using Hatch:

```bash
# Install hatch
pip install hatch

# Run tests across all environments
hatch run test:pytest tests/

# Run tests for a specific Python/NumPy version
hatch run test.py3.11-2.2:pytest tests/

# Enter a development shell
hatch shell
```

See the [Contributing Guide](../contributing.md) for more details on development setup.
