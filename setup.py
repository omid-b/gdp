#!/usr/bin/env python3

import sys
import platform
from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext

cmdclass = {}

if platform.python_implementation() == 'CPython':
	try:
		import wheel.bdist_wheel
	except:
		pass
	else:
		class bdist_wheel(wheel.bdist_wheel.bdist_wheel):
			def finalize_options(self):
				self.py_limited_api = 'cp3{}'.format(sys.version_info[1])
				super().finalize_options()


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        import numpy
        self.include_dirs.append(numpy.get_include())


cmdclass['bdist_wheel'] = bdist_wheel
cmdclass['build_ext'] = build_ext


extensions = [
    Extension("gdp._funcs", ["src/gdp/_funcs.pyx"], py_limited_api=True, define_macros=[('CYTHON_LIMITED_API', '1')]),
    Extension("gdp._geographic", ["src/gdp/_geographic.pyx"], py_limited_api=True, define_macros=[('CYTHON_LIMITED_API', '1')]),
]


setup(
    cmdclass=cmdclass,
    setup_requires=['numpy','cython'],
    include_package_data=True,
    ext_modules=cythonize(extensions)
)





