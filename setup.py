from setuptools import setup, Extension
import numpy
import os
from Cython.Build import cythonize

pgo_mode = os.environ.get('PGO_MODE')

c_opts = [
    '-O3',
    '-march=x86-64-v3',
    '-mavx2',
    '-mfma',
    '-ffast-math',
    '-fopenmp',
    '-flto',
]

l_opts = ['-fopenmp', '-flto']

if pgo_mode == 'GENERATE':
    pgo_flags = ['-fprofile-generate']
    c_opts.extend(pgo_flags)
    l_opts.extend(pgo_flags)
elif pgo_mode == 'USE':
    pgo_flags = ['-fprofile-use', '-fprofile-correction']
    c_opts.extend(pgo_flags)
    l_opts.extend(pgo_flags)

cython_directives = {
    'language_level': "3",
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'nonecheck': False,
    'initializedcheck': False,
    'infer_types': True,
    'unraisable_tracebacks': True,
}

def get_extensions():
    extensions = [
        Extension(
            "nevu_ui.fast.nvvector2.nvvector2",
            ["src/nevu_ui/fast/nvvector2/nvvector2.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=c_opts,
            extra_link_args=l_opts,
        ),
        Extension(
            "nevu_ui.fast.nvrect.nvrect",
            ["src/nevu_ui/fast/nvrect/nvrect.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=c_opts,
            extra_link_args=l_opts,
        ),
        Extension(
            "nevu_ui.fast.nvparam.nvparam",
            ["src/nevu_ui/fast/nvparam/nvparam.pyx"],
            extra_compile_args=c_opts,
            extra_link_args=l_opts,
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "nevu_ui.fast.nevucobj.nevucobj",
            ["src/nevu_ui/fast/nevucobj/nevucobj.pyx"],
            extra_compile_args=c_opts,
            extra_link_args=l_opts,
            include_dirs=[numpy.get_include()]
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
            extra_compile_args=c_opts,
            extra_link_args=l_opts,
        )
    ]

    return cythonize(extensions, compiler_directives=cython_directives, annotate=True)

setup(
    ext_modules=get_extensions()
)