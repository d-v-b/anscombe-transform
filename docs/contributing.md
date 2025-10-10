# Contributing

Thank you for your interest in contributing to the Anscombe Transform codec! This guide will help you get started.

## Development Setup

### Prerequisites

- Python >= 3.11
- [Hatch](https://hatch.pypa.io/) for environment management
- Git

### Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/anscombe-transform.git
cd anscombe-transform
```

2. **Install Hatch**

```bash
pip install hatch
```

3. **Create a development environment**

```bash
# See available environments
hatch env show

# Enter a test environment
hatch shell test.py3.11-2.2
```

4. **Run tests**

```bash
# Run all tests
hatch run test:pytest tests/

# Run specific test file
hatch run test:pytest tests/test_codec.py

# Run with coverage
hatch run test:pytest tests/ --cov=src/anscombe_transform
```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or fix:
```bash
git checkout -b feature/my-new-feature
```

2. Make your changes following the coding standards below

3. Run tests to ensure everything works:
```bash
hatch run test:pytest tests/
```

4. Run linting and formatting:
```bash
hatch run test:ruff check src/ tests/
hatch run test:ruff format src/ tests/
```

### Testing

The project uses pytest for testing. Tests are organized in the `tests/` directory:

- `test_codec.py` - Direct codec encode/decode tests
- `test_zarr.py` - Zarr integration tests for V2 and V3
- `test_notebooks.py` - Notebook execution tests

**Writing Tests**

- Use the `nearly_equal()` fixture for comparing arrays with tolerance
- Test with synthetic Poisson-distributed data
- Cover both Zarr V2 and V3 implementations
- Include edge cases (zero values, large values, etc.)

Example:
```python
def test_my_feature(nearly_equal):
    # Create test data
    data = np.random.poisson(lam=50, size=(10, 100, 100)).astype('int16')

    # Test your feature
    result = my_function(data)

    # Assert with tolerance
    assert nearly_equal(result, expected, conversion_gain=2.5)
```

### Running Tests Across Environments

Test against multiple Python and NumPy versions:

```bash
# Run on all environments
hatch run test:pytest tests/

# Run on specific Python version
hatch run test.py3.12-2.2:pytest tests/

# Test against upstream dependencies
hatch run upstream:pytest tests/
```

## Coding Standards

### Style Guide

- Follow PEP 8
- Use Ruff for linting and formatting
- Maximum line length: 100 characters
- Use type hints for all public functions

### Documentation

- Write docstrings for all public functions and classes
- Use NumPy-style docstrings
- Include examples in docstrings where helpful
- Update relevant documentation in `docs/`

Example docstring:
```python
def my_function(data: np.ndarray, param: float) -> np.ndarray:
    """
    Brief description of what this function does.

    Parameters
    ----------
    data : np.ndarray
        Description of data parameter
    param : float
        Description of param parameter

    Returns
    -------
    np.ndarray
        Description of return value

    Examples
    --------
    >>> data = np.array([1, 2, 3])
    >>> result = my_function(data, 2.5)
    """
    pass
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, Union
import numpy as np

def process_data(
    data: np.ndarray,
    conversion_gain: float,
    zero_level: Optional[float] = None
) -> tuple[np.ndarray, dict]:
    """Process data with optional parameters."""
    pass
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if you've changed APIs or added features

2. **Add tests** for new functionality

3. **Update CHANGELOG** if significant changes were made

4. **Push your branch** to your fork:
```bash
git push origin feature/my-new-feature
```

5. **Open a Pull Request** on GitHub:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI tests pass

### Pull Request Checklist

Before submitting, verify:

- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings written
- [ ] CHANGELOG updated (if applicable)

## Building Documentation

### Local Documentation Server

```bash
# Install docs dependencies
hatch run docs:mkdocs serve

# View at http://127.0.0.1:8000
```

### Building Documentation

```bash
# Build static site
hatch run docs:mkdocs build

# Output in site/
```

## Project Structure

```
anscombe-transform/
├── src/
│   └── anscombe_transform/
│       ├── __init__.py
│       ├── codec.py         # Main codec implementations
│       ├── estimate.py      # Parameter estimation
│       └── version.py       # Version info (auto-generated)
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_codec.py       # Codec tests
│   ├── test_zarr.py        # Zarr integration tests
│   └── test_notebooks.py   # Notebook tests
├── docs/                   # Documentation source
├── examples/               # Example notebooks
├── pyproject.toml          # Project configuration
└── mkdocs.yml             # Documentation config
```

## Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/datajoint/anscombe-transform/discussions)
- **Bug reports?** Open an [Issue](https://github.com/datajoint/anscombe-transform/issues)
- **Need to chat?** Contact the maintainers

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
