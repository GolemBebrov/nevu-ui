import math
from typing import Unpack

import nevu_ui.core.modules as md
from nevu_ui.core import Annotations
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.enums import ConstantLayer, RenderConfig, RenderReturnType
from nevu_ui.core.state import nevu_state
from nevu_ui.presentation.color import PairColorRole, Color
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.components.widgets import Widget, ProgressBarKwargs

class ProgressBar(Widget):
    _current_value: int | float
    color_pair_role: PairColorRole
    def __init__(self, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, **constant_kwargs: Unpack[ProgressBarKwargs]):
        """Initializes a new ProgressBar widget.

        A visual widget that indicates the progress of an operation or a value
        within a defined range. The filled portion of the bar represents the
        current value relative to its minimum and maximum bounds.

        Parameters
        ----------
        size : NvVector2 | list
            The size of the widget.
        style : Style, optional
            The style object for the widget. Defaults to default_style.
        min_value : int or float, optional
            The minimum value of the progress bar. Alias: 'min'.
            Passed via keyword arguments. Defaults to 0.
        max_value : int or float, optional
            The maximum value of the progress bar. Alias: 'max'.
            Passed via keyword arguments. Defaults to 100.
        value : int or float, optional
            The initial value of the progress bar. This will determine the
            initial filled percentage. Passed via keyword arguments.
            Defaults to 0.
        color_pair_role : PairColorRole, optional
            The color role used to determine the color of the filled progress
            portion. Alias: 'role'. Passed via keyword arguments.
            Defaults to PairColorRole.BACKGROUND.
        """
        super().__init__(size, style, **constant_kwargs)
        self.set_progress_by_value(self.value)
    
    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self._changed_value = False
        self._supports_tuple_borderradius = False
    
    def _add_params(self):
        super()._add_params()
        self._add_param("min_value", (int, float), 0, layer=ConstantLayer.Top)
        self._add_param_link("min", "min_value")
        self._add_param("max_value", (int, float), 100, layer=ConstantLayer.Top)
        self._add_param_link("max", "max_value")
        self._add_param("value", (int, float), 0, getter=self.value_getter, setter=self.value_setter, layer=ConstantLayer.Top)
        self._add_param("color_pair_role", PairColorRole, PairColorRole.BACKGROUND)
        self._add_param_link("role", "color_pair_role")
        
    @property
    def progress(self): return self._progress
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.value = self.min_value + (self.max_value - self.min_value) * self._progress
    
    @property
    def min_value(self): return self.get_param_strict("min_value").value
    @min_value.setter
    def min_value(self, value): self.set_param_value("min_value", value)
    @property
    def max_value(self): return self.get_param_strict("max_value").value
    @max_value.setter
    def max_value(self, value): self.set_param_value("max_value", value)
    @property
    def value(self): return self.get_param_strict("value").value
    @value.setter
    def value(self, value): self.set_param_value("value", value)
    
    def set_progress_by_value(self, value: int | float):
        self.progress = (value - self.min_value) / (self.max_value - self.min_value)
        
    def value_getter(self): return self.get_param_strict("value").value
    def value_setter(self, value): 
        self.get_param_strict("value").value = value
        self._changed_value = True
        if not hasattr(self, "_progress"):
            self.set_progress_by_value(value)
        else:
            self.on_value_change()
            self._on_value_change_system()
    
    def _on_value_change_system(self): pass
    def on_value_change(self): pass
    
    def _init_alt(self):
        super()._init_alt()
        self._subtheme_progress = self._alt_subtheme_progress if self.alt else self._main_subtheme_progress
    
    @property
    def _main_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.color_pair_role).color

    @property
    def _alt_subtheme_progress(self):
        return self.style.colortheme.get_pair(self.color_pair_role).oncolor
    
    def _primary_draw(self):
        super()._primary_draw()
        if self._changed and self.surface:
            if nevu_state.window.is_dtype.raylib:
                self.bgsurface = NvRenderTexture(NvVector2(self.surface.texture.width, self.surface.texture.height)) #type: ignore
                display = nevu_state.window.display
                assert nevu_state.window.is_raylib(display)
                with self.bgsurface: #type: ignore
                    display.clear(Color.Blank)
                    display.blit_rect_vec(self.surface.texture, (0,0), mode = md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY) #type: ignore
            else:
                self.bgsurface = md.pygame.Surface(self.surface.get_size(), md.pygame.SRCALPHA)
                self.bgsurface.blit(self.surface, (0,0))
                self.surface.fill((0,0,0,0))
            self._changed_value = True
            self.clear_texture()
    
    def _create_surface(self, bar_surf, coords):
        assert self.surface
        self.clear_texture()
        display = nevu_state.window.display
        if nevu_state.window.is_dtype.raylib:
            with self.surface: #type: ignore
                assert nevu_state.window.is_raylib(display)
                display.clear(Color.Blank)
                display.blit_rect_vec(self.bgsurface.texture, (0,0), mode = md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY) #type: ignore
                display.blit_rect_vec(bar_surf.texture, coords, mode = md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            return
        self.surface.blit(self.bgsurface, (0,0))
        self.surface.blit(bar_surf, coords)
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not (self._changed_value) or self.progress < 0: return
        self._changed_value = False
        inner_vec = self._rsize
        size = NvVector2(math.ceil(inner_vec.x * self.progress), inner_vec.y)
        bw = math.ceil(self.relm(self.style.border_width))
        radius = self.relm(self.style.border_radius) - bw
        min_side = min(self._rsize.x // 2, self._rsize.y // 2)
        radius = min(min_side, max(radius, 0))
        
        y_decrease = 0
        if size.x / 2 < radius:
            y_decrease = math.ceil(radius - (size.x / 2))
            if size.y - y_decrease * 2 > 0: size.y -= y_decrease * 2
        
        if size.x <= 0 or size.y <= 0: return
        
        if isinstance(radius, int | float):
            radius = min(size.x / 2, size.y / 2, radius)
            radius = tuple((radius, radius, radius, radius))
            
        color = self._subtheme_progress
        if len(color) == 3: color = (*color, 255)
        adds = {}
        #if nevu_state.window.is_dtype.raylib:
        #    adds["blitmode"] = md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY
        surf = self.renderer.core.create_clear(size)
        self.renderer.run_base(
                key=RenderConfig.DrawL1,
                radius=self.style.border_radius,
                easy_background=False,
                size = size,
                override_color=color,
                gradient_support=False,
                return_type=RenderReturnType.Modify,
                modify_object=surf
            )
        #surf = self.renderer._create_surf_base(size, override_color=color, radius=radius, **adds)#blitmode=md.rl.BlendMode.BLEND_ALPHA, sdfmode=md.rl.BlendMode.BLEND_ALPHA)
        if nevu_state.window.is_dtype.raylib:
            md.rl.set_texture_filter(surf.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
        coords = (self._rsize_marg)
        coords.y += y_decrease
        assert self.surface
        
        self._create_surface(surf, coords.to_tuple())