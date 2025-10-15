import pygame
import copy

from nevu_ui.core_types import Align
from nevu_ui.utils import mouse
from nevu_ui.widgets import Widget, WidgetKwargs

from typing import Any, TypedDict, NotRequired, Unpack

from nevu_ui.fast.nvvector2 import (
    NvVector2 as Vector2, NvVector2
)
from nevu_ui.style import (
    Style, default_style
)

class InputKwargs(WidgetKwargs):
    is_active: NotRequired[bool]
    multiple: NotRequired[bool]
    allow_paste: NotRequired[bool]
    words_indent: NotRequired[bool]
    max_characters: NotRequired[int | None]
    blacklist: NotRequired[list | None]
    whitelist: NotRequired[list | None]

class Input(Widget):
    blacklist: list | None
    whitelist: list | None
    max_characters: int | None
    multiple: bool
    allow_paste: bool
    words_indent: bool
    is_active: bool
    
    def __init__(self, size: Vector2 | list, style: Style = default_style, default: str = "", placeholder: str = "", on_change_function = None, **constant_kwargs: Unpack[InputKwargs]):
        super().__init__(size, style, **constant_kwargs)
        self._lazy_kwargs = {'size': size}
        self._entered_text = ""

        self.placeholder = placeholder
        self._on_change_fun = on_change_function
        self.text = default
        self._default_text = default

        self._text_surface = None

    def _init_numerical(self):
        super()._init_numerical()
        self._text_scroll_offset = 0
        self._text_scroll_offset_y = 0
        self.max_scroll_y = 0
        self._cursor_place = 0
        self.left_margin = 10
        self.right_margin = 10
        self.top_margin = 5
        self.bottom_margin = 5
        
    def _init_booleans(self):
        super()._init_booleans()
        self.hoverable = False
        self.selected = False
        
    def _init_text_cache(self):
        self._text_surface = None
        self._text_rect = pygame.Rect(0, 0, 0, 0)
        
    def _add_constants(self):
        super()._add_constants()
        self._add_constant("is_active", bool, True)
        self._add_constant("multiple", bool, False)
        self._add_constant("allow_paste", bool, True)
        self._add_constant("words_indent", bool, False)
        self._add_constant("max_characters", (int, type(None)), None)
        self._add_constant("blacklist", (list, type(None)), None)
        self._add_constant("whitelist", (list, type(None)), None)
        
    def _lazy_init(self, size: Vector2|list):
        super()._lazy_init(size)
        self._init_cursor()
        self._right_bake_text()
        
    def _init_cursor(self):
        if not hasattr(self,"_resize_ratio"): self._resize_ratio = NvVector2(1,1)
        if not hasattr(self, 'style'): return
        try: font_height = self._get_line_height()
        except (pygame.error, AttributeError): font_height = self.size.y * self._resize_ratio.y * 0.8
        cursor_width = max(1, int(self.size.x * 0.01 * self._resize_ratio.x))
        self.cursor = pygame.Surface((cursor_width, font_height))
        try: self.cursor.fill(self._subtheme.oncolor)
        except AttributeError: self.cursor.fill((0,0,0))
        
    def _get_line_height(self):
        try:
            if not hasattr(self, '_style') or not self.style.fontname: raise AttributeError("Font not ready")
            return self.get_font().get_height()
        except (pygame.error, AttributeError) as e:
            raise e
        
    def _get_cursor_line_col(self):
        if not self._entered_text: return 0, 0
        lines = self._entered_text.split('\n')
        abs_pos = self._cursor_place
        current_pos = 0
        for i, line in enumerate(lines):
            line_len = len(line)
            if abs_pos <= current_pos + line_len:
                col = abs_pos - current_pos
                return i, col
            current_pos += line_len + 1
        last_line_index = len(lines) - 1
        last_line_len = len(lines[last_line_index]) if last_line_index >= 0 else 0
        return last_line_index, last_line_len
    
    def _get_abs_pos_from_line_col(self, target_line_index, target_col_index):
        lines = self._entered_text.split('\n')
        target_line_index = max(0, min(target_line_index, len(lines) - 1))
        abs_pos = 0
        for i in range(target_line_index): abs_pos += len(lines[i]) + 1
        current_line_len = len(lines[target_line_index]) if target_line_index < len(lines) else 0
        target_col_index = max(0, min(target_col_index, current_line_len))
        abs_pos += target_col_index
        return abs_pos
    
    def _update_scroll_offset(self):
        if not hasattr(self,'style'): return
        if not hasattr(self, 'surface'): return
        try:
            renderFont = self.get_font()
            cursor_line_idx, cursor_col_idx = self._get_cursor_line_col()
            lines = self._entered_text.split('\n')
            cursor_line_text = lines[cursor_line_idx] if cursor_line_idx < len(lines) else ""
            text_before_cursor_in_line = cursor_line_text[:cursor_col_idx]
            ideal_cursor_x_offset = renderFont.size(text_before_cursor_in_line)[0]
            full_line_width = renderFont.size(cursor_line_text)[0]
        except (pygame.error, AttributeError, IndexError): return
        l_margin = self.left_margin * self._resize_ratio[0]
        r_margin = self.right_margin * self._resize_ratio[0]
        visible_width = self.surface.get_width() - l_margin - r_margin
        
        if visible_width < 1: visible_width = 1
        cursor_pos_relative_to_visible_start = ideal_cursor_x_offset - self._text_scroll_offset
        if cursor_pos_relative_to_visible_start < 0: self._text_scroll_offset = ideal_cursor_x_offset
        elif cursor_pos_relative_to_visible_start > visible_width: self._text_scroll_offset = ideal_cursor_x_offset - visible_width

        max_scroll_x = max(0, full_line_width - visible_width)
        self._text_scroll_offset = max(0, min(self._text_scroll_offset, max_scroll_x))

    def _update_scroll_offset_y(self):
        if not self.multiple or not hasattr(self, 'style'): return
        if not self._text_surface: return
        try:
            line_height = self._get_line_height()
            cursor_line, _ = self._get_cursor_line_col()
            ideal_cursor_y_offset = cursor_line * line_height
            total_text_height = self._text_surface.get_height()
        except (pygame.error, AttributeError, IndexError): return
        t_margin = self.top_margin * self._resize_ratio[1]
        b_margin = self.bottom_margin * self._resize_ratio[1]
        visible_height = self.surface.get_height() - t_margin - b_margin
        if visible_height < 1 : visible_height = 1
        self.max_scroll_y = max(0, total_text_height - visible_height)
        if ideal_cursor_y_offset < self._text_scroll_offset_y: self._text_scroll_offset_y = ideal_cursor_y_offset
        elif ideal_cursor_y_offset + line_height > self._text_scroll_offset_y + visible_height: self._text_scroll_offset_y = ideal_cursor_y_offset + line_height - visible_height
        self._text_scroll_offset_y = max(0, min(self._text_scroll_offset_y, self.max_scroll_y))

    def bake_text(self, text, unlimited_y=False, words_indent=False, 
                    alignx=Align.LEFT, aligny=Align.TOP, continuous=False, multiline_mode=False):
        if not hasattr(self, 'style') or not hasattr(self, 'surface'): return
        renderFont = self.get_font()
        line_height = self._get_line_height()
        if continuous:
            try: self._text_surface = renderFont.render(text, True, self._subtheme_font)
            except (pygame.error, AttributeError): self._text_surface = None
            return
        if multiline_mode:
            lines = text.split('\n')
            if not lines: self._text_surface = pygame.Surface((1, line_height), pygame.SRCALPHA); self._text_surface.fill((0,0,0,0)); return
            max_width = 0
            rendered_lines = []
            try:
                for line in lines:
                        line_surface = renderFont.render(line, True, self._subtheme_font)
                        rendered_lines.append(line_surface)
                        max_width = max(max_width, line_surface.get_width())
            except (pygame.error, AttributeError): self._text_surface = None; return
            total_height = len(lines) * line_height
            self._text_surface = pygame.Surface((max(1, max_width), max(line_height, total_height)), pygame.SRCALPHA)
            self._text_surface.fill((0,0,0,0))

            current_y = 0
            for line_surface in rendered_lines:
                self._text_surface.blit(line_surface, (0, current_y))
                current_y += line_height
            return
        lines = []
        current_line = ""
        max_line_width = self.size[0] * self._resize_ratio[0] - self.left_margin*self._resize_ratio[0] - self.right_margin*self._resize_ratio[0]
        processed_text = text.replace('\r\n', '\n').replace('\r', '\n')
        paragraphs = processed_text.split('\n')
        try:
            for para in paragraphs:
                words = para.split(' ') if words_indent else list(para)
                current_line = ""
                sep = " " if words_indent else ""
                for word in words:
                    test_line = current_line + word + sep
                    if renderFont.size(test_line)[0] <= max_line_width:current_line = test_line
                    else:
                        if current_line: lines.append(current_line.rstrip())
                        current_line = word + sep
                if current_line: lines.append(current_line.rstrip())

            max_visible_lines = int((self.size[1] * self._resize_ratio[1] - self.top_margin*self._resize_ratio[1] - self.bottom_margin*self._resize_ratio[1]) / line_height)
            visible_lines = lines[:max_visible_lines]

            if not visible_lines:
                self._text_surface = pygame.Surface((1, 1), pygame.SRCALPHA); self._text_surface.fill((0,0,0,0))
                self._text_rect = self._text_surface.get_rect(topleft=(self.left_margin*self._resize_ratio[0], self.top_margin*self._resize_ratio[1]))
                return
            max_w = max(renderFont.size(line)[0] for line in visible_lines) if visible_lines else 1
            total_h = len(visible_lines) * line_height
            self._text_surface = pygame.Surface((max(1,max_w), max(1,total_h)), pygame.SRCALPHA)
            self._text_surface.fill((0,0,0,0))
            cury = 0
            for line in visible_lines:
                line_surf = renderFont.render(line, True, self._subtheme_font)
                self._text_surface.blit(line_surf, (0, cury))
                cury += line_height

            self._text_rect = self._text_surface.get_rect(topleft=(self.left_margin*self._resize_ratio[0], self.top_margin*self._resize_ratio[1]))
        
        except (pygame.error, AttributeError):
             self._text_surface = None
             self._text_rect = pygame.Rect(0,0,0,0)
             
    def _right_bake_text(self):
        if not hasattr(self, 'style'): return
        text_to_render = self._entered_text if len(self._entered_text) > 0 else self.placeholder
        if self.multiple:
            self.bake_text(text_to_render, multiline_mode=True)
            self._update_scroll_offset_y()
        else:
            self.bake_text(text_to_render, continuous=True)
        self._update_scroll_offset()
        
    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self._init_cursor()
        self._right_bake_text()
        
    @property
    def style(self):
        return self._style()
    @style.setter
    def style(self, style: Style):
        self.clear_surfaces()
        self._changed = True
        self._style = copy.deepcopy(style)
        
        self._update_image()
        self.left_margin =  10
        self.right_margin = 10
        self.top_margin = 5
        self.bottom_margin = 5
        #self._init_cursor()
        if hasattr(self,'_entered_text'):
             self._right_bake_text()
             
    def event_update(self, events: list | None = None):
        if events is None: events = []
        super().event_update(events)
        if not self.is_active:
            if self.selected:
                 self.selected = False
                 self._changed = True
            return
        prev_selected = self.selected
        mouse_collided = self.get_rect().collidepoint(mouse.pos)
        self.check_selected(mouse_collided)
        if prev_selected != self.selected and self.selected:
             self._update_scroll_offset()
             self._update_scroll_offset_y()
        elif prev_selected != self.selected and not self.selected:
             self._changed = True
        if self.selected:
            text_changed = False
            cursor_moved = False
            for event in events:
                if event.type == pygame.KEYDOWN:
                    initial_cursor_place = self._cursor_place
                    initial_text = self._entered_text
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.multiple:
                             if self.max_characters is None or len(self._entered_text) < self.max_characters:
                                self._entered_text = self._entered_text[:self._cursor_place] + '\n' + self._entered_text[self._cursor_place:]
                                self._cursor_place += 1
                    elif event.key == pygame.K_UP:
                        if self.multiple:
                            current_line, current_col = self._get_cursor_line_col()
                            if current_line > 0:
                                self._cursor_place = self._get_abs_pos_from_line_col(current_line - 1, current_col)
                    elif event.key == pygame.K_DOWN:
                         if self.multiple:
                             lines = self._entered_text.split('\n')
                             current_line, current_col = self._get_cursor_line_col()
                             if current_line < len(lines) - 1:
                                 self._cursor_place = self._get_abs_pos_from_line_col(current_line + 1, current_col)
                    elif event.key == pygame.K_RIGHT:
                        self._cursor_place = min(len(self._entered_text),self._cursor_place+1)
                        self._changed = True
                    elif event.key == pygame.K_LEFT:
                        self._cursor_place = max(0,self._cursor_place-1)
                        self._changed = True
                    elif event.key == pygame.K_BACKSPACE:
                        if self._cursor_place > 0:
                            self._entered_text = self._entered_text[:self._cursor_place-1] + self._entered_text[self._cursor_place:]
                            self._cursor_place = max(0,self._cursor_place-1)
                    elif event.key == pygame.K_DELETE:
                         if self._cursor_place < len(self._entered_text):
                              self._entered_text = self._entered_text[:self._cursor_place] + self._entered_text[self._cursor_place+1:]
                    elif event.key == pygame.K_HOME:
                         if self.multiple:
                              line_idx, _ = self._get_cursor_line_col()
                              self._cursor_place = self._get_abs_pos_from_line_col(line_idx, 0)
                         else:
                              self._cursor_place = 0
                    elif event.key == pygame.K_END:
                         if self.multiple:
                              line_idx, _ = self._get_cursor_line_col()
                              lines = self._entered_text.split('\n')
                              line_len = len(lines[line_idx]) if line_idx < len(lines) else 0
                              self._cursor_place = self._get_abs_pos_from_line_col(line_idx, line_len)
                         else:
                              self._cursor_place = len(self._entered_text)
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                        if self.allow_paste:
                            pasted_text = ""
                            try:
                                pasted_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                                if pasted_text:
                                    pasted_text = pasted_text.decode('utf-8').replace('\x00', '')
                            except (pygame.error, UnicodeDecodeError, TypeError):
                                pasted_text = ""

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
                                    self._entered_text = self._entered_text[:self._cursor_place] + filtered_text + self._entered_text[self._cursor_place:]
                                    self._cursor_place += len(filtered_text)

                    elif event.unicode:
                        unicode = event.unicode
                        is_valid_unicode = len(unicode) == 1 and ord(unicode) >= 32 and (unicode != "\x7f")
                        is_newline_ok = self.multiple or (unicode not in '\r\n')

                        if is_valid_unicode and is_newline_ok:
                            if self.max_characters is None or len(self._entered_text) < self.max_characters:
                                valid_char = True
                                if self.blacklist and unicode in self.blacklist: valid_char = False
                                if self.whitelist and unicode not in self.whitelist: valid_char = False

                                if valid_char:
                                    self._entered_text = self._entered_text[:self._cursor_place] + unicode + self._entered_text[self._cursor_place:]
                                    self._cursor_place += len(unicode)

                    if self._cursor_place != initial_cursor_place: cursor_moved = True
                    if self._entered_text != initial_text: text_changed = True
                    if text_changed or cursor_moved: self._changed = True

                elif event.type == pygame.MOUSEWHEEL:
                    if self.multiple and self.selected and mouse_collided:
                         scroll_multiplier = 3
                         line_h = 1
                         try:
                             line_h = self._get_line_height()
                         except: pass
                         scroll_amount = event.y * line_h * scroll_multiplier
                         if not hasattr(self, 'max_scroll_y'): self._update_scroll_offset_y()

                         self._text_scroll_offset_y -= scroll_amount
                         self._text_scroll_offset_y = max(0, min(self._text_scroll_offset_y, getattr(self, 'max_scroll_y', 0)))
                         self._changed = True
            if text_changed:
                 self._right_bake_text()
                 if self._on_change_fun:
                     try:
                          self._on_change_fun(self._entered_text)
                     except Exception as e:
                          print(f"Error in Input on_change_function: {e}")
            elif cursor_moved:
                 self._update_scroll_offset()
                 self._update_scroll_offset_y()
                 
    def check_selected(self, collided):
        if collided and mouse.left_fdown:
            if not self.selected:
                self.selected = True
                self._changed = True
                try:
                    renderFont = self.get_font()
                    relative_x = mouse.pos[0] - self.master_coordinates[0]
                    relative_y = mouse.pos[1] - self.master_coordinates[1]
                    l_margin = self.left_margin * self._resize_ratio[0]
                    t_margin = self.top_margin * self._resize_ratio[1]
                    if self.multiple:
                        line_height = self._get_line_height()
                        if line_height <= 0 : line_height = 1 # Prevent division by zero
                        target_line_idx_float = (relative_y - t_margin + self._text_scroll_offset_y) / line_height
                        target_line_index = max(0, int(target_line_idx_float))
                        lines = self._entered_text.split('\n')
                        target_line_index = min(target_line_index, len(lines) - 1)
                        target_x_in_full_line = relative_x - l_margin + self._text_scroll_offset
                        target_line_text = lines[target_line_index] if target_line_index < len(lines) else ""
                        best_col_index = 0
                        min_diff = float('inf')
                        current_w = 0
                        for i, char in enumerate(target_line_text):
                            char_w = renderFont.size(char)[0]
                            pos_before = current_w
                            pos_after = current_w + char_w
                            diff_before = abs(target_x_in_full_line - pos_before)
                            diff_after = abs(target_x_in_full_line - pos_after)
                            if diff_before <= min_diff:
                                min_diff = diff_before
                                best_col_index = i
                            if diff_after < min_diff:
                                    min_diff = diff_after
                                    best_col_index = i + 1
                            current_w += char_w
                        best_col_index = max(0, min(best_col_index, len(target_line_text)))
                        self._cursor_place = self._get_abs_pos_from_line_col(target_line_index, best_col_index)
                    else:
                        target_x_in_full_text = relative_x - l_margin + self._text_scroll_offset
                        best_index = 0
                        min_diff = float('inf')
                        current_w = 0
                        for i, char in enumerate(self._entered_text):
                            char_w = renderFont.size(char)[0]
                            pos_before = current_w
                            pos_after = current_w + char_w
                            diff_before = abs(target_x_in_full_text - pos_before)
                            diff_after = abs(target_x_in_full_text - pos_after)

                            if diff_before <= min_diff:
                                min_diff = diff_before
                                best_index = i
                            if diff_after < min_diff:
                                min_diff = diff_after
                                best_index = i + 1
                            current_w += char_w

                        best_index = max(0, min(best_index, len(self._entered_text)))
                        self._cursor_place = best_index

                    self._update_scroll_offset()
                    self._update_scroll_offset_y()

                except (pygame.error, AttributeError, IndexError) as e:
                    pass

        elif not collided and mouse.left_fdown:
            if self.selected:
                self.selected = False
                self._changed = True

    @property
    def text(self): return self._entered_text
    
    @text.setter
    def text(self,text: str):
        if not isinstance(text, str): 
            text = str(text)

        original_text = self._entered_text
        if not self.multiple:
            text = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

        if self.max_characters is not None:
            text = text[:self.max_characters]

        self._entered_text = text
        self._cursor_place = min(len(self._entered_text), self._cursor_place)
        self._changed = True
        self._right_bake_text()

        if self._on_change_fun and original_text != self._entered_text:
            try: self._on_change_fun(self._entered_text)
            except Exception as e: print(f"Error in Input on_change_function (setter): {e}")
            
    def secondary_draw_content(self):
        super().secondary_draw_content()
        if not self.visible: return

        if self._changed:
            try:
                renderFont = self.get_font()
                font_loaded = True
                line_height = self._get_line_height()
                cursor_height = self.cursor.get_height()
            except (pygame.error, AttributeError):
                font_loaded = False
                line_height = 15 
                cursor_height = 12 
            if not font_loaded: return
            l_margin = self.relx(self.left_margin)
            r_margin = self.relx(self.right_margin)
            t_margin = self.rely(self.top_margin)
            b_margin =  self.rely(self.bottom_margin)
            clip_rect = self.surface.get_rect()
            clip_rect.left = l_margin
            clip_rect.top = t_margin
            clip_rect.width = self.surface.get_width() - l_margin - r_margin
            clip_rect.height = self.surface.get_height() - t_margin - b_margin
            if clip_rect.width < 0: clip_rect.width = 0
            if clip_rect.height < 0: clip_rect.height = 0
            if self._text_surface:
                if self.multiple:
                    self._text_rect = self._text_surface.get_rect(topleft=(l_margin - self._text_scroll_offset, t_margin - self._text_scroll_offset_y))
                else:
                    self._text_rect = self._text_surface.get_rect(left=l_margin - self._text_scroll_offset,centery=(t_margin + self.surface.get_height() - b_margin) / 2 )
                original_clip = self.surface.get_clip()
                self.surface.set_clip(clip_rect)
                self.surface.blit(self._text_surface, self._text_rect)
                self.surface.set_clip(original_clip)
            if self.selected:
                cursor_visual_x = 0
                cursor_visual_y = 0
                try:
                    if self.multiple:
                        cursor_line, cursor_col = self._get_cursor_line_col()
                        lines = self._entered_text.split('\n')
                        line_text = lines[cursor_line] if cursor_line < len(lines) else ""
                        text_before_cursor_in_line = line_text[:cursor_col]
                        cursor_x_offset = renderFont.size(text_before_cursor_in_line)[0]
                        cursor_visual_x = l_margin + cursor_x_offset - self._text_scroll_offset
                        cursor_visual_y = t_margin + (cursor_line * line_height) - self._text_scroll_offset_y
                    else:
                        text_before_cursor = self._entered_text[:self._cursor_place]
                        cursor_x_offset = renderFont.size(text_before_cursor)[0]
                        cursor_visual_x = l_margin + cursor_x_offset - self._text_scroll_offset
                        cursor_visual_y = (self.surface.get_height() - cursor_height) / 2

                    cursor_draw_rect = self.cursor.get_rect(topleft=(cursor_visual_x, cursor_visual_y))
                    if clip_rect.colliderect(cursor_draw_rect):
                        self.surface.blit(self.cursor, cursor_draw_rect.topleft)
                except (pygame.error, AttributeError, IndexError):pass
    
    def clone(self):
        return Input(self._lazy_kwargs['size'], copy.deepcopy(self.style), copy.copy(self._default_text), copy.copy(self.placeholder), self._on_change_fun, **self.constant_kwargs)
