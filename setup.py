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
            "/arch:AVX2",
            "/fp:fast",
            "/openmp",
            "/GL",
        ]
        l_opts = [
            "/LTCG",
        ]
    else:
        c_opts = [
            "-std=c++17",
            "-O3",
            "-march=x86-64-v3",
            "-mavx2",
            "-mfma",
            "-ffast-math",
            "-fopenmp",
            "-flto",
        ]
        l_opts = [
            "-fopenmp",
            "-flto",
        ]

    cython_directives = {
        "language_level": "3",
        "boundscheck": False,
        "wraparound": False,
        "cdivision": True,
        "nonecheck": False,
        "initializedcheck": False,
        "infer_types": True,
        "unraisable_tracebacks": True,
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
        extra_compile_args=c_opts,
        extra_link_args=l_opts,
        language="c++",
    )


def get_extensions():
    extensions = [
        get_extension(
            "nevu_ui.fast.nvvector2.nvvector2",
            "src/nevu_ui/fast/nvvector2/nvvector2.pyx",
        ),
        get_extension(
            "nevu_ui.fast.nvrect.nvrect", "src/nevu_ui/fast/nvrect/nvrect.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvparam.nvparam", "src/nevu_ui/fast/nvparam/nvparam.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nevucobj.nevucobj", "src/nevu_ui/fast/nevucobj/nevucobj.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nevucache.nevucache",
            "src/nevu_ui/fast/nevucache/nevucache.pyx",
        ),
        get_extension(
            "nevu_ui.fast.logic.fast_logic", "src/nevu_ui/fast/logic/fast_logic.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvshader.nvshader", "src/nevu_ui/fast/nvshader/nvshader.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvdisplay.display", "src/nevu_ui/fast/nvdisplay/display.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvraygrad.nvraygrad",
            "src/nevu_ui/fast/nvraygrad/nvraygrad.pyx",
        ),
        get_extension(
            "nevu_ui.fast.shapes.fast_shapes", "src/nevu_ui/fast/shapes/fast_shapes.pyx"
        ),
        get_extension(
            "nevu_ui.fast.zsystem.fast_zsystem",
            "src/nevu_ui/fast/zsystem/fast_zsystem.pyx",
        ),
        get_extension(
            "nevu_ui.fast.raylib.nevu_raylib", "src/nevu_ui/fast/raylib/nevu_raylib.pyx"
        ),
        get_extension(
            "nevu_ui.fast.nvrendertex.nv_render_tex",
            "src/nevu_ui/fast/nvrendertex/nv_render_tex.pyx",
        ),
        get_extension(
            "nevu_ui.fast.nvspecific.nvspec", "src/nevu_ui/fast/nvspecific/nvspec.pyx"
        ),
    ]

    return cythonize(
        extensions,
        compiler_directives=cython_directives,
        annotate=not no_opt,
        include_path=["src"],
        nthreads=os.cpu_count() or 8,
    )


setup(
    ext_modules=get_extensions(),
    package_dir={"": "src"},
    cmdclass={"build_ext": FastBuildExt},
)
