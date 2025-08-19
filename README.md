# HistogramReader

FIT Detector Histogram Reader Module - A GUI application for reading and analyzing histogram data.

## Overview

HistogramReader is a standalone GUI application that can also be used as a module from other applications. It provides tools for reading, analyzing, and visualizing histogram data from FIT detectors.

## Installation

### As a standalone application:
```bash
pip install histogram-reader
```

### For development:
```bash
git clone <repository-url>
cd HistogramReader
pip install -e .[dev]
```

## Usage

### As a standalone application:
```bash
histogram-reader
```

### As a module:
```python
import histogram_reader
# Use the module functionality
```

## Development

### Setup
```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=histogram_reader
```

### Code Quality
```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

## Contributing

This project uses conventional commits. Please ensure your commit messages follow the format:
```
type(scope): description
```

## License

MIT License - see LICENSE file for details.
