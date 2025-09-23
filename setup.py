from setuptools import setup, Extension

def get_numpy_include():
    import numpy
    return numpy.get_include()

def get_extensions():
    from Cython.Build import cythonize

    extensions = [
        Extension(
            "nevu_ui.fast_logic",
            ["src/nevu_ui/fast_logic.pyx"],
            include_dirs=[get_numpy_include()]
        ),
        Extension(
            "nevu_ui.fast_shapes",
            ["src/nevu_ui/fast_shapes.pyx"],
            include_dirs=[get_numpy_include()]
        ),
        Extension(
            "nevu_ui.fast_zsystem",
            ["src/nevu_ui/fast_zsystem.pyx"],
            include_dirs=[get_numpy_include()]
        ),
    ]
    return cythonize(extensions, compiler_directives={'language_level': "3"})


setup(
    ext_modules = get_extensions()
)