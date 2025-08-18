from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Мы явно описываем наше расширение
# Это более надежный способ, чем просто передавать строку в cythonize
ext_modules = [
    Extension(
        # 1. Имя модуля, как он будет импортироваться.
        # Точки создают структуру пакета.
        "nevu_ui.fast_shapes",

        # 2. Список исходных файлов. Здесь указываем правильный путь.
        ["src/nevu_ui/fast_shapes.pyx"]
    )
]

setup(
    ext_modules = cythonize(ext_modules),
    include_dirs=[numpy.get_include()]
)