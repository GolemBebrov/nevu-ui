import pygame
import copy
import math
import numpy as np
from PIL import Image
from collections.abc import Callable

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.logic import logic_update_helper
from nevu_ui.core_types import HoverState

from nevu_ui.animations import (
    Animation, AnimationManager
)
from nevu_ui.rendering import (
    OutlinedRoundedRect, RoundedRect, AlphaBlit, Gradient
)
from nevu_ui.style import (
    Style, default_style
)
from nevu_ui.core_types import (
    _QUALITY_TO_RESOLUTION, Quality, Align, EventType, CacheType
)
from nevu_ui.utils import (
     Cache, mouse
)
from nevu_ui.fast.nvvector2 import (
    NvVector2 as Vector2, NvVector2
)
from nevu_ui.color import (
    Color, ColorPair, ColorSubTheme, ColorTheme, SubThemeRole, PairColorRole, TupleColorRole
)

class Widget(NevuObject):
    _alt: bool
    will_resize: bool
    clickable: bool
    hoverable: bool
    fancy_click_style: bool
    
    def __init__(self, size: Vector2 | list, style: Style = default_style, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        #=== Text Cache ===
        self._init_text_cache()
        #=== Alt ===
        self._init_alt()
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("alt", bool, False, getter=self._alt_getter, setter=self._alt_setter)
        self._add_constant("will_resize", bool, True)
        self._add_constant("clickable", bool, False)
        self._add_constant("hoverable", bool, True)
        self._add_constant("fancy_click_style", bool, True)
        self._add_constant("resize_bg_image", bool, False)
        self._add_constant("z", int, 1)
        
    def _init_text_cache(self):
        self._text_baked = None
        self._text_surface = None
        self._text_rect = None
        
    def _init_objects(self):
        super()._init_objects()
        self.quality = Quality.Decent
        self._subtheme_role = SubThemeRole.SECONDARY
        self.renderer = BackgroundRenderer(self)
        
    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()
        self._dr_coordinates_new = self.coordinates.copy()

    def _init_booleans(self):
        super()._init_booleans()
        self._optimized_dirty_rect_for_short_animations = True
        self._original_alt = self._alt

    def _init_alt(self):
        if self.alt: self._subtheme_font, self._subtheme_content = self._alt_subtheme_font, self._alt_subtheme_content
        else: self._subtheme_font, self._subtheme_content = self._main_subtheme_font, self._main_subtheme_content
    
    def _lazy_init(self, size: Vector2 | list):
        super()._lazy_init(size)
        self.surface = pygame.Surface(size, flags = pygame.SRCALPHA)
        #if isinstance(self.style.gradient, Gradient): self._draw_gradient()

    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        self._init_alt()
        self._on_style_change()
        
    def _alt_getter(self):
        return self._alt

    def _alt_setter(self, value):
        self._alt = value
        self._init_alt()
        self._on_style_change()
        
    def _toogle_click_style(self):
        if not self.clickable: return
        if self.fancy_click_style:
            self.alt = not self.alt
        else:
            self._on_style_change()
            
    def _on_hover_system(self):
        super()._on_hover_system()
        if not self.hoverable: return
        self._on_style_change()
    def _on_keyup_system(self):
        super()._on_keyup_system()
        if not self.clickable: return
        self._toogle_click_style()
    def _on_click_system(self):
        super()._on_click_system()
        if not self.clickable: return
        self._toogle_click_style()
    def _on_unhover_system(self):
        super()._on_unhover_system()
        if not self.hoverable: return
        self._on_style_change()
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        if self.alt != self._original_alt:
            self.alt = self._original_alt
            
    def clear_all(self):
        """
        Clears all cached data by invoking the clear method on the cache. 
        !WARNING!: may cause bugs and errors
        """
        self.cache.clear()
        
    def clear_surfaces(self):
        """
        Clears specific cached surface-related data by invoking the clear_selected 
        method on the cache with a whitelist of CacheTypes related to surfaces. 
        This includes Image, Scaled_Gradient, Surface, and Borders.
        Highly recommended to use this method instead of clear_all.
        """
        self.cache.clear_selected(whitelist = [CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Background, CacheType.Background])
    
    def _on_style_change(self):
        self.clear_surfaces()
        self._changed = True
        
    def _update_image(self, style: Style | None = None):
        try:
            if not style: style = self.style
            if not style.bgimage: return
            img = pygame.image.load(style.bgimage)
            img.convert_alpha()
            self.cache.set(CacheType.Image, pygame.transform.scale(img, self._csize))
        except Exception: self.cache.clear_selected(whitelist = [CacheType.Image])

    @property
    def _main_subtheme_content(self):
        return self._subtheme.color
    @property
    def _main_subtheme_font(self):
        return self._subtheme.oncolor

    @property
    def _alt_subtheme_content(self):
        return self._subtheme.container
    @property
    def _alt_subtheme_font(self):
        return self._subtheme.oncontainer
    @property
    def _rsize(self) -> NvVector2:
        bw = self.style.borderwidth
        return self._csize - (NvVector2(bw, bw)) /2

    @property
    def _rsize_marg(self) -> NvVector2:
        return (self._csize - self._rsize)/2
    
    def clone(self):
        return Widget(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    
    def primary_draw(self):
        super().primary_draw()
        if self._changed:
            if type(self) == Widget: self._changed = False
            self._dirty_rect.append(self.get_rect())
            TRANSPARENT = (0, 0, 0, 0)
            self.surface.fill(TRANSPARENT)
            self.surface = self.renderer._scale_background(self._csize) if self.will_resize else self.renderer._generate_background()
            
    def logic_update(self):
        super().logic_update()
        new_dr_old, new_first_update = logic_update_helper(
        self._optimized_dirty_rect_for_short_animations,
        self.animation_manager,
        self._csize,
        self.master_coordinates,
        self._dirty_rect,
        self._dr_coordinates_old,
        self._first_update,
        self.first_update_functions,
        self._resize_ratio,
        self._master_z_handler or self._master_z_handler_placeholder
        )
    
        self._dr_coordinates_old = new_dr_old
        self._first_update = new_first_update

    def _boot_up(self):
        pass
        #print(f"booted widget: {self}")

    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False,
                  alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, continuous: bool = False):
        if continuous: self._bake_text_single_continuous(text); return
        is_popped = False
        ifnn = False

        words = list(text)
        marg = ""
        lines = []
        current_line = ""

        renderFont = self.get_font() 
        line_height = renderFont.size("a")[1]

        if words_indent:
            words = text.strip().split()
            marg = " "

        for word in words:
            if word == '\n': ifnn = True
            try:
                w = word[0] + word[1]
                if w == '\ '.strip()+"n": ifnn = True # type: ignore
            except: pass
            if ifnn:
                lines.append(current_line)
                current_line = ""
                test_line = ""
                text_size = 0
                ifnn = False
                continue

            test_line = current_line + word + marg
            text_size = renderFont.size(test_line)
            if text_size[0] > self.relx(self.size[0]):
                lines.append(current_line)
                current_line = word + marg
            else: current_line = test_line
        lines.append(current_line)

        if not unlimited_y:
            while len(lines) * line_height > self._csize[1]:
                lines.pop(-1)
                is_popped = True

        self._text_baked = "\n".join(lines)

        if is_popped:
            if not unlimited_y:
                self._text_baked = self._text_baked[:-3] + "..."
                justify_y = False
            else: justify_y = True
        else: justify_y = False

        self._text_surface = renderFont.render(self._text_baked, True, self._subtheme_font)
        container_rect = self.surface.get_rect()
        text_rect = self._text_surface.get_rect()

        if alignx == Align.LEFT: text_rect.left = container_rect.left
        elif alignx == Align.CENTER: text_rect.centerx = container_rect.centerx
        elif alignx == Align.RIGHT: text_rect.right = container_rect.right

        if aligny == Align.TOP: text_rect.top = container_rect.top
        elif aligny == Align.CENTER: text_rect.centery = container_rect.centery
        elif aligny == Align.BOTTOM: text_rect.bottom = container_rect.bottom

        self._text_rect = text_rect

    def _bake_text_single_continuous(self, text: str):
        assert hasattr(self, "_entered_text")
        renderFont = self.get_font()
        self.font_size = renderFont.size(text)
        self._text_surface = renderFont.render(self._entered_text, True, self._subtheme.oncontainer) #type: ignore
        if not self.font_size[0] + self.relx(10) >= self._csize[0]: 
            self._text_rect = self._text_surface.get_rect(left = self.relx(10), centery = self._csize[1] / 2)
        else: self._text_rect = self._text_surface.get_rect(right = self.relx(self._csize[0] - 10), centery = self._csize[1] / 2)

    def resize(self, resize_ratio: Vector2):
        super().resize(resize_ratio)
        self._resize_ratio = resize_ratio

        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        self.clear_surfaces()
        self._update_image()
        
        self.surface = pygame.Surface(self._csize, flags = pygame.SRCALPHA)

        self._changed = True

class BackgroundRenderer:
    def __init__(self, root: Widget):
        assert isinstance(root, Widget)
        self.root = root
    def _draw_gradient(renderer, _set = False):
        self = renderer.root
        if not self.style.gradient: return
        
        cached_gradient = pygame.Surface(self.size*_QUALITY_TO_RESOLUTION[self.quality], flags = pygame.SRCALPHA)
        if self.style.transparency: cached_gradient = self.style.gradient.with_transparency(self.style.transparency).apply_gradient(cached_gradient)
        else: cached_gradient =  self.style.gradient.apply_gradient(cached_gradient)
        if _set:
            self.cache.set(CacheType.Gradient, cached_gradient)
        else:
            return cached_gradient
    def _scale_gradient(renderer, size = None):
        self = renderer.root
        if not self.style.gradient: return
        size = size or self.size * self._resize_ratio
        cached_gradient = self.cache.get_or_exec(CacheType.Gradient, renderer._draw_gradient)
        if cached_gradient is None: return
        target_size_vector = size
        target_size_tuple = (
            max(1, int(target_size_vector.x)), 
            max(1, int(target_size_vector.y))
        )
        cached_gradient = pygame.transform.smoothscale(cached_gradient, target_size_tuple)
        return cached_gradient
    def _create_surf_base(renderer, size = None, alt = False, radius = None):
        self = renderer.root
        needed_size = (self.size*self._resize_ratio).xy if size is None else size
        surf = pygame.Surface((int(needed_size[0]), int(needed_size[1])), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        color = self._subtheme_content if not alt else self._subtheme_font
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2

        radius = (self._style.borderradius * avg_scale_factor) if radius is None else radius
        surf.blit(RoundedRect.create_sdf([int(needed_size[0]), int(needed_size[1])], int(radius), color), (0, 0))
        return surf
    
    def _create_outlined_rect(renderer, size = None):
        self = renderer.root
        needed_size = (self.size*self._resize_ratio).xy if size is None else size
        if self.will_resize:
            avg_scale_factor = _QUALITY_TO_RESOLUTION[self.quality]
        else:
            avg_scale_factor = (self._resize_ratio[0] + self._resize_ratio[1]) / 2
        radius = self._style.borderradius * avg_scale_factor
        width = self._style.borderwidth * avg_scale_factor
        return OutlinedRoundedRect.create_sdf([int(needed_size[0]), int(needed_size[1])], int(radius), int(width), self._subtheme_font)
    
    def _generate_background(renderer):
        self = renderer.root
        resize_factor = _QUALITY_TO_RESOLUTION[self.quality] if self.will_resize else self._resize_ratio
        bgsurface = pygame.Surface(self.size * resize_factor, flags = pygame.SRCALPHA)
        if isinstance(self.style.gradient, Gradient):
            content_surf = self.cache.get_or_exec(CacheType.Scaled_Gradient, lambda: renderer._scale_gradient(self.size * resize_factor))
            if self.style.transparency: bgsurface.set_alpha(self.style.transparency)
        else: content_surf = self.cache.get(CacheType.Scaled_Gradient)
        if content_surf:
            bgsurface.blit(content_surf,(0,0))
        elif self._hover_state == HoverState.UN_HOVERED or not self.hoverable: bgsurface.fill(self._subtheme_content)
        elif self._hover_state == HoverState.CLICKED and not self.fancy_click_style: bgsurface.fill(Color.lighten(self._subtheme_content))
        else: bgsurface.fill(Color.darken(self._subtheme_content, 0.2))
        if self._style.bgimage:
            img = pygame.image.load(self._style.bgimage)
            img.convert_alpha()
            bgsurface.blit(pygame.transform.smoothscale(img, self.size * resize_factor),(0,0))
        if self._style.borderwidth > 0:
            border = self.cache.get_or_exec(CacheType.Borders, lambda: renderer._create_outlined_rect(self.size * resize_factor))
            if border:
                bgsurface.blit(border,(0,0))
        if self._style.borderradius > 0:
            mask_surf = self.cache.get_or_exec(CacheType.Surface, lambda: renderer._create_surf_base(self.size * resize_factor))
            if mask_surf:
                AlphaBlit.blit(bgsurface, mask_surf,(0,0))
        return bgsurface
    
    def _scale_background(renderer, size = None):
        self = renderer.root
        size = size if size else self.size*self._resize_ratio
        surf = self.cache.get_or_exec(CacheType.Background, renderer._generate_background)
        assert surf
        surf = pygame.transform.smoothscale(surf, (max(1, int(size.x)), max(1, int(size.y))))
        return surf
class Empty_Widget(Widget):
    def draw(self):
        pass

class Tooltip(Widget):
    def __init__(self, text, style: Style = default_style):
        self.text = text
        self.style = style
        self.size = (200,400)
        self.bake_text(self.text,False,True,self.style.text_align_x,self.style.text_align_y)
        raise NotImplementedError("Tooltip is not implemented yet, wait till 0.05")
    def draw(self):
        pass #TODO in version 0.6 :)
    
class Label(Widget):
    words_indent: bool
    def __init__(self, text: str, size: Vector2 | list, style: Style = default_style, **constant_kwargs):
        super().__init__(size, style)
        self._lazy_kwargs = {'size': size, 'text': text}
        self._changed = True
    def clone(self):
        return Label(self._lazy_kwargs['text'], self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("words_indent", bool, False)
    def _lazy_init(self, size: Vector2 | list, text: str): # type: ignore
        super()._lazy_init(size)
        assert isinstance(text, str)
        self._text = "" 
        self.text = text 
    @property
    def text(self):
        return self._text
    def _on_style_change(self):
        super()._on_style_change()
        #print(f"{self} style changed")
        self.bake_text(self._text, False, self.words_indent, self.style.text_align_x, self.style.text_align_y)
    @text.setter
    def text(self, text: str):
        self._changed = True
        self._text = text
        self.bake_text(text, False, self.words_indent, self.style.text_align_x, self.style.text_align_y)

    def resize(self, resize_ratio: Vector2):
        super().resize(resize_ratio)
        self._changed = True
        self.bake_text(self._text, False, self.words_indent, self.style.text_align_x, self.style.text_align_y)

    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self,style: Style):
        self._changed = True
        self._style = copy.deepcopy(style)
        
        self._update_image()

        if hasattr(self,'_text'):
            self.bake_text(self._text)

    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        if self._changed:
            assert self._text_surface is not None and self._text_rect is not None
            self.surface.blit(self._text_surface, self._text_rect)
        
    def secondary_draw_end(self):
        super().secondary_draw_end()
        if not type(self).__subclasses__():
            self._changed = False

class Button(Label):
    throw_errors: bool
    is_active: bool
    def __init__(self, function, text: str, size: Vector2 | list, style: Style = default_style, **constant_kwargs):
        super().__init__(text, size, style, **constant_kwargs)
        self.function = function
    def _init_booleans(self):
        super()._init_booleans()
        self.clickable = True
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("is_active", bool, True)
        self._add_constant("throw_errors", bool, False)

    def _on_click_system(self):
        super()._on_click_system()
        if self.function and self.is_active:
            try: self.function()
            except Exception as e:
                if self.throw_errors: raise e
                else: print(e)
                
    def clone(self):
        return Button(self.function,self._lazy_kwargs['text'], self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)

class Image(Widget):
    def __init__(self, size: Vector2 | list, image_path, style: Style, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self.image_path = image_path
        self._image_original = self.load_image
        self.image = self.image_orig
        self.resize(Vector2())
        
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.image = pygame.transform.scale(self.image_orig, self._csize)
        
    def draw(self):
        super().draw()
        if not self.visible:
            return
        self.surface.blit(self.image,[0,0])
        if self._style().radius > 0:
            self.surface = RoundedSurface.create(self.surface,int(self._style().radius))
        if self._changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
class GifWidget(Widget):
    def __init__(self,size,gif_path=None,style:Style=default_style,frame_duration=100):
        """
        Инициализирует виджет для отображения GIF-анимации.

        Args:
            coordinates (list): Координаты виджета [x, y].
            surf (pygame.Surface): Поверхность, на которой будет отображаться виджет.
            size (list, optional): Размеры виджета [ширина, высота]. Defaults to [100, 100].
            radius (int, optional): Радиус скругления углов. Defaults to 0.
            gif_path (str, optional): Путь к GIF-файлу. Defaults to None.
            frame_duration (int, optional): Длительность одного кадра в миллисекундах. Defaults to 100.
        """
        super().__init__(size,style)
        self.gif_path = gif_path
        self.frames = []
        self.frame_index = 0
        self.frame_duration = frame_duration
        self.last_frame_time = 0
        self.original_size = size
        self._load_gif()
        #self.scale([1,1]) # сразу подгоняем кадры
        self.current_time = 0
        self.scaled_frames = None
        self.resize(self._resize_ratio)
    def _load_gif(self):
        """Загружает GIF-анимацию из файла."""
        if self.gif_path:
            try:
                gif = Image.open(self.gif_path)
                for i in range(gif.n_frames):
                    gif.seek(i)
                    frame_rgb = gif.convert('RGB')
                    frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.size, 'RGB')
                    self.frames.append(frame_surface)
                
            except FileNotFoundError:
                print(f"Error: GIF file not found at {self.gif_path}")
            except Exception as e:
                print(f"Error loading GIF: {e}")

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        """Изменяет размер GIF-анимации.
        Args:
            _resize_ratio (list, optional): Коэффициент масштабирования [scale_x, scale_y]. Defaults to [1, 1].
        """
        if self.frames:
            self.scaled_frames = [pygame.transform.scale(frame,[self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]) for frame in self.frames]
        self._changed = True


    def draw(self):
        """Отрисовывает текущий кадр GIF-анимации."""
        super().draw()
        if not self.visible:
            return
        if not self.frames:
            return
        self.current_time += 1*time.delta_time*100
        if self.current_time > self.frame_duration:
             self.frame_index = (self.frame_index + 1) % len(self.frames)
             self.current_time = 0
             self._changed = True
        if len(self.frames) == 0:
            self._changed = False
        if isinstance(self,GifWidget) and self._changed:
            self._changed = False
            if self.scaled_frames:
                frame_to_draw = self.scaled_frames[self.frame_index] if hasattr(self,"scaled_frames") else self.frames[self.frame_index]
                self.surface.blit(frame_to_draw,(0,0))

class Input(Widget):
    blacklist: list | None
    whitelist: list | None
    max_characters: int | None
    multiple: bool
    allow_paste: bool
    words_indent: bool
    is_active: bool
    def __init__(self, size: Vector2|list, style: Style = default_style, default: str = "", placeholder: str = "", on_change_function = None, **constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size}
        self._entered_text = ""
        self.selected = False
        self.placeholder = placeholder
        self._on_change_fun = on_change_function

        self._text_scroll_offset = 0
        self._text_scroll_offset_y = 0
        self.max_scroll_y = 0
        self._cursor_place = 0
        self._text_surface = None
        self.left_margin = 10
        self.right_margin = 10
        self.top_margin = 5
        self.bottom_margin = 5
        self.text = default
        self._default_text = default
    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
    def _init_text_cache(self):
        self._text_surface = None
        self._text_rect = pygame.Rect(0, 0, 0, 0)
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("is_active", bool, True)
        self._add_constant("multiple", bool, False)
        self._add_constant("allow_paste", bool, True)
        self._add_constant("words_indent", bool, False)
        self._add_constant("max_characters", (int, type(None)), None)
        self._add_constant("blacklist", (list, type(None)), None)
        self._add_constant("whitelist", (list, type(None)), None)
    def _lazy_init(self, size: Vector2|list):
        super()._lazy_init(size)
        self._init_cursor()
        self._right_bake_text()
    def _init_cursor(self):
        if not hasattr(self,"_resize_ratio"): self._resize_ratio = [1,1]
        if not hasattr(self, 'style'): return
        try: font_height = self._get_line_height()
        except (pygame.error, AttributeError): font_height = self.size[1] * self._resize_ratio[1] * 0.8
        cursor_width = max(1, int(self.size[0]*0.01*self._resize_ratio[0]))
        self.cursor = pygame.Surface((cursor_width, font_height))
        try: self.cursor.fill(self._subtheme.oncolor)
        except AttributeError: self.cursor.fill((0,0,0))
    def _get_line_height(self):
        try:
            if not hasattr(self, '_style') or not self.style.fontname: raise AttributeError("Font not ready")
            return self.get_font().get_height()
        except (pygame.error, AttributeError) as e:
            raise e
            fallback_height = self.size[1] * self._resize_ratio[1] - self.top_margin - self.bottom_margin
            return max(5, int(fallback_height * 0.8))
    def _get_cursor_line_col(self):
        if not self._entered_text: return 0, 0
        lines = self._entered_text.split('\n')
        abs_pos = self._cursor_place
        current_pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            if abs_pos <= current_pos + line_len:
                col = abs_pos - current_pos
                return i, col
            current_pos += line_len + 1
        last_line_index = len(lines) - 1
        last_line_len = len(lines[last_line_index]) if last_line_index >= 0 else 0
        return last_line_index, last_line_len
    def _get_abs_pos_from_line_col(self, target_line_index, target_col_index):
        lines = self._entered_text.split('\n')
        target_line_index = max(0, min(target_line_index, len(lines) - 1))
        abs_pos = 0
        for i in range(target_line_index): abs_pos += len(lines[i]) + 1
        current_line_len = len(lines[target_line_index]) if target_line_index < len(lines) else 0
        target_col_index = max(0, min(target_col_index, current_line_len))
        abs_pos += target_col_index
        return abs_pos
    def _update_scroll_offset(self):
        if not hasattr(self,'style'): return
        if not hasattr(self, 'surface'): return
        try:
            renderFont = self.get_font()
            cursor_line_idx, cursor_col_idx = self._get_cursor_line_col()
            lines = self._entered_text.split('\n')
            cursor_line_text = lines[cursor_line_idx] if cursor_line_idx < len(lines) else ""
            text_before_cursor_in_line = cursor_line_text[:cursor_col_idx]
            ideal_cursor_x_offset = renderFont.size(text_before_cursor_in_line)[0]
            full_line_width = renderFont.size(cursor_line_text)[0]
        except (pygame.error, AttributeError, IndexError): return
        l_margin = self.left_margin * self._resize_ratio[0]
        r_margin = self.right_margin * self._resize_ratio[0]
        visible_width = self.surface.get_width() - l_margin - r_margin
        
        if visible_width < 1: visible_width = 1
        cursor_pos_relative_to_visible_start = ideal_cursor_x_offset - self._text_scroll_offset
        if cursor_pos_relative_to_visible_start < 0: self._text_scroll_offset = ideal_cursor_x_offset
        elif cursor_pos_relative_to_visible_start > visible_width: self._text_scroll_offset = ideal_cursor_x_offset - visible_width

        max_scroll_x = max(0, full_line_width - visible_width)
        self._text_scroll_offset = max(0, min(self._text_scroll_offset, max_scroll_x))

    def _update_scroll_offset_y(self):
        if not self.multiple or not hasattr(self, 'style'): return
        if not self._text_surface: return
        try:
            line_height = self._get_line_height()
            cursor_line, _ = self._get_cursor_line_col()
            ideal_cursor_y_offset = cursor_line * line_height
            total_text_height = self._text_surface.get_height()
        except (pygame.error, AttributeError, IndexError): return
        t_margin = self.top_margin * self._resize_ratio[1]
        b_margin = self.bottom_margin * self._resize_ratio[1]
        visible_height = self.surface.get_height() - t_margin - b_margin
        if visible_height < 1 : visible_height = 1
        self.max_scroll_y = max(0, total_text_height - visible_height)
        if ideal_cursor_y_offset < self._text_scroll_offset_y: self._text_scroll_offset_y = ideal_cursor_y_offset
        elif ideal_cursor_y_offset + line_height > self._text_scroll_offset_y + visible_height: self._text_scroll_offset_y = ideal_cursor_y_offset + line_height - visible_height
        self._text_scroll_offset_y = max(0, min(self._text_scroll_offset_y, self.max_scroll_y))

    def bake_text(self, text, unlimited_y=False, words_indent=False, 
                    alignx=Align.LEFT, aligny=Align.TOP, continuous=False, multiline_mode=False):
        if not hasattr(self, 'style') or not hasattr(self, 'surface'): return
        renderFont = self.get_font()
        line_height = self._get_line_height()
        if continuous:
            try: self._text_surface = renderFont.render(text, True, self._subtheme_font)
            except (pygame.error, AttributeError): self._text_surface = None
            return
        if multiline_mode:
            lines = text.split('\n')
            if not lines: self._text_surface = pygame.Surface((1, line_height), pygame.SRCALPHA); self._text_surface.fill((0,0,0,0)); return
            max_width = 0
            rendered_lines = []
            try:
                for line in lines:
                        line_surface = renderFont.render(line, True, self._subtheme_font)
                        rendered_lines.append(line_surface)
                        max_width = max(max_width, line_surface.get_width())
            except (pygame.error, AttributeError): self._text_surface = None; return
            total_height = len(lines) * line_height
            self._text_surface = pygame.Surface((max(1, max_width), max(line_height, total_height)), pygame.SRCALPHA)
            self._text_surface.fill((0,0,0,0))

            current_y = 0
            for line_surface in rendered_lines:
                self._text_surface.blit(line_surface, (0, current_y))
                current_y += line_height
            return
        lines = []
        current_line = ""
        max_line_width = self.size[0] * self._resize_ratio[0] - self.left_margin*self._resize_ratio[0] - self.right_margin*self._resize_ratio[0]
        processed_text = text.replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = processed_text.split('\n')
        try:
            for para in paragraphs:
                words = para.split(' ') if words_indent else list(para)
                current_line = ""
                sep = " " if words_indent else ""
                for word in words:
                    test_line = current_line + word + sep
                    if renderFont.size(test_line)[0] <= max_line_width:current_line = test_line
                    else:
                        if current_line: lines.append(current_line.rstrip())
                        current_line = word + sep
                if current_line: lines.append(current_line.rstrip())

            max_visible_lines = int((self.size[1] * self._resize_ratio[1] - self.top_margin*self._resize_ratio[1] - self.bottom_margin*self._resize_ratio[1]) / line_height)
            visible_lines = lines[:max_visible_lines]

            if not visible_lines:
                self._text_surface = pygame.Surface((1, 1), pygame.SRCALPHA); self._text_surface.fill((0,0,0,0))
                self._text_rect = self._text_surface.get_rect(topleft=(self.left_margin*self._resize_ratio[0], self.top_margin*self._resize_ratio[1]))
                return
            max_w = max(renderFont.size(line)[0] for line in visible_lines) if visible_lines else 1
            total_h = len(visible_lines) * line_height
            self._text_surface = pygame.Surface((max(1,max_w), max(1,total_h)), pygame.SRCALPHA)
            self._text_surface.fill((0,0,0,0))
            cury = 0
            for line in visible_lines:
                line_surf = renderFont.render(line, True, self._subtheme_font)
                self._text_surface.blit(line_surf, (0, cury))
                cury += line_height

            self._text_rect = self._text_surface.get_rect(topleft=(self.left_margin*self._resize_ratio[0], self.top_margin*self._resize_ratio[1]))
        
        except (pygame.error, AttributeError):
             self._text_surface = None
             self._text_rect = pygame.Rect(0,0,0,0)
             
    def _right_bake_text(self):
        if not hasattr(self, 'style'): return
        text_to_render = self._entered_text if len(self._entered_text) > 0 else self.placeholder
        if self.multiple:
            self.bake_text(text_to_render, multiline_mode=True)
            self._update_scroll_offset_y()
        else:
            self.bake_text(text_to_render, continuous=True)
        self._update_scroll_offset()
        
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._init_cursor()
        self._right_bake_text()
    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self, style: Style):
        self.clear_surfaces()
        self._changed = True
        self._style = copy.deepcopy(style)
        
        self._update_image()
        self.left_margin =  10
        self.right_margin = 10
        self.top_margin = 5
        self.bottom_margin = 5
        #self._init_cursor()
        if hasattr(self,'_entered_text'):
             self._right_bake_text()
    def event_update(self, events: list | None = None):
        if events is None: events = []
        super().event_update(events)
        if not self.is_active:
            if self.selected:
                 self.selected = False
                 self._changed = True
            return
        prev_selected = self.selected
        mouse_collided = self.get_rect().collidepoint(mouse.pos)
        self.check_selected(mouse_collided)
        if prev_selected != self.selected and self.selected:
             self._update_scroll_offset()
             self._update_scroll_offset_y()
        elif prev_selected != self.selected and not self.selected:
             self._changed = True
        if self.selected:
            text_changed = False
            cursor_moved = False
            for event in events:
                if event.type == pygame.KEYDOWN:
                    initial_cursor_place = self._cursor_place
                    initial_text = self._entered_text
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.multiple:
                             if self.max_characters is None or len(self._entered_text) < self.max_characters:
                                self._entered_text = self._entered_text[:self._cursor_place] + '\n' + self._entered_text[self._cursor_place:]
                                self._cursor_place += 1
                    elif event.key == pygame.K_UP:
                        if self.multiple:
                            current_line, current_col = self._get_cursor_line_col()
                            if current_line > 0:
                                self._cursor_place = self._get_abs_pos_from_line_col(current_line - 1, current_col)
                    elif event.key == pygame.K_DOWN:
                         if self.multiple:
                             lines = self._entered_text.split('\n')
                             current_line, current_col = self._get_cursor_line_col()
                             if current_line < len(lines) - 1:
                                 self._cursor_place = self._get_abs_pos_from_line_col(current_line + 1, current_col)
                    elif event.key == pygame.K_RIGHT:
                        self._cursor_place = min(len(self._entered_text),self._cursor_place+1)
                        self._changed = True
                    elif event.key == pygame.K_LEFT:
                        self._cursor_place = max(0,self._cursor_place-1)
                        self._changed = True
                    elif event.key == pygame.K_BACKSPACE:
                        if self._cursor_place > 0:
                            self._entered_text = self._entered_text[:self._cursor_place-1] + self._entered_text[self._cursor_place:]
                            self._cursor_place = max(0,self._cursor_place-1)
                    elif event.key == pygame.K_DELETE:
                         if self._cursor_place < len(self._entered_text):
                              self._entered_text = self._entered_text[:self._cursor_place] + self._entered_text[self._cursor_place+1:]
                    elif event.key == pygame.K_HOME:
                         if self.multiple:
                              line_idx, _ = self._get_cursor_line_col()
                              self._cursor_place = self._get_abs_pos_from_line_col(line_idx, 0)
                         else:
                              self._cursor_place = 0
                    elif event.key == pygame.K_END:
                         if self.multiple:
                              line_idx, _ = self._get_cursor_line_col()
                              lines = self._entered_text.split('\n')
                              line_len = len(lines[line_idx]) if line_idx < len(lines) else 0
                              self._cursor_place = self._get_abs_pos_from_line_col(line_idx, line_len)
                         else:
                              self._cursor_place = len(self._entered_text)
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                        if self.allow_paste:
                            pasted_text = ""
                            try:
                                pasted_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                                if pasted_text:
                                    pasted_text = pasted_text.decode('utf-8').replace('\x00', '')
                            except (pygame.error, UnicodeDecodeError, TypeError):
                                pasted_text = ""

                            if pasted_text:
                                filtered_text = ""
                                for char in pasted_text:
                                    valid_char = True
                                    if self.blacklist and char in self.blacklist: valid_char = False
                                    if self.whitelist and char not in self.whitelist: valid_char = False
                                    if not self.multiple and char in '\r\n': valid_char = False
                                    if valid_char: filtered_text += char

                                if self.max_characters is not None:
                                    available_space = self.max_characters - len(self._entered_text)
                                    filtered_text = filtered_text[:max(0, available_space)]

                                if filtered_text:
                                    self._entered_text = self._entered_text[:self._cursor_place] + filtered_text + self._entered_text[self._cursor_place:]
                                    self._cursor_place += len(filtered_text)

                    elif event.unicode:
                        unicode = event.unicode
                        is_valid_unicode = len(unicode) == 1 and ord(unicode) >= 32 and (unicode != "\x7f")
                        is_newline_ok = self.multiple or (unicode not in '\r\n')

                        if is_valid_unicode and is_newline_ok:
                            if self.max_characters is None or len(self._entered_text) < self.max_characters:
                                valid_char = True
                                if self.blacklist and unicode in self.blacklist: valid_char = False
                                if self.whitelist and unicode not in self.whitelist: valid_char = False

                                if valid_char:
                                    self._entered_text = self._entered_text[:self._cursor_place] + unicode + self._entered_text[self._cursor_place:]
                                    self._cursor_place += len(unicode)

                    if self._cursor_place != initial_cursor_place: cursor_moved = True
                    if self._entered_text != initial_text: text_changed = True
                    if text_changed or cursor_moved: self._changed = True

                elif event.type == pygame.MOUSEWHEEL:
                    if self.multiple and self.selected and mouse_collided:
                         scroll_multiplier = 3
                         line_h = 1
                         try:
                             line_h = self._get_line_height()
                         except: pass
                         scroll_amount = event.y * line_h * scroll_multiplier
                         if not hasattr(self, 'max_scroll_y'): self._update_scroll_offset_y()

                         self._text_scroll_offset_y -= scroll_amount
                         self._text_scroll_offset_y = max(0, min(self._text_scroll_offset_y, getattr(self, 'max_scroll_y', 0)))
                         self._changed = True
            if text_changed:
                 self._right_bake_text()
                 if self._on_change_fun:
                     try:
                          self._on_change_fun(self._entered_text)
                     except Exception as e:
                          print(f"Error in Input on_change_function: {e}")
            elif cursor_moved:
                 self._update_scroll_offset()
                 self._update_scroll_offset_y()
    def check_selected(self, collided):
        if collided and mouse.left_fdown:
            if not self.selected:
                self.selected = True
                self._changed = True
                try:
                    renderFont = self.get_font()
                    relative_x = mouse.pos[0] - self.master_coordinates[0]
                    relative_y = mouse.pos[1] - self.master_coordinates[1]
                    l_margin = self.left_margin * self._resize_ratio[0]
                    t_margin = self.top_margin * self._resize_ratio[1]
                    if self.multiple:
                        line_height = self._get_line_height()
                        if line_height <= 0 : line_height = 1 # Prevent division by zero
                        target_line_idx_float = (relative_y - t_margin + self._text_scroll_offset_y) / line_height
                        target_line_index = max(0, int(target_line_idx_float))
                        lines = self._entered_text.split('\n')
                        target_line_index = min(target_line_index, len(lines) - 1)
                        target_x_in_full_line = relative_x - l_margin + self._text_scroll_offset
                        target_line_text = lines[target_line_index] if target_line_index < len(lines) else ""
                        best_col_index = 0
                        min_diff = float('inf')
                        current_w = 0
                        for i, char in enumerate(target_line_text):
                            char_w = renderFont.size(char)[0]
                            pos_before = current_w
                            pos_after = current_w + char_w
                            diff_before = abs(target_x_in_full_line - pos_before)
                            diff_after = abs(target_x_in_full_line - pos_after)
                            if diff_before <= min_diff:
                                min_diff = diff_before
                                best_col_index = i
                            if diff_after < min_diff:
                                    min_diff = diff_after
                                    best_col_index = i + 1
                            current_w += char_w
                        best_col_index = max(0, min(best_col_index, len(target_line_text)))
                        self._cursor_place = self._get_abs_pos_from_line_col(target_line_index, best_col_index)
                    else:
                        target_x_in_full_text = relative_x - l_margin + self._text_scroll_offset
                        best_index = 0
                        min_diff = float('inf')
                        current_w = 0
                        for i, char in enumerate(self._entered_text):
                            char_w = renderFont.size(char)[0]
                            pos_before = current_w
                            pos_after = current_w + char_w
                            diff_before = abs(target_x_in_full_text - pos_before)
                            diff_after = abs(target_x_in_full_text - pos_after)

                            if diff_before <= min_diff:
                                min_diff = diff_before
                                best_index = i
                            if diff_after < min_diff:
                                min_diff = diff_after
                                best_index = i + 1
                            current_w += char_w

                        best_index = max(0, min(best_index, len(self._entered_text)))
                        self._cursor_place = best_index

                    self._update_scroll_offset()
                    self._update_scroll_offset_y()

                except (pygame.error, AttributeError, IndexError) as e:
                    pass

        elif not collided and mouse.left_fdown:
            if self.selected:
                 self.selected = False
                 self._changed = True
    @property
    def text(self): return self._entered_text
    @text.setter
    def text(self,text:str):
        if not isinstance(text, str): text = str(text)

        original_text = self._entered_text
        if not self.multiple:
            text = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

        if self.max_characters is not None:
            text = text[:self.max_characters]

        self._entered_text = text
        self._cursor_place = min(len(self._entered_text), self._cursor_place)
        self._changed = True
        self._right_bake_text()

        if self._on_change_fun and original_text != self._entered_text:
            try: self._on_change_fun(self._entered_text)
            except Exception as e: print(f"Error in Input on_change_function (setter): {e}")
    def secondary_draw(self):
        super().secondary_draw()
        if not self.visible: return

        if self._changed:
            self._changed = False
            try:
                renderFont = self.get_font()
                font_loaded = True
                line_height = self._get_line_height()
                cursor_height = self.cursor.get_height()
            except (pygame.error, AttributeError):
                font_loaded = False
                line_height = 15 
                cursor_height = 12 
            if not font_loaded: return
            l_margin = self.relx(self.left_margin)
            r_margin = self.relx(self.right_margin)
            t_margin = self.rely(self.top_margin)
            b_margin =  self.rely(self.bottom_margin)
            clip_rect = self.surface.get_rect()
            clip_rect.left = l_margin
            clip_rect.top = t_margin
            clip_rect.width = self.surface.get_width() - l_margin - r_margin
            clip_rect.height = self.surface.get_height() - t_margin - b_margin
            if clip_rect.width < 0: clip_rect.width = 0
            if clip_rect.height < 0: clip_rect.height = 0
            if self._text_surface:
                if self.multiple:
                    self._text_rect = self._text_surface.get_rect(topleft=(l_margin - self._text_scroll_offset, t_margin - self._text_scroll_offset_y))
                else:
                    self._text_rect = self._text_surface.get_rect(left=l_margin - self._text_scroll_offset,centery=(t_margin + self.surface.get_height() - b_margin) / 2 )
                original_clip = self.surface.get_clip()
                self.surface.set_clip(clip_rect)
                self.surface.blit(self._text_surface, self._text_rect)
                self.surface.set_clip(original_clip)
            if self.selected:
                cursor_visual_x = 0
                cursor_visual_y = 0
                try:
                    if self.multiple:
                        cursor_line, cursor_col = self._get_cursor_line_col()
                        lines = self._entered_text.split('\n')
                        line_text = lines[cursor_line] if cursor_line < len(lines) else ""
                        text_before_cursor_in_line = line_text[:cursor_col]
                        cursor_x_offset = renderFont.size(text_before_cursor_in_line)[0]
                        cursor_visual_x = l_margin + cursor_x_offset - self._text_scroll_offset
                        cursor_visual_y = t_margin + (cursor_line * line_height) - self._text_scroll_offset_y
                    else:
                        text_before_cursor = self._entered_text[:self._cursor_place]
                        cursor_x_offset = renderFont.size(text_before_cursor)[0]
                        cursor_visual_x = l_margin + cursor_x_offset - self._text_scroll_offset
                        cursor_visual_y = (self.surface.get_height() - cursor_height) / 2

                    cursor_draw_rect = self.cursor.get_rect(topleft=(cursor_visual_x, cursor_visual_y))
                    if clip_rect.colliderect(cursor_draw_rect):
                        self.surface.blit(self.cursor, cursor_draw_rect.topleft)
                except (pygame.error, AttributeError, IndexError):pass
    def clone(self):
        return Input(self._lazy_kwargs['size'], copy.deepcopy(self.style), copy.copy(self._default_text), copy.copy(self.placeholder), self._on_change_fun, **self.constant_kwargs)
class MusicPlayer(Widget):
    def __init__(self, size, music_path, style: Style = default_style):
        super().__init__(size, style)
        pygame.mixer.init()
        self.music_path = music_path
        self.sound = pygame.mixer.Sound(music_path) 
        self.music_length = self.sound.get_length() * 1000 
        self.channel = None 
        self.start_time = 0 
        self.progress = 0
        self.side_button_size = self.size[1] / 4
        self.progress_bar_height = self.size[1] / 4
        self.cross_image = self.draw_cross()
        self.circle_image = self.draw_circle()
        self.button_image = self.circle_image
        self.button_rect = self.button_image.get_rect(center=(self.side_button_size / 2, self.side_button_size / 2))
        self.time_label = Label((size[0] - self.side_button_size * 2, 20),
                              f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}",
                              style(fontsize=12, bordercolor=Color_Type.TRANSPARENT, bgcolor=Color_Type.TRANSPARENT))
        self.is_playing = False
        self.sinus_margin = 0

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.time_label.resize(resize_ratio)
        
    def draw_sinusoid(self,size,frequency,margin):
        self.sinus_surf = pygame.Surface(size,pygame.SRCALPHA)
        self.sinus_surf.fill((0,0,0,0))
        for i in range(int(size[0])):
            y = abs(int(size[1] * math.sin(frequency * i+margin))) 
            y = size[1]-y
            print(y)
            pygame.draw.line(self.sinus_surf,(50,50,200),(i,size[1]),(i,y))
            
    def update(self, *args):
        super().update()
        if self.is_playing:
            self.sinus_margin+=1*time.delta_time
        if self.sinus_margin >= 100:
            self.sinus_margin = 0
        self.time_label.coordinates = [(self.size[0] / 2 - self.time_label.size[0] / 2) * self._resize_ratio[0],(self.size[1] - self.time_label.size[1]) * self._resize_ratio[1]]
        if mouse.left_fdown:
            if pygame.Rect([self.master_coordinates[0], self.master_coordinates[1]],[self.side_button_size, self.side_button_size]).collidepoint(mouse.pos):
                self.toggle_play()

        if self.is_playing:
            self.progress = pygame.time.get_ticks() - self.start_time
            if self.progress >= self.music_length:
                self.stop()
            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
            self.button_image = self.cross_image 
        else:
            self.button_image = self.circle_image
            if self.progress >= self.music_length:
                self.progress = 0

            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
    def format_time(self, milliseconds):
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"
    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
    def play(self):
            self.channel = self.sound.play(0)
            if self.channel is not None:
                self.start_time = self.progress 
                self.is_playing = True
            else:
                print("Error: Could not obtain a channel to play the sound. Jopa also")
    def pause(self):
        if self.is_playing:
            if self.channel:
                self.channel.pause()
            self.is_playing = False
    def stop(self):
        if self.channel:
            self.channel.stop()
        self.is_playing = False
        self.progress = 0
    def draw_cross(self):
        cross_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, (255, 255, 255), (5, 5), (self.side_button_size - 5, self.side_button_size - 5), 3)
        pygame.draw.line(cross_surface, (255, 255, 255), (self.side_button_size - 5, 5), (5, self.side_button_size - 5), 3)
        return cross_surface

    def draw_circle(self):
        circle_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255), (self.side_button_size // 2, self.side_button_size // 2),self.side_button_size // 2 - 5)
        return circle_surface

    def draw(self):
        super().draw()
        self.surface.blit(self.button_image, self.button_rect)
        progress_width = (self.size[0] / 1.2 * (self.progress / self.music_length)) * self._resize_ratio[0] if self.music_length > 0 else 0
        pygame.draw.rect(self.surface, (10, 10, 10),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1],
                          self.size[0] / 1.2 * self._resize_ratio[0],
                          self.progress_bar_height * self._resize_ratio[1]), 0, self.style.radius)
        self.draw_sinusoid([progress_width,self.size[1]/17*self._resize_ratio[1]],0.15,self.sinus_margin)
        self.surface.blit(self.sinus_surf,((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],(self.size[1] / 2 - self.sinus_surf.get_height()-self.progress_bar_height / 2) * self._resize_ratio[1]))
        pygame.draw.rect(self.surface, (50, 50, 200),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1], progress_width,
                          self.progress_bar_height * self._resize_ratio[1]), 0, -1,0,0,self.style.radius,self.style.radius)

        self.time_label.draw()
        self.surface.blit(self.time_label.surface, self.time_label.coordinates)

class ProgressBar(Widget):
    min_value: int | float
    max_value: int | float
    _current_value: int | float
    def __init__(self, size: Vector2 | list, style: Style = default_style,**constant_kwargs):
        super().__init__(size, style, **constant_kwargs)
        self.percentage_of_value = self.value
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("min_value", (int, float), 0)
        self._add_constant("max_value", (int, float), 100)
        self._add_constant("value", (int, float), 0)
    @property
    def percentage(self):
        return self._percentage
    @percentage.setter
    def percentage(self,value):
        self._percentage = value
        self.value = self.min_value+(self.max_value-self.min_value)*self._percentage
    @percentage.setter
    def percentage_of_value(self,value):
        self._percentage = (value-self.min_value)/(self.max_value-self.min_value)
    @property
    def value(self):
        return self._current_value
    @value.setter
    def value(self,value):
        self._current_value = value
        self.percentage_of_value = value
    def secondary_draw(self):
        super().secondary_draw()
        surf = self.renderer._create_surf_base([int(self.relx(self.size[0]*self.percentage))-2,int(self.rely(self.size[1]))-2])
        self.surface.blit(surf,(0,0))
        
class SliderBar(Widget):
    def __init__(self, begin_val: int, end_val: int, size, style, step: int = 1, freedom=False,default=-999.999123):
        self.button = Button(lambda: None, "", [size[1]/1.2, size[1]/1.2], style, active=False, freedom=False)
        super().__init__(size, style, freedom)
        self.begin_val = begin_val 
        self.end_val = end_val      
        self.step = step          
        self.current_value = begin_val 
        self.is_dragging = False    
        self.slider_pos = 0         
        if default!= -999.999123:
            self.current_value = default
        self._update_slider_position()  
    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self,style:Style):
        self._update_image()
        self.cached_gradient = None
        self._changed = True
        self._style = copy.deepcopy(style)
        self.button.style = copy.deepcopy(style)
        
    def _update_slider_position(self):
        """Обновляет позицию ползунка на основе текущего значения"""
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.slider_pos = 0
        else:
            self.slider_pos = (self.current_value - self.begin_val) / range_val * self.size[0]

    def _update_value_from_position(self):
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.current_value = self.begin_val
        else:
            self.current_value = self.begin_val + (self.slider_pos / self.size[0]) * range_val
            self.current_value = round(self.current_value / self.step) * self.step
            self.current_value = max(self.begin_val, min(self.end_val, self.current_value))

    def secondary_update(self, *args):
        super().secondary_update(*args)
        if not self.active: return
        if mouse.left_down or mouse.left_fdown:
            if self.get_rect().collidepoint(mouse.pos): self.is_dragging = True
        else: self.is_dragging = False
        if self.is_dragging:
            self._changed = True
            relative_x = mouse.pos[0] - self.master_coordinates[0]
            self.slider_pos = max(0, min(self.size[0], relative_x))
            self._update_value_from_position()
            self._update_slider_position()
        self.button.coordinates = Vector2(0,0)
        self.button.master_coordinates = Vector2(0,0)
        self.button.update()
    def draw(self):
        if not self.visible:return
        super().draw()
        #pygame.draw.line(self.surface, self.style.bordercolor,(0, self.size[1] // 2), (self.size[0], self.size[1] // 2), 6)
        slider_rect = pygame.Rect(max(0,min(self.slider_pos - self.button.size[0]/2,self.size[0]-self.button.size[0])),(self.size[1]- self.button.size[1])/2,  self.button.size[0], self.button.size[1])
        #pygame.draw.rect(self.surface, self.style.secondarycolor, slider_rect)
        self.button.draw()
        self.surface.blit(self.button.surface, slider_rect)
        self.bake_text(str(self.current_value), alignx=Align.CENTER, aligny=Align.CENTER)
        assert self._text_surface is not None and self._text_rect is not None
        self.surface.blit(self._text_surface, self._text_rect)
        if self._changed:
            self._changed = False

class ElementSwitcher(Widget):
    def __init__(self, size, elements, style: Style = default_style,on_change_function=None):
        super().__init__(size, style)
        self.elements = elements
        self.current_index = 0
        self.button_padding = 10
        self.arrow_width = 10
        self.bake_text(self.current_element_text())
        self.on_change_function = on_change_function
    def current_element_text(self):
        if not self.elements: return ""
        return f"{self.elements[self.current_index]}"
    def next_element(self):
        self.current_index = (self.current_index + 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def previous_element(self):
        self.current_index = (self.current_index - 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def set_index(self,index:int):
        self.current_index = index
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    @property
    def hovered(self):
        return self._hovered
    @hovered.setter
    def hovered(self,value:bool):
        if hasattr(self, "_hovered") and self.hovered == value:
            return
        self._hovered = value
        if not hasattr(self, "elements"):
            self.add_on_first_update(lambda: self.bake_text(self.current_element_text()))
            return
        self.bake_text(self.current_element_text())

    def update(self, *args):
        super().update(*args)
        if not self.active:
            return
        if mouse.left_up and self.hovered:
            click_pos_relative = np.array(mouse.pos) - self.master_coordinates
            center_x = self.surface.get_width() / 2
            button_width = self._text_rect.width / 2 + self.button_padding + self.arrow_width * 2
            if click_pos_relative[0] < center_x - button_width / 2: self.previous_element()
            elif click_pos_relative[0] > center_x + button_width / 2: self.next_element()

    def draw(self):
        super().draw()
        if not self.visible:
            return
        text_center_x = self.surface.get_width() / 2
        text_center_y = self.surface.get_height() / 2
        left_button_center_x = text_center_x - self._text_rect.width / 2 - self.button_padding - self.arrow_width
        right_button_center_x = text_center_x + self._text_rect.width / 2 + self.button_padding + self.arrow_width

        button_center_y = text_center_y
        arrow_color = self.style.fontcolor

        pygame.draw.polygon(self.surface, arrow_color, [
            (left_button_center_x - self.arrow_width, button_center_y),
            (left_button_center_x, button_center_y - self.arrow_width / 2),
            (left_button_center_x, button_center_y + self.arrow_width / 2)])
        pygame.draw.polygon(self.surface, arrow_color, [
            (right_button_center_x + self.arrow_width, button_center_y),
            (right_button_center_x, button_center_y - self.arrow_width / 2),
            (right_button_center_x, button_center_y + self.arrow_width / 2)])

        self.surface.blit(self._text_surface, self._text_rect)

class FileDialog(Button):
    def __init__(self, on_change_function, dialog,text, size, style = default_style, active = True, freedom=False, words_indent=False):
        super().__init__(None, text, size, style, active, False, freedom, words_indent)
        self.on_change_function = on_change_function
        self.dialog = dialog
        self.filepath = None
    def _open_filedialog(self):
        self.filepath = self.dialog()
        
        if self.on_change_function:
            self.on_change_function(self.filepath)
            
    def update(self,*args):
        super().update(*args)
        if not self.active: return
        if self.hovered and mouse.left_up:
                try: self._open_filedialog()
                except Exception as e:
                    print(e)
                    
class RectCheckBox(Widget):
    function: Callable | None
    _active_rect_factor: float | int
    def __init__(self, size: int, style: Style = default_style, **constant_kwargs):
        super().__init__(Vector2([size, size]), style, **constant_kwargs)
        
    def _init_booleans(self):
        super()._init_booleans()
        self._toogled = False
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("function", (type(None), Callable), None)
        self._add_constant_link("on_toogle", "function")
        self._add_constant("toogled", bool, False)
        self._add_constant_link("active", "toogled")
        self._add_constant("active_rect_factor", (float, int), 0.8)
        self._add_constant_link("active_factor", "active_rect_factor")

    @property
    def active_rect_factor(self):
        return self._active_rect_factor
    
    @active_rect_factor.setter
    def active_rect_factor(self, value: float | int):
        self._active_rect_factor = value
        self._changed = True

    @property
    def toogled(self):
        return self._toogled
    
    @toogled.setter
    def toogled(self,value: bool):
        self._toogled = value
        self._changed = True
        if self.function: self.function(value)
        
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if self._changed:
            if self._toogled:
                margin = (self._csize * (1 - self.active_rect_factor)) / 2
                
                offset = NvVector2(round(margin.x), round(margin.y))
                
                active_size = self._csize - (offset * 2)

                active_size.x = max(1, int(active_size.x))
                active_size.y = max(1, int(active_size.y))
                
                inner_radius = self._style.borderradius * self.active_rect_factor
                
                inner_surf = self.renderer._create_surf_base(
                    active_size, 
                    True, 
                    self.relm(inner_radius)
                )
                
                self.surface.blit(inner_surf, offset)
    def _on_click_system(self):
        self.toogled = not self.toogled
        super()._on_click_system()
          
    def clone(self):
        self.constant_kwargs['events'] = self._events
        selfcopy = RectCheckBox(self._lazy_kwargs['size'].x, copy.deepcopy(self.style), **self.constant_kwargs)
        self._event_cycle(EventType.OnCopy, selfcopy)
        return selfcopy