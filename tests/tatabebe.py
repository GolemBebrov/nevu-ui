import pygame
import sys
import os

# --- Константы ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60
IMAGE_PATH = os.path.join('tests', 'test1.png')

# --- Цвета ---
WHITE = (255, 255, 255)
GREY = (40, 40, 40)

# --- Класс для вращающегося объекта ---
class RotatingObject(pygame.sprite.Sprite):
    """
    Класс для спрайта.
    Метод 'correct_rotate' показывает правильный подход с rotate.
    Метод 'bad_rotozoom' показывает неправильный подход с rotozoom.
    """
    def __init__(self, image, pos_center, method):
        super().__init__()
        self.method = method
        
        # Храним оригинал для "правильного" метода
        self.original_image = image
        # Текущее изображение, которое будет меняться
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=pos_center)

        self.angle = 0
        self.rotation_speed = 2.0

    def update(self):
        old_center = self.rect.center

        if self.method == 'correct_rotate':
            # --- ПРАВИЛЬНЫЙ ПОДХОД (с 'плохим' инструментом) ---
            # Угол постоянно меняется...
            self.angle = (self.angle + self.rotation_speed) % 360
            # ...но для поворота всегда используется ЧИСТЫЙ ОРИГИНАЛ.
            # Качество стабильно, но сглаживания нет.
            self.image = pygame.transform.rotate(self.original_image, self.angle)

        elif self.method == 'bad_rotozoom':
            # --- НЕПРАВИЛЬНЫЙ ПОДХОД (с 'хорошим' инструментом) ---
            # Мы берем УЖЕ повернутое изображение и снова его поворачиваем.
            # Даже сглаживание rotozoom не спасает от накопления ошибок
            # и постепенного размытия картинки.
            self.image = pygame.transform.rotozoom(self.image, self.rotation_speed, 1)
        
        # Восстанавливаем центр, чтобы избежать "прыжков"
        self.rect = self.image.get_rect(center=old_center)

# --- Вспомогательные функции ---
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

# --- Инициализация и загрузка ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Правильный подход важнее инструмента!")
clock = pygame.time.Clock()

try:
    source_image = pygame.image.load(IMAGE_PATH).convert_alpha()
    source_image = pygame.transform.scale(source_image, (200, 140))
except pygame.error:
    print(f"Ошибка: Не удалось загрузить изображение '{IMAGE_PATH}'")
    sys.exit()

# --- Создание объектов ---
all_sprites = pygame.sprite.Group()

# Левый объект: ПРАВИЛЬНОЕ использование rotate
correct_approach = RotatingObject(
    image=source_image,
    pos_center=(SCREEN_WIDTH * 0.25, SCREEN_HEIGHT / 2),
    method='correct_rotate'
)

# Правый объект: НЕПРАВИЛЬНОЕ использование rotozoom

all_sprites.add(correct_approach)

# --- Основной цикл ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    screen.fill(GREY)

    # Подписи
    draw_text(screen, "ПРАВИЛЬНО: rotate(оригинал)", 38, SCREEN_WIDTH * 0.25, 100, WHITE)
    draw_text(screen, "Стабильно, но края 'зубчатые'", 28, SCREEN_WIDTH * 0.25, 140, WHITE)

    draw_text(screen, "НЕПРАВИЛЬНО: rotozoom(уже_повернутое)", 38, SCREEN_WIDTH * 0.75, 100, WHITE)
    draw_text(screen, "Качество постепенно размывается", 28, SCREEN_WIDTH * 0.75, 140, WHITE)

    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()