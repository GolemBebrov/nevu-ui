from __future__ import annotations

from typing import TYPE_CHECKING, Any
from .annotations import VERSION

if TYPE_CHECKING:
    from nevu_ui.components.nevuobject import NevuObject

from nevu_ui.core.state import nevu_state

_nv_error_format_template_start1 = (
    """NEVU UI v{version} error in method: '{method_name}'.\nCause: {message}.\n"""
)
_nv_error_format_template_start2 = """NEVU UI v{version} Renderering Error in method: '{method_name}'.\nSelected Backend: {backend}.\nCause: {message}.\n"""
_nv_error_format_template_start3 = """NEVU UI v{version} error.\nCause: {message}.\n"""
_nv_error_format_template_ext1 = """Info: {info}.\n"""
_nv_error_format_template_ext2 = """Possible solution: {solution}.\n"""
_nv_error_format_template_end = """If you believe this is a bug, please report it on 'https://github.com/GolemBebrov/nevu-ui/issues'."""


def format_nverror(
    error_text: str,
    info: str | None = None,
    solution: str | None = None,
    method_name: str = "not specified",
) -> str:
    parts = [
        _nv_error_format_template_start1.format(
            message=error_text, version=VERSION, method_name=method_name
        )
    ]
    if info:
        parts.append(_nv_error_format_template_ext1.format(info=info))

    if solution:
        parts.append(_nv_error_format_template_ext2.format(solution=solution))

    parts.append(f"\n{_nv_error_format_template_end}\n")
    return "".join(parts)

def format_nverror_renderer(
    error_text: str,
    info: str | None = None,
    solution: str | None = None,
    method_name: str = "not specified",
) -> str:
    backend = nevu_state.window.backend
    parts = [
        _nv_error_format_template_start2.format(
            message=error_text,
            version=VERSION,
            method_name=method_name,
            backend=backend,
        )
    ]
    if info:
        parts.append(_nv_error_format_template_ext1.format(info=info))
    if solution:
        parts.append(_nv_error_format_template_ext2.format(solution=solution))
    parts.append(f"\n{_nv_error_format_template_end}\n")
    return "".join(parts)

def format_nverror_paramengine(
    error_text: str, info: str | None = None, solution: str | None = None
) -> str:
    parts = [
        _nv_error_format_template_start3.format(message=error_text, version=VERSION)
    ]
    if info:
        parts.append(_nv_error_format_template_ext1.format(info=info))
    if solution:
        parts.append(_nv_error_format_template_ext2.format(solution=solution))
    parts.append(f"\n{_nv_error_format_template_end}\n")
    return "".join(parts)

def format_nvtype_nvobject_error(
    needed_type: str,
    arg_name: str,
    arg: Any,
    object: NevuObject,
    method_name: str = "not specified",
) -> str:
    arg_name = arg_name.strip()
    needed_type = needed_type.strip()
    return format_nverror(
        f"argument '{arg_name}' must be {needed_type}",
        f"\n   object where error occurred: {object.__class__.__name__} with {object.get_param('id')}\n   argument '{arg_name}' current value is: {arg} (type: {arg.__class__.__name__})",
        "\n   1. If you are using this function in your code:\n      Find the method in your code specified in the traceback, and recheck the arguments passed to it.\n   2. If this error occurred internally within the framework:\n      Check the traceback to identify which high-level component (e.g., Grid, Panel, Button) received the invalid argument in its constructor""",
        method_name,
    )
def format_nvtype_renderer_error(
    cause_message: str,
    method_name: str = "not specified",
    solution: str | None = None,
) -> str:
    solution = (
        solution
        or "Check the traceback to identify which high-level component (e.g., Grid, Scroll, Button) received the invalid argument in its constructor"
    )
    return format_nverror_renderer(
        cause_message,
        "Internal renderer error",
        solution,
        method_name,
    )

def format_param_engine_error(
    cause_message: str,
    object: NevuObject,
    solution: str | None = None,
    add_info: str | None = None,
) -> str:
    solution = (
        solution
        or "Check the traceback to identify which high-level component (e.g., Grid, Scroll, Button) received the invalid argument in its constructor"
    )
    return format_nverror_paramengine(
        cause_message,
        f"object where error occurred: {object.__class__.__name__} with {object.get_param('id')}"
        + (add_info or ""),
        "\n   1. If you are using this function in your code:\n      Find the method in your code specified in the traceback, and recheck the arguments passed to it.\n   2. If this error occurred internally within the framework:\n      Check the traceback to identify which high-level component (e.g., Grid, Scroll, Button) received the invalid argument in its constructor",
    )
