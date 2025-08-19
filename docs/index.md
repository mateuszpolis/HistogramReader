# HistogramReader Documentation

Welcome to the HistogramReader module documentation! This module provides comprehensive histogram reader capabilities for FIT detector data.

## Overview

The HistogramReader module is part of the FIT Detector Toolkit and provides:

- **Data Processing**: Import and process FIT detector data
- **Statistical Analysis**: Advanced statistical analysis of ageing patterns
- **Interactive Visualization**: Modern GUI for data exploration
- **Export Capabilities**: Export results in various formats

## Quick Start

### Installation

```bash
pip install histogram-reader
```

### Basic Usage

```python
from histogram_reader import HistogramReaderApp

# Launch the GUI application
app = HistogramReaderApp()
app.run()
```

### Programmatic Usage

```python
import histogram_reader

# Check if module is available
if histogram_reader.is_module_available():
    # Launch through the launcher interface
    histogram_reader.launch_module()
```

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Contents:

api
```

## Features

### Data Sources
- Multiple file format support
- Flexible data import options
- Batch processing capabilities

### Analysis Tools
- Gaussian fitting
- Statistical analysis
- Trend detection
- Reference channel analysis

### Visualization
- Interactive plots
- Real-time data exploration
- Customizable charts
- Export options

### GUI Features
- Modern, intuitive interface
- Cross-platform compatibility
- Keyboard shortcuts
- Comprehensive help system

## Getting Help

- **Documentation**: This documentation covers all aspects of the module
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/mateuszpolis/histogram-reader/issues)
- **Contributing**: See our [Contributing Guide](https://github.com/mateuszpolis/histogram-reader/blob/main/CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
