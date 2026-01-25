"""Setup script for python-abraflexi."""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read() if os.path.exists("README.md") else ""

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="python-abraflexi",
    version="1.0.0",
    author="Vítězslav Dvořák",
    author_email="info@vitexsoftware.cz",
    description="Python library for AbraFlexi REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VitexSoftware/python-abraflexi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=["abraflexi", "flexibee", "api", "rest", "accounting", "erp"],
    project_urls={
        "Bug Reports": "https://github.com/VitexSoftware/python-abraflexi/issues",
        "Source": "https://github.com/VitexSoftware/python-abraflexi",
    },
)
