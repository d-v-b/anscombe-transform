[![PyPI version](https://badge.fury.io/py/anscombe-transform.svg)](https://badge.fury.io/py/anscombe-transform) ![tests](https://github.com/datajoint/anscombe-transform/actions/workflows/tests.yaml/badge.svg)

# Anscombe transform

This codec is designed for compressing image recordings with Poisson noise, which are produced by photon-limited modalities such multiphoton microscopy, radiography, and astronomy.

The codec assumes that the video is linearly encoded with a potential offset (`zero_level`) and that the `photon_sensitivity` (the average increase in intensity per photon) is either already known or can be accurately estimated from the data.

The codec re-quantizes the grayscale efficiently with a square-root-like transformation to equalize the noise variance across the grayscale levels: the [Anscombe Transform](https://en.wikipedia.org/wiki/Anscombe_transform).
This results in a smaller number of unique grayscale levels and significant improvements in the compressibility of the data without sacrificing signal accuracy.

To use the codec, one must supply two pieces of information: `zero_level` (the input value corresponding to the absence of light) and `photon_sensitivity` (levels/photon).

The codec is used in Zarr as a filter prior to compression.

[Zarr](https://zarr.readthedocs.io/en/stable/index.html).

## Installation

Install via `pip`:

```
pip install anscombe-transform
```

## Development Setup

### Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/anscombe-transform.git
cd anscombe-transform
```

2. **Install Hatch**

Via pip:

```bash
pip install hatch
```

Or [directly](https://hatch.pypa.io/latest/install/#installers).


3. **Create a development environment**

```bash
# See available environments
hatch env show

# Enter a test environment
hatch shell test.py3.11-2.2
```

Install [pre-commit](https://pre-commit.com/#install)

4. **Run tests**

```bash
# Run all tests
hatch run test:pytest tests/

# Run specific test file
hatch run test:pytest tests/test_codec.py

# Run with coverage
hatch run test:pytest tests/ --cov=src/anscombe_transform
```

### Testing

The project uses [pytest](https://docs.pytest.org/en/stable/) for testing. Tests are found in the `tests/` directory.

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


## Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/datajoint/anscombe-transform/discussions)
- **Bug reports?** Open an [Issue](https://github.com/datajoint/anscombe-transform/issues)

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](https://opensource.org/license/mit).
