import pygame
import copy

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils import mouse
from nevu_ui.layouts import LayoutType

from nevu_ui.style import (
    Style, default_style
)

# Warning: Semi-legacy class

class Pages(LayoutType):
    def __init__(self, size: list | NvVector2, style: Style = default_style, content: list | None = None, **constant_kwargs):
        super().__init__(size, style, content, **constant_kwargs)
        self.selected_page = None
        self.selected_page_id = 0
    def _lazy_init(self, size: NvVector2 | list, content: list | None = None):
        super()._lazy_init(size, content)
        if content:
            for item in content:
                self.add_item(item)
    def add_item(self, item: LayoutType): # type: ignore
        if self.is_widget(item): raise ValueError("Widget must be Layout")
        super().add_item(item)
        if self.layout: self.layout._event_on_add_item()
        if not self.selected_page:
            self.selected_page = item
            self.selected_page_id = 0
    def secondary_draw(self):
        super().secondary_draw()
        assert self.surface
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(10),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(40),self.coordinates[1]+self.rely(20)],2)
        pygame.draw.line(self.surface,(0,0,0),[self.coordinates[0]+self.relx(10),self.coordinates[1]+self.rely(20)],[self.coordinates[0]+self.relx(20),self.coordinates[1]+self.rely(40)],2)
        
        self.items[self.selected_page_id].draw()
        for i in range(len(self.items)):
            if i != self.selected_page_id: pygame.draw.circle(self.surface,(0,0,0),[self.coordinates[0]+self.relx(20+i*20),self.coordinates[1]+self.rely(self.size[1]-10)],self.relm(5))
            else: pygame.draw.circle(self.surface,(255,0,0),[self.coordinates[0]+self.relx(20+i*20),self.coordinates[1]+self.rely(self.size[1]-10)],self.relm(5))
    def move_by_point(self, point: int):
        self.selected_page_id += point
        if self.selected_page_id < 0: self.selected_page_id = len(self.items)-1
        self.selected_page = self.items[self.selected_page_id]
        if self.selected_page_id >= len(self.items): self.selected_page_id = 0
        self.selected_page = self.items[self.selected_page_id]
    def get_left_rect(self):
        return pygame.Rect(self.coordinates[0]+(self.first_parent_menu.coordinatesMW[0]),self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],
                            self.relx(self.size[0]/10),self.rely(self.size[1]))
    def get_right_rect(self):
        return pygame.Rect(self.coordinates[0]+self.relx(self.size[0]-self.size[0]/10)+self.first_parent_menu.coordinatesMW[0],self.coordinates[1]+self.first_parent_menu.coordinatesMW[1],
                            self.relx(self.size[0]/10),self.rely(self.size[1]))
    def secondary_update(self, *args):
        super().secondary_update()
        if mouse.left_fdown:
            rectleft = self.get_left_rect()
            rectright = self.get_right_rect()
            if rectleft.collidepoint(mouse.pos): self.move_by_point(-1)
            if rectright.collidepoint(mouse.pos): self.move_by_point(1)
        selected_page = self.items[self.selected_page_id]
        assert isinstance(selected_page, LayoutType)
        selected_page.coordinates = [self.coordinates[0]+self.relx(self.size[0]/2-self.items[self.selected_page_id].size[0]/2),
                                    self.coordinates[1]+self.rely(self.size[1]/2-self.items[self.selected_page_id].size[1]/2),]
        selected_page.first_parent_menu = self.first_parent_menu
        if not selected_page.booted: selected_page._boot_up()
        selected_page.update()
        
    def get_selected(self): return self.items[self.selected_page_id]
    
    def clone(self):
        return Pages(self._lazy_kwargs['size'], copy.deepcopy(self.style), self._lazy_kwargs['content'], **self.constant_kwargs)
