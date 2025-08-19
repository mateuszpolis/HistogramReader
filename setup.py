#!/usr/bin/env python3
"""Setup script for the HistogramReader package."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="histogram-reader",
    version="1.0.0",
    author="Mateusz Polis, mateusz.polis@cern.ch",
    description="Histogram Reader Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "tkinter-tooltip>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "histogram-reader=histogram_reader.main:main",
        ],
    },
)
