import pygame
from warnings import deprecated
from pygame._sdl2 import Texture, Image
import pyray as rl

from nevu_ui.presentation.animations import AnimationType
from nevu_ui.fast.logic import logic_update_helper
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.rendering.pygame.renderer import BackgroundRendererPygame
from nevu_ui.rendering.raylib.renderer import BackgroundRendererRayLib
from nevu_ui.rendering.blit import ReverseAlphaBlit
from nevu_ui.core.state import nevu_state
from typing import Any, Unpack
from nevu_ui.components.nevuobj import NevuObject
from nevu_ui.components.widgets import WidgetKwargs
from nevu_ui.presentation.color import SubThemeRole, PairColorRole
from nevu_ui.presentation.style import Style, default_style

from nevu_ui.core.enums import (
    Align, CacheType, ConstantLayer, Backend
)

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
        if nevu_state.window.is_dtype.sdl:
            assert isinstance(self.surface, pygame.Surface)
            texture = Texture.from_surface(nevu_state.renderer, self.surface)
            texture = Image(texture)
        elif nevu_state.window.is_dtype.raylib:
            raise NotImplementedError("raylib texture conversion is not implemented yet.")
            #texture = convert_surface_to_gl_texture(nevu_state.window.display.renderer, self.surface)
        return texture #type: ignore
    
    def _add_params(self):
        super()._add_params()
        self._add_param("alt", bool, False, getter=self._alt_getter, setter=self._alt_setter, layer=ConstantLayer.Complicated)
        self._add_param("clickable", bool, False)
        self._add_param("hoverable", bool, False)
        self._add_param("fancy_click_style", bool, False)
        self._add_param("resize_bg_image", bool, False)
        self._change_param_default("z", 1)
        self._add_param("inline", bool, False)
        self._add_param("font_role", PairColorRole, PairColorRole.SURFACE_VARIANT)
        self._add_param("_draw_borders", bool, True)
        self._add_param("_draw_content", bool, True)
        self._change_param_default("subtheme_role", SubThemeRole.SECONDARY)
        
    def _init_text_cache(self):
        self._text_baked = None
        self._text_surface = None
        self._text_rect = None
        assert nevu_state.window
        if nevu_state.window._backend == Backend.RayLib:
            self._text_font_size = None
            self._text_spacing = None
        
    def _init_objects(self):
        super()._init_objects()
        assert nevu_state.window, "Window not initialized!"
        if nevu_state.window.is_dtype.raylib:
            self.renderer = BackgroundRendererRayLib(self)
        else:
            self.renderer = BackgroundRendererPygame(self)
        self._master_mask = None
        if not nevu_state.window.is_dtype.raylib:
            self._primary_draw_content = self._pygame_primary_draw_content
        else:
            self._primary_draw_content = self._raylib_primary_draw_content
    
    def _init_lists(self):
        super()._init_lists()
        self._dr_coordinates_old = self.coordinates.copy()
        self._inline_add_coords = NvVector2()

    def _init_booleans(self):
        super()._init_booleans()
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
            self._normalize_br_num()
        elif isinstance(self.style.borderradius, tuple):
            self._normalize_br_tuple()

    def _normalize_br_num(self):
        br = self.style.borderradius
        br = max(br, 0)
        br = min(br, self.size.x / 2)
        br = min(br, self.size.y / 2)
        if br != self.style.borderradius: self._changed = True
        self.style.borderradius = br #type: ignore
        self.clear_surfaces()
        self.clear_texture()
    
    def _normalize_br_tuple(self):
        assert isinstance(self.style.borderradius, tuple)
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
    
    def _regen_surface(self):
        assert nevu_state.window
        if nevu_state.window.is_dtype.raylib: 
            if hasattr(self, 'surface') and self.surface: rl.unload_render_texture(self.surface) #type: ignore
            self.surface = rl.load_render_texture(int(self._csize.x), int(self._csize.y))
            rl.set_texture_filter(self.surface.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
            rl.set_texture_wrap(self.surface.texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
        else:
            self.surface = pygame.Surface(self._csize, flags = pygame.SRCALPHA)
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self._original_alt = self.alt
        if self.inline: return
        self._regen_surface()
    
    def _on_subtheme_role_change(self):
        super()._on_subtheme_role_change()
        if self.booted:
            self._init_alt()
        self._on_style_change()

    def _alt_getter(self): return self._alt
    def _alt_setter(self, value):
        self._alt = value
        self._init_alt()
        self._on_style_change()
        
    def _toogle_click_style(self):
        if not self.clickable: return
        if self.get_param_strict("fancy_click_style").value: self.alt = not self.alt
        else: self._on_style_change()

    def _on_hover_system(self):
        super()._on_hover_system()
        if not self.get_param_strict("hoverable").value: return
        self._on_style_change()
    def _on_keyup_system(self):
        super()._on_keyup_system()
        if self.alt != self._original_alt:
            self.alt = self._original_alt
        if not self.get_param_strict("clickable").value: return
        self._on_style_change()
    def _on_click_system(self):
        super()._on_click_system()
        if not self.get_param_strict("clickable").value: return
        self._toogle_click_style()
    def _on_unhover_system(self):
        super()._on_unhover_system()
        
        if not self.get_param_strict("hoverable").value: return
        self._on_style_change()
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        if self.alt != self._original_alt:
            self.alt = self._original_alt
        if not self.get_param_strict("hoverable").value: return
        self._on_style_change()
    
    def _clear_rl_specific(self):
        assert nevu_state.window
        if not nevu_state.window.is_dtype.raylib: return 
        if self.cache.get(CacheType.RlFont): rl.unload_font(self.cache.get(CacheType.RlFont)) #type: ignore
        if self.cache.get(CacheType.Surface): rl.unload_render_texture(self.cache.get(CacheType.Surface)) #type: ignore
    
    def clear_all(self):
        """
        Clears all cached data by invoking the clear method on the cache. 
        !WARNING!: may cause bugs and errors
        """
        self._clear_rl_specific()
        self.cache.clear()
        
    def clear_surfaces(self):
        """
        Clears specific cached surface-related data by invoking the clear_selected 
        method on the cache with a whitelist of CacheTypes related to surfaces. 
        This includes Image, Scaled_Gradient, Surface, and Borders.
        Highly recommended to use this method instead of clear_all.
        """
        self._clear_rl_specific()
        self.cache.clear_selected(whitelist = [CacheType.Scaled_Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Borders, CacheType.Scaled_Background, CacheType.Background, CacheType.Texture, CacheType.RlFont])
    
    def _on_style_change(self):
        self._on_style_change_content()
        self._on_style_change_additional()
        
    def _on_style_change_content(self):
        self.clear_surfaces()
        self.clear_texture()
        self._changed = True

    def _on_style_change_additional(self): 
        assert nevu_state.window
        if nevu_state.window.is_dtype.raylib and hasattr(self, "_text_surface") and self._text_surface:
            rl.unload_render_texture(self._text_surface)
        self._text_surface = None
        self._text_rect = None
        
    def _update_image(self, style: Style | None = None):
        try:
            if not style: style = self.style
            if not style.bgimage: return
            img = pygame.image.load(style.bgimage)
            img.convert_alpha()
            self.cache.set(CacheType.Image, pygame.transform.scale(img, self._csize))
        except Exception: self.cache.clear_selected(whitelist = [CacheType.Image])

    @property
    def font_role(self): return self.style.font_role or self.get_param_strict("font_role").value
    
    def _main_subtheme_content(self): return self._subtheme.oncontainer
    def _main_subtheme_border(self): return self._subtheme.container
    def _alt_subtheme_content(self): return self._subtheme.oncolor
    def _alt_subtheme_border(self):return self._subtheme.color
    def _main_subtheme_font(self): return self.style.colortheme.get_pair(self.font_role).color
    def _alt_subtheme_font(self): return self.style.colortheme.get_pair(self.font_role).oncolor
    
    def _primary_draw(self):
        super()._primary_draw()
        if self._dead: return
        if not self._changed: return
        self._primary_draw_content()
    
    def _primary_draw_content(self): pass

    def _pygame_primary_draw_content(self):
        assert self.surface and isinstance(self.surface, pygame.Surface)
        assert isinstance(self.renderer, BackgroundRendererPygame), "Cannot use pygame renderer for non-pygame widget"
        if self.inline: 
            surf = self.renderer._generate_background(only_content = self._draw_content, sdf = self._sdf_mode)
            assert surf
            dest_pos = self.coordinates.to_round().to_tuple()
            if self._master_mask:
                mask_offset = NvVector2(0, 0)
                if self._sdf_mode: mask_offset += NvVector2(1, 1)
                if self.style.borderwidth > 0: mask_offset += NvVector2(1, 1)

                read_pos = (self.coordinates.to_round() - self._inline_add_coords.to_round() - mask_offset.to_round())

                ReverseAlphaBlit.blit(surf, self._master_mask, read_pos.to_tuple()) #type: ignore
            self.surface.blit(surf, dest_pos)
        else:
            cache =  self.renderer._generate_background(only_content = self._draw_content, sdf = self._sdf_mode)
            assert cache
            self.surface = cache.copy()

    def _raylib_primary_draw_content(self):
        assert isinstance(self.renderer, BackgroundRendererRayLib), "Cannot use raylib renderer for non-raylib widget"
        if self.inline: 
            raise ValueError("Raylib inline widget is not supported for now Sowwy OW<")
        else:
            cache =  self.renderer._generate_background(only_content = self._draw_content, sdf = self._sdf_mode)
            assert cache
            assert nevu_state.window
            rl.begin_texture_mode(self.surface) #type: ignore
            display = nevu_state.window.display
            assert nevu_state.window.is_raylib(display)
            display.clear(rl.BLANK) #type: ignore
            if isinstance(self.style.borderradius, tuple):
                radius = tuple(map(self.relm, self.style.borderradius)) 
            else:
                radius = [self.relm(self.style.borderradius)]*4
            display.blit_sdf(cache.texture, (0, 0, cache.texture.width, cache.texture.height), radius) #type: ignore
            rl.end_texture_mode()
            rl.unload_render_texture(cache)
    
    def _secondary_draw_end(self):
        if self._changed and nevu_state.renderer:
            self.texture = self.cache.get_or_exec(CacheType.Texture, self.convert_texture)
        assert nevu_state.window
        super()._secondary_draw_end()
    
    def clear_texture(self): self.cache.clear_selected(whitelist = [CacheType.Texture])
    
    def _logic_update(self):
        super()._logic_update()
        logic_update_helper(
        self._csize, self.absolute_coordinates, self._dr_coordinates_old,
        self._resize_ratio, nevu_state.z_system)
        
        if hasattr(self, "texture") and self.texture and (alpha := self.animation_manager.get_animation_value(AnimationType.OPACITY)):
            self.texture.alpha = alpha
            
        if self._first_update:
            self._first_update = False
            for function in self._first_update_functions:
                function()

    def _boot_up(self): pass

    @deprecated("Use renderer.bake_text() instead. This method will be removed in a future version.")
    def bake_text(self, text: str, unlimited_y: bool = False, words_indent: bool = False,
                alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, continuous: bool = False, size_x = None, size_y = None, color = None):
        size_x = size_x or self._csize.x
        size_y = size_y or self._csize.y
        size = NvVector2(size_x, size_y)
        self.renderer.bake_text(text, unlimited_y, words_indent, self.style, size, color)

    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist = [CacheType.RelSize])
        self.clear_surfaces()
        self._update_image()
        assert nevu_state.window
        self._regen_surface()
        self._changed = True