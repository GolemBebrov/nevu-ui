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

def get_extension(name: str, source: str) -> Extension:
    return Extension(
        name,
        [source],
        include_dirs=[numpy.get_include()],
        extra_compile_args=c_opts,
        extra_link_args=l_opts,
    )

def get_extensions():
    extensions = [
        get_extension(
            "nevu_ui.fast.nvvector2.nvvector2",
            "src/nevu_ui/fast/nvvector2/nvvector2.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvrect.nvrect",
            "src/nevu_ui/fast/nvrect/nvrect.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvparam.nvparam",
            "src/nevu_ui/fast/nvparam/nvparam.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nevucobj.nevucobj",
            "src/nevu_ui/fast/nevucobj/nevucobj.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nevucache.nevucache",
            "src/nevu_ui/fast/nevucache/nevucache.pyx"
        ),
        get_extension(
            "nevu_ui.fast.logic.fast_logic",
            "src/nevu_ui/fast/logic/fast_logic.pyx"
        ),
        get_extension(
            "nevu_ui.fast.shapes.fast_shapes",
            "src/nevu_ui/fast/shapes/fast_shapes.pyx"
        ),
        get_extension(
            "nevu_ui.fast.zsystem.fast_zsystem",
            "src/nevu_ui/fast/zsystem/fast_zsystem.pyx"
        ),
        get_extension(
            "nevu_ui.fast.raylib.nevu_raylib",
            "src/nevu_ui/fast/raylib/nevu_raylib.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvrendertex.nv_render_tex",
            "src/nevu_ui/fast/nvrendertex/nv_render_tex.pyx"
        ),
    ]

    return cythonize(extensions, compiler_directives=cython_directives, annotate=True)

setup(
    ext_modules=get_extensions()
)