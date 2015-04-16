from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "hands-c",
    ext_modules = cythonize("hands.py")
)
