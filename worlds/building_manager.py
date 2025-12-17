# worlds/building_manager.py
import os
import pygame

from worlds.building import Building


class BuildingManager:
    def __init__(self, balance, cell_size, buildings_folder="assets/buildings"):
        self.balance = balance
        self.cell_size = cell_size
        self.buildings_folder = buildings_folder

        # список Building
        self.buildings = []
        # спрайты: type -> Surface
        self.sprites = {}

        self._load_sprites()

    def _load_sprites(self):
        buildings_cfg = self.balance.get("buildings", {})
        for btype, cfg in buildings_cfg.items():
            sprite_name = cfg.get("sprite")
            path = os.path.join(self.buildings_folder, sprite_name) if sprite_name else None
            self.sprites[btype] = self._load_sprite(path)

    def _load_sprite(self, path):
        try:
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.cell_size, self.cell_size))
        except Exception as e:
            print("Ошибка загрузки спрайта здания:", path, e)
        surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        surf.fill((120, 120, 120, 255))
        return surf

    # ---------- добавление / размещение ----------

    def can_place(self, gx, gy, grid_cols, grid_rows):
        if gx < 0 or gy < 0 or gx >= grid_cols or gy >= grid_rows:
            return False
        for b in self.buildings:
            if b.grid_x == gx and b.grid_y == gy:
                return False
        return True

    def place_building(self, gx, gy, btype):
        b = Building(btype, gx, gy, level=1)
        self.buildings.append(b)
        return b

    # ---------- апгрейды ----------

    def get_upgrade_cost(self, building):
        up_cfg = self.balance["upgrade"]
        base_cost = up_cfg["base_cost"]           # dict
        growth = up_cfg["cost_growth"]
        lvl = building.level
        # умножаем base_cost на growth^(lvl-1)
        scaled_cost = {}
        factor = growth ** (lvl - 1)
        for rid, base in base_cost.items():
            scaled_cost[rid] = int(base * factor)
        return scaled_cost

    def upgrade_building(self, building):
        building.level += 1

    # ---------- производство ----------

    def produce_all(self, resource_manager):
        for b in self.buildings:
            self._produce_from_building(b, resource_manager)

    def _produce_from_building(self, building, resource_manager):
        cfg = self.balance["buildings"].get(building.type)
        if not cfg:
            return

        prod = cfg.get("production", {})
        cons = cfg.get("consumption", {})
        mult = cfg.get("level_multiplier", 1.0)

        # вычисляем множитель уровня
        if building.level > 1:
            level_factor = mult ** (building.level - 1)
        else:
            level_factor = 1.0

        # проверка, хватает ли ресурсов на потребление
        scaled_cons = {}
        for rid, amount in cons.items():
            scaled_cons[rid] = amount * level_factor
        if not resource_manager.can_afford_cost(scaled_cons):
            return  # здание не работает, если не хватает ресурсов

        # списываем потребление
        resource_manager.pay_cost(scaled_cons)

        # даём производство
        scaled_prod = {}
        for rid, amount in prod.items():
            scaled_prod[rid] = amount * level_factor
        resource_manager.add_many(scaled_prod)

    # ---------- загрузка/сохранение ----------

    def to_save_data(self):
        return [b.to_dict() for b in self.buildings]

    def load_from_save_data(self, data_list):
        self.buildings = [Building.from_dict(d) for d in data_list]

    # ---------- отрисовка ----------

    def update_animations(self, dt):
        for b in self.buildings:
            if b.build_anim > 0:
                b.build_anim -= dt
                if b.build_anim < 0:
                    b.build_anim = 0

    # ---------- информация об апгрейде и производстве ----------

    def get_building_cfg(self, building):
        if building is None:
            return {}
        return self.balance.get("buildings", {}).get(building.type, {})

    def get_max_level(self, building):
        cfg = self.get_building_cfg(building)
        return cfg.get("max_level", 5)  # если не указано — максимум 5

    def get_production_info(self, building):
        """
        Возвращает:
        {
            "current": {rid: value},
            "next": {rid: value},
            "gain": {rid: value},
            "max_level": int
        }
        """
        if building is None:
            return {"current": {}, "next": {}, "gain": {}, "max_level": 1}

        cfg = self.get_building_cfg(building)
        base_prod = cfg.get("production", {})
        mult = cfg.get("level_multiplier", 1.0)

        current = {}
        next_ = {}
        gain = {}

        for rid, amount in base_prod.items():
            cur = amount * (mult ** (building.level - 1))
            nxt = amount * (mult ** building.level)
            current[rid] = cur
            next_[rid] = nxt
            gain[rid] = nxt - cur

        return {
            "current": current,
            "next": next_,
            "gain": gain,
            "max_level": self.get_max_level(building)
        }

    def draw(self, screen):
        for b in self.buildings:
            sprite = self.sprites.get(b.type)
            if not sprite:
                continue
            px = b.grid_x * self.cell_size
            py = b.grid_y * self.cell_size

            if b.build_anim > 0:
                k = 1.0 - b.build_anim / 300.0
                k = max(0.0, min(1.0, k))
                size = int(self.cell_size * (0.6 + 0.4 * k))
                offset = (self.cell_size - size) // 2
                spr = pygame.transform.smoothscale(sprite, (size, size))
                screen.blit(spr, (px + offset, py + offset))
            else:
                screen.blit(sprite, (px, py))
