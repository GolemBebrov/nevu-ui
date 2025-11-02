import moderngl as gl
import pygame
import sys
import nevu_ui as ui
from PIL import Image

# --- Инициализация Pygame и вашего UI Framework ---
pygame.init()
window = ui.Window((600, 600), open_gl_mode=True, resize_type=ui.ResizeType.CropToRatio, ratio=ui.NvVector2(1, 1))

# Получаем контекст для удобства, но для рендеринга будем использовать API
ctx = window.display.renderer
assert isinstance(ctx, gl.Context)


def load_texture_from_file(path: str) -> ui.NevuSurface:
    """Загружает изображение из файла и возвращает готовую NevuSurface."""
    try:
        img = Image.open(path).convert('RGBA')
        # Правильно переворачиваем для ModernGL
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img_data = img.tobytes()

        # 1. Создаем исходную поверхность из данных файла
        source_texture = ui.NevuSurface.from_data(img_data, img.size)
        
        return source_texture
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {path}")
        # Возвращаем пустую поверхность, чтобы избежать падения
        return ui.NevuSurface((1, 1))


def create_rounded_surface(source_surface: ui.NevuSurface, radius: float) -> ui.NevuSurface:
    """
    Применяет SDF скругление к исходной поверхности и возвращает новую.
    """
    rounded_surface = ui.NevuSurface(source_surface.size)
    
    rounded_surface.clear(color=(0.0, 0.0, 0.0, 0.0))

    rounded_surface.blit_sdf(source_surface, ui.NvVector2(0, 0), radius=radius)
    
    return rounded_surface

if __name__ == "__main__":
    original_surf = load_texture_from_file("tests/test1.png")
    rounded_surf = create_rounded_surface(ui.NevuSurface((100, 300)), radius=0.5) 

    running = True
    while running:
        window.update(pygame.event.get(), 999999)

        ctx.screen.use()

        ctx.clear(1.0, 1.0, 1.0)
        window.display.blit(original_surf, (50, 50))

        #window.display.blit(rounded_surf, (50, 50))
        pygame.display.flip()

    pygame.quit()
    sys.exit()
