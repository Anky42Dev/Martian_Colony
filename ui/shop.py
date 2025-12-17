# ui/shop.py
import pygame


class Shop:
    def __init__(self, balance, building_manager, resource_manager, panel_width, screen_width, btn_image):
        self.balance = balance
        self.building_manager = building_manager
        self.resource_manager = resource_manager

        self.panel_width = panel_width
        self.screen_width = screen_width

        self.btn_image = btn_image
        self.button_rects = {}
        self.hover_key = None

        self.items = {}
        self._init_items()

        self.shop_flash_time = 0

    # ------------------------------------------------------------
    # ИНИЦИАЛИЗАЦИЯ
    # ------------------------------------------------------------
    def _init_items(self):
        for btype, cfg in self.balance["buildings"].items():
            base_price = cfg["base_price"]  # dict
            self.items[btype] = {
                "name": cfg["name"],
                "price": base_price.copy()
            }

    def layout_buttons(self):
        x = self.screen_width - self.panel_width + 20
        y = 120
        for btype in self.items.keys():
            rect = self.btn_image.get_rect(topleft=(x, y))
            self.button_rects[btype] = rect
            y += rect.height + 24

    # ------------------------------------------------------------
    # ВЗАИМОДЕЙСТВИЕ
    # ------------------------------------------------------------
    def handle_mouse_motion(self, pos):
        mx, my = pos
        self.hover_key = None
        if mx > self.screen_width - self.panel_width:
            for key, rect in self.button_rects.items():
                if rect.collidepoint(mx, my):
                    self.hover_key = key
                    break

    def click(self, pos, game_state, toast):
        mx, my = pos
        if mx <= self.screen_width - self.panel_width:
            return

        for btype, rect in self.button_rects.items():
            if rect.collidepoint(mx, my):
                self._buy_building(btype, game_state, toast)
                return

    # ------------------------------------------------------------
    # ПОКУПКА
    # ------------------------------------------------------------
    def _buy_building(self, btype, game_state, toast):
        item = self.items[btype]
        price = item["price"]

        # ✅ ОТЛАДКА (оставь, пока тестируешь)
        print("=== ПОКУПКА ===")
        print("Тип:", btype)
        print("Цена:", price)
        print("Материалы:", self.resource_manager.get("materials"))
        print("can_afford:", self.resource_manager.can_afford_cost(price))

        # ✅ 1. Проверка unlock
        cfg = self.balance["buildings"][btype]
        unlock = cfg.get("unlock", {})

        # минимальные материалы
        min_mat = unlock.get("min_materials", 0)
        if self.resource_manager.get("materials") < min_mat:
            toast.show(f"Нужно минимум {min_mat} материалов!", 2000)
            return

        # зависимые здания
        requires = unlock.get("requires", [])
        for req in requires:
            if not any(b.type == req for b in self.building_manager.buildings):
                toast.show("Сначала постройте: " + ", ".join(requires), 2000)
                return

        # ✅ 2. Проверка цены
        if not self.resource_manager.can_afford_cost(price):
            toast.show("Недостаточно ресурсов!", 2000)
            return

        # ✅ 3. Списание цены
        self.resource_manager.pay_cost(price)

        # ✅ 4. Рост цены
        growth = cfg["price_growth"]
        new_price = {}
        for rid, val in price.items():
            new_price[rid] = int(val * growth)
        item["price"] = new_price

        # ✅ 5. Выбор здания для размещения
        game_state.selected_building_type = btype
        toast.show(f"Постройте: {item['name']}", 2000)
        self.shop_flash_time = 200

    # ------------------------------------------------------------
    # ОБНОВЛЕНИЕ И ОТРИСОВКА
    # ------------------------------------------------------------
    def update(self, dt):
        if self.shop_flash_time > 0:
            self.shop_flash_time -= dt
            if self.shop_flash_time < 0:
                self.shop_flash_time = 0

    def _total_materials_cost(self, price_dict):
        return int(price_dict.get("materials", 0))

    def draw(self, screen, font, building_manager):
        panel_x = self.screen_width - self.panel_width
        panel = pygame.Surface((self.panel_width, screen.get_height()), pygame.SRCALPHA)
        panel.fill((10, 10, 20, 0))
        screen.blit(panel, (panel_x, 0))

        title = font.render("МАГАЗИН", True, (255, 200, 120))
        screen.blit(title, (panel_x + 20, 20))

        for btype, rect in self.button_rects.items():
            item = self.items[btype]
            price = item["price"]
            total_mat = self._total_materials_cost(price)
            affordable = self.resource_manager.can_afford_cost(price)

            btn_img = self.btn_image.copy()

            # затемнение, если не хватает ресурсов
            if not affordable:
                dark = pygame.Surface(btn_img.get_size(), pygame.SRCALPHA)
                dark.fill((0, 0, 0, 90))
                btn_img.blit(dark, (0, 0))

            # hover
            if self.hover_key == btype:
                glow = pygame.Surface(btn_img.get_size(), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 50))
                btn_img.blit(glow, (0, 0))

            screen.blit(btn_img, rect.topleft)

            # мини‑здание
            sprite = building_manager.sprites.get(btype)
            if sprite:
                small = pygame.transform.scale(sprite, (40, 40))
                icon_x = rect.x + 10
                icon_y = rect.y + (rect.height - 40) // 2
                screen.blit(small, (icon_x, icon_y))
            else:
                icon_x = rect.x + 10

            # цена
            price_color = (200, 200, 120) if affordable else (150, 80, 80)
            price_text = font.render(str(total_mat), True, price_color)
            price_x = icon_x + 50
            price_y = rect.y + (rect.height - price_text.get_height()) // 2
            screen.blit(price_text, (price_x, price_y))

        # вспышка
        if self.shop_flash_time > 0:
            alpha = int(120 * (self.shop_flash_time / 200.0))
            flash = pygame.Surface((self.panel_width, screen.get_height()), pygame.SRCALPHA)
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (panel_x, 0))
