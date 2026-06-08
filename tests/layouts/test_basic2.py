import nevu_ui as ui
from nevu_ui.core import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
import pyray as rl
from raylib import rl as rla, ffi
import pygame
from nevu_ui.fast.logic.fast_logic import fast_cycle_list, fast_cycle_tuple, fast_cycle_range
from nevu_ui.fast.nvrect import NvRect
import time
pygame.init()

class BatchManager:
    def __init__(self):
        self.texture: rl.RenderTexture = None
        self.max_size = (10000, 10000)
        self._dirty = False
        self.t_coordinates: dict[int, tuple[int, int]] = {}
        self.t_texture_links: dict[int, rl.RenderTexture] = {}
        self.t_texture_rects: dict[int, NvRect] = {}
        
    def mark_dirty(self):
        self._dirty = True
        
    def register(self, texture):
        self.t_texture_links[id(texture)] = texture
        self.mark_dirty()
    
    def change(self, texture_id, new_texture):
        self.t_texture_links[texture_id] = new_texture
        rl.begin_texture_mode(self.texture)
        nevu_state.window.renderer.blit(new_texture.texture, self.t_texture_rects[texture_id])
        rl.end_texture_mode()
        
    @staticmethod
    def get_texture_size(texture: rl.Texture):
        return texture.width, texture.height  
    
    def get_texture_rect_by_id(self, texture_id):
        return self.t_texture_rects[texture_id]
    
    def _get_texture_rect_by_id_inner(self, texture_id):
        coords = self.t_coordinates[texture_id]
        tex = self.t_texture_links[texture_id].texture
        atlas_height = self.texture.texture.height
        inverted_y = atlas_height - coords[1] - tex.height
        return NvRect(coords[0], inverted_y, tex.width, -tex.height)
    
    def update(self):
        if not self._dirty: return
        self._dirty = False
        if self.texture:
            rl.unload_render_texture(self.texture)
        x, y = self.regen_coordinates()
        self.texture = rl.load_render_texture(int(x), int(y))
        rl.begin_texture_mode(self.texture)
        nevu_state.window.renderer.clear(rl.DARKBROWN)
        for texture_id, coordinates in self.t_coordinates.items():
            nevu_state.window.renderer.blit(self.t_texture_links[texture_id].texture, coordinates)
            self.t_texture_rects[texture_id] = self._get_texture_rect_by_id_inner(texture_id)
        rl.end_texture_mode()
        
    def regen_coordinates(self):
        curr_coord = NvVector2()
        max_vec = NvVector2()
        
        row_height = 0
        self.t_coordinates = {}
        
        sorted_texture_links = sorted(self.t_texture_links.items(), key=lambda x: (x[1].texture.height, x[1].texture.width), reverse=True)
        
        for name, curr_texture in sorted_texture_links:
            tex_w = curr_texture.texture.width
            tex_h = curr_texture.texture.height
            
            if curr_coord.x + tex_w > self.max_size[0]:
                curr_coord.x = 0
                curr_coord.y += row_height
                row_height = 0
            
            row_height = max(row_height, tex_h)
            
            self.t_coordinates[name] = curr_coord.get_int_tuple()
            
            max_vec.x = max(max_vec.x, curr_coord.x + tex_w)
            max_vec.y = max(max_vec.y, curr_coord.y + tex_h)
            
            curr_coord.x += tex_w
            
        return max(1, max_vec.x), max(1, max_vec.y)

class Cout:
    def2 = "def1"
    def __init__(self):
        pass

    def __rshift__(self, other):
        if other == "\n":
            print()
            return Cout()
        print(other, end = "")
        return Cout()

class Std: 
    __sluts__ = "__bob__"
    def __bob__(self):
        print('bob')
    def __init__(self):
        self.cout = Cout()
        self.endL = "\n"

std = Std()
std.cout >> "выпускай" >> "блядь" >> "быстрее" >> "новый" >> "суко" >> "версию парсера блядь" >> std.endL

if __name__ == "__main__" and False:
    import random
    window = ui.Window((300, 300), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1), backend=ui.Backend.RayLib)
    batch_manager = BatchManager()
    masiv = []
    changed = True
    colors = [rl.RED, rl.GREEN, rl.BLUE, rl.PURPLE, rl.GRAY, rl.DARKGREEN, rl.GOLD, rl.PINK, rl.LIME, rl.BEIGE]
    for i in range(200):
        size = (random.randint(100, 300), random.randint(100, 300))
        #size = (300,300)
        masiv.append(size)
        texrure = rl.load_render_texture(size[0], size[1])
        rl.begin_texture_mode(texrure)
        rl.clear_background(random.choice(colors))
        rl.end_texture_mode()
        batch_manager.register(texrure)
    
    batch_manager.update()
    print(batch_manager.t_coordinates)
    print("sizes",masiv)
    additional_y = 0
    additional_x = 0
    display = window.display
    timer = 1
    max_sec = 1
    w_rect = NvRect(0, 0, window.size.x, window.size.y)
    need_to_draw = []
    def resize_wrect(*args):
        global w_rect, changed
        w_rect = NvRect(0, 0, window.size.x, window.size.y)
        print("CCCCCCCCCHHHHHHHHHHHHHHHHHHHHHHAAAAAAAAAAAAAAAAGED")
        changed = True
    window.add_event(ui.NevuEvent(None, resize_wrect, ui.EventType.Resize))
    while True:
        window.begin_frame()
        window.display.clear(rl.WHITE)
        drawed = 0
        for idr in need_to_draw:
            text_rect = batch_manager.get_texture_rect_by_id(idr)
            #print(cor_text_rect)
            #print(NvRect(additional_x, additional_y, window.size.x, window.size.y))
            w_rect.x = -additional_x
            w_rect.y = -additional_y
            drawed += 1
            window.display.blit_rect_vec(batch_manager.texture.texture, source_rect=text_rect.get_tuple(), coordinates=(text_rect.x+additional_x, text_rect.y+additional_y))
           # rl.draw_texture_v(batch_manager.texture.texture, rl.Vector2(text_rect.x, text_rect.y), rl.WHITE) #rl.Rectangle(0, 0, text_rect.width, text_rect.height), rl.Vector2(0,0), 0, rl.WHITE)
            assert window.is_raylib(window.display)
            #window.display.blit_rect_pro(batch_manager.texture.texture, rl.Rectangle(text_rect.x+additional_x, text_rect.y+additional_y, text_rect.w, text_rect.h), source_rect=rl.Rectangle(text_rect.x, text_rect.y, text_rect.w, text_rect.h))
            pass
        
        if changed:
            changed = False
            rand_s = list(batch_manager.t_coordinates.keys())[random.randint(0, len(batch_manager.t_coordinates)-1)]
            rand_t = list(batch_manager.t_texture_links.values())[random.randint(0, len(batch_manager.t_texture_links)-1)]
            batch_manager.change(rand_s, rand_t)
            need_to_draw.clear()
            for idr in batch_manager.t_coordinates.keys():
                text_rect = batch_manager.get_texture_rect_by_id(idr)
                cor_text_rect = text_rect.xywh
                cor_text_rect.h = -cor_text_rect.h 
                #print(cor_text_rect)
                #print(NvRect(additional_x, additional_y, window.size.x, window.size.y))
                w_rect.x = -additional_x
                w_rect.y = -additional_y
                if not cor_text_rect.collide_rect(w_rect):
                    continue
                need_to_draw.append(idr)
        print("DRAWED", drawed)
        window.update(None)
        rl.draw_fps(10,10)
        oldx = additional_x
        oldy = additional_y
        if rl.is_key_up(rl.KeyboardKey.KEY_DOWN): additional_y += 1000*ui.time.dt
        if rl.is_key_up(rl.KeyboardKey.KEY_UP): additional_y -= 1000*ui.time.dt
        if rl.is_key_up(rl.KeyboardKey.KEY_RIGHT): additional_x += 1000*ui.time.dt
        if rl.is_key_up(rl.KeyboardKey.KEY_LEFT): additional_x -= 1000*ui.time.dt
        if oldx != additional_x or oldy != additional_y:
            changed = True
        window.end_frame()

if __name__ == "__main__" and False:
    window = ui.Window((300, 300), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1), backend=ui.Backend.RayLib)
    menu = ui.Menu(window, (300, 300))
    menu.layout = ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3)
    menu.layout.add_item(ui.Button(lambda: print("You clicked!"), "КНОПКА!", [50%ui.fill, 50%ui.gc], ui.Style(font_name="tests/vk_font.ttf")), 2, 2)
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
    rl.set_target_fps(75)
    while True:
        window.begin_frame()
        window.display.clear(ui.Color.White)
        print(ui.time.fps)
        menu.update()
        menu.draw()
        window.update(None, 99)
        window.end_frame()

if __name__ == "__main__" and False:
    window = ui.Window((300, 300), title="Test Window", resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1,1), backend=ui.Backend.RayLib)
    menu = ui.Menu(window, (300, 300))
    menu.layout = ui.Grid([100%ui.vw, 100%ui.vh], row=3, column=3)
    anim_manager = ui.animations.AnimationManager()
    anim_manager.add_continuous_animation(ui.AnimationType.Position, ui.animations.Vector2Animation(NvVector2(40, 0), NvVector2(-40, 0), 2, ui.animations.ease_in))
    menu.layout.add_item(ui.Label("КНОПКА!", [50%ui.fill, 50%ui.gc], ui.Style(font_name="tests/vk_font.ttf", border_radius=100, font_size=20), clickable=True, hoverable=True, animation_manager=anim_manager), 2, 2)
    rl.set_trace_log_level(rl.TraceLogLevel.LOG_WARNING)
    menu.update()
    menu.draw()
    widget: ui.Widget = menu.layout.get_item(2, 2)
    while False:
        window.begin_frame()
        window.update(None, 75)
        window.display.clear(ui.Color.White)
        menu.update()
        menu.draw()
        
        
        window.end_frame()
    else:
        def draw_nv_pro(a):
            start_func(widget.surface.render_texture)
            draw_func(widget.surface.texture, pos)
            end_func()
        def draw_nv_rec(a):
            start_func(widget.surface.render_texture)
            draw_func(widget.surface.texture, pos, True, color)
            end_func()
        fast_cycle_fun = fast_cycle_range
        draw_func = ui.fast.raylib.rl_fast_blit_rec
        start_func = ui.fast.raylib.begin_texture_mode
        end_func = ui.fast.raylib.end_texture_mode
        pos = (0, 0, 100, 100)
        pos2 = (0, 0)
        size = (100, 100, 0, 0)
        origin = (0, 0)
        color = (255, 255, 255, 255)
        rotation = 0
        time_func = lambda: time.perf_counter()
        t1 = time_func()

        fast_cycle_range(draw_nv_rec, 0, 50000, 1)
        #for i in range(50000):
        #    start_func(widget.surface.render_texture)
        #    draw_func(widget.surface.texture, pos, True, color)
        #    end_func()
        
        t2 = time_func()
        print(f"Cython rec binding: {(t2 - t1) * 1000:.2f}ms")
        draw_func = rl.draw_texture_pro
        start_func = rl.begin_texture_mode
        end_func = rl.end_texture_mode
        t3 = time_func()
        for i in range(50000):
            start_func(widget.surface.render_texture)
            draw_func(widget.surface.texture, pos, size, origin, rotation, color)
            end_func()
        t4 = time_func()
        print(f"Pyray pro binding: {(t4 - t3) * 1000:.2f}ms")
        display = nevu_state.window.renderer
        assert nevu_state.window.is_raylib(display)
        draw_func = rl.draw_texture_rec
        start_func = rl.begin_texture_mode
        end_func = rl.end_texture_mode
        t5 = time_func()
        for i in range(50000):
            start_func(widget.surface.render_texture)
            draw_func(widget.surface.texture, size, pos2, color)
            end_func()
        t6 = time_func()
        print(f"Pyray rec binding: {(t6 - t5) * 1000:.2f}ms")
        
        draw_func = ui.fast.raylib.rl_fast_blit_pro
        start_func = ui.fast.raylib.begin_texture_mode
        end_func = ui.fast.raylib.end_texture_mode
        
 
        t7 = time_func()
        fast_cycle_range(draw_nv_pro, 0, 50000, 1)
        #for i in range(50000):
        #    start_func(widget.surface.render_texture)
        #    draw_func(widget.surface.texture, pos)
        #    end_func()
        t8 = time_func()
        print(f"Cython pro binding: {(t8 - t7) * 1000:.2f}ms")

if __name__ == "__main__" and False:
    window = ui.Window((300, 300), backend=ui.Backend.RayLib)
    time_func = lambda: time.perf_counter()
    
    texture = rl.load_render_texture(100, 100)
    texture_bg = rl.load_render_texture(100, 100)
    nv_texture = ui.NvRenderTexture(ui.NvVector2(100, 100))
    nv_texture_bg = ui.NvRenderTexture(ui.NvVector2(100, 100))
    TEST_NUM = 5000
    
    state1 = (0, 0, 100, 100)
    state2 = (0, 0)
    state3 = (255, 255, 255, 255)
    
    t1 = time_func()
    rl.begin_texture_mode(texture_bg)
    for i in range(TEST_NUM):    
        rl.draw_texture_rec(texture.texture, state1, state2, state3)
    rl.end_texture_mode()
    t2 = time_func()
    print(f"python: {(t2 - t1) * 1000:.2f}ms")
    display = ui.nevu_state.window.renderer
    assert window.is_raylib(display)
    blit_func = display.fast_blit
    #ui.fast.logic.fast_logic.fast_cycle_range(blit_func, 0, TEST_NUM, 1)
    t3 = time_func()
    rl.begin_texture_mode(nv_texture_bg.render_texture)
    for i in range(TEST_NUM):    
        nv_texture_bg.fast_blit(nv_texture, (0,0))
    rl.end_texture_mode()
    t4 = time_func()
    print(f"cython: {(t4 - t3) * 1000:.2f}ms")
    exit(0)


if __name__ == "__main__":
    time_func = lambda: time.perf_counter()
    from nevu_ui.fast.nvvector2 import NvVector2
    
    vec1 = NvVector2(0.0, 0.0)
    
    TEST_NUM = 500000
    t1 = time_func()
    for i in range(TEST_NUM):
        NvVector2(0.0, 0.0)
    t2 = time_func()
    print(f"cython: {(t2 - t1) * 1000:.2f}ms")
    t3 = time_func()
    for i in range(TEST_NUM):
        NvVector2.from_xy(0.0, 0.0)
    t4 = time_func()
    print(f"cython: {(t4 - t3) * 1000:.2f}ms")