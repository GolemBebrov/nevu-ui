from .color import *  # Импортируем все из colors.py (Color, Color_Type, Theme, Color.RED и т.д.)
from .style import *   # Импортируем все из style.py (Style, Align, default_style, Theme.DARK и т.д.)
from .widgets import *
from .layouts import *
from .menu import *
from .window import *
from .utils import *
from .ui_manager import *
from .nevuobj import NevuObject
from .animations import *
from .core_types import *

#бля это херня просто что бы пукет работал безэтой херни хуета полуается
__all__ = [ # Определяем публичный API пакета
    'Color', 'Color_Type',  # Из colors.py
    'Style', 'Align', 'default_style', # Из style.py
    'Widget', 'Label', 'Button', 'Empty_Widget','CheckBox', 'ImageWidget', 'GifWidget', 'Input', 'MusicPlayer',
    'LayoutType', 'Grid', 'CheckBoxGrid', 'Pages', 'Gallery_Pages', 'Infinite_Scroll', 'Appending_Layout_H', 'Appending_Layout_V', # Из layouts.py
    'Menu',
    'Event',
    'time', 'mouse', 'Time', 'Mouse', 'Keyboard',
    'RoundedSurface',
    'Group'
]