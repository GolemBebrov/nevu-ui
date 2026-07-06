import copy
from functools import partial
from typing import Unpack

from nevu_ui.components.layouts import LayoutType
from nevu_ui.components.widgets import Widget
from nevu_ui.core import modules as md
from nevu_ui.core.enums import (
    Align,
    Backend,
    CacheType,
    EventType,
    HoverState,
    ParamLayer,
    RenderArgs,
    RenderConfig,
    RenderReturnType,
)
from nevu_ui.core.size.rules import SizeRule
from nevu_ui.core.state import _analize_bg, nevu_state
from nevu_ui.fast import Cache, NvParam, NvRect, NvRenderTexture, NvVector2
from nevu_ui.fast.logic.fast_logic import rel_helper, relm_helper, vec_rel_helper
from nevu_ui.fast.nvspecific.nvspec import (
    menu_draw_pygame,
    menu_draw_raylib,
    menu_draw_sdl,
)
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color import Color, SubThemeRole
from nevu_ui.presentation.color.color import is_rgba
from nevu_ui.presentation.style import Style, StyleKwargs, default_style
from nevu_ui.rendering import DrawBaseCall, DrawBordersCall
from nevu_ui.rendering.pygame.new_renderer import PygameRenderer
from nevu_ui.rendering.raylib.new_renderer import RaylibRenderer
from nevu_ui.utils import NevuEvent
from nevu_ui.window import Window


class MenuRendererProxy:
    def __init__(self, menu):
        self.menu = menu
        self.clickable = False
        self.hoverable = False
        self._old_color = (1, 1, 1)
        self.animate_color_change = False
        self._set_new_color = lambda *args: None
        self._changed_size = True
        self.hover_state = HoverState.NotHovered
        self._color_anim_manager = None
        self.inline = NvParam("asd", False, False, False, bool, None, None)
        self.animate_color_change = NvParam(
            "Faputa Solo SOSU!!!!", -1999, False, False, bool, None, None
        )  # Only False is used in hereэ
        self.id = NvParam("id", 9999, "Never", "", str)
        self.alt = NvParam(
            "altushka", 9099, self.menu.alt, None, bool, None, None
        )  # Only self.menu.alt is used in here
        self.inverted = NvParam(
            "inverted", 9099, self.menu.alt, None, bool, None, None
        )  # Only self.menu.inverted is used in here

    def get_param_strict(self, name):
        return getattr(self, name)

    def get_param_value(self, name):
        return getattr(self, name).value

    def get_param(self, name):
        return getattr(self, name)

    @property
    def _draw_borders(self):
        return True

    @property
    def _csize(self):
        return self.menu.rel(self.menu.size)

    @property
    def _hover_state(self):
        return HoverState.NotHovered

    @property
    def subtheme_content(self):
        return self.menu._subtheme_content()

    @property
    def subtheme_border(self):
        return self.menu._subtheme_border()

    def __getattr__(self, name):
        return getattr(self.menu, name)


class MenuLayoutProxy:
    def __init__(self, menu):
        self.menu = menu
        self.first_parent_menu = self.menu
        self.booted = True

    @property
    def original_size(self):
        return self.menu._window.original_size

    def __getattr__(self, name):
        if name == "original_size":
            return self.menu._window.original_size
        return getattr(self.menu, name)


class Menu:
    def _initial_resize(self):
        if self._layouts_cook_time and self._enable_layouts_cook_time:
            if (
                abs(self._layouts_cook_time - self._layouts_cook_time_max)
                > self._layouts_cook_time_delay
            ):
                self.add_next_frame_action(
                    lambda: (
                        self._resize_with_ratio(self._resize_ratio),
                        self._initial_resize(),
                    )
                )
            else:
                self.add_next_frame_action(self._initial_resize)
            self._layouts_cook_time -= 1

    __slots__ = (
        "_absolute_coordinates",
        "_tuple_absolute_coordinates",
        "_draw_borders",
        "_layouts_cook_time",
        "_layouts_cook_time_max",
        "_layouts_cook_time_delay",
        "_first_update_functions",
        "_next_frame_functions",
        "_draw_content",
        "override_color",
        "alt",
        "_window",
        "window_surface",
        "cache",
        "_style",
        "_subtheme_role",
        "_enable_layouts_cook_time",
        "original_size",
        "_renderer_proxy",
        "_renderer",
        "_layout_proxy",
        "_convert_item_coord",
        "_parse_fillx",
        "_parse_gcx",
        "_parse_vx",
        "_percent_helper",
        "_read_item_coords",
        "_resize_ratio",
        "_size",
        "_rel_size",
        "coordinates",
        "_layout",
        "_changed",
        "_relative_placed",
        "_bg_transparent",
        "_relative_x",
        "_relative_y",
        "enabled",
        "visible",
        "_main_draw",
        "_subtheme_border",
        "_subtheme_content",
        "first_window_size",
        "first_coordinates",
        "_opened_sub_menu",
        "_args_menus_to_draw",
        "_surface",
    )

    def __init__(
        self,
        window: Window | None,
        size: list | tuple | NvVector2,
        style: Style = default_style,
        alt: bool = False,
        layout=None,
        _draw_borders=True,
        _draw_content=True,
        override_color=None,
    ):

        # === Layouts cook time ===
        # this is used to prevent incorrect layout positioning before first actial resize
        # the more you add cook_time the more time it will be before app launch
        # delay is used to skip first frame/frames. mostly for optimization
        self._layouts_cook_time = 10
        self._layouts_cook_time_max = 10
        self._layouts_cook_time_delay = 3
        self._enable_layouts_cook_time = False

        # === Coordinates ===
        self._absolute_coordinates = NvVector2.from_xy(0, 0)
        self._tuple_absolute_coordinates = (0, 0)
        self.first_coordinates = NvVector2.from_xy(0, 0)

        # === NevuObject like API ===
        self._draw_borders = _draw_borders
        self._draw_content = _draw_content
        self.override_color = override_color
        self._first_update_functions = [self._initial_resize]
        self._next_frame_functions = []
        self.alt = alt
        self._init_primary(window, style)

        if not self._window:
            return

        # === Window dependent ===
        self.first_window_size = self._window.original_size
        self._renderer_proxy = MenuRendererProxy(self)
        if self._window.renderer_type.raylib:
            self._renderer = RaylibRenderer(self._renderer_proxy)
        else:
            self._renderer = PygameRenderer(self._renderer_proxy)

        self._renderer.base_configure()
        self._borrow_from_layout()
        self._init_size(size)
        self._init_secondary()
        self._init_subtheme(alt)

        self._opened_sub_menu = None
        if layout:
            self.layout = layout

    # NevuObject like rel API
    def relx(
        self, num: int | float, min: int | None = None, max: int | None = None
    ) -> int | float:
        return rel_helper(num, self._resize_ratio.x, min, max)

    def rely(
        self, num: int | float, min: int | None = None, max: int | None = None
    ) -> int | float:
        return rel_helper(num, self._resize_ratio.y, min, max)

    def relm(self, num: int | float) -> int | float:
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, -1.0, -1.0)

    def rel(self, mass: NvVector2) -> NvVector2:
        return vec_rel_helper(mass, self._resize_ratio.x, self._resize_ratio.y)  # type: ignore

    def _clear_all(self):
        if nevu_state.window.renderer_type.raylib:
            self._clear_rl_specific()
        self.cache.clear()

    def _clear_surfaces(self):
        if nevu_state.window.renderer_type.raylib:
            self._clear_rl_specific()
        self.cache.clear_selected(
            whitelist=[
                CacheType.Scaled_Image,
                CacheType.Scaled_Gradient,
                CacheType.Surface,
                CacheType.Borders,
                CacheType.Scaled_Borders,
                CacheType.Scaled_Background,
                CacheType.Background,
                CacheType.Texture,
                CacheType.RlFont,
                CacheType.Background,
                CacheType.Borders,
            ]
        )

    def _borrow_from_layout(self):
        self._layout_proxy = MenuLayoutProxy(self)
        self._convert_item_coord = partial(
            LayoutType._convert_item_coord, self._layout_proxy
        )  # type: ignore
        self._parse_fillx = partial(LayoutType._parse_fillx, self._layout_proxy)  # type: ignore
        self._parse_gcx = partial(LayoutType._parse_gcx, self._layout_proxy)  # type: ignore
        self._parse_vx = partial(LayoutType._parse_vx, self._layout_proxy)  # type: ignore
        self._percent_helper = partial(LayoutType._percent_helper)
        self._read_item_coords = partial(
            LayoutType.read_item_coords, self._layout_proxy
        )  # type: ignore

    @property
    def _sdl_texture(self):
        return self.cache.get_or_exec(CacheType.Texture, self.convert_to_sdl2_texture)

    def convert_to_sdl2_texture(self, surface=None):
        if nevu_state.renderer is None:
            raise ValueError("Window not initialized!")
        assert self._window, "Window not initialized!"
        surface = surface or self._surface
        if not self._window.renderer_type.sdl:
            raise ValueError(
                "convert_to_sdl2_texture is supported only in SDL backend! UWO"
            )
        texture = md.pygame._sdl2.Texture(
            nevu_state.renderer, (self._rel_size).to_tuple(), target=True
        )  # type: ignore
        nevu_state.renderer.target = texture
        ntext = md.pygame._sdl2.Texture.from_surface(nevu_state.renderer, surface)  # type: ignore
        nevu_state.renderer.blit(
            ntext, md.pygame.Rect(0, 0, *(self._rel_size).to_tuple())
        )
        nevu_state.renderer.target = None
        return texture

    def _update_size(self):
        return (self._rel_size).to_pygame()

    @property
    def _pygame_size(self) -> list:
        result = self.cache.get_or_exec(CacheType.RelSize, self._update_size)
        return result or [0, 0]

    def _clear_rl_specific(self):
        Widget._clear_rl_specific(self)  # type: ignore

    def _init_primary(self, window: Window | None, style: Style):
        self._window = window
        self.window_surface = None
        self.cache = Cache()
        self.style = style
        self._subtheme_role = self.style.subtheme_role or SubThemeRole.PRIMARY
        if self._window:
            self._window.add_event(NevuEvent(self, self._resize, EventType.Resize))

    def _init_size(self, size: list | tuple | NvVector2):
        self._resize_ratio = NvVector2.from_xy(1, 1)
        initial_size = list(size)  # type: ignore
        for i in range(len(initial_size)):
            item = initial_size[i]
            if isinstance(item, SizeRule):
                converted, is_ruled = self._convert_item_coord(item, i)
                initial_size[i] = float(converted)
            else:
                initial_size[i] = float(item)
        self.size = NvVector2(initial_size)
        self.coordinates = NvVector2()
        self._layout: LayoutType | None = None

    def _init_secondary(self):
        self._changed = True
        self._update_surface()
        self._relative_placed = False
        self._bg_transparent = False
        self._relative_x = None
        self._relative_y = None
        self.enabled = True
        self.visible = True
        backends_to_draw = {
            Backend.Pygame: menu_draw_pygame,
            Backend.Sdl: menu_draw_sdl,
            Backend.RayLib: menu_draw_raylib,
        }
        self._main_draw = backends_to_draw.get(nevu_state.window._backend)

    def _init_subtheme(self, alt):
        if not alt:
            self._subtheme_border = self._main_subtheme_border
            self._subtheme_content = self._main_subtheme_content
        else:
            self._subtheme_border = self._alt_subtheme_border
            self._subtheme_content = self._alt_subtheme_content

    def _main_subtheme_content(self):
        return self._subtheme.oncolor

    def _main_subtheme_border(self):
        return self._subtheme.color

    def _alt_subtheme_content(self):
        return self._subtheme.oncontainer

    def _alt_subtheme_border(self):
        return self._subtheme.container

    def build_background(self):
        self._renderer.core.create_clear(self._rel_size)
        easy_background = self._draw_borders
        override_color = self.override_color or None or self._subtheme_content()
        if len(override_color) == 3:
            override_color = (*override_color, 255)
        assert is_rgba(override_color)
        if self._draw_content:
            bg = self.cache.get_or_exec(
                CacheType.Background,
                lambda: self._renderer.run_base(
                    DrawBaseCall(
                        color=override_color,
                        radius=self.style.border_radius,
                        gradient_support=True,
                        image_support=True,
                        easy_background=easy_background,
                        return_type=RenderReturnType.CreateNew,
                    ),
                    key=RenderConfig.DrawL1,
                ),
            )
        else:
            bg = self._renderer.core.create_clear(self._rel_size)
        if self._draw_borders:
            final = self.cache.get_or_exec(
                CacheType.Borders,
                lambda: self._renderer.run_borders(
                    DrawBordersCall(
                        subject=bg, return_type=RenderReturnType.CreateNew, pos=(0, 0)
                    ),
                    key=RenderConfig.DrawL2,
                ),
            )
        else:
            return bg
        return final

    def _generate_background(self):
        base_func = self.build_background()
        return (
            self.convert_to_sdl2_texture(base_func)
            if nevu_state.window.renderer_type.sdl
            else base_func
        )

    def add_first_update_action(self, function):
        self._first_update_functions.append(function)

    def add_next_frame_action(self, function):
        self._next_frame_functions.append(function)

    @property
    def _subtheme(self):
        return self.style.colortheme.get_subtheme(self._subtheme_role)

    @property
    def absolute_coordinates(self) -> NvVector2:
        return self._absolute_coordinates

    @absolute_coordinates.setter
    def absolute_coordinates(self, coordinates: NvVector2):
        if self._window is None:
            raise ValueError("Window is not initialized!")
        self._absolute_coordinates = coordinates + self._window.offset
        self._tuple_absolute_coordinates = self._absolute_coordinates.get_int_tuple()

    @property
    def size(self) -> NvVector2:
        return self._size

    @size.setter
    def size(self, size: NvVector2):
        if self._window is None:
            raise ValueError("Window is not initialized!")
        self._size = size
        self._rel_size = size * self._resize_ratio

    def _abs_coordinates_update(self):
        self.absolute_coordinates = self.coordinates

    def open_submenu(self, menu, style: Style | None = None, *args):
        assert isinstance(menu, Menu)
        self._opened_sub_menu = menu
        self._args_menus_to_draw = []
        for item in args:
            self._args_menus_to_draw.extend(item)
        if style:
            self._opened_sub_menu.apply_style_to_layout(style)
        self._opened_sub_menu._resize_with_ratio(self._resize_ratio)

    def close_submenu(self):
        self._opened_sub_menu = None

    def _update_surface(self):
        assert self._window
        if self._window.renderer_type.raylib:
            self._surface = NvRenderTexture(self._rel_size)
            md.rl.set_texture_filter(
                self._surface.texture, md.rl.TextureFilter.TEXTURE_FILTER_BILINEAR
            )
            return
        if self.style.border_radius > 0:
            self._surface = md.pygame.Surface(self._pygame_size, md.pygame.SRCALPHA)
        else:
            self._surface = md.pygame.Surface(self._pygame_size)

        if self.style.transparency:
            self._surface.set_alpha(self.style.transparency)

    def _resize(self, size: NvVector2):
        self._resize_ratio = NvVector2.from_xy(
            size[0] / self.first_window_size[0], size[1] / self.first_window_size[1]
        )
        self._resize_base()

    def _resize_with_ratio(self, ratio: NvVector2):
        self._resize_ratio = ratio
        self._resize_base()

    def _resize_base(self):
        self._clear_surfaces()
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        self._changed = True

        ratio = self._resize_ratio
        window = self._window
        rel_size = self.size * ratio
        style = self.style

        self._rel_size = rel_size

        if window is None:
            return
        if self._relative_placed:
            assert self._relative_x and self._relative_y
            window_size = window.size - window._x2_offset
            target_pos = window_size * (
                NvVector2.from_xy(self._relative_x, self._relative_y) / 100
            )
            widget_center_offset = rel_size / 2
            self.coordinates = target_pos - widget_center_offset

        self._abs_coordinates_update()
        self._update_surface()

        if layout := self._layout:
            layout._resize(ratio)
            layout.coordinates = (rel_size - layout._csize) / 2
            layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates

            layout.update()
            layout.draw()

        if style.transparency:
            self._surface.set_alpha(style.transparency)  # type: ignore

    @property
    def style(self) -> Style:
        return self._style

    @style.setter
    def style(self, style: Style):
        self._style = copy.copy(style)

    def apply_style_to_layout(self, style: Style):
        self._changed = True
        self.style = style()
        self.cache.clear()
        self._init_subtheme(self.alt)
        if self._layout:
            self._layout.apply_style_to_childs(style)

    def apply_style_patch_to_layout(self, **patch: Unpack[StyleKwargs]):
        self._changed = True
        self.style = self.style(**patch)
        self.cache.clear()
        self._init_subtheme(self.alt)
        if self._layout:
            self._layout.apply_style_patch_to_childs(**patch)

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, layout: LayoutType):
        assert self._window, "Window is not set!"
        if not layout._can_be_main_layout:
            raise ValueError(f"Layout {type(layout).__name__} can't be main")
        if self._layout:
            self._layout.kill()
        self._read_item_coords(layout)
        layout._init_start()
        layout._connect_to_menu(self)
        layout.first_parent_menu = self
        layout._boot_up()
        layout._resize(self._resize_ratio)
        relsize = self.size * self._resize_ratio
        layout.coordinates = (relsize - layout._csize) / 2
        layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates
        self._layout = layout
        layout.update()

    def set_coordinates(self, x: int, y: int, relative=False):
        if self._window is None:
            raise ValueError("Window is not initialized!")
        self.coordinates = NvVector2.from_xy(x, y)
        if relative:
            percent_x = (
                (x + self._rel_size[0] / 2)
                / (self._window.size[0] - self._window._crop_width_offset)
                * 100
            )
            percent_y = (
                (y + self._rel_size[1] / 2)
                / (self._window.size[1] - self._window._crop_height_offset)
                * 100
            )
            self._on_set_coordinates(True, percent_x, percent_y)
            return
        self._on_set_coordinates(False, None, None)

    def set_coordinates_relative(self, percent_x: int, percent_y: int):
        if self._window is None:
            raise ValueError("Window is not initialized!")
        self.coordinates = NvVector2.from_xy(
            (self._window.size[0] - self._window._crop_width_offset) / 100 * percent_x
            - self.size[0] / 2,
            (self._window.size[1] - self._window._crop_height_offset) / 100 * percent_y
            - self.size[1] / 2,
        )
        self._on_set_coordinates(True, percent_x, percent_y)

    def _on_set_coordinates(self, arg0, arg1, arg2):
        self._abs_coordinates_update()
        self._relative_placed = arg0
        self._relative_x = arg1
        self._relative_y = arg2
        self.first_coordinates = self.coordinates

    def _draw_sdl(self, bg):
        assert self._window, "Window is not initialized!"
        assert self._window.renderer_type.sdl, "Backend is not SDL!"
        renderer = nevu_state.renderer
        assert renderer, "SDL Renderer is not initialized!"
        layout = self._layout
        if layout is not None:
            renderer.target = self._sdl_texture
            renderer.blit(bg, self.get_rect())
            layout.draw()
            renderer.target = None
        self._window._renderer.blit(self._sdl_texture, self._tuple_absolute_coordinates)

    def _draw_raylib(self, bg):
        assert self._window, "Window is not initialized!"
        assert self._window.renderer_type.raylib, "Backend is not Raylib!"
        display = nevu_state.window.renderer
        main_nvtex = self._surface
        assert self._window.is_raylib(display)
        assert main_nvtex, "Surface is not initialized!"
        assert isinstance(main_nvtex, NvRenderTexture), (
            "Surface is not NvRenderTexture!"
        )

        layout = self._layout

        if layout is not None:
            layout._rl_predraw_widgets()
        with main_nvtex:  # type: ignore
            main_nvtex.fast_clear(Color.Blank)
            begin_blend_mode(5)
            main_nvtex.fast_blit(bg, (0, 0))
            if layout is not None:
                layout.draw()
            end_blend_mode()

        begin_blend_mode(5)
        main_nvtex.fast_blit(
            main_nvtex, self.absolute_coordinates.get_int_tuple()
        )  # dirty cython but fustarrr
        end_blend_mode()

    def _draw_pygame(self, bg):
        assert self._window, "Window is not initialized!"
        assert self._window.renderer_type.pygame, "Backend is not Pygame!"
        surface = self._surface
        assert isinstance(surface, md.pygame.Surface), (
            "_surface is not md.pygame surface!"
        )
        surface.fill(Color.Blank)
        surface.blit(bg, (0, 0))
        layout = self._layout
        if layout is not None:
            layout.draw()
        self._window._renderer.blit(surface, self._tuple_absolute_coordinates)

    def draw(self):
        if not self.visible:
            return
        scaled_bg = self.cache.get_or_exec(
            CacheType.Scaled_Background, self._generate_background
        )
        if main_draw := self._main_draw:
            main_draw(self, scaled_bg)
        else:
            raise ValueError(
                f"Backend {nevu_state.window._backend} is not supported! UWU"
            )
        if submenu := self._opened_sub_menu:
            for item in self._args_menus_to_draw:
                item.draw()
            submenu.draw()

    def update(self):
        if not self.enabled:
            return
        if self._window is None:
            return

        assert isinstance(self._window, Window)

        if self._first_update_functions:
            for action in self._first_update_functions:
                action()
            self._first_update_functions.clear()

        if self._next_frame_functions:
            for action in self._next_frame_functions:
                action()
            self._next_frame_functions.clear()

        if grad := self.style.gradient:
            if hasattr(grad, "update"):
                self._changed = grad.update()
                if self._changed:
                    self._clear_surfaces()

        if submenu := self._opened_sub_menu:
            submenu.update()
            return

        if layout := self._layout:
            layout.absolute_coordinates = layout.coordinates + self.absolute_coordinates
            layout.update()

    def get_rect(self):
        return md.pygame.Rect((0, 0), self._rel_size)

    def get_nvrect(self):
        return NvRect(NvVector2.from_xy(0, 0), self._rel_size)

    def kill(self):
        self.enabled = False

        if self._layout:
            self._layout._kill_base()
            self._layout = None

        if hasattr(self, "_opened_sub_menu") and self._opened_sub_menu:
            self._opened_sub_menu.kill()
            self._opened_sub_menu = None

        if hasattr(self, "_args_menus_to_draw"):
            for item in self._args_menus_to_draw:
                item.kill()
            self._args_menus_to_draw.clear()

        self._clear_rl_specific()
        self._clear_all()

        self._surface = None
        self._window = None

        if nevu_state.window:
            nevu_state.window.z_system.mark_dirty()
