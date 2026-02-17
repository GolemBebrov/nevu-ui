import nevu_ui as ui
from nevu_ui.core import nevu_state
from nevu_ui.fast.nvvector2 import NvVector2
import pyray as rl
import pygame
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
        nevu_state.window.display.blit(new_texture.texture, self.t_texture_rects[texture_id])
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
        nevu_state.window.display.clear(rl.DARKBROWN)
        for texture_id, coordinates in self.t_coordinates.items():
            nevu_state.window.display.blit(self.t_texture_links[texture_id].texture, coordinates)
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

if __name__ == "__main__":
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