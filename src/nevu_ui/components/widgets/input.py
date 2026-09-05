import copy
import math
from typing import Any, Callable, Unpack

import nevu_ui.core.modules as md
from nevu_ui.components.widgets.typehints import InputKwargs
from nevu_ui.components.widgets.widget import Widget
from nevu_ui.core import Annotations
from nevu_ui.core.enums import BindType, CustomFunctions, RenderReturnType
from nevu_ui.core.state import nevu_state
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.presentation.color import Color
from nevu_ui.presentation.style import Style
from nevu_ui.rendering import DrawTextCall
from nevu_ui.utils import Keys, keyboard, mouse


class Input(Widget):
    # === Params ===
    max_characters: int | None
    allow_paste: bool
    words_indent: bool
    is_active: bool
    multi_line: bool
    blacklist: list | tuple | str | None
    whitelist: list | tuple | str | None
    padding: list
    cursor_width: int
    default: str
    placeholder: str
    text: str
    on_change_function: Callable[["Input", str], None] | None
    # ==============

    def __init__(
        self,
        size: Annotations.nevuobj_size = None,
        style: Annotations.nevuobj_style = None,
        **constant_kwargs: Unpack[InputKwargs],
    ):
        super().__init__(size, style, **constant_kwargs)
        self.text = ""
        self._text_surface = None
        self.add_first_update_action(self._process_padding)

    def _init_numerical(self):
        super()._init_numerical()
        self._scroll_offset = NvVector2()
        self.max_scroll_y = 0
        self.cursor_place = 0
        self._selection_anchor: int | None = None
        if isinstance(self.padding, tuple):
            self.padding = list(self.padding)
        if len(self.padding) != 4:
            raise ValueError(
                "Input padding must have 4 values (left, top, right, bottom)"
            )
        self.top_left_padding = NvVector2()
        self.bottom_right_padding = NvVector2()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        nevu_state.keyboard_focused = value
        if not value:
            self._selection_anchor = None

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self.selected = False
        self._changed_text = False
        self._changed_cursor = False
        self._add_custom_flags(CustomFunctions.event_update)

    def _init_text_cache(self):
        self._text_surface = None
        self._text_rect = NvRect(0, 0, 0, 0)

    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self._init_cursor()
        self._draw_text()
        self.text = self.default

    def _init_cursor(self):
        font_height = int(self._get_line_height())
        cursor_width = max(1, int(self.cursor_width * self._resize_ratio.x))
        renderer_type = nevu_state.window.renderer_type
        cursor_size = NvVector2.from_xy(cursor_width, font_height)
        if renderer_type.raylib:
            cursor = NvRenderTexture(cursor_size)
        elif renderer_type.pygame_like:
            cursor = md.pygame.Surface(cursor_size).convert_alpha()
        else:
            cursor = None

        if not cursor:
            self.cursor = None
            return

        cursor.fill(self.style.get_content_color(self.subtheme_role, inverted = not self.inverted))
        self.cursor = cursor

    def text_setter(self, value: str | None):
        if value is None:
            return self.default
        value = str(value)
        if not self.multi_line:
            value = value.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        if self.max_characters is not None:
            value = value[: self.max_characters]
        self.cursor_place = min(len(value), self.cursor_place)
        if self._selection_anchor is not None:
            self._selection_anchor = min(len(value), self._selection_anchor)
        self._changed = True

        if not self.booted:
            return value

        self._draw_text(text_override=value)

        if self.on_change_function:
            try:
                self.on_change_function(self, value)
            except Exception as e:
                print(
                    f"Error in Input with {self.id} in on_change_function.\nCause: {e}"
                )

        return value

    def _add_params(self):
        super()._add_params()
        self._add_param("is_active", bool, True)
        self._add_param("multi_line", bool, False)
        self._add_param("allow_paste", bool, True)
        self._add_param("words_indent", bool, False)
        self._add_param("max_characters", (int, type(None)), None)
        self._add_param("blacklist", (list, str, type(None), tuple), None)
        self._add_param("whitelist", (list, str, type(None), tuple), None)
        self._add_param("padding", (list, tuple), (0, 0, 0, 0))
        self._add_param("cursor_width", int, 2)
        self._add_param("default", str, "")
        self._add_param("placeholder", str, "")
        self._add_param("on_change_function", Any, None)
        self._add_param("text", str | None, None, setter=self.text_setter)
        self._block_param("text")

    def _process_padding(self):
        base_padding = list(self.padding)
        bw = self.style.border_width
        br = self.style.border_radius
        if isinstance(br, tuple):
            for i, item in enumerate(br):
                base_padding[i] += item + bw
        else:
            for i in range(len(base_padding)):
                base_padding[i] += br + bw

        def max_elem(a, b, name):
            return self._ensure_padding(max(a, b) / 2, name)

        max_left = max_elem(base_padding[0], base_padding[3], "left")
        max_right = max_elem(base_padding[1], base_padding[2], "right")
        max_top = max_elem(base_padding[0], base_padding[1], "top")
        max_bottom = max_elem(base_padding[2], base_padding[3], "bottom")

        self.top_left_padding = NvVector2.from_xy(max_left, max_top)
        self.bottom_right_padding = NvVector2.from_xy(max_right, max_bottom)

    def _ensure_padding(self, value, name):
        if value < 0:
            print(f"Warning: {name} padding with value: {value}, will be set to 0")
            return 0
        return value

    def _get_line_height(self):
        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            rl_font = self.renderer.core.get_font()
            return md.rl.measure_text_ex(rl_font, "A", rl_font.baseSize, 0).y
        elif rtype.pygame_like:
            return self.get_font().get_height()
        else:
            return self.style.font_size

    def _get_cursor_line_col(self, lines=None, abs_pos=None) -> NvVector2:
        if not self.text:
            return NvVector2.from_xy(0, 0)
        lines = lines or self.text.split("\n")
        pos = self.cursor_place if abs_pos is None else abs_pos
        current_pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            if pos <= current_pos + line_len:
                return NvVector2.from_xy(i, pos - current_pos)
            current_pos += line_len + 1
        last_line_index = len(lines) - 1
        last_line_len = len(lines[last_line_index]) if last_line_index >= 0 else 0
        return NvVector2.from_xy(last_line_index, last_line_len)

    def _get_line_abs_pos(self, target_line_index, target_col_index, lines=None):
        lines = lines or self.text.split("\n")
        len_lines = len(lines)
        target_line_index = int(max(0, min(target_line_index, len_lines - 1)))
        abs_pos = target_line_index

        for i in range(target_line_index):
            abs_pos += len(lines[i])

        current_line_len = (
            len(lines[target_line_index]) if target_line_index < len_lines else 0
        )
        target_col_index = max(0, min(target_col_index, current_line_len))
        abs_pos += target_col_index
        return abs_pos

    def _update_scroll_offset_x(self, lines=None):
        measure = self._measure_text
        lines = lines or self.text.split("\n")
        cursor_grid = self._get_cursor_line_col(lines)
        cursor_grid_x = int(cursor_grid.x)
        curr_line_text = lines[cursor_grid_x] if cursor_grid_x < len(lines) else ""
        ideal_offset_x = measure(curr_line_text[: int(cursor_grid.y)])[0]
        scroll_offset = self._scroll_offset
        relative_cursor_pos = ideal_offset_x - scroll_offset.x
        visible_width = round(
            max(
                (
                    self.current_size
                    - self.rel(self.top_left_padding + self.bottom_right_padding)
                ).x,
                1,
            )
        )

        if relative_cursor_pos < 0:
            scroll_offset.x = ideal_offset_x
        elif relative_cursor_pos > visible_width:
            scroll_offset.x = ideal_offset_x - visible_width

        scroll_offset.x = max(
            0, min(scroll_offset.x, max(0, measure(curr_line_text)[0] - visible_width))
        )

    def _measure_texture(self, object):
        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            return [object.texture.width, object.texture.height]
        elif rtype.pygame_like:
            return object.get_size()
        else:
            return [0, 0]

    def _update_scroll_offset_y(self):
        if not self.multi_line:
            return
        if not (text_surf := self._text_surface):
            return
        line_height = self._get_line_height()
        cursor_grid = self._get_cursor_line_col()

        scroll_offset = self._scroll_offset
        ideal_offset_y = cursor_grid.x * line_height
        visible_height = round(
            max(
                (
                    self.current_size
                    - self.rel(self.top_left_padding + self.bottom_right_padding)
                ).y,
                1,
            )
        )

        if ideal_offset_y < scroll_offset.y:
            scroll_offset.y = ideal_offset_y
        elif ideal_offset_y + line_height > scroll_offset.y + visible_height:
            scroll_offset.y = ideal_offset_y + line_height - visible_height

        max_scroll_y = max(0, self._measure_texture(text_surf)[1] - visible_height)
        scroll_offset.y = max(0, min(scroll_offset.y, max_scroll_y))
        self.max_scroll_y = max_scroll_y

    def _create_text_surfacelike(self, size: NvVector2 | None):
        if size is None:
            self._text_surface = None
            return

        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            rl = md.rl
            ceil = math.ceil
            result_surfacelike = NvRenderTexture(
                NvVector2.from_xy(ceil(size.x), ceil(size.y))
            )
            texture = result_surfacelike.texture
            rl.set_texture_filter(
                texture, rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X
            )
            result_surfacelike.clear(Color.Blank)
        elif rtype.pygame_like:
            result_surfacelike = md.pygame.Surface(
                size, md.pygame.SRCALPHA
            ).convert_alpha()
            result_surfacelike.fill(Color.Blank)
        else:
            raise ValueError("Unsupported backend. Owi")

        self._text_surface = result_surfacelike

    def _draw_continuous_text(self, text: str):
        result = self.renderer.run_text(
            DrawTextCall(
                text=text or "",
                words_indent=self.words_indent,
                return_type=RenderReturnType.CreateNew,
                continuous=True,
            )
        )
        assert result

        self._text_rect, self._text_surface = result
        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            rl = md.rl
            rl.set_texture_filter(
                self._text_surface.texture,
                rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X,
            )
            rl.set_texture_wrap(
                self._text_surface.texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP
            )

    def _draw_multiline_text(self, text: str):
        text = text or ""
        renderFont = self.get_font()
        line_height = int(self._get_line_height())
        lines = text.split("\n")
        rtype = nevu_state.window.renderer_type

        if not lines:
            if rtype.raylib:
                self._create_text_surfacelike(NvVector2(1, line_height))
            elif rtype.pygame_like:
                text_surface = md.pygame.Surface(
                    (1, line_height), md.pygame.SRCALPHA
                ).convert_alpha()
                text_surface.fill((0, 0, 0, 0))
                self._text_surface = text_surface
            return

        max_width = 0
        measure = self._measure_text
        for line in lines:
            line_width = measure(line)[0]
            max_width = max(max_width, line_width)
        total_height = len(lines) * line_height

        self._create_text_surfacelike(
            NvVector2(max(1, max_width), max(line_height, total_height))
        )

        text_surf = self._text_surface
        assert text_surf

        if rtype.raylib:
            assert isinstance(text_surf, NvRenderTexture)
            with text_surf:
                color = self.subtheme_font
                if len(color) == 3:
                    color = (*color, 255)

                draw_text_ex = md.rl.draw_text_ex
                font_size = self.renderer.core.get_font_size()

                current_y = 0
                for line in lines:
                    draw_text_ex(renderFont, line, (0, current_y), font_size, 0, color)  # type: ignore
                    current_y += line_height
        else:
            assert isinstance(text_surf, md.pygame.Surface)
            assert isinstance(renderFont, md.pygame.font.Font)
            rendered_lines = []
            rendered_lines_append = rendered_lines.append
            render_text = renderFont.render
            color = self.subtheme_font

            for line in lines:
                line_surface = render_text(line, True, color)
                rendered_lines_append(line_surface)

            current_y = 0
            text_surf_blit = text_surf.blit
            for line_surface in rendered_lines:
                text_surf_blit(line_surface, (0, current_y))
                current_y += line_height

    def _draw_text(self, text_override: str | None = None):
        self.clear_surfaces()
        text = text_override if text_override is not None else self.text
        text_to_render = text if len(text) > 0 else self.placeholder
        if self.multi_line:
            self._draw_multiline_text(text_to_render)
            self._update_scroll_offset_y()
        else:
            self._draw_continuous_text(text_to_render)
        self._update_scroll_offset_x()

    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._process_padding()
        self._init_cursor()
        self._draw_text()

    @property
    def cursor_place(self):
        return self._cursor_place

    @cursor_place.setter
    def cursor_place(self, cursor_place: int):
        if not self.text:
            self._cursor_place = 0
            return
        self._cursor_place = max(0, min(len(self.text), cursor_place))
        if hasattr(self, "cache"):
            self.clear_texture()

    def _get_selection_range(self) -> tuple[int, int] | None:
        if self._selection_anchor is None or self._selection_anchor == self.cursor_place:
            return None
        start = max(0, min(self._selection_anchor, self.cursor_place))
        end = max(0, min(len(self.text), max(self._selection_anchor, self.cursor_place)))
        if start == end:
            return None
        return start, end

    def _delete_selection(self) -> bool:
        sel = self._get_selection_range()
        if not sel:
            return False
        start, end = sel
        self._selection_anchor = None
        self.cursor_place = start
        self.text = self.text[:start] + self.text[end:]
        self._changed = True
        return True

    def _copy_selection_to_clipboard(self) -> bool:
        sel = self._get_selection_range()
        if not sel:
            return False
        start, end = sel
        copied_text = self.text[start:end]
        rtype = nevu_state.window.renderer_type

        if rtype.raylib:
            md.rl.set_clipboard_text(copied_text)
        elif rtype.pygame_like:
            md.pygame.scrap.put_text(copied_text)
        return True

    def _parse_key_back(self, ctrl):
        if self._delete_selection():
            return
        cursor_place = int(self.cursor_place)
        text = self.text
        if ctrl:
            prev_space = 0
            for i in range(cursor_place - 1, 0, -1):
                if not text[i - 1].isalnum() and text[i].isalnum():
                    prev_space = i
                    break
            delete_to = max(0, prev_space)
            if delete_to == cursor_place:
                delete_to -= 1
            text = text[:delete_to] + text[cursor_place:]
            cursor_place = delete_to
        else:
            text = text[: cursor_place - 1] + text[cursor_place:]
            cursor_place = max(0, cursor_place - 1)

        self._selection_anchor = None
        self.cursor_place = cursor_place
        self.text = text

    def _parse_paste(self):
        pasted_text = ""
        rtype = nevu_state.window.renderer_type

        if rtype.raylib:
            pasted_text = md.rl.get_clipboard_text()
        elif rtype.pygame_like:
            try:
                pasted_text = md.pygame.scrap.get_text()
                if isinstance(pasted_text, bytes):
                    pasted_text = pasted_text.decode("utf-8")
                pasted_text = pasted_text.replace("\x00", "")
            except (UnicodeDecodeError, TypeError, AttributeError):
                pasted_text = ""

        if pasted_text:
            self._delete_selection()
            filtered_text = ""
            text = self.text
            blacklist = self.blacklist
            whitelist = self.whitelist
            self._selection_anchor = None
            filtered_chars = []
            for char in pasted_text:
                valid_char = True
                if (
                    (blacklist and char in blacklist)
                    or (whitelist and char not in whitelist)
                    or (not self.multi_line and char in "\r\n")
                ):
                    valid_char = False
                if valid_char:
                    filtered_chars.append(char)
            filtered_text = "".join(filtered_chars)

            if (max_chars := self.max_characters) is not None:
                available_space = max(0, max_chars - len(text))
                filtered_text = filtered_text[:available_space]

            if filtered_text:
                cursor_place = self.cursor_place
                text = text[:cursor_place] + filtered_text + text[cursor_place:]
                cursor_place += len(filtered_text)

            self.text = text

            if filtered_text:
                self.cursor_place = cursor_place

    def _parse_unicode(self, unicode_char: str | int):
        if isinstance(unicode_char, int):
            unicode_char = chr(unicode_char)

        unicode_char_len = len(unicode_char)
        max_chars = self.max_characters

        if not (
            unicode_char_len == 1
            and unicode_char.isprintable()
            and (self.multi_line or unicode_char not in "\r\n")
        ):
            return

        blacklist = self.blacklist
        whitelist = self.whitelist
        if (blacklist and unicode_char in blacklist) or (
            whitelist and unicode_char not in whitelist
        ):
            return

        self._delete_selection()
        text = self.text
        if max_chars is not None and len(text) >= max_chars:
            return

        cursor_place = self.cursor_place
        if cursor_place is not None:
            text = text[: int(cursor_place)] + unicode_char + text[int(cursor_place) :]
        cursor_place += unicode_char_len
        self._selection_anchor = None
        self.text = text
        self.cursor_place = cursor_place

    def _parse_key_right(self, ctrl, initial_cursor_place: int, shift: bool = False):
        self._changed_cursor = True
        cursor_place = int(self.cursor_place)
        text = self.text

        if not shift and self._selection_anchor is not None and not ctrl:
            sel = self._get_selection_range()
            if sel:
                self.cursor_place = sel[1]
                self._selection_anchor = None
                return

        if shift and self._selection_anchor is None:
            self._selection_anchor = initial_cursor_place

        if not ctrl:
            self.cursor_place = min(len(text), cursor_place + 1)
        else:
            text_length = len(text)
            next_space = next(
                (
                    i
                    for i in range(cursor_place + 1, text_length)
                    if not text[i].isalnum() and text[i - 1].isalnum()
                ),
                text_length,
            )
            cursor_place = min(text_length, next_space)
            if cursor_place == initial_cursor_place and cursor_place < text_length:
                cursor_place += 1
            self.cursor_place = cursor_place

        if not shift:
            self._selection_anchor = None

    def _parse_key_left(self, ctrl, initial_cursor_place: int, shift: bool = False):
        self._changed_cursor = True
        cursor_place = int(self.cursor_place)
        text = self.text

        if not shift and self._selection_anchor is not None and not ctrl:
            sel = self._get_selection_range()
            if sel:
                self.cursor_place = sel[0]
                self._selection_anchor = None
                return

        if shift and self._selection_anchor is None:
            self._selection_anchor = initial_cursor_place

        if not ctrl:
            self.cursor_place = max(0, cursor_place - 1)
        else:
            prev_space = next(
                (
                    i
                    for i in range(cursor_place - 1, 0, -1)
                    if not text[i - 1].isalnum() and text[i].isalnum()
                ),
                0,
            )
            cursor_place = max(0, prev_space)
            if cursor_place == initial_cursor_place and cursor_place > 0:
                cursor_place -= 1
            self.cursor_place = cursor_place

        if not shift:
            self._selection_anchor = None

    def _parse_key_end(self, shift: bool = False):
        if shift and self._selection_anchor is None:
            self._selection_anchor = self.cursor_place

        if self.multi_line:
            lines = self.text.split("\n")
            line_grid = self._get_cursor_line_col(lines)
            line_len = len(lines[int(line_grid.x)]) if line_grid.x < len(lines) else 0
            self.cursor_place = self._get_line_abs_pos(line_grid.x, line_len, lines)
        else:
            self.cursor_place = len(self.text)

        if not shift:
            self._selection_anchor = None

    def _parse_key_home(self, shift: bool = False):
        if shift and self._selection_anchor is None:
            self._selection_anchor = self.cursor_place

        if self.multi_line:
            line_grid = self._get_cursor_line_col()
            self.cursor_place = self._get_line_abs_pos(line_grid.x, 0)
        else:
            self.cursor_place = 0

        if not shift:
            self._selection_anchor = None

    def _parse_arrow_keys(
        self, ctrl: bool, initial_cursor_place: int, shift: bool = False
    ) -> bool:
        fdown = keyboard.is_fdown
        if shift and self._selection_anchor is None:
            self._selection_anchor = initial_cursor_place

        if fdown(Keys.Up):
            if self.multi_line:
                current_grid = self._get_cursor_line_col()
                if current_grid.x > 0:
                    self.cursor_place = self._get_line_abs_pos(
                        current_grid.x - 1, current_grid.y
                    )
            if not shift:
                self._selection_anchor = None
            return True
        elif fdown(Keys.Down):
            if self.multi_line:
                lines = self.text.split("\n")
                current_grid = self._get_cursor_line_col(lines)
                if current_grid.x < len(lines) - 1:
                    self.cursor_place = self._get_line_abs_pos(
                        current_grid.x + 1, current_grid.y, lines
                    )
            if not shift:
                self._selection_anchor = None
            return True
        elif fdown(Keys.Right):
            self._parse_key_right(ctrl, initial_cursor_place, shift)
            return True
        elif fdown(Keys.Left):
            self._parse_key_left(ctrl, initial_cursor_place, shift)
            return True
        return False

    def _parse_numpad_keys(self, ctrl: bool, shift: bool = False) -> bool:
        fdown = keyboard.is_fdown
        if fdown(Keys.Backspace):
            if self.cursor_place > 0 or self._get_selection_range():
                self._parse_key_back(ctrl)
            return True
        elif fdown(Keys.Delete):
            if not self._delete_selection():
                text = self.text
                if self.cursor_place < len(text):
                    self.text = text[: self.cursor_place] + text[self.cursor_place + 1 :]
            return True
        elif fdown(Keys.Home):
            self._parse_key_home(shift)
            return True
        elif fdown(Keys.End):
            self._parse_key_end(shift)
            return True
        return False

    def _parse_keydown(self):
        down = keyboard.is_down
        ctrl = down(Keys.LeftCtrl) or down(Keys.RightCtrl)
        shift = down(Keys.LeftShift) or down(Keys.RightShift)

        if keyboard.is_fdown(Keys.Enter):
            self._delete_selection()
            text = self.text
            max_chars = self.max_characters
            if self.multi_line and (max_chars is None or len(text) < max_chars):
                cursor_place = self.cursor_place
                self.text = text[:cursor_place] + "\n" + text[cursor_place:]
                cursor_place += 1
                self.cursor_place = cursor_place
                self._selection_anchor = None
            return

        if ctrl:
            if down(Keys.A):
                self._selection_anchor = 0
                self.cursor_place = len(self.text)
                self._update_scroll_offset_x()
                self._update_scroll_offset_y()
                self._changed = True
                return
            elif down(Keys.C):
                self._copy_selection_to_clipboard()
                return
            elif down(Keys.X):
                if self._copy_selection_to_clipboard():
                    self._delete_selection()
                return
            elif keyboard.is_fdown(Keys.V) and self.allow_paste:
                self._parse_paste()
                return

        if self._parse_arrow_keys(ctrl, self.cursor_place, shift):
            return
        if self._parse_numpad_keys(ctrl, shift):
            return

        if ctrl or down(Keys.LeftAlt) or down(Keys.RightAlt):
            return

        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            unicode_char = md.rl.get_char_pressed()
        elif rtype.pygame_like:
            unicode_char = nevu_state.window.pygame_unicode
        else:
            return

        if not unicode_char:
            return
        assert isinstance(unicode_char, int | str)
        self._parse_unicode(unicode_char)

    def _system_callback_binds(self):
        super()._system_callback_binds()
        self._system_callbacks.bind(BindType.Click, lambda *args: self.check_selected())
        self._system_callbacks.bind(BindType.Scroll, _input_on_scroll)
        self._system_callbacks.bind(
            BindType.StyleChange, _input_on_style_change, add_to_end=False
        )

    def _event_update(self, events: list | None = None):
        events = nevu_state.current_events
        if events is None:
            events = []
        super()._event_update(events)

        selected = self.selected

        if not self.is_active:
            if selected:
                self.selected = False
                self._selection_anchor = None
                self._changed = True
            return

        prev_selected = selected
        upd_scrollx = self._update_scroll_offset_x
        upd_scrolly = self._update_scroll_offset_y

        if mouse.left_fdown:
            mouse_collided = self.get_nvrect().collide_point(mouse.pos)
            if selected:
                if not mouse_collided:
                    selected = False
                    self._selection_anchor = None
                    self._changed = True
                else:
                    upd_scrollx()
                    upd_scrolly()
                self.clear_texture()
        elif mouse.left_up and selected:
            if self._selection_anchor == self.cursor_place:
                self._selection_anchor = None
        elif mouse.left_down and selected:
            relative_mouse_pos = mouse.pos - self.absolute_coordinates
            top_left_padding = self.rel(self.top_left_padding)
            scrolled_vec = (relative_mouse_pos - top_left_padding) + self._scroll_offset

            if self.multi_line:
                line_height = self._get_line_height()
                if line_height <= 0:
                    line_height = 1
                lines = self.text.split("\n")
                target_line_index = max(0, min(int(scrolled_vec.y / line_height), len(lines) - 1))
                target_line_text = lines[target_line_index] if target_line_index < len(lines) else ""
                best_col_index = self._find_best_cursor_index(target_line_text, scrolled_vec.x)
                best_idx = self._get_line_abs_pos(target_line_index, best_col_index, lines)
            else:
                best_idx = self._find_best_cursor_index(self.text, scrolled_vec.x)

            if best_idx != self.cursor_place:
                self.cursor_place = best_idx
                self._changed = True
                upd_scrollx()
                upd_scrolly()

        if prev_selected != selected:
            if selected:
                upd_scrollx()
                upd_scrolly()
            else:
                self._changed_cursor = True

        if selected:
            cursor_moved = False
            changed_text = self._changed_text
            initial_cursor_place = self.cursor_place
            initial_text = self.text
            self._parse_keydown()
            if self.cursor_place != initial_cursor_place:
                cursor_moved = True
            if self.text != initial_text:
                changed_text = True
            if changed_text or cursor_moved:
                self._changed = True

            if changed_text:
                self._draw_text()
                changed_text = False
                if on_change := self.on_change_function:
                    try:
                        on_change(self, self.text)
                    except Exception as e:
                        print(
                            f"Error in Input with {self.id} in on_change_function.\nCause: {e}"
                        )

            elif cursor_moved:
                upd_scrollx()
                upd_scrolly()

            self._changed_text = changed_text

        self.selected = selected

    def _measure_text(self, text: str):
        renderFont = self.get_font()
        rtype = nevu_state.window.renderer_type
        if rtype.raylib:
            measure = md.rl.measure_text_ex
            res = measure(renderFont, text, renderFont.baseSize, 0)  # type: ignore
            return res.x, res.y
        elif rtype.pygame_like:
            return renderFont.size(text)  # type: ignore
        else:
            return 0, 0

    def _find_best_cursor_index(self, text: str, x_pos: float) -> int:
        if not text:
            return 0
        measure = self._measure_text
        total_w = measure(text)[0]

        if x_pos >= total_w:
            return len(text)
        if x_pos <= 0:
            return 0

        best_index = 0
        min_diff = float("inf")
        for i in range(len(text) + 1):
            w = measure(text[:i])[0]
            diff = abs(x_pos - w)
            if diff < min_diff:
                min_diff = diff
                best_index = i

        return best_index

    def check_selected(self):
        self.selected = True
        self._changed = True
        relative_mouse_pos = mouse.pos - self.absolute_coordinates
        top_left_padding = self.rel(self.top_left_padding)
        scrolled_vec = (relative_mouse_pos - top_left_padding) + self._scroll_offset

        text = self.text
        if self.multi_line:
            line_height = self._get_line_height()
            if line_height <= 0:
                line_height = 1
            target_line_index = max(0, int(scrolled_vec.y / line_height))
            lines = text.split("\n")
            target_line_index = min(target_line_index, len(lines) - 1)
            target_line_text = (
                lines[target_line_index] if target_line_index < len(lines) else ""
            )
            best_col_index = self._find_best_cursor_index(
                target_line_text, scrolled_vec.x
            )
            self.cursor_place = self._get_line_abs_pos(
                target_line_index, best_col_index, lines
            )
            self._selection_anchor = self.cursor_place
        else:
            best_index = self._find_best_cursor_index(text, scrolled_vec.x)
            self._selection_anchor = best_index
            self.cursor_place = best_index
            lines = None
        self._update_scroll_offset_x(lines)
        self._update_scroll_offset_y()

    def secondary_draw_content(self):
        if not self._changed:
            return
        assert self.surface

        rel = self.rel
        curr_size = self.current_size

        top_left_padding = rel(self.top_left_padding)
        bottom_right_padding = rel(self.bottom_right_padding)

        top_left_scrolled = top_left_padding - self._scroll_offset

        clip = (curr_size - top_left_padding - bottom_right_padding).to_round()
        clip.x, clip.y = max(clip.x, 0), max(clip.y, 0)

        if clip.x <= 0 or clip.y <= 0:
            return

        rtype = nevu_state.window.renderer_type
        text_surface = self._text_surface
        surface = self.surface
        multi_line = self.multi_line

        if not self._text_surface:
            self._draw_text()
            text_surface = self._text_surface

        clip_rect = None
        if rtype.pygame_like:
            pygame = md.pygame
            surface_t = pygame.Surface
            assert isinstance(surface, surface_t)
            assert isinstance(text_surface, surface_t)
            clip_rect = surface.get_rect()
            assert isinstance(clip_rect, pygame.Rect)
            clip_rect.topleft = top_left_padding.get_int_tuple()
            clip_rect.size = clip.get_int_tuple()

            original_clip = surface.get_clip()
            surface.set_clip(clip_rect)
            if self.selected:
                self._draw_selection(
                    rtype,
                    surface,
                    curr_size,
                    top_left_padding,
                    top_left_scrolled,
                    multi_line,
                )

            if multi_line:
                text_rect = text_surface.get_rect(
                    topleft=top_left_scrolled.get_int_tuple()
                )
            else:
                text_rect = text_surface.get_rect(
                    left=int(top_left_scrolled.x),
                    centery=int(
                        (
                            top_left_padding.y
                            + surface.get_height()
                            - bottom_right_padding.y
                        )
                        / 2
                    ),
                )

            surface.blit(text_surface, text_rect)
            surface.set_clip(original_clip)

        elif rtype.raylib:
            rl = md.rl
            assert isinstance(text_surface, NvRenderTexture)
            assert isinstance(surface, NvRenderTexture)
            with surface:
                rl.begin_scissor_mode(
                    int(top_left_padding.x),
                    int(top_left_padding.y),
                    int(clip.x),
                    int(clip.y),
                )
                begin_blend_mode(self._correct_blend)

                if self.selected:
                    self._draw_selection(
                        rtype,
                        surface,
                        curr_size,
                        top_left_padding,
                        top_left_scrolled,
                        multi_line,
                    )

                if multi_line:
                    dest_pos = (int(top_left_scrolled.x), int(top_left_scrolled.y))
                else:
                    text_vec = NvVector2.from_xy(
                        top_left_scrolled.x,
                        top_left_padding.y
                        + (
                            (curr_size.y - top_left_padding.y - bottom_right_padding.y)
                            - text_surface.height
                        )
                        / 2,
                    )
                    dest_pos = text_vec.get_int_tuple()
                surface.fast_blit(text_surface, dest_pos)
                end_blend_mode()
                rl.end_scissor_mode()

        if self.selected:
            self._draw_cursor(
                rtype,
                surface,
                curr_size,
                top_left_padding,
                top_left_scrolled,
                clip,
                clip_rect,
                multi_line,
            )

    def _draw_selection(
        self,
        rtype,
        surface,
        curr_size,
        top_left_padding,
        top_left_scrolled,
        multi_line=False,
    ):
        sel = self._get_selection_range()
        if not sel:
            return

        selection_start, selection_end = sel
        line_height = self._get_line_height()
        measure = self._measure_text

        selection_color = Color.with_alpha(self.style.get_content_color(self.subtheme_role, inverted = not self.inverted), 180)
        selection_tuple_color = (selection_color[0], selection_color[1], selection_color[2], selection_color[3])

        if multi_line:
            lines = self.text.split("\n")
            start_grid = self._get_cursor_line_col(lines, abs_pos=selection_start)
            end_grid = self._get_cursor_line_col(lines, abs_pos=selection_end)

            start_line, start_column = int(start_grid.x), int(start_grid.y)
            end_line, end_column = int(end_grid.x), int(end_grid.y)

            for line_idx in range(start_line, end_line + 1):
                if line_idx >= len(lines):
                    break
                line_text = lines[line_idx]

                column_from = start_column if line_idx == start_line else 0
                column_to = end_column if line_idx == end_line else len(line_text)

                x1 = measure(line_text[:column_from])[0]
                x2 = measure(line_text[:column_to])[0]

                rect_x = top_left_scrolled.x + x1
                rect_y = top_left_scrolled.y + line_idx * line_height
                rect_w = max(4.0 if column_from == column_to else 1.0, x2 - x1)
                rect_h = line_height

                self._render_selection_rect(
                    rtype, surface, rect_x, rect_y, rect_w, rect_h, selection_tuple_color
                )
        else:
            x1_offset = measure(self.text[:selection_start])[0]
            x2_offset = measure(self.text[:selection_end])[0]

            rect_x = top_left_scrolled.x + x1_offset
            rect_y = (
                top_left_padding.y
                + (
                    (curr_size.y - top_left_padding.y - self.rel(self.bottom_right_padding).y)
                    - line_height
                )
                / 2
            )
            rect_w = max(1.0, x2_offset - x1_offset)
            rect_h = line_height

            self._render_selection_rect(
                rtype, surface, rect_x, rect_y, rect_w, rect_h, selection_tuple_color
            )

    def _render_selection_rect(
        self, rtype, surface, rect_x, rect_y, rect_w, rect_h, sel_color
    ):
        if rect_w <= 0 or rect_h <= 0:
            return
        if rtype.pygame_like:
            sel_surf = md.pygame.Surface((int(rect_w), int(rect_h)), md.pygame.SRCALPHA)
            sel_surf.fill(sel_color)
            surface.blit(sel_surf, (int(rect_x), int(rect_y)))
        elif rtype.raylib:
            md.rl.draw_rectangle(
                int(rect_x), int(rect_y), int(rect_w), int(rect_h), sel_color
            )

    def _draw_cursor(
        self,
        rtype,
        surface,
        curr_size,
        top_left_padding,
        top_left_scrolled,
        clip,
        clip_rect=None,
        multi_line=False,
    ):
        line_height = self._get_line_height()
        cursor = self.cursor
        assert cursor
        cursor_size = NvVector2.from_xy(cursor.get_width(), cursor.get_height())
        measure = self._measure_text

        if multi_line:
            lines = self.text.split("\n")
            cursor_grid_vec = self._get_cursor_line_col(lines)
            line_idx, col_idx = int(cursor_grid_vec.x), int(cursor_grid_vec.y)
            current_text_line = lines[line_idx] if line_idx < len(lines) else ""
            text_before_cursor = current_text_line[:col_idx]
            cursor_x_offset = measure(text_before_cursor)[0]
            cursor_actual_pos = top_left_scrolled + NvVector2.from_xy(
                cursor_x_offset, line_idx * line_height
            )
        else:
            text_before_cursor = self.text[: self.cursor_place]
            cursor_x_offset = measure(text_before_cursor)[0]
            cursor_actual_pos = NvVector2.from_xy(
                top_left_scrolled.x + cursor_x_offset,
                top_left_padding.y
                + (
                    (curr_size.y - top_left_padding.y - self.rel(self.bottom_right_padding).y)
                    - cursor_size.y
                )
                / 2,
            )

        if rtype.pygame_like:
            pygame = md.pygame
            surface_t = pygame.Surface
            assert isinstance(cursor, surface_t)
            assert isinstance(surface, surface_t)
            assert clip_rect
            cursor_draw_rect = cursor.get_rect(topleft=cursor_actual_pos.to_tuple())
            if clip_rect.colliderect(cursor_draw_rect):
                surface.blit(cursor, cursor_draw_rect.topleft)

        elif rtype.raylib:
            rl = md.rl
            assert isinstance(cursor, NvRenderTexture)
            assert isinstance(surface, NvRenderTexture)
            cursor_rect_rl = (
                cursor_actual_pos.x,
                cursor_actual_pos.y,
                cursor_size.x,
                cursor_size.y,
            )
            clip_rect_rl = (top_left_padding.x, top_left_padding.y, clip.x, clip.y)
            if not rl.check_collision_recs(cursor_rect_rl, clip_rect_rl):
                return
            with surface:
                color = self.subtheme.oncolor
                if len(color) == 3:
                    color = (*color, 255)
                rl.draw_rectangle(
                    int(cursor_actual_pos.x),
                    int(cursor_actual_pos.y),
                    int(cursor_size.x),
                    int(cursor_size.y),
                    color,
                )


# === NOT CLASS FUNCTIONS ===


def _input_on_scroll(self, side: bool):
    self.clear_texture()
    direction = -1 if side else 1

    scroll_multiplier = 3
    line_h = self._get_line_height()

    scroll_amount = direction * line_h * scroll_multiplier
    self._update_scroll_offset_y()
    self._scroll_offset.y -= scroll_amount
    self._scroll_offset.y = max(0, min(self._scroll_offset.y, self.max_scroll_y))
    self._changed = True


def _input_on_style_change(self):
    self._process_padding()
    self.clear_surfaces()
    if not self.booted:
        return
    self._draw_text()
    self._changed = True
