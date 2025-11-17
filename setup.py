#!/usr/bin/env python3
"""
Setup script for Python Threading Learning App
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="python-threading-examples",
    version="1.0.0",
    description="Comprehensive Python threading examples and learning materials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Python Threading Learning Project",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        # No required dependencies - uses Python standard library only!
    ],
    extras_require={
        "qt": ["PyQt6>=6.4.0"],  # OR PySide6>=6.4.0
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "threading-examples=launcher.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="threading concurrency parallelism education learning examples",
)
