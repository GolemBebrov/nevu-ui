from nevu_ui import NevuObject
import nevu_ui as ui
import time
a1 = NevuObject((2,2), ui.default_style)
tries = 1000000

t1 = time.time()
for i in range(tries):
    a1.get_rect()
t2 = time.time()
print(t2-t1)
t3 = time.time()
for i in range(tries):
    a1.get_nvrect()
t4 = time.time()
print(t4-t3)
t5 = time.time()
for i in range(tries):
    a1.get_rect_static()
t6 = time.time()
print(t6-t5)
print("total time:", t6-t1)

print(f"ситон вариант быстрее pygame в {((t2-t1)/(t4-t3))} раз")
print(f"ситон вариант быстрее tuple в {((t6-t4)/(t4-t3))} раз")