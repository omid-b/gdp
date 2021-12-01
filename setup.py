#!/usr/bin/env python3

from setuptools import setup
from Cython.Build import cythonize

setup(
	include_package_data=True,
	ext_modules=cythonize("src/gdp/_*.pyx")
)

