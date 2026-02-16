import pygame
import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import mouse
from nevu_ui.layouts import LayoutType
from nevu_ui.style import Style, default_style

#!!! Removed !!!#
class Pages:
    def __init__(self, deprecated = True):
        raise DeprecationWarning("Pages is deprecated")