from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "helpers-c",
    ext_modules = cythonize("helpers.py")
)
