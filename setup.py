from setuptools import setup, Extension
import numpy
import os

c_opts = ['-O3', '-march=native', '-ffast-math', '-fopenmp']
l_opts = ['-fopenmp']

cython_directives = {
    'language_level': "3",
    'boundscheck': False,  
    'wraparound': False,  
    'cdivision': True,   
    'nonecheck': False,   
    'initializedcheck': False 
}

def get_extensions():
    from Cython.Build import cythonize

    extensions = [
        Extension(
            "nevu_ui.fast.nvvector2.nvvector2",
            ["src/nevu_ui/fast/nvvector2/nvvector2.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=['-O3', '-march=native', '-ffast-math'],
        ),
        Extension(
            "nevu_ui.fast.logic.fast_logic",
            ["src/nevu_ui/fast/logic/fast_logic.pyx"],
            extra_compile_args=c_opts, 
            extra_link_args=l_opts,
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "nevu_ui.fast.shapes.fast_shapes",
            ["src/nevu_ui/fast/shapes/fast_shapes.pyx"],
            extra_compile_args=c_opts, 
            extra_link_args=l_opts,
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "nevu_ui.fast.zsystem.fast_zsystem",
            ["src/nevu_ui/fast/zsystem/fast_zsystem.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=['-O3'],
        )
    ]
    
    return cythonize(extensions, compiler_directives=cython_directives)

setup(
    ext_modules = get_extensions()
)