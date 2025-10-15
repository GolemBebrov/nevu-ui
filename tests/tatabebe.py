
a = input()
lena = len(a)
assert lena >= 3, "нето !!!!!!!!!!!!"
if lena % 3 == 0:
    a = a[::-1] 
    print(a)
else:
    print(a[:3])