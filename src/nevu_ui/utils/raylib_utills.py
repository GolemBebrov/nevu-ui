import pyray as rl

def load_image_texture(path: str, manipulation_func = None) -> rl.Texture:
    image = rl.load_image(path)
    if manipulation_func:
        manipulation_func(image)
    texture = rl.load_texture_from_image(image)
    rl.unload_image(image)
    return texture

def load_image(path: str, manipulation_func = None) -> rl.Image:
    image = rl.load_image(path)
    if manipulation_func:
        manipulation_func(image)
    return image

def blit_sdf(self, source, dest: rl.Rectangle | tuple[int, int], flip = True):