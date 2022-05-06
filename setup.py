#!/usr/bin/env python3

from distutils.core import setup
from Cython.Build import cythonize

setup(
	include_package_data=True,
	ext_modules=cythonize("src/gdp/_*.pyx"),
    include_dirs=[get_numpy_include()]
)


class get_numpy_include(object):
    """Defer numpy.get_include() until after numpy is installed."""
    def __str__(self):
        import numpy
        return numpy.get_include()


