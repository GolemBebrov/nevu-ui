from nevu_ui.state import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2

def to_relative(vector: NvVector2) -> NvVector2:
    assert nevu_state.window, "Window is not initialized"
    return vector / nevu_state.window.size