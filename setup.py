#!/usr/bin/env python3

from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        import numpy
        self.include_dirs.append(numpy.get_include())

# extensions = [
#     Extension("_dat", ["src/gdp/_dat.pyx"]),
#     Extension("_geographic", ["src/gdp/_geographic.pyx"]),
# ]

extensions = [
    Extension("_dat",
              ["src/gdp/_dat.pyx"],
              py_limited_api=True,
              define_macros=[('CYTHON_LIMITED_API', '1')]
             ),
    Extension("_geographic",
              ["src/gdp/_geographic.pyx"],
              py_limited_api=True,
              define_macros=[('CYTHON_LIMITED_API', '1')]
             ),
]

setup(
    cmdclass={'build_ext':build_ext},
    setup_requires=['numpy','cython'],
    include_package_data=True,
    ext_modules=cythonize(extensions)
)





