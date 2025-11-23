import pygame
import moderngl
import numpy
import nevu_ui as ui
import nevu_ui.window as window
pygame.init()

screen_width = 800
screen_height = 600

screen = ui.Window((screen_width, screen_height), resizable = True, open_gl_mode=True, ratio=ui.NvVector2(1, 1))

ctx = screen.display.renderer

import freetype
import moderngl
import numpy

class Font:
    def __init__(self, ctx: moderngl.Context, font_path: str, font_size: int):
        self.ctx = ctx
        self.font_path = font_path
        self.font_size = font_size
        self.char_data = {}
        self.atlas_texture = self._create_atlas()
        self.program = self._create_shader()
        
        self.vbo = self.ctx.buffer(reserve=1024 * 1024)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '4f', 'in_vertex')],
        )
    
    def _create_shader(self):
        return self.ctx.program(
            vertex_shader='''
                #version 330
                in vec4 in_vertex;
                out vec2 v_text;
                uniform vec2 u_resolution;
                void main() {
                    vec2 pos = in_vertex.xy;
                    vec2 ndc = pos / u_resolution * 2.0 - 1.0;
                    gl_Position = vec4(ndc.x, -ndc.y, 0.0, 1.0);
                    v_text = in_vertex.zw;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec2 v_text;
                out vec4 f_color;
                uniform sampler2D u_texture;
                uniform vec4 u_color;
                void main() {
                    float alpha = texture(u_texture, v_text).r;
                    f_color = vec4(u_color.rgb, u_color.a * alpha);
                }
            '''
        )

    def _create_atlas(self):
        face = freetype.Face(self.font_path)
        face.set_pixel_sizes(0, self.font_size)
        
        atlas_size = (1024, 1024)
        atlas_texture = self.ctx.texture(atlas_size, 1, dtype='f1')
        atlas_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        pen_x, pen_y = 0, 0
        max_row_height = 0

        for char_code in range(32, 127):
            char = chr(char_code)
            face.load_char(char, freetype.FT_LOAD_RENDER)
            bitmap = face.glyph.bitmap

            if pen_x + bitmap.width > atlas_size[0]:
                pen_x = 0
                pen_y += max_row_height
                max_row_height = 0

            if bitmap.buffer:
                atlas_texture.write(
                    bytes(bitmap.buffer),
                    viewport=(pen_x, pen_y, bitmap.width, bitmap.rows)
                )

            self.char_data[char] = {
                'atlas_x0': pen_x / atlas_size[0],
                'atlas_y0': pen_y / atlas_size[1],
                'atlas_x1': (pen_x + bitmap.width) / atlas_size[0],
                'atlas_y1': (pen_y + bitmap.rows) / atlas_size[1],
                'width': bitmap.width,
                'height': bitmap.rows,
                'bearing_x': face.glyph.bitmap_left,
                'bearing_y': face.glyph.bitmap_top,
                'advance': face.glyph.advance.x >> 6,
            }

            pen_x += bitmap.width + 1
            max_row_height = max(max_row_height, bitmap.rows)
        
        return atlas_texture

    def render(self, text: str, pos: tuple[int, int], rgba_color: tuple[int, int, int, int], viewport_size: tuple[int, int]):
        vertices = []
        pen_x, pen_y = pos
        
        for char in text:
            if char not in self.char_data:
                continue

            data = self.char_data[char]
            
            x0 = pen_x + data['bearing_x']
            y0 = pen_y - (data['height'] - data['bearing_y'])
            x1 = x0 + data['width']
            y1 = y0 + data['height']

            u0 = data['atlas_x0']
            v0 = data['atlas_y0']
            u1 = data['atlas_x1']
            v1 = data['atlas_y1']
            
            vertices.extend([
                x0, y0, u0, v0,
                x1, y0, u1, v0,
                x0, y1, u0, v1,
                
                x1, y0, u1, v0,
                x1, y1, u1, v1,
                x0, y1, u0, v1,
            ])
            
            pen_x += data['advance']

        if not vertices:
            return

        vertex_data = numpy.array(vertices, dtype='f4')
        self.vbo.write(vertex_data)

        norm_color = (
            rgba_color[0] / 255.0, 
            rgba_color[1] / 255.0, 
            rgba_color[2] / 255.0, 
            rgba_color[3] / 255.0
        )
        self.program['u_resolution'].value = viewport_size
        self.program['u_color'].value = norm_color
        
        self.atlas_texture.use(0)
        
        self.vao.render(moderngl.TRIANGLES, vertices=len(vertex_data) // 4)

def surface_to_texture(surface: pygame.Surface):
    texture_data = pygame.image.tobytes(surface, 'RGB', True)
    texture = ctx.texture(surface.get_size(), 3, texture_data)
    return texture

image = pygame.Surface((100, 100))
image.fill((255, 0, 0))
pygame.draw.rect(image, (0, 255, 0), (25, 25, 50, 50))

tex1 = ui.NevuSurface.from_texture(surface_to_texture(image), image.get_size())
texture = ui.NevuSurface(image.get_size())
texture.use()
texture.clear()
texture.blit(tex1, (0,0))
texture.use_texture(0)
ctx.screen.use()
ctx: moderngl.Context
running = True
display: window.display.DisplayGL = screen.display
fps_counter = 0
#screen.add_event(ui.NevuEvent(ctx,))
while running:
    events = pygame.event.get()
    screen.update(events, 999999)
    
    display.clear((0, 0.5, 1, 1))
    ctx.enable(moderngl.BLEND)
    display.blit(texture, (*screen.offset.to_tuple(), *(screen.size - screen.offset*2)))
    if fps_counter % 60 == 0:
        print(ui.time.fps)
        fps_counter = 0
    fps_counter += 1
    #blit(100, 100, 200, 200)
    #blit(400, 300, 150, 150, 0.25, 0.25, 0.5, 0.5)

    display.update()

pygame.quit()