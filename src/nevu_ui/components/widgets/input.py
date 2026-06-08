import copy
from typing import Unpack
import math

import nevu_ui.core.modules as md
from nevu_ui.core import Annotations
from nevu_ui.fast.nvrendertex import NvRenderTexture
from nevu_ui.fast.raylib.nevu_raylib import begin_blend_mode, end_blend_mode
from nevu_ui.utils import mouse, keyboard, Keys
from nevu_ui.presentation.color import Color
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.fast.nvrect import NvRect
from nevu_ui.core.state import nevu_state
from nevu_ui.components.widgets import Widget, InputKwargs
from nevu_ui.core.enums import RenderConfig, RenderReturnType
from nevu_ui.presentation.style import Style

class Input(Widget):
    max_characters: int | None
    allow_paste: bool
    words_indent: bool
    is_active: bool
    padding: list
    
    def __init__(self, size: Annotations.nevuobj_size = None, style: Annotations.nevuobj_style = None, default: str = "", placeholder: str = "", on_change_function = None, **constant_kwargs: Unpack[InputKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._entered_text = ""
        self.placeholder = placeholder
        self._on_change_fun = on_change_function
        self.text = default
        self._default_text = default
        self._text_surface = None
        self.add_first_update_action(self._process_padding)

    def _init_numerical(self):
        super()._init_numerical()
        self._scroll_offset = NvVector2()
        self.max_scroll_y = 0
        self.cursor_place = 0
        if isinstance(self.padding, tuple):
            self.padding = list(self.padding)
        if len(self.padding) != 4:
            raise ValueError("Input padding must have 4 values (left, top, right, bottom)")
        self.lt_margin = NvVector2()
        self.rb_margin = NvVector2()
        
    def _process_padding(self):
        base_padding = self.padding.copy()
        br = self.style.border_radius
        if isinstance(br, tuple):
            for i, item in enumerate(br):
                base_padding[i] += item
        else:
            for i in range(len(base_padding)):
                base_padding[i] += br  
                  
        def max_elem(a, b, name): 
            return self._ensure_padding(max(a, b) / 2, name)
        
        max_left = max_elem(base_padding[0], base_padding[3], "left")
        max_right = max_elem(base_padding[1], base_padding[2], "right")
        max_top = max_elem(base_padding[0], base_padding[1], "top")
        max_bottom = max_elem(base_padding[2], base_padding[3], "bottom")
        
        self.lt_margin += NvVector2(max_left, max_top)
        self.rb_margin += NvVector2(max_right, max_bottom)
        self._changed = True

    @property
    def multiple(self): return self.get_param_strict("multiple").value
    
    def _ensure_padding(self, value, name):
        if value < 0:
            print(f"Warning: {name} padding with value: {value}, will be set to 0")
            return 0
        return value

    def _on_style_change_content(self):
        super()._on_style_change_content()
        if self._first_update: return
        self._process_padding()

    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self.selected = False
        self._changed_text = False
        self._custom_event_update = True
        self._changed_cursor = False
        
    def _init_text_cache(self):
        self._text_surface = None
        self._text_rect = NvRect(0, 0, 0, 0)
    
    def _init_objects(self):
        super()._init_objects()
    
    def _add_params(self):
        super()._add_params()
        self._add_param("is_active", bool, True)
        self._add_param("multiple", bool, False)
        self._add_param("allow_paste", bool, True)
        self._add_param("words_indent", bool, False)
        self._add_param("max_characters", (int, type(None)), None)
        self._add_param("blacklist", (list, str, type(None), tuple), None)
        self._add_param("whitelist", (list, str, type(None), tuple), None)
        self._add_param("padding", (list, tuple), (0,0,0,0))
        self._add_param("cursor_width", int, 2)
    
    @property
    def whitelist(self): return self.get_param_strict("whitelist").value
    @whitelist.setter
    def whitelist(self, value): self.set_param_value("whitelist", value)
    @property
    def blacklist(self): return self.get_param_strict("blacklist").value
    @blacklist.setter
    def blacklist(self, value): self.set_param_value("blacklist", value)
    
    def _lazy_init(self, size: NvVector2 | list):
        super()._lazy_init(size)
        self._init_cursor()
        self._right_bake_text()
        
    def _init_cursor(self):
        font_height = int(self._get_line_height())
        cursor_width = max(1, int(self.get_param_strict("cursor_width").value * self._resize_ratio.x))
        dtype = nevu_state.window.renderer_type
        if dtype.raylib: 
            cursor = NvRenderTexture(NvVector2(cursor_width, font_height))
        elif dtype.pygame_like:
            cursor = md.pygame.Surface(NvVector2(cursor_width, font_height))
        else:
            cursor = None
            
        if not cursor: 
            self.cursor = None
            return
          
        cursor.fill(self._subtheme.oncolor)
        self.cursor = cursor
        
    def _get_line_height(self):
        dtype = nevu_state.window.renderer_type
        if dtype.raylib: 
            rl_font = self._get_raylib_font()
            return md.rl.measure_text_ex(rl_font, "A", rl_font.baseSize, 0).y
        elif dtype.pygame_like: return self._get_pygame_font().get_height()
        else: return self.style.font_size
        
    def _get_cursor_line_col(self, lines = None) -> NvVector2:
        if not self._entered_text: return NvVector2(0, 0)
        lines = lines or self._entered_text.split('\n')
        abs_pos = self.cursor_place
        current_pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            if abs_pos <= current_pos + line_len:
                return NvVector2(i, abs_pos - current_pos)
            current_pos += line_len + 1
        last_line_index = len(lines) - 1
        last_line_len = len(lines[last_line_index]) if last_line_index >= 0 else 0
        return NvVector2(last_line_index, last_line_len)
    
    def _get_line_abs_pos(self, target_line_index, target_col_index, lines = None):
        lines = lines or self._entered_text.split('\n')
        len_lines = len(lines)
        target_line_index = int(max(0, min(target_line_index, len_lines - 1)))
        abs_pos = 0
        
        for i in range(target_line_index): 
            abs_pos += len(lines[i]) + 1
            
        current_line_len = len(lines[target_line_index]) if target_line_index < len_lines else 0
        target_col_index = max(0, min(target_col_index, current_line_len))
        abs_pos += target_col_index
        return abs_pos
    
    def _update_scroll_offset_x(self, lines = None):
        measure = self._measure_text
        
        lines = lines or self._entered_text.split('\n')
        cursor_grid = self._get_cursor_line_col(lines)
        c_grid_x = int(cursor_grid.x)
        curr_line_text = lines[c_grid_x] if c_grid_x < len(lines) else ""
        ideal_offset_x = measure(curr_line_text[:int(cursor_grid.y)])[0]
        scroll_offset = self._scroll_offset
        relative_cursor_pos = ideal_offset_x - scroll_offset.x
        visible_width = round(max((self._csize - self.rel(self.lt_margin + self.rb_margin)).x, 1))
        
        if relative_cursor_pos < 0: 
            scroll_offset.x = ideal_offset_x
        elif relative_cursor_pos > visible_width: 
            scroll_offset.x = ideal_offset_x - visible_width

        scroll_offset.x = max(0, min(scroll_offset.x, max(0, measure(curr_line_text)[0] - visible_width)))
        
    def _measure_texture(self, object):
        dtype = nevu_state.window.renderer_type
        if dtype.raylib:
            return [object.texture.width, object.texture.height]
        elif dtype.pygame_like:
            return object.get_size()
        else:
            return [0, 0]
    
    def _update_scroll_offset_y(self):
        if not self.multiple: return
        if not (text_surf := self._text_surface): return
        line_height = self._get_line_height()
        cursor_grid = self._get_cursor_line_col()
        
        scroll_offset = self._scroll_offset
        ideal_offset_y = cursor_grid.x * line_height
        visible_height = round(max((self._csize - self.rel(self.lt_margin + self.rb_margin)).y, 1))
        
        if ideal_offset_y < scroll_offset.y: 
            scroll_offset.y = ideal_offset_y
        elif ideal_offset_y + line_height > scroll_offset.y + visible_height: 
            scroll_offset.y = ideal_offset_y + line_height - visible_height
        
        max_scroll_y = max(0, self._measure_texture(text_surf)[1] - visible_height)
        scroll_offset.y = max(0, min(scroll_offset.y, max_scroll_y))
        self.max_scroll_y = max_scroll_y

    def _create_textsurf(self, size, pygame_args = None):
        if size is None:
            self._text_surface = None
            return
        
        dtype = nevu_state.window.renderer_type
        if dtype.raylib:
            rl = md.rl
            ceil = math.ceil
            text_surface = NvRenderTexture(NvVector2(ceil(size.x), ceil(size.y)))
            texture = text_surface.texture
            rl.set_texture_filter(texture, rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X)
            rl.set_texture_wrap(texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
            with text_surface:
                text_surface.fast_clear(Color.Blank)
            self._text_surface = text_surface
        elif dtype.pygame_like:
            pygame_args = pygame_args or []
            text_surface = md.pygame.Surface(size, md.pygame.SRCALPHA)
            text_surface.fill((0, 0, 0, 0))
            self._text_surface = text_surface
        else:
            raise ValueError("Unsupported backend")
        
    def _continuous_bake_text(self, text: str | None = None): 
            self._text_rect, self._text_surface = self.renderer.run_text(RenderConfig.DrawL3, text = text or self.text or "", words_indent = self.words_indent, return_type=RenderReturnType.CreateNew, continuous=True)
            dtype = nevu_state.window.renderer_type
            if dtype.raylib:
                rl = md.rl
                rl.set_texture_filter(self._text_surface.texture, rl.TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X)
                rl.set_texture_wrap(self._text_surface.texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
            return
    
    def _multiline_bake_text(self, text: str | None = None):
        text = text or self.text or ""
        renderFont = self.get_font()
        line_height = int(self._get_line_height())
        lines = text.split('\n')
        dtype = nevu_state.window.renderer_type
        
        if not lines: 
            if dtype.raylib:
                self._create_textsurf(NvVector2(1, line_height))
            elif dtype.pygame_like:
                text_surface = md.pygame.Surface((1, line_height), md.pygame.SRCALPHA)
                text_surface.fill((0 ,0 ,0, 0))
                self._text_surface = text_surface
            return
        
        max_width = 0
        measure = self._measure_text
        for line in lines:
            w = measure(line)[0]
            if w > max_width: 
                max_width = w
        total_height = len(lines) * line_height
        
        self._create_textsurf(NvVector2(max(1, max_width), max(line_height, total_height)))
        
        text_surf = self._text_surface
        assert text_surf

        if dtype.raylib:
            assert isinstance(text_surf, NvRenderTexture)
            with text_surf:
                color = self.subtheme_font
                if len(color) == 3: 
                    color = (*color, 255)
                
                draw_text_ex = md.rl.draw_text_ex
                font_size = self.get_font_size()
                
                current_y = 0
                for line in lines:
                    draw_text_ex(renderFont, line, (0, current_y), font_size, 0, color) # type: ignore
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

    def _right_bake_text(self):
        self.clear_surfaces()
        entered_text = self._entered_text
        text_to_render = entered_text if len(entered_text) > 0 else self.placeholder
        if self.multiple:
            self._multiline_bake_text(text_to_render)
            self._update_scroll_offset_y()
        else: self._continuous_bake_text(text_to_render)
        self._update_scroll_offset_x()
        
    def _resize_content(self, resize_ratio: NvVector2):
        super()._resize_content(resize_ratio)
        self._init_cursor()
        self._right_bake_text()
        
    @property
    def style(self): return self._style
    @style.setter
    def style(self, style: Style):
        self.clear_surfaces()
        self._style = copy.deepcopy(style)
        if not self.booted: return
        self._changed = True
        if hasattr(self,'_entered_text'):
            self._right_bake_text()

    @property
    def cursor_place(self): return self._cursor_place
    @cursor_place.setter
    def cursor_place(self, cursor_place: int):
        self._cursor_place = cursor_place
        if hasattr(self, 'cache'): self.clear_texture()
    
    def _parse_key_back(self, ctrl):
        cursor_place = int(self.cursor_place)
        entered_text = self._entered_text
        if ctrl:
            prev_space = 0
            for i in range(cursor_place - 1, 0, -1):
                if not entered_text[i-1].isalnum() and entered_text[i].isalnum():
                    prev_space = i
                    break
            delete_to = max(0, prev_space)
            if delete_to == cursor_place: delete_to -= 1
            entered_text = entered_text[:delete_to] + entered_text[cursor_place:]
            cursor_place = delete_to
        else:
            entered_text = entered_text[:cursor_place-1] + entered_text[cursor_place:]
            cursor_place = max(0, cursor_place - 1)
        
        self._entered_text = entered_text
        self.cursor_place = cursor_place
    
    def _parse_paste(self):
        pasted_text = ""
        dtype = nevu_state.window.renderer_type
        
        if dtype.raylib:
            pasted_text = md.rl.get_clipboard_text()
            
        elif dtype.pygame_like:            
            try:
                pasted_text = md.pygame.scrap.get_text()
                if isinstance(pasted_text, bytes):
                    pasted_text = pasted_text.decode('utf-8')
                pasted_text = pasted_text.replace('\x00', '')
            except (UnicodeDecodeError, TypeError, AttributeError): 
                pasted_text = ""

        if pasted_text:
            filtered_text = ""
            entered_text = self._entered_text
            bl_list = self.blacklist
            wt_list = self.whitelist
            mult = self.multiple
            temp_chars = []
            for char in pasted_text:
                valid_char = True
                if bl_list and char in bl_list: valid_char = False
                if wt_list and char not in wt_list: valid_char = False
                if not mult and char in '\r\n': valid_char = False
                if valid_char: temp_chars.append(char)
            filtered_text = "".join(temp_chars)
                
            if (max_chars := self.max_characters) is not None:
                available_space = max_chars - len(entered_text)
                filtered_text = filtered_text[:max(0, available_space)]
                
            if filtered_text:
                cursor_place = self.cursor_place
                entered_text = entered_text[:cursor_place] + filtered_text + entered_text[cursor_place:]
                cursor_place += len(filtered_text)
                self.cursor_place = cursor_place
                
            self._entered_text = entered_text
                
    def _parse_unicode(self, unicode_char: str | int):
        if isinstance(unicode_char, int): 
            unicode_char = chr(unicode_char)

        unicode_char_len = len(unicode_char)
        unicode_valid = unicode_char_len == 1 and unicode_char.isprintable()
        correct_newline = self.multiple or (unicode_char not in '\r\n')
        entered_text = self._entered_text
        max_chars = self.max_characters

        if not (unicode_valid and correct_newline): return
        if max_chars is not None and len(entered_text) >= max_chars: return

        valid_char = True
        bl_list = self.blacklist
        wt_list = self.whitelist
        if bl_list and unicode_char in bl_list: valid_char = False
        if wt_list and unicode_char not in wt_list: valid_char = False
        if valid_char:
            cursor_place = self.cursor_place
            if cursor_place is not None:
                entered_text = entered_text[:int(cursor_place)] + unicode_char + entered_text[int(cursor_place):]
            cursor_place += unicode_char_len
            self.cursor_place = cursor_place
        self._entered_text = entered_text
    
    def _parse_key_right(self, ctrl, initial_cursor_place: int):
        self._changed_cursor = True
        cursor_place = int(self.cursor_place)
        entered_text = self._entered_text
        
        if not ctrl:
            self.cursor_place = min(len(entered_text), cursor_place + 1)
            return
        
        entered_text_len = len(entered_text)
        next_space = next((i for i in range(cursor_place + 1, entered_text_len)
                        if not entered_text[i].isalnum()
                        and entered_text[i - 1].isalnum()), entered_text_len)
        cursor_place = min(entered_text_len, next_space)
        if cursor_place == initial_cursor_place and cursor_place < entered_text_len:
            cursor_place += 1
        
        self.cursor_place = cursor_place
    
    def _parse_key_left(self, ctrl, initial_cursor_place: int):
        self._changed_cursor = True
        cursor_place = int(self.cursor_place)
        
        if not ctrl:
            self.cursor_place = max(0, cursor_place - 1)
            return
        
        entered_text = self._entered_text
        prev_space = next((i for i in range(cursor_place - 1, 0, -1)
                        if not entered_text[i - 1].isalnum()
                        and entered_text[i].isalnum()), 0)
        cursor_place = max(0, prev_space)
        if cursor_place == initial_cursor_place and cursor_place > 0:
            cursor_place -= 1
            
        self.cursor_place = cursor_place

    def _parse_key_end(self):
        if self.multiple:
            lines = self._entered_text.split('\n')
            line_grid = self._get_cursor_line_col(lines)
            line_len = len(lines[int(line_grid.x)]) if line_grid.x < len(lines) else 0
            self.cursor_place = self._get_line_abs_pos(line_grid.x, line_len, lines)
        else: self.cursor_place = len(self._entered_text)
        
    def _parse_arrow_keys(self, ctrl, initial_cursor_place: int) -> bool:
        fdown = keyboard.is_fdown
        if fdown(Keys.Up):
            if self.multiple:
                current_grid = self._get_cursor_line_col()
                if current_grid.x > 0:
                    self.cursor_place = self._get_line_abs_pos(current_grid.x - 1, current_grid.y)
            return True
        elif fdown(Keys.Down):
            if self.multiple:
                lines = self._entered_text.split('\n')
                current_grid = self._get_cursor_line_col(lines)
                if current_grid.x < len(lines) - 1:
                    self.cursor_place = self._get_line_abs_pos(current_grid.x + 1, current_grid.y, lines)
            return True
        elif fdown(Keys.Right):
            self._parse_key_right(ctrl, initial_cursor_place)
            return True
        elif fdown(Keys.Left):
            self._parse_key_left(ctrl, initial_cursor_place)
            return True
        return False
    
    def _parse_numpad_keys(self, ctrl) -> bool:
        fdown = keyboard.is_fdown
        if fdown(Keys.Backspace):
            if self.cursor_place > 0: self._parse_key_back(ctrl)
            return True
        elif fdown(Keys.Delete):
            entered_text = self._entered_text
            if self.cursor_place < len(entered_text):
                self._entered_text = entered_text[:self.cursor_place] + entered_text[self.cursor_place+1:]
            return True
        elif fdown(Keys.Home):
            if self.multiple:
                line_grid = self._get_cursor_line_col()
                self.cursor_place = self._get_line_abs_pos(line_grid.x, 0)
            else: self.cursor_place = 0
            return True
        elif fdown(Keys.End):
            self._parse_key_end()
            return True
        return False
    
    def _parse_keydown(self):
        down = keyboard.is_down
        ctrl = down(Keys.LeftCtrl) or down(Keys.RightCtrl)

        if keyboard.is_fdown(Keys.Enter):
            entered_text = self._entered_text
            max_chars = self.max_characters
            if self.multiple and (max_chars is None or len(entered_text) < max_chars):
                cursor_place = self.cursor_place
                self._entered_text = entered_text[:cursor_place] + '\n' + entered_text[cursor_place:]
                cursor_place += 1
                self.cursor_place = cursor_place
            return

        if self._parse_arrow_keys(ctrl, 0): return
        if self._parse_numpad_keys(ctrl): return

        if down(Keys.V) and ctrl and self.allow_paste: 
            self._parse_paste()
            return
        
        if ctrl or down(Keys.LeftAlt) or down(Keys.RightAlt): return
        dtype = nevu_state.window.renderer_type
        if dtype.raylib: 
            unicode_char = md.rl.get_char_pressed()
        elif dtype.pygame_like: 
            unicode_char = nevu_state.window.pygame_unicode
        else: return
        if not unicode_char: return
        assert isinstance(unicode_char, int | str)
        self._parse_unicode(unicode_char)
    
    def _on_click_system(self):
        super()._on_click_system()
        self.check_selected()
    
    def _event_update(self, events: list | None = None):
        events = nevu_state.current_events
        if events is None: events = []
        super()._event_update(events)

        selected = self.selected

        if not self.get_param_strict("is_active").value:
            if selected: 
                self.selected = False
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
                    self._changed = True
                else:
                    upd_scrollx()
                    upd_scrolly()
                self.clear_texture()
        if prev_selected != selected:
            if selected:
                upd_scrollx()
                upd_scrolly()
            else: self._changed_cursor = True

        if selected:
            cursor_moved = False
            changed_text = self._changed_text
            initial_cursor_place = self.cursor_place
            initial_text = self._entered_text
            self._parse_keydown()
            if self.cursor_place != initial_cursor_place: cursor_moved = True
            if self._entered_text != initial_text: changed_text = True
            if changed_text or cursor_moved: self._changed = True

            if changed_text:
                self._right_bake_text()
                changed_text = False
                if on_change := self._on_change_fun:
                    try: on_change(self._entered_text)
                    except Exception as e: print(f"Error in Input on_change_function: {e}")

            elif cursor_moved:
                upd_scrollx()
                upd_scrolly()

            self._changed_text = changed_text

        self.selected = selected
        
    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)
        self.clear_texture()
        direction = -1 if side else 1

        scroll_multiplier = 3
        line_h = self._get_line_height()
        
        scroll_amount = direction * line_h * scroll_multiplier
        self._update_scroll_offset_y()
        self._scroll_offset.y -= scroll_amount
        self._scroll_offset.y = max(0, min(self._scroll_offset.y, self.max_scroll_y))
        self._changed = True
    
    def _measure_text(self, text: str):
        renderFont = self.get_font()
        dtype = nevu_state.window.renderer_type
        if dtype.raylib:
            measure = md.rl.measure_text_ex
            res = measure(renderFont, text, renderFont.baseSize, 0) #type: ignore
            return (res.x, res.y)
        elif dtype.pygame_like: 
            return renderFont.size(text) #type: ignore
        else:
            return (0, 0)
        
    def _find_best_cursor_index(self, renderFont, text, x_pos):
        best_index = 0
        min_diff = float('inf')
        current_w = 0
        measure = self._measure_text
        for i, char in enumerate(text):
            char_w = measure(char)[0]
            pos_before = current_w
            pos_after = current_w + char_w
            diff_before = abs(x_pos - pos_before)
            diff_after = abs(x_pos - pos_after)
            if diff_before <= min_diff:
                min_diff = diff_before
                best_index = i
            if diff_after < min_diff:
                min_diff = diff_after
                best_index = i + 1
            current_w += char_w
        return max(0, min(best_index, len(text)))

    def check_selected(self):
        self.selected = True
        self._changed = True
        renderFont = self.get_font()
        relative_vec = mouse.pos - self.absolute_coordinates
        lt_marg_vec = self.rel(self.lt_margin)
        scrolled_vec = (relative_vec - lt_marg_vec) + self._scroll_offset
        entered_text = self._entered_text
        if self.multiple:
            line_height = self._get_line_height()
            if line_height <= 0 : line_height = 1
            target_line_index = max(0, int(scrolled_vec.y / line_height))
            lines = entered_text.split('\n')
            target_line_index = min(target_line_index, len(lines) - 1)
            target_line_text = lines[target_line_index] if target_line_index < len(lines) else ""
            best_col_index = self._find_best_cursor_index(renderFont, target_line_text, scrolled_vec.x)
            self.cursor_place = self._get_line_abs_pos(target_line_index, best_col_index)
        else:
            best_index = self._find_best_cursor_index(renderFont, entered_text, scrolled_vec.x)
            self.cursor_place = best_index
            lines = None
        self._update_scroll_offset_x(lines)
        self._update_scroll_offset_y()
        
    @property
    def text(self): return self._entered_text # type: ignore
    @text.setter
    def text(self, text: str | int | float):
        text = str(text)
        original_text = self._entered_text
        if not self.multiple:
            text = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        if self.max_characters is not None: text = text[:self.max_characters]
        entered_text = text
        self.cursor_place = min(len(entered_text), self.cursor_place)
        self._changed = True
        self._entered_text = entered_text
        
        if not self.booted: return
        self._right_bake_text()

        if self._on_change_fun and original_text != entered_text:
            try: self._on_change_fun(entered_text)
            except Exception as e: print(f"Error in Input on_change_function (setter): {e}")
    def secondary_draw_content(self):
        if not self.visible: return
        if not self._changed: return
        assert self.surface
        line_height = self._get_line_height()
        
        cursor = self.cursor
        assert cursor
        rel_func = self.rel
        curr_size = self._csize
        
        cursor_size_vec = NvVector2.from_xy(cursor.get_width(), cursor.get_height())
        
        lt_marg_vec = rel_func(self.lt_margin)
        rb_marg_vec = rel_func(self.rb_margin)
        
        lt_scrolled_vec = lt_marg_vec - self._scroll_offset
        
        clip = (curr_size - lt_marg_vec - rb_marg_vec).to_round()
        clip.x, clip.y = max(clip.x, 0), max(clip.y, 0)
    
        if clip.x <= 0 or clip.y <= 0: return

        dtype = nevu_state.window.renderer_type
        text_surface = self._text_surface
        surface = self.surface
        multiple = self.multiple
        
        assert text_surface
        
        if dtype.pygame_like:
            pygame = md.pygame
            surface_t = pygame.Surface
            assert isinstance(surface, surface_t)
            assert isinstance(text_surface, surface_t)
            clip_rect = surface.get_rect()
            assert isinstance(clip_rect, pygame.Rect)
            clip_rect.topleft = lt_marg_vec.get_int_tuple()
            clip_rect.size = clip.get_int_tuple()
            if multiple:
                text_rect = text_surface.get_rect(topleft = lt_scrolled_vec.get_int_tuple())
            else:
                text_rect = text_surface.get_rect(left = int(lt_scrolled_vec.x), centery = int((lt_marg_vec.y + surface.get_height() - rb_marg_vec.y) / 2) )
            
            original_clip = surface.get_clip()
            surface.set_clip(clip_rect)
            surface.blit(text_surface, text_rect)
            surface.set_clip(original_clip)
            
        elif dtype.raylib:
            rl = md.rl
            assert isinstance(text_surface, NvRenderTexture)
            assert isinstance(surface, NvRenderTexture)
            with surface:
                rl.begin_scissor_mode(int(lt_marg_vec.x), int(lt_marg_vec.y), int(clip.x), int(clip.y))
                begin_blend_mode(self._correct_blend)
                if multiple:
                    text_vec = lt_scrolled_vec.xy
                else:
                    text_vec = NvVector2(lt_scrolled_vec.x, 
                                         lt_marg_vec.y + ((curr_size.y - lt_marg_vec.y - rb_marg_vec.y) - text_surface.height) / 2)
                dest_pos = text_vec.get_int_tuple()
                surface.fast_blit(text_surface, dest_pos)
                end_blend_mode()
                rl.end_scissor_mode() 
                
        if self.selected:
            measure = self._measure_text
            if multiple:
                lines = self._entered_text.split('\n')
                cursor_grid  = self._get_cursor_line_col(lines)
                line_text = lines[int(cursor_grid.x)] if cursor_grid.x < len(lines) else ""
                text_before_cursor_in_line = line_text[:int(cursor_grid.y)]
                cursor_x_offset = measure(text_before_cursor_in_line)[0]
                cursor_visual_vec = NvVector2.from_xy(lt_scrolled_vec.x + cursor_x_offset,
                                            lt_scrolled_vec.y + (cursor_grid.x * line_height))
            else:
                text_before_cursor = self._entered_text[:self.cursor_place]
                cursor_x_offset = measure(text_before_cursor)[0]
                cursor_visual_vec = NvVector2.from_xy(lt_scrolled_vec.x + cursor_x_offset,
                                            (curr_size.y - cursor_size_vec.y) / 2)

            if dtype.pygame_like:
                pygame = md.pygame
                surface_t = pygame.Surface
                assert isinstance(cursor, surface_t)
                assert isinstance(surface, surface_t)
                assert clip_rect # type: ignore
                cursor_draw_rect = cursor.get_rect(topleft = cursor_visual_vec.to_tuple())
                if clip_rect.colliderect(cursor_draw_rect):
                    surface.blit(cursor, cursor_draw_rect.topleft)
                    
            elif dtype.raylib:
                rl = md.rl
                assert isinstance(cursor, NvRenderTexture)
                assert isinstance(surface, NvRenderTexture)
                cursor_rect_rl = (cursor_visual_vec.x, cursor_visual_vec.y, cursor_size_vec.x, cursor_size_vec.y)
                clip_rect_rl = (lt_marg_vec.x, lt_marg_vec.y, clip.x, clip.y)
                
                if not rl.check_collision_recs(cursor_rect_rl, clip_rect_rl): return
                with surface: 
                    color = self._subtheme.oncolor
                    if len(color) == 3: color = (*color, 255)
                    rl.draw_rectangle(int(cursor_visual_vec.x), int(cursor_visual_vec.y), int(cursor_size_vec.x), int(cursor_size_vec.y), color)
        
    def _create_clone(self): return self.__class__(self._template['size'], copy.deepcopy(self.style), copy.copy(self._default_text), copy.copy(self.placeholder), self._on_change_fun, **self.constant_kwargs)