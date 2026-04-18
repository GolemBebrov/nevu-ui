from abc import abstractmethod, ABC
import weakref
from typing_extensions import TypedDict, Unpack, Any, TYPE_CHECKING, NotRequired, Callable, overload

if TYPE_CHECKING:
    from nevu_ui.presentation.style import Style
    from nevu_ui.components.widgets import Widget
    from nevu_ui.rendering.raylib.gradient import ClickGradient
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.annotations import Annotations
from nevu_ui.presentation.color import Color
from nevu_ui.core.enums import RenderArgs, RenderConfig, _RenderArg, HoverState, RenderReturnType, Align

class _BaseCoreNamespace(ABC):
    __slots__ = ["_renderer"]
    def __init__(self, renderer):
        self._renderer = weakref.proxy(renderer)
    
    @property
    def root(self) -> "Widget": return self._renderer.root
    
    @property
    def style(self) -> Style: return self.root.style
    
    @abstractmethod
    def get_gradient(self, style = None):
        raise NotImplementedError
    
    @abstractmethod
    def create_clear(self, size: Annotations.dest_like | NvVector2):
        raise NotImplementedError
    
    @abstractmethod
    def draw_rect(self, subject, pos: Annotations.dest_like | NvVector2, size: Annotations.dest_like | NvVector2, color: Annotations.rgba_color = Color.White, radii: Annotations.rect_like | int = 0):
        raise NotImplementedError

    @abstractmethod
    def load_image(self, path: str, size: Annotations.dest_like | NvVector2 | None = None):
        raise NotImplementedError   
    
    @abstractmethod
    def measure_text(self, font: Any, text: str, font_size: float) -> NvVector2:
        raise NotImplementedError
    
    def get_color_on_hover(self, color: Annotations.rgb_color):
        root = self.root
        hover_state = root._hover_state
        if hover_state == HoverState.CLICKED and not root.get_param_strict("fancy_click_style").value and root.get_param_strict("clickable").value: 
            color = Color.lighten(color, 0.2)
        elif hover_state == HoverState.HOVERED and root.get_param_strict("hoverable").value: 
            color = Color.darken(color, 0.2)
        return color
    
    def split_words(self, words: list[str], font: Any, font_size: float, max_width: float, marg = " ") -> list[str]:
        current_line = ""
        lines = []
        
        for word in words:
            force_next_line = False
            if word == '\n': force_next_line = True
            elif len(word) >= 2 and word[0] == '\\' and word[1] == 'n': force_next_line = True
            
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

    def select_return(self, returntype: RenderReturnType, null: Callable, outside: Callable, raw: Callable, modify: Callable, create_new: Callable): 
        match returntype:
            case RenderReturnType.Raw: return raw
            case RenderReturnType.Null: return null
            case RenderReturnType.Outside: return outside
            case RenderReturnType.Modify: return modify
            case RenderReturnType.CreateNew: return create_new
    
    def normalize_radius(self, radius: int | float | tuple): 
        if isinstance(radius, int | float):
            radius = (radius, radius, radius, radius)
        return radius
    
    def normalize_radius_relative(self, radius: int | float | tuple, mid_ratio: int | float | None = None) -> Annotations.rect_like:
        ratio = mid_ratio or self.root.relm(1)
        if not isinstance(radius, int | float):
            return tuple(map(lambda x: x * ratio, radius)) # type: ignore
        radius *= ratio
        radius = (radius, radius, radius, radius)
        return radius

    def align_rect(self, align_x: Align, align_y: Align, rect: Annotations.rect_like, text_width: float, text_height: float):
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
    def root(self) -> "Widget": return self._renderer.root
    
    @property
    def style(self) -> Style: return self.root.style

class _ModifyKwargs(TypedDict):
    modify_object: NotRequired[Any]

class DrawBaseKwargs(TypedDict):
    size: NotRequired[NvVector2]
    radius: NotRequired[tuple[int, int, int, int] | int | float]
    override_color: NotRequired[Annotations.rgba_color]
    cached: NotRequired[bool]
    standstill: NotRequired[bool]
    gradient_support: NotRequired[bool]
    image_support: NotRequired[bool]
    easy_background: NotRequired[bool]
    override_inline: NotRequired[bool]
    return_type: NotRequired[RenderReturnType]

class AllDrawBaseKwargs(DrawBaseKwargs, _ModifyKwargs): pass

class DrawTextKwargs(TypedDict):
    text: str
    override_style: NotRequired[Style]
    override_font_size: NotRequired[float]
    override_color: NotRequired[Annotations.rgba_color]
    continuous: NotRequired[bool]
    size: NotRequired[NvVector2]
    unlimited_y: NotRequired[bool]
    words_indent: NotRequired[bool]
    override_inline: NotRequired[bool]
    max_size: NotRequired[NvVector2]
    return_type: NotRequired[RenderReturnType]

class AllDrawTextKwargs(DrawTextKwargs, _ModifyKwargs): pass

class DrawEffectsKwargs(TypedDict):
    click_gradient: ClickGradient
    click_subject: NotRequired[Any]
    radius: NotRequired[tuple[int, int, int, int] | int | float]
    return_type: NotRequired[RenderReturnType]

class AllDrawEffectsKwargs(DrawEffectsKwargs, _ModifyKwargs): pass

class DrawBordersKwargs(TypedDict):
    subject: Any
    override_color: NotRequired[Annotations.rgba_color]
    border_width: NotRequired[int | float]
    radius: NotRequired[tuple[int, int, int, int] | int | float]
    no_borders: NotRequired[bool]
    override_position: NotRequired[tuple[int, int]]
    return_type: NotRequired[RenderReturnType]
    override_bg_color: NotRequired[Annotations.rgb_like_color]

class AllDrawBordersKwargs(DrawBordersKwargs, _ModifyKwargs): pass

class BaseRenderer(ABC):
    __slots__ = ["_root", "core", "_pipeline", "_key_to_func", "unsafe"]
    def __init__(self, root):
        self._root: Widget = weakref.proxy(root) # type: ignore
        self.core: _BaseCoreNamespace = self._get_core_namespace()
        self.unsafe: _BaseSpecifiedDraw = self._get_unsafe_namespace()
        self._pipeline = {}
        self._key_to_func = {
            RenderArgs.DrawBase: self._draw_base,
            RenderArgs.DrawBorders: self._draw_borders,
            RenderArgs.DrawText: self._draw_text,
            RenderArgs.DrawEffects: self._draw_effects
        }
    
    def configure(self, render_key: RenderConfig, render_arg: type[_RenderArg]):
        self._pipeline[render_key] = render_arg
    
    def base_configure(self):
        self.configure(RenderConfig.DrawL1, RenderArgs.DrawBase)
        self.configure(RenderConfig.DrawL2, RenderArgs.DrawBorders)
        self.configure(RenderConfig.DrawL3, RenderArgs.DrawText)
        self.configure(RenderConfig.DrawL4, RenderArgs.DrawCustom)
        self.configure(RenderConfig.DrawL5, RenderArgs.DrawEffects)
    
    def run(self, key: RenderConfig, **kwargs):
        """Warning: there is no typehints in kwargs, you need to be careful or use specific run functions"""
        if key not in self._pipeline: return
        pipeline_item = self._pipeline[key]
        if pipeline_item in self._key_to_func:
            return self._key_to_func[pipeline_item](**kwargs)
        elif pipeline_item == RenderArgs.DrawCustom:
            return pipeline_item.custom_func(**kwargs)
    
    @overload
    def run_base(self, key: RenderConfig | None = None, **kwargs: Unpack[DrawBaseKwargs]): ...
    
    @overload
    def run_base(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawBaseKwargs]): ...
    
    def run_base(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawBaseKwargs]):
        return self._run_spec(key, RenderArgs.DrawBase, **kwargs)

    @overload
    def run_borders(self, key: RenderConfig | None = None, **kwargs: Unpack[DrawBordersKwargs]): ...
    
    @overload
    def run_borders(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawBordersKwargs]): ...
    
    def run_borders(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawBordersKwargs]):
        return self._run_spec(key, RenderArgs.DrawBorders, **kwargs)
    
    @overload
    def run_text(self, key: RenderConfig | None = None, **kwargs: Unpack[DrawTextKwargs]): ...
    
    @overload
    def run_text(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawTextKwargs]): ...
    
    def run_text(self, key: RenderConfig | None = None, **kwargs: Unpack[AllDrawTextKwargs]):
        return self._run_spec(key, RenderArgs.DrawText, **kwargs)
    
    @overload
    def run_effects(self, key: RenderConfig | None = None, **kwargs : Unpack[DrawEffectsKwargs]): ...
    
    @overload
    def run_effects(self, key: RenderConfig | None = None, **kwargs : Unpack[AllDrawEffectsKwargs]): ...
    
    def run_effects(self, key: RenderConfig | None = None, **kwargs : Unpack[AllDrawEffectsKwargs]):
        return self._run_spec(key, RenderArgs.DrawEffects, **kwargs)
    
    def _run_spec(self, key: RenderConfig | None = None, needed_arg: Any = RenderArgs.DrawBase, **kwargs):
        if not key:
            key = self._pipeline[list(self._pipeline.values()).index(needed_arg)]
        assert key
        if key not in self._pipeline: return
        if self._pipeline[key] != needed_arg: raise ValueError(f"in {key}, expected {needed_arg.__name__}, got {self._pipeline[key].__name__}")
        return self.run(key, **kwargs)
    
    @property
    def root(self): return self._root
    
    @property
    def style(self): return self.root.style
    
    @abstractmethod
    def _get_core_namespace(self):
        raise NotImplementedError

    @abstractmethod
    def _get_unsafe_namespace(self):
        raise NotImplementedError
    
    @abstractmethod
    def _draw_base(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def _draw_text(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def _draw_effects(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def _draw_borders(self, **kwargs):
        raise NotImplementedError
    