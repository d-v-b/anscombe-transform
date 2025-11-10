# Contributing

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

The project uses [pytest](https://docs.pytest.org/en/stable/) for testing. Tests are organized in the `tests/` directory.

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
