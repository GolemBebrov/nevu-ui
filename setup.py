from setuptools import setup, Extension
import numpy
def get_numpy_include():
    import numpy
    return numpy.get_include()

def get_extensions():
    from Cython.Build import cythonize

    extensions = [
        Extension(
            "nevu_ui.fast.nvvector2.nvvector2",
            ["src/nevu_ui/fast/nvvector2/nvvector2.pyx"],
            include_dirs=[numpy.get_include()],
        ),
        Extension(
            "nevu_ui.fast.logic.fast_logic",
            ["src/nevu_ui/fast/logic/fast_logic.pyx"],
            include_dirs=[get_numpy_include()]
        ),

        Extension(
            "nevu_ui.fast.shapes.fast_shapes",
            ["src/nevu_ui/fast/shapes/fast_shapes.pyx"],
            extra_compile_args=['-fopenmp'], 
            extra_link_args=['-fopenmp'],
            include_dirs=[get_numpy_include()]
        ),
        Extension(
            "nevu_ui.fast.zsystem.fast_zsystem",
            ["src/nevu_ui/fast/zsystem/fast_zsystem.pyx"],
            include_dirs=[numpy.get_include()],
        )

    ]
    return cythonize(extensions, compiler_directives={'language_level': "3"})


setup(
    ext_modules = get_extensions()
)