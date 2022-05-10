#!/usr/bin/env python3

from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    cmdclass={'build_ext':build_ext},
    setup_requires=['numpy','cython'],
    include_package_data=True,
    ext_modules=cythonize(["src/gdp/_dat.pyx", "src/gdp/_geographic.pyx"]),
)





