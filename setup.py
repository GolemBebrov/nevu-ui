from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Явно описываем наше расширение
ext_modules = [
    Extension(
        # Имя модуля для импорта
        "nevu_ui.fast_logic",
        # Путь к исходному файлу от корня проекта
        ["src/nevu_ui/fast_logic.pyx"]
    )
]

setup(
    ext_modules = cythonize(ext_modules),
    # Не забываем указать заголовочные файлы NumPy
    include_dirs=[numpy.get_include()]
)