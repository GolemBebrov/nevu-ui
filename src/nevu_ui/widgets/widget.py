import pygame
from warnings import deprecated
from pygame._sdl2 import Texture, Image
from nevu_ui.animations import AnimationType
from nevu_ui.fast.logic import logic_update_helper
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.rendering.background_renderer import BackgroundRenderer
from nevu_ui.rendering.blit import ReverseAlphaBlit
from nevu_ui.core.state import nevu_state
from nevu_ui.rendering import Shader
from nevu_ui.window.display import DisplayGL
from nevu_ui.nevuobj import NevuObject, NevuObjectKwargs
from nevu_ui.color import SubThemeRole, PairColorRole
from nevu_ui.style import Style, default_style

from nevu_ui.core.enums import (
    Quality, Align, CacheType
)
from typing import (
    Any, NotRequired, Unpack
)

class WidgetKwargs(NevuObjectKwargs):
    alt: NotRequired[bool]
    clickable: NotRequired[bool]
    hoverable: NotRequired[bool]
    fancy_click_style: NotRequired[bool]
    resize_bg_image: NotRequired[bool]
    z: NotRequired[int]
    inline: NotRequired[bool]
    font_role: NotRequired[PairColorRole]
    _draw_borders: NotRequired[bool]
    _draw_content: NotRequired[bool]

class Widget(NevuObject):
    _alt: bool
    clickable: bool
    hoverable: bool
    fancy_click_style: bool
    z: int
    inline: bool
    font_role: PairColorRole
    _draw_borders: bool
    _master_mask: Any
    _inline_add_coords: NvVector2
    _draw_content: bool
    _sdf_mode: bool
    
    def __init__(self, size: NvVector2 | list, style: Style = default_style, **constant_kwargs: Unpack[WidgetKwargs]):
        super().__init__(size, style, **constant_kwargs)
        #=== Text Cache ===
        self._init_text_cache()
        #=== Alt ===
        self._init_alt()
    
    def convert_texture(self):
        if nevu_state.renderer is None:
            raise ValueError("Window not initialized!")
        assert nevu_state.window, "Window not initialized!"
        assert self.surface, "Surface not initialized!"
        if nevu_state.window._gpu_mode:
            texture = Texture.from_surface(nevu_state.renderer, self.surface)
            texture = Image(texture)
        elif nevu_state.window._open_gl_mode:
            assert isinstance(nevu_state.window.display, DisplayGL)
            raise NotImplementedError("GL texture conversion is not implemented yet.")
            #texture = convert_surface_to_gl_texture(nevu_state.window.display.renderer, self.surface)
        return texture #type: ignore
    
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("alt", bool, False, getter=self._alt_getter, setter=self._alt_setter)
        self._add_constant("clickable", bool, False)
        self._add_constant("hoverable", bool, True)
        self._add_constant("fancy_click_style", bool, True)
        self._add_constant("resize_bg_image", bool, False)
        self._add_constant("z", int, 1)
        self._add_constant("inline", bool, False)
        self._add_constant("font_role", PairColorRole, PairColorRole.SURFACE_VARIANT)
        self._add_constant("_draw_borders", bool, True)
        self._add_constant("_draw_content", bool, True)
        
    def _init_text_cache(self):
        self._text_baked = None
        self._text_surface = None
        self._text_rect = None
        
    def _init_objects(self):
        super()._init_objects()
        self._subtheme_role = SubThemeRole.SECONDARY
        self.renderer = BackgroundRenderer(self)
        self._master_mask = None
        
    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()
        self._dr_coordinates_new = self.coordinates.copy()
        self._inline_add_coords = NvVector2()

    def _init_booleans(self):
        super()._init_booleans()
        self._optimized_dirty_rect_for_short_animations = True
        self._original_alt = self._alt
        self._sdf_mode = True
        self._supports_tuple_borderradius = True

    def _init_style(self, style: Style | str):
        super()._init_style(style)
        if isinstance(self.style.borderradius, tuple) and not self._supports_tuple_borderradius:
            print(f"Warning: tuple border radius is not support in {self.__class__.__name__}")
            self.style.borderradius = self.style.borderradius[0]
        self.add_first_update_action(self._normalize_borderradius)

    def _normalize_borderradius(self):  
        if isinstance(self.style.borderradius, int | float):
            br = self.style.borderradius
            br = max(br, 0)
            br = min(br, self.size.x / 2)
            br = min(br, self.size.y / 2)
            if br != self.style.borderradius: self._changed = True
            self.style.borderradius = br #type: ignore
            self.clear_surfaces()
            self.clear_texture()

        elif isinstance(self.style.borderradius, tuple):
            br = list(self.style.borderradius)
            for i in range(len(br)):
                br[i] = max(br[i], 0)
                br[i] = min(br[i], self.size.x / 2)
                br[i] = min(br[i], self.size.y / 2)
            new_br = tuple(br)
            if new_br != self.style.borderradius:
                self.style.borderradius = new_br #type: ignore
                self._changed = True
                self.clear_surfaces()
                self.clear_texture()
    def _init_alt(self):
        if self.alt: 
            self._subtheme_border = self._alt_subtheme_border
            self._subtheme_content =  self._alt_subtheme_content
            self._subtheme_font = self._alt_subtheme_font
        else:
            self._subtheme_border = self._main_subtheme_border
            self._subtheme_content = self._main_subtheme_content
            self._subtheme_font = self._main_subtheme_font
    
    @property
    def subtheme_border(self): return self._subtheme_border()
    @property
    def subtheme_content(self): return self._subtheme_content()
    @property
    def subtheme_font(self): return self._subtheme_font()
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        if self.inline: return
        self.surface = pygame.Surface(size, flags = pygame.SRCALPHA)

    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        self._init_alt()
        self._on_style_change()
        
    def _alt_getter(self): return self._alt
    def _alt_setter(self, value):
        self._alt = value
        self._init_alt()
        self._on_style_change()
        
    def _toogle_click_style(self):
        if not self.clickable: return
        if self.fancy_click_style: self.alt = not self.alt
        else: self._on_style_change()

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
        self.cache.clear_selected(whitelist = [CacheType.Scaled_Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Borders, CacheType.Scaled_Background, CacheType.Background, CacheType.Texture])
    
    def _on_style_change(self):
        self._on_style_change_content()
        self._on_style_change_additional()
    def _on_style_change_content(self):
        self.clear_surfaces()
        self._changed = True
    def _on_style_change_additional(self): pass
        
    def _update_image(self, style: Style | None = None):
        try:
            if not style: style = self.style
            if not style.bgimage: return
            img = pygame.image.load(style.bgimage)
            img.convert_alpha()
            self.cache.set(CacheType.Image, pygame.transform.scale(img, self._csize))
        except Exception: self.cache.clear_selected(whitelist = [CacheType.Image])

    def _main_subtheme_content(self): return self._subtheme.color
    def _main_subtheme_border(self): return self._subtheme.oncolor
    def _alt_subtheme_content(self): return self._subtheme.container
    def _alt_subtheme_border(self):return self._subtheme.oncontainer
    def _main_subtheme_font(self): return self.style.colortheme.get_pair(self.font_role).color
    def _alt_subtheme_font(self): return self.style.colortheme.get_pair(self.font_role).oncolor
    
    def primary_draw(self):
        super().primary_draw()
        if self.dead: return
        if not self._changed: return
        
        assert self.surface
        if self.inline: 
            surf = self.renderer._generate_background(only_content = self._draw_content, sdf = self._sdf_mode)
            assert surf
            dest_pos = self.coordinates.to_round().to_tuple()
            if self._master_mask:
                mask_offset = NvVector2(0, 0)
                if self._sdf_mode: 
                    mask_offset += NvVector2(1, 1)
                if self.style.borderwidth > 0:
                    mask_offset += NvVector2(1, 1)

                read_pos = (self.coordinates.to_round() - self._inline_add_coords.to_round() - mask_offset.to_round())

                ReverseAlphaBlit.blit(surf, self._master_mask, read_pos.to_tuple()) #type: ignore
            self.surface.blit(surf, dest_pos)
        else:
            cache =  self.renderer._generate_background(only_content = self._draw_content, sdf = self._sdf_mode)
            assert cache
            self.surface = cache.copy()
    def secondary_draw_end(self):
        if self._changed and nevu_state.renderer:
            self.texture = self.cache.get_or_exec(CacheType.Texture, self.convert_texture)
        super().secondary_draw_end()
    
    def clear_texture(self): self.cache.clear_selected(whitelist = [CacheType.Texture])
    
    def logic_update(self):
        super().logic_update()
        new_dr_old, new_first_update = logic_update_helper(
        self._optimized_dirty_rect_for_short_animations,
        self._csize, self.absolute_coordinates,
        self._dirty_rect, self._dr_coordinates_old,
        self._first_update, self.first_update_functions,
        self._resize_ratio, nevu_state.z_system)
        self._dr_coordinates_old = new_dr_old
        self._first_update = new_first_update
        if hasattr(self, "texture") and self.texture and (alpha := self.animation_manager.get_animation_value(AnimationType.OPACITY)):
            self.texture.alpha = alpha

    def _boot_up(self): pass

    @deprecated("Use renderer.bake_text() instead. This method will be removed in a future version.")
    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False,
                alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, continuous: bool = False, size_x = None, size_y = None, color = None):
        size_x = size_x or self._csize.x
        size_y = size_y or self._csize.y
        size = NvVector2(size_x, size_y)
        self.renderer.bake_text(text, unlimited_y, words_indent, alignx, aligny, size, color)

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist = [CacheType.RelSize])
        self.clear_surfaces()
        self._update_image()
        self.surface = pygame.Surface(self._csize, flags = pygame.SRCALPHA)
        self._changed = True