import pygame
import math

from nevu_ui.utils import mouse, time
from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.widgets import Widget, Label

from nevu_ui.style import (
    Style, default_style
)

class MusicPlayer(Widget):
    def __init__(self, size, music_path, style: Style = default_style):
        super().__init__(size, style)
        pygame.mixer.init()
        self.music_path = music_path
        self.sound = pygame.mixer.Sound(music_path) 
        self.music_length = self.sound.get_length() * 1000 
        self.channel = None 
        self.start_time = 0 
        self.progress = 0
        self.side_button_size = self.size[1] / 4
        self.progress_bar_height = self.size[1] / 4
        self.cross_image = self.draw_cross()
        self.circle_image = self.draw_circle()
        self.button_image = self.circle_image
        self.button_rect = self.button_image.get_rect(center=(self.side_button_size / 2, self.side_button_size / 2))
        self.time_label = Label((size[0] - self.side_button_size * 2, 20),
                              f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}",
                              style(fontsize=12, bordercolor=(2,2,2), bgcolor=Color_Type.TRANSPARENT))
        self.is_playing = False
        self.sinus_margin = 0

    def resize(self, resize_ratio: NvVector2):
        super().resize(resize_ratio)
        self.time_label.resize(resize_ratio)
        
    def draw_sinusoid(self,size,frequency,margin):
        self.sinus_surf = pygame.Surface(size,pygame.SRCALPHA)
        self.sinus_surf.fill((0,0,0,0))
        for i in range(int(size[0])):
            y = abs(int(size[1] * math.sin(frequency * i+margin))) 
            y = size[1]-y
            print(y)
            pygame.draw.line(self.sinus_surf,(50,50,200),(i,size[1]),(i,y))
            
    def update(self, *args):
        super().update()
        if self.is_playing:
            self.sinus_margin+=1*time.delta_time
        if self.sinus_margin >= 100:
            self.sinus_margin = 0
        self.time_label.coordinates = [(self.size[0] / 2 - self.time_label.size[0] / 2) * self._resize_ratio[0],(self.size[1] - self.time_label.size[1]) * self._resize_ratio[1]]
        if mouse.left_fdown:
            if pygame.Rect([self.master_coordinates[0], self.master_coordinates[1]],[self.side_button_size, self.side_button_size]).collidepoint(mouse.pos):
                self.toggle_play()

        if self.is_playing:
            self.progress = pygame.time.get_ticks() - self.start_time
            if self.progress >= self.music_length:
                self.stop()
            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
            self.button_image = self.cross_image 
        else:
            self.button_image = self.circle_image
            if self.progress >= self.music_length:
                self.progress = 0

            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
    def format_time(self, milliseconds):
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"
    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
    def play(self):
            self.channel = self.sound.play(0)
            if self.channel is not None:
                self.start_time = self.progress 
                self.is_playing = True
            else:
                print("Error: Could not obtain a channel to play the sound. Jopa also")
    def pause(self):
        if self.is_playing:
            if self.channel:
                self.channel.pause()
            self.is_playing = False
    def stop(self):
        if self.channel:
            self.channel.stop()
        self.is_playing = False
        self.progress = 0
    def draw_cross(self):
        cross_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, (255, 255, 255), (5, 5), (self.side_button_size - 5, self.side_button_size - 5), 3)
        pygame.draw.line(cross_surface, (255, 255, 255), (self.side_button_size - 5, 5), (5, self.side_button_size - 5), 3)
        return cross_surface

    def draw_circle(self):
        circle_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255), (self.side_button_size // 2, self.side_button_size // 2),self.side_button_size // 2 - 5)
        return circle_surface

    def draw(self):
        super().draw()
        self.surface.blit(self.button_image, self.button_rect)
        progress_width = (self.size[0] / 1.2 * (self.progress / self.music_length)) * self._resize_ratio[0] if self.music_length > 0 else 0
        pygame.draw.rect(self.surface, (10, 10, 10),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1],
                          self.size[0] / 1.2 * self._resize_ratio[0],
                          self.progress_bar_height * self._resize_ratio[1]), 0, self.style.radius)
        self.draw_sinusoid([progress_width,self.size[1]/17*self._resize_ratio[1]],0.15,self.sinus_margin)
        self.surface.blit(self.sinus_surf,((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],(self.size[1] / 2 - self.sinus_surf.get_height()-self.progress_bar_height / 2) * self._resize_ratio[1]))
        pygame.draw.rect(self.surface, (50, 50, 200),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1], progress_width,
                          self.progress_bar_height * self._resize_ratio[1]), 0, -1,0,0,self.style.radius,self.style.radius)

        self.time_label.draw()
        self.surface.blit(self.time_label.surface, self.time_label.coordinates)
