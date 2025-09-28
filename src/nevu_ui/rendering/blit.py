import pygame
import numpy as np

class AlphaBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft, special_flags=pygame.BLEND_RGBA_MULT)

class FastBlit:
    @staticmethod
    def blit(dest_surf: pygame.Surface, source_surf: pygame.Surface, dest_pos: tuple[int, int]):
        x, y = dest_pos
        width, height = source_surf.get_size()
        roi_rect = pygame.Rect(x, y, width, height)
        roi_rect_clipped = roi_rect.clip(dest_surf.get_rect())

        if roi_rect_clipped.width == 0 or roi_rect_clipped.height == 0:
            return

        src_x_offset = roi_rect_clipped.x - roi_rect.x
        src_y_offset = roi_rect_clipped.y - roi_rect.y

        try:
            src_slice_x = slice(src_x_offset, src_x_offset + roi_rect_clipped.width)
            src_slice_y = slice(src_y_offset, src_y_offset + roi_rect_clipped.height)
            dest_slice_x = slice(roi_rect_clipped.x, roi_rect_clipped.right)
            dest_slice_y = slice(roi_rect_clipped.y, roi_rect_clipped.bottom)

            source_rgb_view = pygame.surfarray.pixels3d(source_surf)[src_slice_x, src_slice_y]
            dest_rgb_view = pygame.surfarray.pixels3d(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_rgb_view, source_rgb_view)
            
            source_alpha_view = pygame.surfarray.pixels_alpha(source_surf)[src_slice_x, src_slice_y]
            dest_alpha_view = pygame.surfarray.pixels_alpha(dest_surf)[dest_slice_x, dest_slice_y]
            np.copyto(dest_alpha_view, source_alpha_view)

        except ValueError:
            clipped_source_rect = pygame.Rect(src_x_offset, src_y_offset, roi_rect_clipped.width, roi_rect_clipped.height)
            dest_surf.blit(source_surf.subsurface(clipped_source_rect), roi_rect_clipped.topleft)