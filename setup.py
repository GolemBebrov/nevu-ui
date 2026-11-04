import os
import sys

import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

no_opt = sys.flags.optimize > 0
if "-O" in sys.argv:
    no_opt = True
    sys.argv[:] = [arg for arg in sys.argv if arg != "-O"]

if no_opt:
    os.environ["CFLAGS"] = "-O0 -pipe -g0 -w"
    os.environ["CXXFLAGS"] = "-O0 -pipe -g0 -w"

    if sys.platform == "win32":
        c_opts = [
            "/std:c++17",
            "/Od",
            "/MP",
            "/w",
        ]
        l_opts = []
    else:
        c_opts = [
            "-std=c++17",
            "-O0",
            "-pipe",
            "-fno-var-tracking",
            "-g0",
            "-w",
        ]
        l_opts = []

    macros = []

    cython_directives = {
        "language_level": "3",
        "boundscheck": True,
        "wraparound": True,
        "cdivision": False,
        "nonecheck": True,
        "initializedcheck": True,
        "infer_types": True,
        "unraisable_tracebacks": True,
    }
else:
    if sys.platform == "win32":
        c_opts = [
            "/std:c++17",
            "/O2",
            "/Ob3",
            "/Oi",
            "/Ot",
            "/arch:AVX2",
            "/fp:fast",
            "/GL",
            "/Gw",
            "/Gy",
            "/GS-",
        ]
        l_opts = [
            "/LTCG",
            "/OPT:REF",
            "/OPT:ICF",
        ]
    else:
        c_opts = [
            "-std=c++17",
            "-O3",
            "-march=x86-64-v3",
            "-mtune=native",
            "-mavx2",
            "-mfma",
            "-ffast-math",
            "-flto=auto",
            "-fno-semantic-interposition",
            "-fno-plt",
            "-fomit-frame-pointer",
            "-fstrict-aliasing",
            "-fvisibility-inlines-hidden",
        ]
        l_opts = [
            "-flto=auto",
            "-Wl,-O3",
            "-Wl,-Bsymbolic-functions",
            "-Wl,--as-needed",
        ]

    macros = [
        ("NDEBUG", "1"),
        ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ("CYTHON_WITHOUT_ASSERTIONS", "1"),
        ("CYTHON_CLINE_IN_TRACEBACK", "0"),
    ]

    cython_directives = {
        "language_level": "3",
        "boundscheck": False,
        "wraparound": False,
        "cdivision": True,
        "cdivision_warnings": False,
        "nonecheck": False,
        "initializedcheck": False,
        "infer_types": True,
        "unraisable_tracebacks": False,
        "binding": False,
        "overflowcheck": False,
        "profile": False,
        "linetrace": False,
        "embedsignature": False,
        "auto_pickle": False,
        "optimize.use_switch": True,
        "optimize.unpack_method_calls": True,
    }


class FastBuildExt(build_ext):
    def initialize_options(self):
        super().initialize_options()
        self.parallel = os.cpu_count() or 8


def get_extension(name: str, source: str) -> Extension:
    return Extension(
        name,
        [source],
        include_dirs=[numpy.get_include(), "src"],
        define_macros=macros,
        extra_compile_args=c_opts,
        extra_link_args=l_opts,
        language="c++",
    )


def get_extensions():
    extensions = [
        get_extension(
            "nevu_ui.cython.vector2.vector2",
            "src/nevu_ui/cython/vector2/vector2.pyx",
        ),
        get_extension(
            "nevu_ui.cython.rect.rect", "src/nevu_ui/cython/rect/rect.pyx"
        ),
        get_extension(
            "nevu_ui.cython.nvparam.nvparam", "src/nevu_ui/cython/nvparam/nvparam.pyx"
        ),
        get_extension(
            "nevu_ui.cython.nevucobject.nevucobject", "src/nevu_ui/cython/nevucobject/nevucobject.pyx"
        ),
        get_extension(
            "nevu_ui.cython.font.font", "src/nevu_ui/cython/font/font.pyx"
        ),
        get_extension(
            "nevu_ui.cython.surface.surface", "src/nevu_ui/cython/surface/surface.pyx"
        ),
        get_extension(
            "nevu_ui.cython.callbacks.callbacks", "src/nevu_ui/cython/callbacks/callbacks.pyx"
        ),
        get_extension(
            "nevu_ui.cython.cache.cache",
            "src/nevu_ui/cython/cache/cache.pyx",
        ),
        get_extension(
            "nevu_ui.cython.logic.logic", "src/nevu_ui/cython/logic/logic.pyx"
        ),
        get_extension(
            "nevu_ui.cython.raylib_shader.raylib_shader", "src/nevu_ui/cython/raylib_shader/raylib_shader.pyx"
        ),
        get_extension(
            "nevu_ui.cython.display.display", "src/nevu_ui/cython/display/display.pyx"
        ),
        get_extension(
            "nevu_ui.cython.raylib_gradient.raylib_gradient",
            "src/nevu_ui/cython/raylib_gradient/raylib_gradient.pyx",
        ),
        get_extension(
            "nevu_ui.cython.shapes.shapes", "src/nevu_ui/cython/shapes/shapes.pyx"
        ),
        get_extension(
            "nevu_ui.cython.z_system.z_system",
            "src/nevu_ui/cython/z_system/z_system.pyx",
        ),
        get_extension(
            "nevu_ui.cython.raylib.raylib", "src/nevu_ui/cython/raylib/raylib.pyx"
        ),
    ]

    return cythonize(
        extensions,
        compiler_directives=cython_directives,
        annotate=False,
        include_path=["src"],
        nthreads=os.cpu_count() or 8,
    )


setup(
    ext_modules=get_extensions(),
    package_dir={"": "src"},
    cmdclass={"build_ext": FastBuildExt},
)
