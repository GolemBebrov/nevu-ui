import pygame
import copy
from typing import Unpack, override

from nevu_ui.utils import mouse
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.core.state import nevu_state
from nevu_ui.components.widgets import Widget, InputKwargs
from nevu_ui.presentation.style import Style, default_style

class Input(Widget):
    max_characters: int | None
    multiple: bool
    allow_paste: bool
    words_indent: bool
    is_active: bool
    padding: list
    
    def __init__(self, size: NvVector2 | list, style: Style = default_style, default: str = "", placeholder: str = "", on_change_function = None, **constant_kwargs: Unpack[InputKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size}
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
        def max_elem(a, b, name): return self._ensure_padding(max(a, b) / 2, name)
        base_padding = self.padding.copy()
        if isinstance(self.style.borderradius, tuple):
            for i, item in enumerate(self.style.borderradius):
                base_padding[i] += item
        else:
            for i in range(len(base_padding)):
                base_padding[i] += self.style.borderradius
        max_left = max_elem(base_padding[0], base_padding[3], "left")
        max_right = max_elem(base_padding[1], base_padding[2], "right")
        max_top = max_elem(base_padding[0], base_padding[1], "top")
        max_bottom = max_elem(base_padding[2], base_padding[3], "bottom")
        self.lt_margin += NvVector2(max_left, max_top)
        self.rb_margin += NvVector2(max_right, max_bottom)
        self._changed = True

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
        self._changed_cursor = False
        
    def _init_text_cache(self):
        self._text_surface = None
        self._text_rect = pygame.Rect(0, 0, 0, 0)
        
    def _add_params(self):
        super()._add_params()
        self._add_param("is_active", bool, True)
        self._add_param("multiple", bool, False)
        self._add_param("allow_paste", bool, True)
        self._add_param("words_indent", bool, False)
        self._add_param("max_characters", (int, type(None)), None)
        self._add_param("blacklist", (list, type(None)), None)
        self._add_param("whitelist", (list, type(None)), None)
        self._add_param("padding", (list, tuple), (0,0,0,0))
    
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
        if not hasattr(self,"_resize_ratio"): self._resize_ratio = NvVector2(1,1)
        if not hasattr(self, 'style'): return
        try: font_height = self._get_line_height()
        except (pygame.error, AttributeError): font_height = int(self.size.y * self._resize_ratio.y * 0.8)
        cursor_width = max(1, int(self.size.x * 0.01 * self._resize_ratio.x))
        self.cursor = pygame.Surface((cursor_width, font_height))
        try: self.cursor.fill(self._subtheme.oncolor)
        except AttributeError: self.cursor.fill((0,0,0))
        
    def _get_line_height(self):
        try:
            if not hasattr(self, '_style') or not self.style.fontname: raise AttributeError("Font not ready")
            return self.get_pygame_font().get_height()
        except (pygame.error, AttributeError) as e: raise e
        
    def _get_cursor_line_col(self) -> NvVector2:
        if not self._entered_text: return NvVector2(0, 0)
        lines = self._entered_text.split('\n')
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
    
    def _get_line_abs_pos(self, target_line_index, target_col_index):
        lines = self._entered_text.split('\n')
        target_line_index = max(0, min(target_line_index, len(lines) - 1))
        abs_pos = 0
        for i in range(int(target_line_index)): abs_pos += len(lines[i]) + 1
        current_line_len = len(lines[int(target_line_index)]) if target_line_index < len(lines) else 0
        target_col_index = max(0, min(target_col_index, current_line_len))
        abs_pos += target_col_index
        return abs_pos
    
    def _update_scroll_offset_x(self):
        if not hasattr(self,'style'): return
        if not hasattr(self, 'surface'): return
        try:
            renderFont = self.get_pygame_font()
            cursor_grid = self._get_cursor_line_col()
            lines = self._entered_text.split('\n')
            curr_line_text = lines[int(cursor_grid.x)] if cursor_grid.x < len(lines) else ""
            text_before_cursor = curr_line_text[:int(cursor_grid.y)]
            ideal_offset_x = renderFont.size(text_before_cursor)[0]
            line_width = renderFont.size(curr_line_text)[0]
        except (pygame.error, AttributeError, IndexError): return
        assert self.surface
        sum_margin_vec = self.rel(self.lt_margin + self.rb_margin)
        visible_width = max((self._csize - sum_margin_vec).to_int().x, 1)
        relative_cursor_pos = ideal_offset_x - self._scroll_offset.x
        if relative_cursor_pos < 0: self._scroll_offset.x = ideal_offset_x
        elif relative_cursor_pos > visible_width: self._scroll_offset.x = ideal_offset_x - visible_width
        max_scroll_x = max(0, line_width - visible_width)
        self._scroll_offset.x = max(0, min(self._scroll_offset.x, max_scroll_x))

    def _update_scroll_offset_y(self):
        if not self.multiple or not hasattr(self, 'style'): return
        if not self._text_surface: return
        try:
            line_height = self._get_line_height()
            cursor_grid = self._get_cursor_line_col()
            ideal_offset_y = cursor_grid.x * line_height
            total_text_height = self._text_surface.get_height()
        except (pygame.error, AttributeError, IndexError): return
        sum_margin = self.rel(self.lt_margin + self.rb_margin)
        visible_height = max((self._csize - sum_margin).to_int().y, 1)
        self.max_scroll_y = max(0, total_text_height - visible_height)
        if ideal_offset_y < self._scroll_offset.y: self._scroll_offset.y = ideal_offset_y
        elif ideal_offset_y + line_height > self._scroll_offset.y + visible_height: self._scroll_offset.y = ideal_offset_y + line_height - visible_height
        self._scroll_offset.y = max(0, min(self._scroll_offset.y, self.max_scroll_y))

    @override
    def bake_text(self, text: str, words_indent = False, continuous = False, multiline_mode = False): # type: ignore
        renderFont = self.get_pygame_font()
        line_height = int(self._get_line_height())
        
        if continuous:
            try: self._text_surface = renderFont.render(text, True, self.subtheme_font)
            except (pygame.error, AttributeError): self._text_surface = None
            return
        
        if multiline_mode:
            lines = text.split('\n')
            
            if not lines: 
                self._text_surface = pygame.Surface((1, line_height), pygame.SRCALPHA)
                self._text_surface.fill((0 ,0 ,0, 0))
                return
            
            max_width = 0
            rendered_lines = []
            
            for line in lines:
                    line_surface = renderFont.render(line, True, self.subtheme_font)
                    rendered_lines.append(line_surface)
                    if line_surface.get_width() > max_width: max_width = line_surface.get_width()
                    
            total_height = len(lines) * line_height
            self._text_surface = pygame.Surface((max(1, max_width), max(line_height, total_height)), pygame.SRCALPHA)
            self._text_surface.fill((0 ,0, 0, 0))

            current_y = 0
            for line_surface in rendered_lines:
                self._text_surface.blit(line_surface, (0, current_y))
                current_y += line_height
            return
        
        lines = []
        current_line = ""
        max_line_width = int(self._csize[0] - self.relx(self.lt_margin.x + self.rb_margin.x))
        
        processed_text = text.replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = processed_text.split('\n')
        
        try:
            for para in paragraphs:
                words = para.split() if words_indent else list(para)
                current_line = ""
                sep = " " if words_indent else ""
                for word in words:
                    test_line = current_line + word + sep
                    if renderFont.size(test_line)[0] <= max_line_width: 
                        current_line = test_line
                    else:
                        if current_line: lines.append(current_line.rstrip())
                        current_line = word + sep
                if current_line: lines.append(current_line.rstrip())

            rel_lt_vec, rel_rb_vec = self.rel(self.lt_margin), self.rel(self.rb_margin)
            visible_area_height = self._csize.y - (rel_lt_vec.y + rel_rb_vec.y)
            
            if line_height > 0:
                max_visible_lines = int(visible_area_height / line_height)
            else:
                max_visible_lines = 1
                
            visible_lines = lines[:max_visible_lines]

            if not visible_lines:
                self._text_surface = pygame.Surface((1, 1), pygame.SRCALPHA); self._text_surface.fill((0,0,0,0))
                self._text_rect = self._text_surface.get_rect(topleft=(rel_lt_vec.to_int().to_tuple()))
                return
            
            max_width = 0
            for line in visible_lines:
                line_width = renderFont.size(line)[0]
                if line_width > max_width: max_width = line_width
            max_width = max(1, max_width)
            
            total_h = len(visible_lines) * line_height
            self._text_surface = pygame.Surface((max_width, max(1, total_h)), pygame.SRCALPHA)
            self._text_surface.fill((0,0,0,0))
            
            curr_y = 0
            for line in visible_lines:
                line_surf = renderFont.render(line, True, self.subtheme_font)
                self._text_surface.blit(line_surf, (0, curr_y))
                curr_y += line_height
            self._text_rect = self._text_surface.get_rect(topleft=(rel_lt_vec.to_int().to_tuple()))
        
        except (pygame.error, AttributeError):
            self._text_surface = None
            self._text_rect = pygame.Rect(0,0,0,0)
            
    def _right_bake_text(self):
        self.clear_surfaces()
        if not hasattr(self, 'style'): return
        text_to_render = self._entered_text if len(self._entered_text) > 0 else self.placeholder
        if self.multiple:
            self.bake_text(text_to_render, multiline_mode=True)
            self._update_scroll_offset_y()
        else: self.bake_text(text_to_render, continuous=True)
        self._update_scroll_offset_x()
        
    def _resize(self, resize_ratio: NvVector2):
        super()._resize(resize_ratio)
        self._init_cursor()
        self._right_bake_text()
        
    @property
    def style(self): return self._style()
    @style.setter
    def style(self, style: Style):
        self.clear_surfaces()
        self._style = copy.deepcopy(style)
        if not self.booted: return
        self._changed = True
        self._update_image()
        if hasattr(self,'_entered_text'):
            self._right_bake_text()

    @property
    def cursor_place(self): return self._cursor_place
    @cursor_place.setter
    def cursor_place(self, cursor_place: int):
        self._cursor_place = cursor_place
        if hasattr(self, 'cache'): self.clear_texture()
    
    def _parse_backspace(self, ctrl):
        if ctrl:
            prev_space = 0
            for i in range(self.cursor_place - 1, 0, -1):
                if not self._entered_text[i-1].isalnum() and self._entered_text[i].isalnum():
                    prev_space = i
                    break
            delete_to = max(0, prev_space)
            if delete_to == self.cursor_place: delete_to -= 1
            self._entered_text = self._entered_text[:delete_to] + self._entered_text[self.cursor_place:]
            self.cursor_place = delete_to
        else:
            self._entered_text = self._entered_text[:self.cursor_place-1] + self._entered_text[self.cursor_place:]
            self.cursor_place = max(0,self.cursor_place-1)
    
    def _parse_paste(self):
        pasted_text = ""
        try:
            pasted_text = pygame.scrap.get_text()
            if isinstance(pasted_text, bytes):
                pasted_text = pasted_text.decode('utf-8')
            pasted_text = pasted_text.replace('\x00', '')
        except (pygame.error, UnicodeDecodeError, TypeError, AttributeError): pasted_text = ""
        if pasted_text:
            filtered_text = ""
            for char in pasted_text:
                valid_char = True
                if self.blacklist and char in self.blacklist: valid_char = False
                if self.whitelist and char not in self.whitelist: valid_char = False
                if not self.multiple and char in '\r\n': valid_char = False
                if valid_char: filtered_text += char
            if self.max_characters is not None:
                available_space = self.max_characters - len(self._entered_text)
                filtered_text = filtered_text[:max(0, available_space)]
            if filtered_text:
                self._entered_text = self._entered_text[:self.cursor_place] + filtered_text + self._entered_text[self.cursor_place:]
                self.cursor_place += len(filtered_text)
                
    def _parse_unicode(self, unicode_char: str):
        unicode_valid = len(unicode_char) == 1 and unicode_char.isprintable()
        correct_newline = self.multiple or (unicode_char not in '\r\n')
        if (unicode_valid and correct_newline and self.max_characters is None) or (self.max_characters and len(self._entered_text) < self.max_characters ):
            valid_char = True
            if self.blacklist and unicode_char in self.blacklist: valid_char = False
            if self.whitelist and unicode_char not in self.whitelist: valid_char = False
            if valid_char:
                self._entered_text = self._entered_text[:self.cursor_place] + unicode_char + self._entered_text[self.cursor_place:]
                self.cursor_place += len(unicode_char)
    
    def _parse_right(self, ctrl, initial_cursor_place: int):
        if ctrl:
            next_space = next((i for i in range(self.cursor_place + 1, len(self._entered_text))
                            if not self._entered_text[i].isalnum()
                            and self._entered_text[i - 1].isalnum()), len(self._entered_text))
            self.cursor_place = min(len(self._entered_text), next_space if next_space != len(self._entered_text) else len(self._entered_text))
            if self.cursor_place == initial_cursor_place and self.cursor_place < len(self._entered_text):
                self.cursor_place += 1
        else:
            self.cursor_place = min(len(self._entered_text), self.cursor_place+1)
        self._changed_cursor = True
    
    def _parse_left(self, ctrl, initial_cursor_place: int):
        if ctrl:
            prev_space = next((i for i in range(self.cursor_place - 1, 0, -1)
                            if not self._entered_text[i - 1].isalnum()
                            and self._entered_text[i].isalnum()), 0)
            self.cursor_place = max(0, prev_space)
            if self.cursor_place == initial_cursor_place and self.cursor_place > 0:
                self.cursor_place -= 1
        else: self.cursor_place = max(0,self.cursor_place-1)
        self._changed_cursor = True
        
    def _parse_end(self):
        if self.multiple:
            line_grid = self._get_cursor_line_col()
            lines = self._entered_text.split('\n')
            line_len = len(lines[int(line_grid.x)]) if line_grid.x < len(lines) else 0
            self.cursor_place = self._get_line_abs_pos(line_grid.x, line_len)
        else: self.cursor_place = len(self._entered_text)
        
    def _parse_arrow_events(self, ctrl, event, initial_cursor_place: int):
        if event.key == pygame.K_UP:
            if self.multiple:
                current_grid = self._get_cursor_line_col()
                if current_grid.x > 0:
                    self.cursor_place = self._get_line_abs_pos(current_grid.x - 1, current_grid.y)
        elif event.key == pygame.K_DOWN:
            if self.multiple:
                lines = self._entered_text.split('\n')
                current_grid = self._get_cursor_line_col()
                if current_grid.x < len(lines) - 1:
                    self.cursor_place = self._get_line_abs_pos(current_grid.x + 1, current_grid.y)
        elif event.key == pygame.K_RIGHT:
            self._parse_right(ctrl, initial_cursor_place)
        elif event.key == pygame.K_LEFT:
            self._parse_left(ctrl, initial_cursor_place)
    
    def _parse_numpad_events(self, ctrl, event):
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_place > 0: self._parse_backspace(ctrl)
        elif event.key == pygame.K_DELETE:
            if self.cursor_place < len(self._entered_text):
                self._entered_text = self._entered_text[:self.cursor_place] + self._entered_text[self.cursor_place+1:]
        elif event.key == pygame.K_HOME:
            if self.multiple:
                line_grid = self._get_cursor_line_col()
                self.cursor_place = self._get_line_abs_pos(line_grid.x, 0)
            else: self.cursor_place = 0
        elif event.key == pygame.K_END:
            self._parse_end()
            
    def _parse_keydown_events(self, event, initial_cursor_place: int):
        ctrl = event.mod & pygame.KMOD_CTRL
        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER] and (self.multiple and (self.max_characters is None or len(self._entered_text) < self.max_characters)):
            self._entered_text = self._entered_text[:self.cursor_place] + '\n' + self._entered_text[self.cursor_place:]
            self.cursor_place += 1
        self._parse_arrow_events(ctrl, event, initial_cursor_place)
        self._parse_numpad_events(ctrl, event)
        if event.key == pygame.K_v and ctrl:
            if self.allow_paste: self._parse_paste()
        elif unicode_char := event.unicode: self._parse_unicode(unicode_char)
    
    def _on_click_system(self):
        super()._on_click_system()
        self.check_selected()
    
    def _event_update(self, events: list | None = None):
        events = nevu_state.current_events
        if events is None: events = []
        
        super()._event_update(events)
        def off_selection(self): self.selected = False; self._changed = True
        if not self.is_active:
            if self.selected: off_selection(self)
            return
        prev_selected = self.selected
        if mouse.left_fdown:
            mouse_collided = self.get_rect().collidepoint(mouse.pos)
            if self.selected and not mouse_collided:
                off_selection(self)
                self.clear_texture()
            elif self.selected and mouse_collided:
                self._update_scroll_offset_x()
                self._update_scroll_offset_y()
                self.clear_texture()
        
        if prev_selected != self.selected:
            if self.selected:
                self._update_scroll_offset_x()
                self._update_scroll_offset_y()
            else: self._changed_cursor = True
            
        if self.selected:
            cursor_moved = False
            for event in events:
                if event.type == pygame.KEYDOWN:
                    initial_cursor_place = self.cursor_place
                    initial_text = self._entered_text
                    self._parse_keydown_events(event, initial_cursor_place)
                    if self.cursor_place != initial_cursor_place: cursor_moved = True
                    if self._entered_text != initial_text: self._changed_text = True
                    if self._changed_text or cursor_moved: self._changed = True

            if self._changed_text:
                self._right_bake_text()
                self._changed_text = False
                if self._on_change_fun:
                    try: self._on_change_fun(self._entered_text)
                    except Exception as e: print(f"Error in Input on_change_function: {e}")

            elif cursor_moved:
                self._update_scroll_offset_x()
                self._update_scroll_offset_y()

    def _on_scroll_system(self, side: bool):
        super()._on_scroll_system(side)
        self.clear_texture()
        direction = -1 if side else 1

        scroll_multiplier = 3
        line_h = self._get_line_height()
        
        scroll_amount = direction * line_h * scroll_multiplier
        if not hasattr(self, 'max_scroll_y'): self._update_scroll_offset_y()
        self._scroll_offset.y -= scroll_amount
        self._scroll_offset.y = max(0, min(self._scroll_offset.y, getattr(self, 'max_scroll_y', 0)))
        self._changed = True
    
    def _find_best_cursor_index(self, renderFont, text, x_pos):
        best_index = 0
        min_diff = float('inf')
        current_w = 0
        for i, char in enumerate(text):
            char_w = renderFont.size(char)[0]
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
        if self.selected: return
        self.selected = True
        self._changed = True
        try:
            renderFont = self.get_pygame_font()
            relative_vec = mouse.pos - self.absolute_coordinates
            lt_marg_vec = self.rel(self.lt_margin)
            cropped_vec = relative_vec - lt_marg_vec
            scrolled_vec = cropped_vec + self._scroll_offset
            if self.multiple:
                line_height = self._get_line_height()
                if line_height <= 0 : line_height = 1
                target_line_index = max(0, int(scrolled_vec.y / line_height))
                lines = self._entered_text.split('\n')
                target_line_index = min(target_line_index, len(lines) - 1)
                target_line_text = lines[target_line_index] if target_line_index < len(lines) else ""
                best_col_index = self._find_best_cursor_index(renderFont, target_line_text, scrolled_vec.x)
                self.cursor_place = self._get_line_abs_pos(target_line_index, best_col_index)
            else:
                best_index = self._find_best_cursor_index(renderFont, self._entered_text, scrolled_vec.x)
                self.cursor_place = best_index
            self._update_scroll_offset_x()
            self._update_scroll_offset_y()
        except (pygame.error, AttributeError, IndexError) as e: pass
        
    @property
    def text(self): return self._entered_text # type: ignore
    @text.setter
    def text(self, text: str | int | float):
        text = str(text)
        original_text = self._entered_text
        if not self.multiple:
            text = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        print("setted", text)
        if self.max_characters is not None: text = text[:self.max_characters]
        self._entered_text = text
        self.cursor_place = min(len(self._entered_text), self.cursor_place)
        self._changed = True
        
        if not self.booted: return
        self._right_bake_text()

        if self._on_change_fun and original_text != self._entered_text:
            try: self._on_change_fun(self._entered_text)
            except Exception as e: print(f"Error in Input on_change_function (setter): {e}")
            
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return
        if not self._changed: return
        assert self.surface
        try:
            renderFont = self.get_pygame_font()
            if not renderFont: raise AttributeError
            line_height = self._get_line_height()
            cursor_height = self.cursor.get_height()
        except (pygame.error, AttributeError): return
        
        lt_marg_vec = self.rel(self.lt_margin)
        rb_marg_vec = self.rel(self.rb_margin)
        lt_scrolled_vec = lt_marg_vec - self._scroll_offset
        clip = (self._csize - lt_marg_vec - rb_marg_vec).to_int()
        clip.x, clip.y = max(clip.x, 0), max(clip.y, 0)
    
        if clip.x <= 0 or clip.y <= 0: return
         
        clip_rect = self.surface.get_rect()
        clip_rect.topleft = lt_marg_vec.to_int()
        clip_rect.size = clip.to_int()
        
        if self._text_surface:
            if self.multiple:
                self._text_rect = self._text_surface.get_rect(topleft = lt_scrolled_vec.to_int().to_tuple())
            else:
                self._text_rect = self._text_surface.get_rect(left = int(lt_scrolled_vec.x), centery = int((lt_marg_vec.y + self.surface.get_height() - rb_marg_vec.y) / 2) )
            
            original_clip = self.surface.get_clip()
            self.surface.set_clip(clip_rect)
            self.surface.blit(self._text_surface, self._text_rect)
            self.surface.set_clip(original_clip)
            
        if self.selected:
            cursor_visual = NvVector2()
            try:
                if self.multiple:
                    cursor_grid  = self._get_cursor_line_col()
                    lines = self._entered_text.split('\n')
                    line_text = lines[int(cursor_grid.x)] if cursor_grid.x < len(lines) else ""
                    text_before_cursor_in_line = line_text[:int(cursor_grid.y)]
                    cursor_x_offset = renderFont.size(text_before_cursor_in_line)[0]
                    cursor_visual.x = int(lt_scrolled_vec.x + cursor_x_offset)
                    cursor_visual.y = int(lt_scrolled_vec.y + (cursor_grid.x * line_height))
                else:
                    text_before_cursor = self._entered_text[:self.cursor_place]
                    cursor_x_offset = renderFont.size(text_before_cursor)[0]
                    cursor_visual.x = int(lt_scrolled_vec.x + cursor_x_offset )
                    cursor_visual.y = int((self.surface.get_height() - cursor_height) / 2)
                
                cursor_draw_rect = self.cursor.get_rect(topleft=(cursor_visual.x, cursor_visual.y))
                if clip_rect.colliderect(cursor_draw_rect):
                    self.surface.blit(self.cursor, cursor_draw_rect.topleft)
                    
            except (pygame.error, AttributeError, IndexError):
                print("Error drawing cursor")
    
    def clone(self): return Input(self._lazy_kwargs['size'], copy.deepcopy(self.style), copy.copy(self._default_text), copy.copy(self.placeholder), self._on_change_fun, **self.constant_kwargs)