
import pygame

class NvVector2(pygame.Vector2):
    def __mul__(self, other): # type: ignore
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x * other.x, self.y * other.y)
        return NvVector2(super().__mul__(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __neg__(self):
        return NvVector2(-self.x, -self.y)

    def __add__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x + other.x, self.y + other.y)
        return NvVector2(super().__add__(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(self.x - other.x, self.y - other.y)
        return NvVector2(super().__sub__(other))

    def __rsub__(self, other):
        if isinstance(other, pygame.Vector2):
            return NvVector2(other.x - self.x, other.y - self.y)
        return NvVector2(super().__rsub__(other))

    def to_int(self):
        return NvVector2(int(self.x), int(self.y))

    def to_float(self):
        return NvVector2(float(self.x), float(self.y))

    def to_abs(self):
        return NvVector2(abs(self.x), abs(self.y))

    def to_neg(self):
        return NvVector2(-self.x, -self.y)

    def for_each(self, func):
        return NvVector2(func(self.x), func(self.y))
