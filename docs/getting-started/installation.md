# Installation

## From PyPI

The recommended way to install the Anscombe Transform codec is via pip:

```bash
pip install anscombe-transform
```

## Development Installation

This project uses [hatch](https://hatch.pypa.io/latest/install/#installers) for managing the development environment.

You can install `hatch` via pip:

```bash
pip install hatch
```

Or [directly](https://hatch.pypa.io/latest/install/#installers).

```bash
# Run tests across all environments
hatch run test:pytest tests/

# Run tests for a specific Python/NumPy version
hatch run test.py3.11-2.2:pytest tests/

# Enter a development shell
hatch shell
```

See the [Contributing Guide](../contributing.md) for more details on development setup.
