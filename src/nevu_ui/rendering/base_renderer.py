from __future__ import annotations

import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    NotRequired,
    TypedDict,
    Unpack,
    overload,
)

if TYPE_CHECKING:
    from nevu_ui.components.widgets import Widget
    from nevu_ui.presentation.style import Style
    from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.core.annotations import Annotations
from nevu_ui.core.enums import (
    Align,
    HoverState,
    RenderArgs,
    RenderConfig,
    RenderReturnType,
    _RenderArg,
)
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.presentation.color import Color


class _BaseCoreNamespace(ABC):
    __slots__ = ["_renderer"]

    def __init__(self, renderer):
        self._renderer = weakref.proxy(renderer)

    @property
    def root(self) -> "Widget":
        return self._renderer.root

    @property
    def style(self) -> "Style":
        return self.root.style

    @abstractmethod
    def get_gradient(self, style=None):
        raise NotImplementedError

    @abstractmethod
    def get_font(self, name: str | None = None, size=None):
        raise NotImplementedError

    @abstractmethod
    def create_clear(self, size: Annotations.dest_like | NvVector2):
        raise NotImplementedError

    @abstractmethod
    def draw_rect(
        self,
        subject,
        pos: Annotations.dest_like | NvVector2,
        size: Annotations.dest_like | NvVector2,
        color: Annotations.rgba_color = Color.White,
        radii: Annotations.rect_like | int = 0,
    ):
        raise NotImplementedError

    @abstractmethod
    def load_image(
        self, path: str, size: Annotations.dest_like | NvVector2 | None = None
    ):
        raise NotImplementedError

    @abstractmethod
    def measure_text(self, font: Any, text: str, font_size: float) -> NvVector2:
        raise NotImplementedError

    @abstractmethod
    def get_font_size(self, override_size=None) -> int | float:
        raise NotImplementedError

    def get_color_on_hover(self, color: Annotations.rgb_color):
        root = self.root
        hover_state = root._hover_state
        if (
            hover_state == HoverState.Clicked
            and not root.invert_on_click
            and root.clickable
        ):
            color = Color.lighten(color, 0.2)
        elif hover_state == HoverState.Hovered and root.hoverable:
            color = Color.darken(color, 0.2)
        return color

    def split_words(
        self, words: list[str], font: Any, font_size: float, max_width: float, marg=" "
    ) -> list[str]:
        current_line = ""
        lines = []

        for word in words:
            force_next_line = False
            if word == "\n":
                force_next_line = True
            elif len(word) >= 2 and word[0] == "\\" and word[1] == "n":
                force_next_line = True

            if force_next_line:
                lines.append(current_line)
                current_line = ""
                continue

            test_line = current_line + word + marg
            text_size_vec = self.measure_text(font, test_line, font_size)

            if text_size_vec.x > max_width:
                lines.append(current_line)
                current_line = word + marg
            else:
                current_line = test_line

        lines.append(current_line)
        return lines

    def select_return(
        self,
        returntype: RenderReturnType,
        null: Callable,
        outside: Callable,
        raw: Callable,
        modify: Callable,
        create_new: Callable,
    ):
        match returntype:
            case RenderReturnType.Raw:
                return raw
            case RenderReturnType.Null:
                return null
            case RenderReturnType.Outside:
                return outside
            case RenderReturnType.Modify:
                return modify
            case RenderReturnType.CreateNew:
                return create_new

    def normalize_radius(self, radius: int | float | tuple):
        if isinstance(radius, int | float):
            radius = (radius, radius, radius, radius)
        return radius

    def normalize_radius_relative(
        self, radius: int | float | tuple, mid_ratio: int | float | None = None
    ) -> Annotations.rect_like:
        ratio = mid_ratio or self.root.relm(1)
        if not isinstance(radius, int | float):
            return tuple(map(lambda x: x * ratio, radius))  # type: ignore
        radius *= ratio
        radius = (radius, radius, radius, radius)
        return radius

    def align_rect(
        self,
        align_x: Align,
        align_y: Align,
        rect: Annotations.rect_like,
        text_width: float,
        text_height: float,
    ):
        result_x = rect[0]
        result_y = rect[1]

        if align_x == Align.LEFT:
            result_x = rect[0]
        elif align_x == Align.CENTER:
            result_x = rect[0] + (rect[2] - text_width) / 2
        elif align_x == Align.RIGHT:
            result_x = rect[0] + rect[2] - text_width

        if align_y == Align.TOP:
            result_y = rect[1]
        elif align_y == Align.CENTER:
            result_y = rect[1] + (rect[3] - text_height) / 2
        elif align_y == Align.BOTTOM:
            result_y = rect[1] + rect[3] - text_height

        return round(result_x), round(result_y)


class _BaseSpecifiedDraw(ABC):
    """namespace for backend specific draw functions"""

    __slots__ = ["_renderer"]

    def __init__(self, renderer):
        self._renderer = weakref.proxy(renderer)

    @property
    def root(self) -> "Widget":
        return self._renderer.root

    @property
    def style(self) -> Style:
        return self.root.style


class _BaseCall:
    pass


@dataclass(kw_only=True, slots=True)
class DrawBaseCall(_BaseCall):
    size: NvVector2 | None = None
    radius: tuple[int, int, int, int] | int | float | None = None
    color: Annotations.rgba_color | None = None
    cached: bool = False
    standstill: bool = False
    gradient_support: bool = False
    image_support: bool = False
    easy_background: bool = False
    inline: bool = False
    cache: Any = None
    return_type: RenderReturnType = RenderReturnType.Null
    modify_object: Any = None


@dataclass(kw_only=True, slots=True)
class DrawTextCall(_BaseCall):
    text: str
    style: Style | None = None
    font_size: float | None = None
    color: Annotations.rgba_color | None = None
    continuous: bool = False
    size: NvVector2 | None = None
    unlimited_y: bool = False
    words_indent: bool = False
    inline: bool = False
    max_size: NvVector2 | None = None
    return_type: RenderReturnType = RenderReturnType.Null
    modify_object: Any = None


@dataclass(kw_only=True, slots=True)
class DrawEffectsCall(_BaseCall):
    click_gradient: ClickGradient
    click_subject: Any | None = None
    radius: tuple[int, int, int, int] | int | float | None = None
    return_type: RenderReturnType = RenderReturnType.Null
    modify_object: Any = None


@dataclass(kw_only=True, slots=True)
class DrawBordersCall(_BaseCall):
    subject: Any
    color: Annotations.rgba_color | None = None
    border_width: int | float | None = None
    radius: tuple[int, int, int, int] | int | float | None = None
    no_borders: bool = False
    pos: tuple[int, int] | None = None
    return_type: RenderReturnType = RenderReturnType.Null
    bg_color: Annotations.rgb_like_color | None = None
    modify_object: Any = None


class BaseRenderer(ABC):
    __slots__ = [
        "_root",
        "core",
        "_pipeline",
        "_key_to_func",
        "unsafe",
        "release",
        "_render_arg_to_name",
    ]

    def _get_unexpected_error(self, error, func_name):
        raise ValueError(
            Annotations.format_nvtype_renderer_error(
                f"unexpected error - '{error}'", self._root, func_name
            )
        )

    def __init__(self, root):
        self._root: Widget = weakref.proxy(root)  # type: ignore
        self.core: _BaseCoreNamespace = self._get_core_namespace()
        self.unsafe: _BaseSpecifiedDraw = self._get_unsafe_namespace()
        self.release: bool = False
        self._pipeline = {}
        self._key_to_func = {
            RenderArgs.DrawBase: self._draw_base,
            RenderArgs.DrawBorders: self._draw_borders,
            RenderArgs.DrawText: self._draw_text,
            RenderArgs.DrawEffects: self._draw_effects,
        }
        self._render_arg_to_name = {}

    def configure(self, render_key: RenderConfig, render_arg: type[_RenderArg]):
        self._pipeline[render_key] = render_arg

    def base_configure(self):
        self.configure(RenderConfig.DrawL1, RenderArgs.DrawBase)
        self.configure(RenderConfig.DrawL2, RenderArgs.DrawBorders)
        self.configure(RenderConfig.DrawL3, RenderArgs.DrawText)
        self.configure(RenderConfig.DrawL4, RenderArgs.DrawCustom)
        self.configure(RenderConfig.DrawL5, RenderArgs.DrawEffects)

    def run(self, key: RenderConfig, call: _BaseCall):
        """Warning: there is no typehints in kwargs, you need to be careful or use specific run functions"""
        if key not in self._pipeline:
            return
        pipeline_item = self._pipeline[key]
        if self.release:
            if pipeline_item in self._key_to_func:
                return self._key_to_func[pipeline_item](call)
            elif pipeline_item == RenderArgs.DrawCustom:
                return pipeline_item.custom_func(call)
        else:
            try:
                if pipeline_item in self._key_to_func:
                    return self._key_to_func[pipeline_item](call)
                elif pipeline_item == RenderArgs.DrawCustom:
                    return pipeline_item.custom_func(call)
            except Exception as e:
                raise self._get_unexpected_error(
                    e,
                    (self._key_to_func[pipeline_item].__name__)
                    .strip("_")
                    .replace("draw", "run"),
                )

    def run_base(self, call: DrawBaseCall, key: RenderConfig = RenderConfig.Auto):
        return self._run_spec(call, RenderArgs.DrawBase, key)

    def run_borders(self, call: DrawBordersCall, key: RenderConfig = RenderConfig.Auto):
        return self._run_spec(call, RenderArgs.DrawBorders, key)

    def run_text(self, call: DrawTextCall, key: RenderConfig = RenderConfig.Auto):
        try:
            self.core.get_font()
        except Exception as e:
            raise ValueError(
                Annotations.format_nvtype_renderer_error(
                    e,
                    self._root,
                    "run_text",
                    solution="make sure you are running the application with a specified font or change the font_name in the current Widget style",
                )
            )
        return self._run_spec(call, RenderArgs.DrawText, key)

    def run_effects(self, call: DrawEffectsCall, key: RenderConfig = RenderConfig.Auto):
        return self._run_spec(call, RenderArgs.DrawEffects, key)

    def _run_spec(
        self,
        call: _BaseCall,
        needed_arg: Any = RenderArgs.DrawBase,
        key: RenderConfig = RenderConfig.Auto,
    ):
        if key == RenderConfig.Auto:
            key = next((k for k, v in self._pipeline.items() if v == needed_arg), None)  # type: ignore

        if not key:
            raise ValueError(
                f"The required render argument '{needed_arg}' is not configured in the pipeline."
            )

        assert isinstance(key, RenderConfig)

        if key not in self._pipeline:
            return

        if self._pipeline[key] != needed_arg:
            expected_name = getattr(
                needed_arg, "__name__", getattr(needed_arg, "name", str(needed_arg))
            )
            got_name = getattr(
                self._pipeline[key],
                "__name__",
                getattr(self._pipeline[key], "name", str(self._pipeline[key])),
            )
            raise ValueError(f"in {key}, expected {expected_name}, got {got_name}")

        return self.run(key, call)

    @property
    def root(self):
        return self._root

    @property
    def style(self):
        return self.root.style

    @abstractmethod
    def _get_core_namespace(self):
        raise NotImplementedError

    @abstractmethod
    def _get_unsafe_namespace(self):
        raise NotImplementedError

    @abstractmethod
    def _draw_base(self, call: DrawBaseCall):
        raise NotImplementedError

    @abstractmethod
    def _draw_text(self, call: DrawTextCall):
        raise NotImplementedError

    @abstractmethod
    def _draw_effects(self, call: DrawEffectsCall):
        raise NotImplementedError

    @abstractmethod
    def _draw_borders(self, call: DrawBordersCall):
        raise NotImplementedError
