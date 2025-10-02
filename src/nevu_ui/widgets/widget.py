import pygame
import copy

from nevu_ui.nevuobj import NevuObject
from nevu_ui.fast.logic import logic_update_helper
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.color import SubThemeRole
from nevu_ui.rendering.background_renderer import BackgroundRenderer

from nevu_ui.style import (
    Style, default_style
)
from nevu_ui.core_types import (
    Quality, Align, CacheType
)

class Widget(NevuObject):
    _alt: bool
    will_resize: bool
    clickable: bool
    hoverable: bool
    fancy_click_style: bool
    resize_bg_image: bool
    z: int
    inline: bool
    
    def __init__(self, size: NvVector2 | list, style: Style = default_style, **constant_kwargs):
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
        self._add_constant("inline", bool, False)
        
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
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        if self.inline: return
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
        self.cache.clear_selected(whitelist = [CacheType.Image, CacheType.Scaled_Gradient, CacheType.Surface, CacheType.Borders, CacheType.Scaled_Borders, CacheType.Scaled_Background, CacheType.Background])
    
    def _on_style_change(self):
        self._on_style_change_content()
        self._on_style_change_additional()
        
    def _on_style_change_content(self):
        self.clear_surfaces()
        self._changed = True
        
    def _on_style_change_additional(self):
        pass
        
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
        bw = self.relm(self.style.borderwidth)
        return self._csize - (NvVector2(bw, bw)) * 2

    @property
    def _rsize_marg(self) -> NvVector2:
        return self._csize - self._rsize 
    
    def clone(self):
        return Widget(self._lazy_kwargs['size'], copy.deepcopy(self.style), **self.constant_kwargs)
    
    def primary_draw(self):
        super().primary_draw()
        if self._changed:
            if type(self) == Widget: self._changed = False
            self._dirty_rect.append(self.get_rect())
            TRANSPARENT = (0, 0, 0, 0)
            if self.inline: 
                
                surf = self.renderer._scale_background(self._csize.to_round()) if self.will_resize else self.renderer._generate_background()
                #self.surface.fill(TRANSPARENT, [self.coordinates.to_round().to_tuple(),surf.get_size()])
                self.surface.blit(surf, self.coordinates.to_round().to_tuple())
            else:
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
                  alignx: Align = Align.CENTER, aligny: Align = Align.CENTER, continuous: bool = False, size_x = None, size_y = None):
        if continuous: self._bake_text_single_continuous(text); return
        is_popped = False
        ifnn = False
        size_x = size_x or self.relx(self.size[0])
        size_y = size_y or self.rely(self.size[1])
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
            if text_size[0] > size_x:
                lines.append(current_line)
                current_line = word + marg
            else: current_line = test_line
        lines.append(current_line)

        if not unlimited_y:
            while len(lines) * line_height > size_y:
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
        if self.inline:
            container_rect = pygame.Rect(self.coordinates.to_round().to_tuple(), self._csize.to_round())
        else:
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

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._resize_ratio = resize_ratio

        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        self.clear_surfaces()
        self._update_image()
        
        self.surface = pygame.Surface(self._csize, flags = pygame.SRCALPHA)

        self._changed = True