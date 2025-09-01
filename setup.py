from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

ext_modules = [
    Extension(
        "nevu_ui.fast_logic",
        ["src/nevu_ui/fast_logic.pyx"],
    ),
    Extension(
        "nevu_ui.fast_shapes",
        ["src/nevu_ui/fast_shapes.pyx"],
    ),

]

setup(
    ext_modules = cythonize(ext_modules),
    include_dirs=[numpy.get_include()]
)