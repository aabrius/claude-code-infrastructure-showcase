#!/usr/bin/env python3
"""
Setup script for Google Ad Manager API integration package.
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "AI-friendly Google Ad Manager API integration with MCP, REST API, and Python SDK"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f.readlines() 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "googleads>=44.0.0",
        "google-api-python-client>=2.100.0",
        "google-auth>=2.23.0",
        "google-auth-oauthlib>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
    ]

# Optional dependencies for different features
extras_require = {
    "mcp": [
        "fastmcp>=1.0.0",
    ],
    "api": [
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "httpx>=0.24.0",
    ],
    "excel": [
        "openpyxl>=3.1.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
    ],
}

# Convenience extras
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="gam-api",
    version="1.0.0",
    author="GAM API Team",
    author_email="support@example.com",
    description="AI-friendly Google Ad Manager API integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/gam-api",
    project_urls={
        "Documentation": "https://gam-api.readthedocs.io/",
        "Source": "https://github.com/example/gam-api",
        "Tracker": "https://github.com/example/gam-api/issues",
    },
    packages=find_packages(where=".", include=["src*"]),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [],
    },
    include_package_data=True,
    package_data={
        "src": [
            "config/*.yaml",
            "config/*.example",
        ],
    },
    zip_safe=False,
    keywords=[
        "google", "ad-manager", "gam", "advertising", "api", "mcp", "ai", "assistant",
        "reports", "analytics", "programmatic", "rest", "sdk"
    ],
    license="MIT",
    platforms=["any"],
)