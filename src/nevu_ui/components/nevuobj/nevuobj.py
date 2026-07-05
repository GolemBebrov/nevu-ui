import copy
import difflib
import math
import weakref
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Unpack, overload

from typing_extensions import deprecated

import nevu_ui.core.modules as md

if TYPE_CHECKING:
    from pyray import Font

from nevu_ui.components.nevuobj.typehints import (
    NevuObjectKwargs,
    NevuObjectKwargsLong,
    NevuObjectKwargsShort,
    NevuObjectTemplate,
    nevu_object_globals,
)
from nevu_ui.core import Annotations
from nevu_ui.core.classes import Events, Strategy, _strategy_type
from nevu_ui.core.enums import (
    AnimationType,
    CacheType,
    EventType,
    HoverState,
    ParamLayer,
)
from nevu_ui.core.size.rules import Px, SizeRule
from nevu_ui.core.state import nevu_state
from nevu_ui.fast import NevuCobject, NvVector2, ZRequest
from nevu_ui.fast.logic import get_rect_helper, get_rect_helper_pygame
from nevu_ui.overlay.tooltip import Tooltip
from nevu_ui.parser.base import standart_config
from nevu_ui.presentation.animations import AnimationManager
from nevu_ui.presentation.color import SubThemeRole
from nevu_ui.presentation.style import Style, default_style
from nevu_ui.rendering.base_renderer import BaseRenderer
from nevu_ui.rendering.pygame.new_renderer import PygameRenderer
from nevu_ui.rendering.raylib.new_renderer import RaylibRenderer
from nevu_ui.utils import NevuEvent

global_counter = 0


def add_obj(self):
    global global_counter
    global_counter += 1
    # print(self.__class__.__name__, "added, counter:", global_counter)


def del_obj(self):
    global global_counter
    global_counter -= 1
    # rint(self, "deleted, counter:", global_counter)


class NevuObject(NevuCobject):
    _supports_tuple_borderradius = True
    # === Params ===
    id: str | None
    floating: bool
    single_instance: bool
    events: Events
    z: int
    subtheme_role: SubThemeRole
    animation_manager: AnimationManager
    tooltip: Tooltip
    # ==============

    renderer: BaseRenderer

    # INIT STRUCTURE: ====================
    #    __init__ >
    #        preinit >
    #            flags
    #            test_flags
    #            constants l1
    #        basic_variables >
    #            booleans/dependent flags
    #            numerical
    #            lists/vectors
    #            constants l2
    #        complicated_variables >
    #            style
    #            objects
    #            constants l3
    #    _lazy_init >
    #        size/master dependent code
    # ======================================

    _supports_global_size = True

    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size,
        style: Annotations.nevuobj_style,
        **constant_kwargs: Unpack[NevuObjectKwargsShort],
    ): ...
    @overload
    def __init__(
        self,
        size: Annotations.nevuobj_size,
        style: Annotations.nevuobj_style,
        **constant_kwargs: Unpack[NevuObjectKwargsLong],
    ): ...
    def __init__(
        self,
        size: Annotations.nevuobj_size,
        style: Annotations.nevuobj_style,
        **constant_kwargs: Unpack[NevuObjectKwargs],
    ):
        self.constant_kwargs = constant_kwargs.copy()
        if self._supports_global_size:
            _size = size or nevu_object_globals.library.get("size")
        else:
            _size = size
        if _size is None:
            raise ValueError(
                f"Size is None in {self.__class__.__name__} and no global size set."
            )
        self._template = NevuObjectTemplate(_size)
        style = style or nevu_object_globals.library.get("style") or default_style
        self._first_update_functions = []

        # === Pre Init ===
        # === Flags ===
        self._init_flags()

        # === Test Flags ===
        self._init_test_flags()

        # === Constants Declaration ===
        self._declare_constants(**constant_kwargs)

        # === Constants L1 ===
        self._init_param_layer(ParamLayer.Top, **constant_kwargs)

        # === Basic Variables ===
        # === Booleans(Flags) ===
        self._init_booleans()

        # === Numerical(int, float) ===
        self._init_numerical()

        # === Lists/Vectors ===
        self._init_lists()

        # === Constants L2 ===
        self._init_param_layer(ParamLayer.Basic, **constant_kwargs)

        # === Complicated Variables ===
        # === Style ===
        self._init_style(style)  # type: ignore

        # === Objects ===
        self._init_objects()

        # === Constants L3 ===
        self._init_param_layer(ParamLayer.Complicated, **constant_kwargs)

        if __debug__:
            add_obj(self)
            weakref.finalize(self, del_obj, self.__class__.__name__)

    # === ParamEngine functions ===
    # INFO: ParamEngine Version V4.2C

    def _add_param(
        self,
        name,
        supported_classes: tuple | Any,
        default: Any,
        getter: Callable | None = None,
        setter: Callable | None = None,
        layer=1,
    ):
        super()._add_param(
            name,
            supported_classes,
            default,
            self._ensure_func_safety(getter),
            self._ensure_func_safety(setter),
            layer,
        )

    def _change_param_name(self, name: str, new_name: str):
        if name == new_name:
            return
        param_names = self._get_param_names()
        if name not in param_names:
            raise KeyError(f"Constant '{name}' does not exist and cannot be renamed.")
        if new_name in param_names:
            raise ValueError(f"Constant '{new_name}' already exists.")
        param = self._find_param(name)
        assert param
        param.name = new_name

    def _change_param_default(self, name: str, default: Any):
        if name not in self._get_param_names():
            raise KeyError(f"Constant '{name}' does not exist and cannot be changed.")
        self.get_param_strict(name).default = default

    def _block_param(self, name: str):
        param_names = self._get_param_names()
        if name not in param_names:
            raise KeyError(f"Constant '{name}' does not exist and cannot be renamed.")
        self._blacklisted_params.append(name)

    def _add_params(self):
        self._add_param("id", (str, type(None)), None)
        self._add_param("floating", bool, False)
        self._add_param("single_instance", bool, False)
        self._add_param(
            "events", Events, Events(), setter=self._set_events, layer=ParamLayer.Basic
        )
        self._add_param("z", int, 0)
        self._add_param_link("depth", "z")
        self._add_param(
            "tooltip",
            Tooltip | type(None),
            None,
            layer=ParamLayer.Lazy,
            setter=self._tooltip_setter,
        )
        self._add_param(
            "subtheme_role",
            SubThemeRole,
            SubThemeRole.TERTIARY,
            setter=self._subtheme_role_setter,
            layer=ParamLayer.Complicated,
        )
        self._add_param(
            "animation_manager",
            AnimationManager | type(None),
            None,
            layer=ParamLayer.Top,
        )
        self._add_param_link("anim_manager", "animation_manager")
        self._add_param(
            "strategy", type(_strategy_type), Strategy.Relative, layer=ParamLayer.Basic
        )

    def _add_param_link(self, link_name: str, name: str):
        self._param_links[link_name] = name

    def _preinit_params(self, layer):
        for param in self.params:
            if param.layer != layer:
                continue
            if param.name in self.constant_kwargs:
                continue
            val = nevu_object_globals.library.get(param.name)
            param.value = val if val is not None else param.default

    def _apply_params(self, current_layer, **kwargs):
        constant_name = None
        needed_types = None
        processed = set()
        for name, value in kwargs.items():
            name = name.lower()
            constant_name, needed_types, layer = self._extract_param_data(name)
            if current_layer != layer:
                continue
            if constant_name in processed:
                raise ValueError(f"Constant {name}({constant_name}) is already set.")
            self._process_param(name, constant_name, needed_types, value)
            processed.add(constant_name)

    def _extract_param_data(self, name):
        if name in self._get_param_names():
            param = self._find_param(name)
        elif name in self._param_links.keys():
            param = self._find_param(self._param_links[name])
        else:
            available_param_names = ", ".join(sorted(self._get_param_names()))
            suggestion = difflib.get_close_matches(name, self._get_param_names())
            cause = f"parameter '{name}' not found"
            if suggestion:
                cause += f". did you mean {suggestion[0]}?"
            raise ValueError(
                Annotations.format_param_engine_error(
                    cause,
                    self,
                    add_info="\nAvailable params:\n" + available_param_names,
                )
            )

        assert param
        return param.name, param.type, param.layer

    def _is_valid_type(self, value, needed_types):
        needed_types = (needed_types,)
        for needed_type in needed_types:
            if needed_type == Callable and callable(value):
                return True
            if needed_type == Any:
                return True
            if type(needed_type) == tuple:
                if needed_type[0] == Any:
                    return True
            # print(value, needed_type)
            if isinstance(value, needed_type):
                return True
        return False

    def _process_param(self, name, param_name, needed_types, value):
        assert needed_types
        if param_name not in self._get_param_names():
            if param_name in self._blacklisted_params:
                raise ValueError(f"Param {name} is unconfigurable")
            if not self._is_valid_type(value, needed_types):
                raise TypeError(
                    f"Invalid type for param '{param_name}' in {self.__class__.__name__} instance. ",
                    f"Expected {needed_types}, but got {type(value).__name__}.",
                )
        param = self.get_param_strict(param_name)
        assert param
        param.set(value)

    # === Initialization ===
    def _boot_up(self):
        pass

    def _create_template(self, size: NvVector2 | list):
        return NevuObjectTemplate(size)

    def _init_flags(self):
        pass

    def _init_test_flags(self):
        pass

    def _init_numerical(self):
        pass

    def _declare_constants(self, **kwargs):
        self._add_params()

    def _init_param_layer(self, layer, **kwargs):
        self._preinit_params(layer)
        self._apply_params(layer, **kwargs)

    def _init_style(self, style: Style | str):
        if isinstance(style, str):
            if result := standart_config.styles.get(style, None):
                self.style = result
            else:
                if not standart_config.styles:
                    raise ValueError("No config styles found")
                suggestions = difflib.get_close_matches(
                    "style", standart_config.styles.keys()
                )
                err_msg = f"style {style} not found."
                if suggestions:
                    err_msg += f" did you mean {', '.join(suggestions)}?"
                raise ValueError(Annotations.format_param_engine_error(err_msg, self))
        else:
            self.style = style

    def _init_objects(self):
        self._hover_state: HoverState = HoverState.NotHovered
        if self.animation_manager is not None:
            self.animation_manager = copy.deepcopy(self.animation_manager)
        else:
            self.animation_manager = AnimationManager()
        self.z_request: ZRequest | None = None
        if nevu_state.window.renderer_type.raylib:
            self.renderer = RaylibRenderer(self)
        else:
            self.renderer = PygameRenderer(self)
        self.renderer.base_configure()

    def _set_position_anim_flag(self, value: bool):
        self._has_position_anim = value

    def _init_booleans(self):
        pass

    def _init_lists(self):
        self._resize_ratio = NvVector2(1, 1)
        self.coordinates = NvVector2()
        self.absolute_coordinates = NvVector2()
        self._next_frame_functions = []

    def _init_start(self):
        if self.booted:
            return
        self._wait_mode = False
        self._template.size = list(self._template.size)
        for i, item in enumerate(self._template.size):  # type: ignore
            self._template.size[i] = self._handle_size_rules(item)  # type: ignore
        if not self._wait_mode:
            self._lazy_init(**self._template.__dict__)

    def _lazy_init_wrapper(self, *args, **kwargs):
        self._lazy_init(*args, **kwargs)
        self._init_param_layer(ParamLayer.Lazy, **self.constant_kwargs)

    def _lazy_init(self, size):
        self.size = size if isinstance(size, NvVector2) else NvVector2(size)
        self.original_size = self.size.copy()
        self.add_first_update_action(self._reset_tooltip)

    def _reset_tooltip(self):
        if self.constant_kwargs.get("tooltip"):
            self.tooltip = self.constant_kwargs.get("tooltip")

    def _handle_size_rules(
        self, number: SizeRule | int | float
    ) -> SizeRule | int | float:
        if isinstance(number, SizeRule):
            if type(number) == Px:
                return number.value
            else:
                self._wait_mode = True
        return number

    # === Utils ===

    def _coordinates_setter(self, coordinates: NvVector2) -> bool:
        return True

    @property
    def wait_mode(self):
        return self._wait_mode

    @wait_mode.setter
    def wait_mode(self, value: bool):
        if self._wait_mode == True and not value:
            self._lazy_init_wrapper(**self._template.__dict__)
        self._wait_mode = value

    @property
    def _csize(self) -> NvVector2:
        return self.cache.get_or_exec(CacheType.RelSize, self._update_size)

    def add_first_update_action(self, function):
        self._first_update_functions.append(self._ensure_func_safety(function))

    def add_next_frame_action(self, function):
        self._next_frame_functions.append(self._ensure_func_safety(function))

    def _get_raylib_font_nocache(self, override_size=None) -> "Font":
        font_size = self.renderer.core.get_font_size(override_size)

        def _load_font_with_cyrillic():
            codepoints = list(range(32, 127)) + list(range(1024, 1104)) + [1025, 1105]
            glyph_count = len(codepoints)
            rl = md.rl
            ffi = rl.ffi
            c_array = ffi.new("int[]", codepoints)
            c_ptr = ffi.cast("int *", c_array)
            if self.style.font_name == "Arial":
                font = rl.get_font_default()
            else:
                font = rl.load_font_ex(
                    self.style.font_name, round(font_size), c_ptr, glyph_count
                )
            if font.glyphCount == 0:
                raise ValueError(f"Font {self.style.font_name} not found")
            return font

        return _load_font_with_cyrillic()

    def get_font(self, override_size=None):
        return self.renderer.core.get_font(override_size)

    @property
    def max_borderradius(self):
        return min(self._no_borders_size.x, self._no_borders_size.y) / 2

    @property
    def _no_borders_size(self) -> NvVector2:
        bw = self.relm(self.style.border_width)
        return self._csize - (NvVector2.from_xy(bw, bw) * 2) + NvVector2.from_xy(1, 1)

    @property
    def _borders_marg_size(self) -> NvVector2:
        return (self._csize - self._no_borders_size) / 2

    def _subtheme_role_setter(self, value: SubThemeRole):
        self.cache.clear()
        self._on_subtheme_role_change()
        return value

    def _on_subtheme_role_change(self):
        pass

    @property
    def _subtheme(self):
        return self.style.colortheme.get_subtheme(
            self.get_param_strict("subtheme_role").value
        )

    def _tooltip_setter(self, value: Tooltip | None):
        if value:
            value.connect_to_master(self)
        return value

    # === Action functions ===
    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value
        self._on_visible_set()

    def _on_visible_set(self):
        pass

    def activate(self):
        self.active = True

    def disactivate(self):
        self.active = False

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        self._on_active_set()

    def _on_active_set(self):
        pass

        # === Event functions ===

    def subscribe(self, event: NevuEvent):
        """Adds a new event listener to the object.
        Args:
            event (NevuEvent): The event to subscribe
        Returns:
            None
        """
        self.get_param_value("events").add(event)

    def _set_events(self, value: Events):
        value.on_add = self._on_event_add  # type: ignore
        return self.get_param_value("events")

    def _on_event_add(self):
        self.constant_kwargs["events"] = self.get_param_value("events")

    def _resize(self, resize_ratio: NvVector2):
        if self.get_param_value("strategy") == Strategy.Static:
            return
        self._resize_content(resize_ratio)

    def _resize_content(self, resize_ratio: NvVector2):
        self._changed = True
        self._resize_ratio = resize_ratio
        self.cache.clear_selected(whitelist=[CacheType.RelSize])
        if self.tooltip:
            self.tooltip.resize(resize_ratio)

    @property
    def style(self) -> Style:
        return self._style

    @style.setter
    def style(self, style: Style):
        self._changed = True
        self._style = copy.copy(style)
        self._on_style_change()

    def _on_style_change(self):
        self._on_style_change_content()
        self._on_style_change_additional()

    def _on_style_change_content(self):
        pass

    def _on_style_change_additional(self):
        pass

        # === Zsystem functions ===

        # === User hooks ===

    def on_click(self):
        """Override this function to run code when the object is clicked"""

    def on_hover(self):
        """Override this function to run code when the object is hovered"""

    def on_keyup(self):
        """Override this function to run code when a key is released"""

    def on_keyup_abandon(self):
        """Override this function to run code when a key is released outside of the object"""

    def on_unhover(self):
        """Override this function to run code when the object is unhovered"""

    def on_scroll(self, side: bool):
        """Override this function to run code when the object is scrolled"""

    def on_change(self):
        """Override this function to run code when the object is changed"""

        # === Update stubs ===

    def secondary_update(self):
        pass

    def _logic_update(self):
        pass

    def _animation_update(self):
        pass

    def _event_update(self, events):
        pass

        # === Draw stubs ===

    def _primary_draw(self):
        pass

    def secondary_draw_content(self):
        pass

    def _secondary_draw_end(self):
        pass

    def secondary_draw(self):
        pass

        # === Hover state ===

    @property
    def hover_state(self):
        return self._hover_state

    @hover_state.setter
    def hover_state(self, value: HoverState):
        if self._hover_state == value and not self._force_state_set_continue:
            return
        self.on_state_change(value)
        self._on_state_change_system(value)

        if self._force_state_set_continue:
            self._force_state_set_continue = False
        self._hover_state = value

        self.style.mark_state(value)

        match self._hover_state:
            case HoverState.Clicked:
                self._group_on_click()
            case HoverState.Hovered:
                if self._is_kup:
                    self._group_on_keyup()
                    self._is_kup = False
                else:
                    self._group_on_hover()
            case HoverState.NotHovered:
                if self._kup_abandoned:
                    self._group_on_keyup_abandon()
                    self._kup_abandoned = False
                else:
                    self._group_on_unhover()

        self.after_state_change()
        self._after_state_change_system()

    def after_state_change(self):
        pass

    def _after_state_change_system(self):
        pass

        # === Rect functions ===

    def get_pygame_rect(self):
        return get_rect_helper_pygame(
            self.absolute_coordinates, self._resize_ratio, self.size
        )

    def get_rect_static(self):
        return get_rect_helper(self.coordinates, self._resize_ratio, self.size)

        # === Cache update functions ===

    def _update_size(self):
        return self.rel(self.size)

        # === Relative functions ===
        # Empty... :3
        # Realized in NevuCobject

        # === Clone functions ===

    def _create_clone(self):
        cls = self.__class__
        return cls(
            self._template["size"], copy.deepcopy(self.style), **self.constant_kwargs
        )

    def clone(self):
        new_self = self._create_clone()
        self._on_copy_system(new_self)
        self.on_copy(new_self)
        new_self._on_copy_system_after()
        new_self.on_copy_after()
        return new_self

    def _on_copy_system(self, clone: "NevuObject", no_cache: bool = False):
        clone._active = self._active
        clone._visible = self._visible
        clone._dead = self._dead
        if not no_cache:
            clone.cache = self.cache.copy()

    def _on_copy_system_after(self):
        pass

    def on_copy(self, clone):
        pass

    def on_copy_after(self):
        pass

    def __deepcopy__(self, *args, **kwargs):
        return self.clone()

        # === Kill functions ===

    def _clear_z_request(self):
        if hasattr(self, "z_request") and self.z_request:
            self.z_request.on_click_func = None
            self.z_request.on_hover_func = None
            self.z_request.on_scroll_func = None
            self.z_request.on_unhover_func = None
            self.z_request.on_keyup_func = None
            self.z_request.on_keyup_abandon_func = None
            self.z_request = None

    def kill(self):
        self._kill_base()
        self._kill_end()

    def _kill_base(self):
        self._dead = True
        self.visible = False
        self.is_active = False

        self._clear_z_request()
        if hasattr(self, "renderer"):
            self.renderer = None
        if self._sended_z_link and nevu_state.window:
            nevu_state.window.z_system.mark_dirty()

    def _kill_end(self):
        pass
