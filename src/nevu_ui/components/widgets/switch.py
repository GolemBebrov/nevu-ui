import copy
from typing import Unpack, Callable

import nevu_ui.core.modules as md
from nevu_ui.core import Annotations
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.presentation.color import SubThemeRole, Color
from nevu_ui.presentation.animations import AnimationManager, animations_library, Vector2Animation
from nevu_ui.core import nevu_state
from nevu_ui.components.widgets import Widget, SwitchKwargs, SwitchTemplate
from nevu_ui.core.enums import RenderConfig, RenderReturnType, CacheType, SwitchAxis, ConstantLayer, RenderArgs, AnimationManagerState
from nevu_ui.utils import time, mouse

class Switch(Widget):
    def __init__(self, base_state: bool = False, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, **constant_kwargs: Unpack[SwitchKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._template = SwitchTemplate(self._template.size, base_state)
    
    def _init_lists(self):
        super()._init_lists()
        self._bg_circle_coords = NvVector2.from_xy(0, 0)
        self._bg_circle_coords_before = NvVector2.from_xy(0, 0)
        self._goal_circle_coords = NvVector2.from_xy(0, 0)
        self._click_pos = None
        self._click_treshold = 5
    
    def _init_flags(self):
        super()._init_flags()
        self._changed_bg_circle = True
        self._custom_secondary_draw = True
    
    def _init_objects(self):
        super()._init_objects()
        self._bg_circle = None
        self._bg_circle_anim_manager = None
        self._bg_surf = None
    
    def _init_numerical(self):
        super()._init_numerical()
        self._after_key_down_time = None
    
    def _on_click_system(self):
        super()._on_click_system()
        self._after_key_down_time = 0
        self._click_pos = mouse.pos
    
    def _on_keyup_system(self):
        super()._on_keyup_system()
        down_time = self._after_key_down_time
        if self._dragging:
            self._after_kup()
        elif down_time is not None and down_time < 0.5:
            self.state = not self.state
        self._after_key_down_time = None
    
    def _on_keyup_abandon_system(self):
        super()._on_keyup_abandon_system()
        if self._dragging:
            self._after_kup()
        self._after_key_down_time = None

    def _after_kup(self):
        self._dragging = False
        self._click_pos = None
        axis = self._get_correct_axis()
        main_coords = 0 if axis == SwitchAxis.Horizontal else 1
        self.state = self._bg_circle_coords[main_coords] > self._rsize[main_coords] / 2 - self.minimal_side / 2
    
    def _add_params(self):
        super()._add_params()
        self._add_param("axis", SwitchAxis, SwitchAxis.Auto, layer = ConstantLayer.Basic)
        self._add_param("on_switch_change", type(None) | Callable, None)
    
    def _lazy_init(self, size: NvVector2 | list, state: bool = False):
        super()._lazy_init(size)
        self.state = state
    
    @property
    def bg_circle_coords(self): return self._bg_circle_coords
    
    @bg_circle_coords.setter
    def bg_circle_coords(self, value): 
        self._set_bg_circle_coords(value)
        
    def _set_bg_circle_coords(self, value, anim_time = 0.15):
        self._bg_circle_anim_manager = AnimationManager(warn=False)
        self._goal_circle_coords = NvVector2(value)
        self._bg_circle_anim_manager.add_start_animation("main", Vector2Animation(self._bg_circle_coords, self._goal_circle_coords, anim_time, animations_library.smootherstep))
    
    @property
    def state(self): return self._state
    
    @state.setter
    def state(self, value):
        if self._state != value:
            on_switch_change = self.get_param_value("on_switch_change")
            if on_switch_change is not None:
                on_switch_change(self, value)
        self._state = value
        axis = self._get_correct_axis()
        main_coord = 0 if axis == SwitchAxis.Horizontal else 1
        bg_coords = self._bg_circle_coords.xy
        if self._state is True:
            bg_coords[main_coord] = self._rsize[main_coord] - self.minimal_side
        else:
            bg_coords[main_coord] = 0
        self.bg_circle_coords = bg_coords
       # self.add_next_frame_action(self._rebuild_bg)
            
    @property
    def minimal_side(self): return min(self._rsize.x, self._rsize.y)
    
    def _create_bg_circle(self):
        minimal_size = self.minimal_side
        size = NvVector2.from_xy(minimal_size, minimal_size)
        dtype = nevu_state.window.renderer_type
        if dtype.pygame_like:
            bg_texture = md.pygame.Surface(size, md.pygame.SRCALPHA)
        elif dtype.raylib:
            bg_texture = NvRenderTexture(size)
        else:
            raise ValueError("Unsupported backend")
        bg_texture.fill((0, 0, 0, 0))
        self.renderer.run_base(
            key = RenderConfig.DrawL1,
            return_type=RenderReturnType.Modify,
            size = size, gradient_support=False, image_support=False, cache = None,
            radius = 999, override_color=self.subtheme_font, standstill=True, modify_object=bg_texture
        )
        return bg_texture
    
    def _rebuild_bg(self):
        if not self._bg_circle or not self._bg_surf: return
        dtype = nevu_state.window.renderer_type
        surface = self.surface
        if dtype.pygame_like:
            assert isinstance(surface, md.pygame.Surface)
            surface.fill((0, 0, 0, 0))
            surface.blit(self._bg_surf, (0, 0))
            surface.blit(self._bg_circle, (self._bg_circle_coords + self._rsize_marg).get_round().get_int_tuple())
        elif dtype.raylib:
            assert isinstance(surface, NvRenderTexture)
            surface_fblit = surface.fast_blit
            with surface:
                surface.fast_clear(Color.Blank)
                begin_blend_mode(md.rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                surface_fblit(self._bg_surf, (0, 0))
                surface_fblit(self._bg_circle, (self._bg_circle_coords + self._rsize_marg).get_round().get_int_tuple())
                end_blend_mode()
        
    
    def _logic_update(self):
        super()._logic_update()
        if self._after_key_down_time is not None:
            self._after_key_down_time += time.dt
        
        bg_anim_manager = self._bg_circle_anim_manager
        
        if bg_anim_manager is not None:
            if bg_anim_manager.state != AnimationManagerState.Start:
                self._bg_circle_coords = self._goal_circle_coords.xy
                self._bg_circle_anim_manager = None
                self._changed_bg_circle = True
                return
            bg_anim_manager.update()
            value = bg_anim_manager.get_animation_value("main")
            if value is not None:
                self._bg_circle_coords = value
                self._changed_bg_circle = True
                
        if not self._bg_circle:
            self._bg_circle = self._create_bg_circle()
            self._changed_bg_circle = True

        curr_pos = mouse.pos
           
        if self._dragging:
            pos = NvVector2.from_xy(0, 0)
            click_pos = self._click_pos
            assert click_pos
            coords_before = self._bg_circle_coords_before
            rsize = self._rsize
            minimal_side = self.minimal_side
            
            if self._get_correct_axis() == SwitchAxis.Horizontal:
                pos.x = max(0, min(curr_pos.x - click_pos.x + coords_before.x, rsize.x - minimal_side))
            else:
                pos.y = max(0, min(curr_pos.y - click_pos.y + coords_before.y, rsize.y - minimal_side))
            
            self._changed_bg_circle = True
            self._bg_circle_coords = pos
            
        elif self._click_pos is not None and self._after_key_down_time is not None:
            if abs(curr_pos.x - self._click_pos.x) > self._click_treshold or abs(curr_pos.y - self._click_pos.y) > self._click_treshold or self._after_key_down_time > 0.5:
                self._dragging = True
                self._bg_circle_coords_before = self._bg_circle_coords.xy
        if self._changed:
            self._changed_bg_circle = False
            
        if self._changed_bg_circle is True:
            self._rebuild_bg()
            self._changed_bg_circle = False
    
    def secondary_draw_content(self):
        super().secondary_draw_content()
        self._bg_surf = self.cache.get(CacheType.Borders)

        
    def _secondary_draw_end(self):
        super()._secondary_draw_end()
        self._bg_circle = self._create_bg_circle()
        self._rebuild_bg()
        
    def _get_correct_axis(self):
        axis = self.get_param_value("axis")
        if axis == SwitchAxis.Auto:
            if self.size.x > self.size.y:
                axis = SwitchAxis.Horizontal
            else:
                axis = SwitchAxis.Vertical
        return axis
    
    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._bg_circle = None
    
    def _create_clone(self):
        return self.__class__(self._template.state, self._template.size, copy.deepcopy(self.style), **self.constant_kwargs)