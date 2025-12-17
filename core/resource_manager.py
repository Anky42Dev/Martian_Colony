# core/resource_manager.py
import os
import pygame


class ResourceManager:
    def __init__(self, balance, icons_folder="assets/icons"):
        self.balance = balance
        self.icons_folder = icons_folder

        # ресурсы: id -> value
        self.values = {}
        # видимость и порядок
        self.ordered_resources = []
        # иконки: id -> Surface
        self.icons = {}

        self._init_from_balance()

    def _init_from_balance(self):
        resources_cfg = self.balance.get("resources", [])
        for res in resources_cfg:
            rid = res["id"]
            self.values[rid] = res.get("initial", 0)
            if res.get("visible", True):
                self.ordered_resources.append(rid)

            icon_name = res.get("icon")
            if icon_name:
                path = os.path.join(self.icons_folder, icon_name)
            else:
                path = None
            self.icons[rid] = self._load_icon(path)

    def _load_icon(self, path):
        try:
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (32, 32))
        except Exception as e:
            print("Ошибка загрузки иконки ресурса:", path, e)
        # заглушка
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.fill((200, 200, 200, 180))
        pygame.draw.line(surf, (255, 0, 0), (0, 0), (31, 31), 2)
        pygame.draw.line(surf, (255, 0, 0), (31, 0), (0, 31), 2)
        return surf

    # ---------- работа с ресурсами ----------

    def get(self, rid):
        return self.values.get(rid, 0)

    def set(self, rid, value):
        self.values[rid] = value

    def add(self, rid, delta):
        self.values[rid] = self.values.get(rid, 0) + delta

    def add_many(self, changes: dict):
        for rid, delta in changes.items():
            self.add(rid, delta)

    def can_afford_cost(self, cost: dict) -> bool:
        for rid, needed in cost.items():
            if self.get(rid) < needed:
                return False
        return True

    def pay_cost(self, cost: dict) -> bool:
        if not self.can_afford_cost(cost):
            return False
        for rid, needed in cost.items():
            self.add(rid, -needed)
        return True

    # ---------- отрисовка ресурсов ----------

    def draw_top_center(self, screen, font, width):
        center_x = width // 2
        y = 10

        pieces = []
        total_width = 0

        for rid in self.ordered_resources:
            icon = self.icons[rid]
            value = int(self.get(rid))
            txt = font.render(str(value), True, (255, 255, 255))
            w = icon.get_width() + 6 + txt.get_width() + 20
            pieces.append((icon, txt, w))
            total_width += w

        x = center_x - total_width // 2
        for icon, txt, w in pieces:
            screen.blit(icon, (x, y))
            screen.blit(txt, (x + icon.get_width() + 6, y + (icon.get_height() - txt.get_height()) // 2))
            x += w
