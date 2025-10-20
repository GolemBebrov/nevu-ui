import sdl2
import sdl2.ext
import pygame
import time
import sys
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


def fine_render(font: pygame.font.Font, text, x, y, color):
    text_surface_orig = font.render(text, True, color)
    text_surface_orig.set_colorkey((0, 0, 0))
    
    text_surface = pygame.Surface(text_surface_orig.get_size(), flags=pygame.SRCALPHA)
    text_surface.blit(text_surface_orig, (0, 0))
    text_rect = text_surface.get_rect(center=(x, y))
    return text_surface

def run_test():
    sdl2.ext.init()
    pygame.init()

    window = sdl2.ext.Window(
        "Тест NevuSurface",
        size=(WINDOW_WIDTH, HEIGHT),
        flags=sdl2.SDL_WINDOW_SHOWN|sdl2.SDL_WINDOW_RESIZABLE
    )

    pygame.display.set_mode((1, 1), pygame.NOFRAME | pygame.HIDDEN)
    print("Создано служебное невидимое окно для Pygame.")

    renderer = sdl2.SDL_CreateRenderer(
        window.window, -1, sdl2.SDL_RENDERER_ACCELERATED
    )
    if not renderer:
        raise RuntimeError(f"Не удалось создать рендерер: {sdl2.SDL_GetError().decode()}")

    print("Внедрение рендерера SDL2 в nevu_state...")
    ui.state.nevu_state.renderer = renderer
    print("Рендерер успешно установлен.")

    main_canvas = ui.NevuSurface((WINDOW_WIDTH, HEIGHT))
    
    pygame_surf_red = pygame.Surface((150, 100), flags=pygame.SRCALPHA)
    pygame_surf_red.fill((255, 0, 0, 255))
    nevu_surf_from_pygame = ui.NevuSurface.from_surface(pygame_surf_red)
    
    font = pygame.font.SysFont("Arial", 64)
    text_surface_pygame = fine_render(font, "Тест из Pygame", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, (255, 255, 255))

    nevu_text = ui.NevuSurface.from_surface(text_surface_pygame)

    running = True
    last_time = time.time()
    frame_count = 0

    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        if not running:
            break
        
        main_canvas.fill((10, 20, 40))
        main_canvas.blit(nevu_surf_from_pygame, (50, 50))
        main_canvas.blit(nevu_text, (50, 250))

        sdl2.SDL_RenderClear(renderer)
        sdl2.SDL_RenderCopy(renderer, main_canvas._texture, None, None)
        sdl2.SDL_RenderPresent(renderer)

        frame_count += 1
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count
            print(f"Тест NevuSurface | FPS: {fps}")
            frame_count = 0
            last_time = current_time

    print("Завершение работы и освобождение ресурсов...")
    main_canvas.destroy()
    nevu_surf_from_pygame.destroy()
    nevu_text.destroy()
    
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(window.window)
    pygame.quit()
    sdl2.ext.quit()
    print("Тест завершен.")


if __name__ == "__main__":
    import nevu_ui as ui
    WINDOW_WIDTH, HEIGHT = 800, 600
    run_test()