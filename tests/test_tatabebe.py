import pygame
from nevu_ui import fast_nvvector2 # Замените на имя вашего модуля
import timeit
NvVector2 = fast_nvvector2.NvVector2
# Настройки теста
NUM_VECTORS = 10000
NUM_ITERATIONS = 1000

# --- Тест для NvVector2 ---
nv_vectors = [NvVector2(i, i) for i in range(NUM_VECTORS)]
nv_add_vector = NvVector2(1.5, -2.5)

def test_nvvector():
    for v in nv_vectors:
        v += nv_add_vector

nv_time = timeit.timeit(test_nvvector, number=NUM_ITERATIONS)
print(f"NvVector2 time: {nv_time:.6f} seconds")


# --- Тест для pygame.Vector2 ---
pg_vectors = [pygame.Vector2(i, i) for i in range(NUM_VECTORS)]
pg_add_vector = pygame.Vector2(1.5, -2.5)

def test_pgvector():
    for v in pg_vectors:
        v += pg_add_vector

pg_time = timeit.timeit(test_pgvector, number=NUM_ITERATIONS)
print(f"pygame.Vector2 time: {pg_time:.6f} seconds")

# --- Сравнение ---
if nv_time < pg_time:
    print(f"\nNvVector2 быстрее в {pg_time / nv_time:.2f} раз")
else:
    print(f"\npygame.Vector2 быстрее в {nv_time / pg_time:.2f} раз")