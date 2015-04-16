from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "ofcp-c",
    ext_modules = cythonize("OFCP_AI.py")
)
