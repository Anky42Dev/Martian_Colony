# worlds/grid.py
import pygame


class Grid:
    def __init__(self, width, height, cell_size, shop_width):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.shop_width = shop_width

        self.cols = (self.width - self.shop_width) // self.cell_size
        self.rows = self.height // self.cell_size

        self.hover_cell = (0, 0)

    def update_hover(self, mouse_pos):
        mx, my = mouse_pos
        self.hover_cell = (mx // self.cell_size, my // self.cell_size)

    def draw(self, screen):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # вертикальные линии
        for x in range(self.cols + 1):
            px = x * self.cell_size
            pygame.draw.line(surf, (255, 255, 255, 40), (px, 0), (px, self.height), 1)

        # горизонтальные линии только по полю слева
        for y in range(self.rows + 1):
            py = y * self.cell_size
            pygame.draw.line(surf, (255, 255, 255, 40), (0, py), (self.width - self.shop_width, py), 1)

        screen.blit(surf, (0, 0))

    def draw_hover(self, screen, can_place):
        gx, gy = self.hover_cell
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return

        px = gx * self.cell_size
        py = gy * self.cell_size
        color = (60, 220, 120) if can_place else (220, 80, 80)

        s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        s.fill((*color, 80))
        screen.blit(s, (px, py))
        pygame.draw.rect(screen, color, (px, py, self.cell_size, self.cell_size), 2)
