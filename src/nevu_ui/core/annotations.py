from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from nevu_ui.components.nevuobj import NevuObject
    from nevu_ui.presentation.style import Style

from nevu_ui.core.classes import SurfaceLike
from nevu_ui.core.size.units import SizeRule
from nevu_ui.core.state import nevu_state

VERSION = "0.8.2B"

# Deprecated
nv_error_message_template = """Error occurred in {class_name} with {id}.\n
expected: {expected}, got: {got}
"""

# === New error format ===
nv_error_format_template_start1 = (
    """NEVU UI v{version} error in method: '{method_name}'.\nCause: {message}.\n"""
)
nv_error_format_template_start2 = """NEVU UI v{version} error in BgRenderer method: '{method_name}'.\nSelected Backend: {backend}.\nCause: {message}.\n"""
nv_error_format_template_start3 = """NEVU UI v{version} error.\nCause: {message}.\n"""
nv_error_format_template_ext1 = """Info: {info}.\n"""
nv_error_format_template_ext2 = """Possible solution: {solution}.\n"""
nv_error_format_template_end = """If you believe this is a bug, please report it on 'https://github.com/GolemBebrov/nevu-ui/issues'."""


class Annotations:
    # === size annotations ===
    any_number = float | int
    dest_like = tuple[any_number, any_number] | list[any_number]
    rect_like = tuple[any_number, any_number, any_number, any_number] | list[any_number]

    # === color annotations ===
    rgb_color = tuple[int, int, int]
    rgba_color = tuple[int, int, int, int]
    rgb_like_color = rgb_color | rgba_color
    hsl_color = tuple[float, float, float]
    hsla_color = tuple[float, float, float, int]
    hex_color = str
    any_color = rgb_like_color | hsl_color | hex_color

    # === NevuObject annotation ===
    size_item = int | SizeRule | float
    nevuobj_size = tuple[size_item, size_item] | list[size_item] | Any | None
    nevuobj_style = Any | str | None

    @staticmethod
    def is_surface_like(item: Any) -> TypeGuard[SurfaceLike]:
        result = hasattr(item, "blit") and callable(item.blit)
        result = result and hasattr(item, "fill") and callable(item.fill)
        return result

    @staticmethod
    def get_error_text(base_class: "NevuObject", item, expected_class):
        return nv_error_message_template.format(
            class_name=base_class.__class__.__name__,
            id=id(base_class),
            expected=expected_class.__name__,
            got=type(item),
        )

    @staticmethod
    def format_nverror(
        error_text: str,
        info: str | None = None,
        solution: str | None = None,
        method_name: str = "not specified",
    ) -> str:
        parts = [
            nv_error_format_template_start1.format(
                message=error_text, version=VERSION, method_name=method_name
            )
        ]

        if info:
            parts.append(nv_error_format_template_ext1.format(info=info))

        if solution:
            parts.append(nv_error_format_template_ext2.format(solution=solution))

        parts.append(f"\n{nv_error_format_template_end}\n")

        return "".join(parts)

    @staticmethod
    def format_nverror_renderer(
        error_text: str,
        info: str | None = None,
        solution: str | None = None,
        method_name: str = "not specified",
    ) -> str:
        backend = nevu_state.window._backend
        parts = [
            nv_error_format_template_start2.format(
                message=error_text,
                version=VERSION,
                method_name=method_name,
                backend=backend,
            )
        ]

        if info:
            parts.append(nv_error_format_template_ext1.format(info=info))

        if solution:
            parts.append(nv_error_format_template_ext2.format(solution=solution))

        parts.append(f"\n{nv_error_format_template_end}\n")

        return "".join(parts)

    @staticmethod
    def format_nverror_paramengine(
        error_text: str, info: str | None = None, solution: str | None = None
    ) -> str:
        parts = [
            nv_error_format_template_start3.format(message=error_text, version=VERSION)
        ]

        if info:
            parts.append(nv_error_format_template_ext1.format(info=info))

        if solution:
            parts.append(nv_error_format_template_ext2.format(solution=solution))

        parts.append(f"\n{nv_error_format_template_end}\n")

        return "".join(parts)

    @staticmethod
    def format_nvtype_nvobject_error(
        needed_type: str,
        arg_name: str,
        arg: Any,
        object: "NevuObject",
        method_name: str = "not specified",
    ) -> str:
        arg_name = arg_name.strip()
        needed_type = needed_type.strip()
        return Annotations.format_nverror(
            f"argument '{arg_name}' must be {needed_type}",
            f"\n   object where error occurred: {object.__class__.__name__} with {object.get_param('id')}\n   argument '{arg_name}' current value is: {arg} (type: {arg.__class__.__name__})",
            f"""\n   1. If you are using this function in your code:\n      Find the method in your code specified in the traceback, and recheck the arguments passed to it.\n   2. If this error occurred internally within the framework:\n      Check the traceback to identify which high-level component (e.g., Grid, Panel, Button) received the invalid argument in its constructor""",
            method_name,
        )

    @staticmethod
    def format_nvtype_renderer_error(
        cause_message: str,
        object: "NevuObject",
        method_name: str = "not specified",
        solution: str | None = None,
    ) -> str:
        solution = (
            solution
            or f"""Check the traceback to identify which high-level component (e.g., Grid, Panel, Button) received the invalid argument in its constructor"""
        )
        return Annotations.format_nverror_renderer(
            cause_message,
            f"object where error occurred: {object.__class__.__name__} with {object.get_param('id')}",
            solution,
            method_name,
        )

    @staticmethod
    def format_param_engine_error(
        cause_message: str,
        object: "NevuObject",
        solution: str | None = None,
        add_info: str | None = None,
    ) -> str:
        solution = (
            solution
            or f"""Check the traceback to identify which high-level component (e.g., Grid, Panel, Button) received the invalid argument in its constructor"""
        )
        return Annotations.format_nverror_paramengine(
            cause_message,
            f"object where error occurred: {object.__class__.__name__} with {object.get_param('id')}"
            + (add_info or ""),
            f"""\n   1. If you are using this function in your code:\n      Find the method in your code specified in the traceback, and recheck the arguments passed to it.\n   2. If this error occurred internally within the framework:\n      Check the traceback to identify which high-level component (e.g., Grid, Panel, Button) received the invalid argument in its constructor""",
        )
