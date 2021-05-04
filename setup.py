#!/usr/bin/env python3
from setuptools import setup

setup(
    python_requires='>=3.4',
    name="pysubdivx",
    description="Library to search and download subtitles from subdivx",
    author='Alex Left',
    author_email='alejandro.izquierdo.b@mrmilu.com',
    url='',
    version='0.3.0',
    packages=["subdivx"],
    license='GPL-v3',
    long_description=open('README.md').read(),
    install_requires=["patool", "BS4", "requests"]
)
