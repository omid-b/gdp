#!/usr/bin/env python3

from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        # __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    cmdclass={'build_ext':build_ext},
    setup_requires=['numpy'],
    include_package_data=True,
    ext_modules=cythonize("src/gdp/_*.pyx"),
)

# from distutils.core import setup
# from Cython.Build import cythonize

# class get_numpy_include(object):
#     """Defer numpy.get_include() until after numpy is installed."""
#     def __str__(self):
#         import numpy
#         return numpy.get_include()

# setup(
# 	include_package_data=True,
# 	ext_modules=cythonize("src/gdp/_*.pyx"),
#     include_dirs=[get_numpy_include()]
# )




