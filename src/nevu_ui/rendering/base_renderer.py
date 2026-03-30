from abc import abstractmethod, ABC
import weakref
from typing_extensions import TypedDict, Unpack

from nevu_ui.core.enums import RenderArgs, RenderConfig

class _BaseDrawNamespace(ABC):
    __slots__ = ["_renderer"]
    def __init__(self, renderer):
        self._renderer = weakref.proxy(renderer)
    
    @property
    def root(self): return self._renderer.root
    @property
    def style(self): return self.root.style
    
    @abstractmethod
    def gradient(self, coordinates: tuple[int, int], style = None):
        raise NotImplementedError
    
    @abstractmethod
    def create_clear(self, size):
        raise NotImplementedError
    
    @abstractmethod
    def draw_rect(self, subject = None):
        raise NotImplementedError

    @abstractmethod
    def load_image(self, path: str, size: tuple[int, int] | None = None):
        raise NotImplementedError   

class DrawBaseKwargs(TypedDict):
    pass

class DrawTextKwargs(TypedDict):
    pass

class DrawEffectsKwargs(TypedDict):
    pass

class BaseRenderer(ABC):
    __slots__ = ["_root", "draw", "_pipeline", "_key_to_func"]
    def __init__(self, root):
        self._root = weakref.proxy(root)
        self.draw: _BaseDrawNamespace = self._get_draw_namespace()
        self._pipeline = {}
        self._key_to_func = {
            RenderArgs.DrawBase: self._draw_base,
            RenderArgs.DrawText: self._draw_text,
            RenderArgs.DrawEffects: self._draw_effects
        }
    
    def configure(self, render_key: RenderConfig, render_args: RenderArgs):
        self._pipeline[render_key] = render_args
    
    def run(self, key: RenderConfig, **kwargs):
        """Warning: there is no typehints in kwargs, you need to be careful or use specific run functions"""
        if key not in self._pipeline: return
        pipeline_item = self._pipeline[key]
        if pipeline_item in self._key_to_func:
            self._key_to_func[pipeline_item](**kwargs)
        elif pipeline_item == RenderArgs.DrawCustom:
            pipeline_item.custom_func(**kwargs)
    
    def run_base(self, key: RenderConfig, **kwargs: Unpack[DrawBaseKwargs]):
        self._run_spec(key, RenderArgs.DrawBase, **kwargs)
    
    def run_text(self, key: RenderConfig, **kwargs: Unpack[DrawTextKwargs]):
        self._run_spec(key, RenderArgs.DrawText, **kwargs)
    
    def run_effects(self, key: RenderConfig, **kwargs : Unpack[DrawEffectsKwargs]):
        self._run_spec(key, RenderArgs.DrawEffects, **kwargs)
    
    def _run_spec(self, key: RenderConfig, needed_arg, **kwargs):
        if key not in self._pipeline: return
        if self._pipeline[key] != needed_arg: raise ValueError(f"in {key}, expected {needed_arg.__name__}, got {self._pipeline[key].__name__}")
        self.run(key, **kwargs)
    
    @property
    def root(self): return self._root
    
    @abstractmethod
    def _get_draw_namespace(self):
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