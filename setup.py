#!/usr/bin/env python3

"""gdp

Geophysical Data Processing using Python!

"""

import re
import os
import sys
import numpy
from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext

ext_kwargs = {}
if os.environ.get("DISC_COV", None) is not None:
    ext_kwargs["define_macros"].append(("CYTHON_TRACE_NOGIL", 1))

extensions = [
    Extension(
        name="gdp._extensions._geographic",
        sources=[os.path.join("src", "gdp", "_extensions", "_geographic.pyx")],
        include_dirs=[numpy.get_include()],
        language="c",
        **ext_kwargs
    ),
    Extension(
        name="gdp._extensions._funcs",
        sources=[os.path.join("src", "gdp", "_extensions", "_funcs.pyx")],
        include_dirs=[numpy.get_include()],
        language="c",
        **ext_kwargs
    ),
]

# cmdclass['bdist_wheel']
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            self.root_is_pure = False
            _bdist_wheel.finalize_options(self)

except ImportError:
    bdist_wheel = None


# cmdclass['_build_ext']
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        self.include_dirs.append(numpy.get_include())


# read package version; variable: __version__
with open("src/gdp/_version.py") as fp:
    exec(fp.read())


setup_kwargs = {}
setup_kwargs["name"] = "gdp"
setup_kwargs["version"] = __version__
setup_kwargs["cmdclass"] = {"bdist_wheel": bdist_wheel, "build_ext": build_ext}
setup_kwargs["ext_modules"] = cythonize(
    extensions, compiler_directives={"language_level": 3}
)

setup(**setup_kwargs)


