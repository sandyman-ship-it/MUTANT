#!/usr/bin/env python
from mutant import version
from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(
    name="mutant",
    version=version,
    long_description=__doc__,
    url="https://github.com/Clinical-Genomics/MUTANT",
    author="Isak Sylvin",
    author_email='isak.sylvin@scilifelab.se',
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['mutant=mutant.cli:root'],
    },
)
