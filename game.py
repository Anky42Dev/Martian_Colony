# game.py
import pygame
import os
import json

from core.game_state import GameState
from core.resource_manager import ResourceManager
from core.save_manager import SaveManager

from worlds.grid import Grid
from worlds.building_manager import BuildingManager

from ui.shop import Shop
from toast import ToastManager
from quest_manager import QuestManager



class Game:
    def __init__(self, screen, width, height):
        self.save_manager = SaveManager("save.json")

        self.screen = screen
        self.width = width
        self.height = height

        self.clock = pygame.time.Clock()
        # при гибели
        # кнопка рестарта при гибели
        restart_path = "assets/ui/btn_new_game.png"  # или твой путь
        self.restart_img = pygame.image.load(restart_path).convert_alpha()

        # hover‑версия (если хочешь подсветку)
        self.restart_img_hover = self.restart_img.copy()
        glow = pygame.Surface(self.restart_img_hover.get_size(), pygame.SRCALPHA)
        glow.fill((255, 255, 255, 60))
        self.restart_img_hover.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # позиция кнопки
        self.restart_btn_rect = self.restart_img.get_rect(
            center=(self.width // 2, self.height // 2 + 80)
        )

        self.restart_hover = False

        # ---- базовые параметры ----
        self.shop_width = 320
        self.cell_size = 128

        # ---- фон ----
        bg_path = os.path.join("assets", "backgrounds", "background_mars.png")
        self.background = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # ---- шрифты ----
        self.font = pygame.font.SysFont("arial", 20)
        self.hint_font = pygame.font.SysFont("arial", 24, bold=True)
        self.quest_font = pygame.font.SysFont("arial", 22, bold=True)
        # ---- кнопка выхода в главное меню ----
        exit_path = os.path.join("assets", "ui", "exit_button.png")
        self.exit_img = pygame.image.load(exit_path).convert_alpha()

        # создаём слегка подсвеченную версию для hover
        self.exit_img_hover = self.exit_img.copy()
        glow = pygame.Surface(self.exit_img_hover.get_size(), pygame.SRCALPHA)
        glow.fill((255, 255, 255, 60))
        self.exit_img_hover.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.exit_rect = self.exit_img.get_rect()
        # поставь куда удобно, это пример — над игровым полем слева от магазина
        self.exit_rect.topleft = (self.width - self.shop_width - self.exit_rect.width - 20, 20)
        self.exit_hover = False

        # ---- баланс ----
        self.balance = self.load_balance()

        # ---- core ----
        self.state = GameState()
        self.resources = ResourceManager(self.balance)
        self.save_manager = SaveManager()

        # ---- мир ----
        self.grid = Grid(self.width, self.height, self.cell_size, self.shop_width)
        self.buildings = BuildingManager(self.balance, self.cell_size)

        # ---- UI ----
        btn_img = self._load_button_image(os.path.join("assets", "ui", "btn_shop.png"))
        self.shop = Shop(
            balance=self.balance,
            building_manager=self.buildings,
            resource_manager=self.resources,
            panel_width=self.shop_width,
            screen_width=self.width,
            btn_image=btn_img
        )
        self.shop.layout_buttons()

        self.toast = ToastManager(self.font)
        self.quests = QuestManager(self.quest_font)

        self.click_particles = []

        self.setup_quests()
        self.load_game()

        # окно апгрейда
        self.upgrade_window_open = False
        self.upgrade_target = None
        self.upgrade_rect = pygame.Rect(self.width // 2 - 200, self.height // 2 - 150, 400, 300)
        self.upgrade_btn = pygame.Rect(0, 0, 0, 0)

    # ---------- загрузчики ----------
    def _draw_upgrade_window(self):
        if not self.upgrade_window_open or not self.upgrade_target:
            return

        b = self.upgrade_target

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (40, 40, 60), self.upgrade_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.upgrade_rect, 2, border_radius=10)

        x, y, w, h = self.upgrade_rect

        title = self.font.render(f"Улучшение: {b.type}", True, (255, 220, 120))
        self.screen.blit(title, (x + 20, y + 20))

        lvl_text = self.font.render(f"Уровень: {b.level}", True, (255, 255, 255))
        self.screen.blit(lvl_text, (x + 20, y + 70))

        cost = self.buildings.get_upgrade_cost(b)
        cost_str = ", ".join(f"{rid}: {int(val)}" for rid, val in cost.items())
        cost_text = self.font.render(f"Стоимость: {cost_str}", True, (200, 200, 120))
        self.screen.blit(cost_text, (x + 20, y + 110))

        self.upgrade_btn = pygame.Rect(x + 100, y + 180, 200, 50)
        pygame.draw.rect(self.screen, (80, 120, 80), self.upgrade_btn, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.upgrade_btn, 2, border_radius=8)

        btn_text = self.font.render("Улучшить", True, (255, 255, 255))
        self.screen.blit(btn_text, (self.upgrade_btn.x + 40, self.upgrade_btn.y + 10))

    def load_balance(self):
        if not os.path.exists("balance.json"):
            print("Внимание: нет balance.json")
            return {}
        try:
            with open("balance.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Ошибка чтения balance.json:", e)
            return {}

    def _load_button_image(self, path):
        try:
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return img
        except Exception as e:
            print("Ошибка загрузки кнопки магазина:", path, e)
        surf = pygame.Surface((260, 64), pygame.SRCALPHA)
        surf.fill((40, 40, 60, 220))
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
        return surf

    # ---------- квесты ----------

    def setup_quests(self):
        self.quests.add_quest(
            "collect_5_materials",
            "Добудьте 5 материалов, кликая по земле",
            lambda: self.resources.get("materials") >= 5
        )
        self.quests.add_quest(
            "build_solar",
            "Постройте солнечную панель",
            lambda: any(b.type == "solar_panel" for b in self.buildings.buildings)
        )

    # ============================================================
    # Обработка событий
    # ============================================================
    def handle_event(self, event):
        # hover для кнопки рестарта (когда колония мертва)
        if self.state.state == "dead":
            self.restart_hover = self.restart_btn_rect.collidepoint(
                event.pos) if event.type == pygame.MOUSEMOTION else self.restart_hover
        # если колония погибла — работает только кнопка рестарта
        if self.state.state == "dead":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_btn_rect.collidepoint(event.pos):
                    self.reset_game()
                    return
            return

        if event.type == pygame.MOUSEMOTION:
            self.grid.update_hover(event.pos)
            self.shop.handle_mouse_motion(event.pos)

            # hover для кнопки выхода
            self.exit_hover = self.exit_rect.collidepoint(event.pos)

        # окно апгрейда
        # --- если окно апгрейда открыто ---
        if self.upgrade_window_open:

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # 1. кнопка выхода в меню
                if self.exit_rect.collidepoint(event.pos):
                    print("EXIT BUTTON CLICKED")
                    return "exit_to_menu"

                # 2. клик по кнопке апгрейда
                if self.upgrade_btn.collidepoint(event.pos):
                    self._try_upgrade_current()
                    self.upgrade_window_open = False
                    return

                # 3. клик ВНЕ окна апгрейда — закрываем окно, но НЕ return!
                if not self.upgrade_rect.collidepoint(event.pos):
                    self.upgrade_window_open = False
                    # продолжаем обработку клика дальше

        # --- обычный режим (окно апгрейда закрыто или только что закрыто) ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # 1. кнопка выхода в меню
            if self.exit_rect.collidepoint(event.pos):
                print("EXIT BUTTON CLICKED")
                return "exit_to_menu"

            # 2. клик по правой панели — магазин
            if mx > self.width - self.shop_width:
                self.shop.click(event.pos, self.state, self.toast)
                return

            # 3. клик по зданию — открыть окно апгрейда
            for b in self.buildings.buildings:
                rect = pygame.Rect(
                    b.grid_x * self.cell_size,
                    b.grid_y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                if rect.collidepoint(mx, my):
                    self.upgrade_target = b
                    self.upgrade_window_open = True
                    return

            # 4. размещение выбранного здания
            gx, gy = self.grid.hover_cell
            if self.state.selected_building_type and self.buildings.can_place(
                    gx, gy, self.grid.cols, self.grid.rows
            ):
                self.buildings.place_building(gx, gy, self.state.selected_building_type)
                self.state.selected_building_type = None
                return

            # 5. добыча материалов
            if mx < self.width - self.shop_width:
                gain = self.balance["click"]["materials_gain"]
                self.resources.add("materials", gain)
                self.click_particles.append({
                    "x": mx,
                    "y": my,
                    "text": f"+{gain}",
                    "life": 600
                })

                if self.state.first_goal and self.resources.get("materials") >= 5:
                    self.state.first_goal = False
                    self.state.show_hint = False
                    self.toast.show("Вы добыли первые материалы!", 2500)

    # ============================================================
    # Обновление
    # ============================================================
    def update(self, dt):
        if not self.state.is_playing():
            return

        self.quests.update()
        self.toast.update(dt)
        self.shop.update(dt)
        self.buildings.update_animations(dt)

        # частицы
        for p in self.click_particles:
            p["y"] -= 0.05 * dt
            p["life"] -= dt
        self.click_particles = [p for p in self.click_particles if p["life"] > 0]

        # потребление глобальное (еда/вода населением)
        self.state.consumption_timer += dt
        if self.state.consumption_timer >= self.state.consumption_interval:
            self.state.consumption_timer = 0
            pop = self.resources.get("population")
            self.resources.add("food", -0.5 * pop)
            self.resources.add("water", -0.5 * pop)

            if self.resources.get("food") <= 0 or self.resources.get("water") <= 0:
                self.resources.add("population", -1)
                if self.resources.get("population") < 0:
                    self.resources.set("population", 0)
                self.toast.show("Люди умирают от голода или жажды...", 3000)
                if self.resources.get("population") <= 0:
                    self.state.set_dead()

        # производство от зданий
        self.buildings.produce_all(self.resources)

    # ============================================================
    # Отрисовка
    # ============================================================
    def draw(self):
        self.screen.blit(self.background, (0, 0))

        self.grid.draw(self.screen)
        self.buildings.draw(self.screen)
        self._draw_click_particles()
        self._draw_ui()
        # кнопка выхода
        self.screen.blit(self.exit_img, self.exit_rect.topleft)

        self.quests.draw(self.screen)
        self.toast.draw(self.screen, self.width, self.height)

        if self.state.selected_building_type:
            can_place = self.buildings.can_place(
                self.grid.hover_cell[0], self.grid.hover_cell[1],
                self.grid.cols, self.grid.rows
            )
            self.grid.draw_hover(self.screen, can_place)

        if self.upgrade_window_open:
            self._draw_upgrade_window()

        if self.state.state == "dead":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # текст
            txt = self.font.render("Колония погибла...", True, (255, 80, 80))
            self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - 40))

            # кнопка рестарта
            if self.restart_hover:
                self.screen.blit(self.restart_img_hover, self.restart_btn_rect.topleft)
            else:
                self.screen.blit(self.restart_img, self.restart_btn_rect.topleft)

            return  # важно: не рисуем остальной UI

            self._draw_upgrade_window()
    def _draw_click_particles(self):
        for p in self.click_particles:
            alpha = max(0, min(255, int(p["life"] / 600 * 255)))
            surf = self.font.render(p["text"], True, (255, 255, 255))
            surf.set_alpha(alpha)
            self.screen.blit(surf, (p["x"], p["y"]))

    def _draw_ui(self):
        # ресурсы сверху
        self.resources.draw_top_center(self.screen, self.font, self.width)

        # подсказка в начале
        if self.state.show_hint:
            hint = self.hint_font.render("Кликай по земле, чтобы добыть материалы!", True, (255, 220, 120))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 60))

        # магазин
        self.shop.draw(self.screen, self.font, self.buildings)

    # ---------- апгрейд ----------

    def _try_upgrade_current(self):
        if not self.upgrade_target:
            return
        cost = self.buildings.get_upgrade_cost(self.upgrade_target)
        if not self.resources.can_afford_cost(cost):
            self.toast.show("Недостаточно ресурсов для улучшения!", 2000)
            return
        self.resources.pay_cost(cost)
        self.buildings.upgrade_building(self.upgrade_target)
        self.toast.show("Здание улучшено!", 2000)
    # ---------- информация об апгрейде и производстве ----------

    def get_building_cfg(self, building):
        """
        Безопасно достаём конфиг здания из balance.json.
        """
        return self.balance.get("buildings", {}).get(building.type, {})

    def get_max_level(self, building):
        """
        Максимальный уровень здания из конфига. Если не задан — 1.
        В balance.json для каждого здания можно прописать "max_level".
        """
        cfg = self.get_building_cfg(building)
        return cfg.get("max_level", 1)

    def get_production_info(self, building):
        """
        Возвращает словарь с данными по производству:
        {
            "current": {rid: value},   # текущее производство на этом уровне
            "next":    {rid: value},   # производство на следующем уровне
            "gain":    {rid: value},   # прирост при апгрейде
            "max_level": int
        }
        Если у здания нет production — вернёт пустые словари.
        """
        cfg = self.get_building_cfg(building)
        base_prod = cfg.get("production", {})
        mult = cfg.get("level_multiplier", 1.0)

        current = {}
        next_ = {}
        gain = {}

        for rid, amount in base_prod.items():
            current_val = amount * (mult ** (building.level - 1))
            next_val = amount * (mult ** (building.level))
            current[rid] = current_val
            next_[rid] = next_val
            gain[rid] = next_val - current_val

        max_level = self.get_max_level(building)

        return {
            "current": current,
            "next": next_,
            "gain": gain,
            "max_level": max_level
        }

    def draw_upgrade_window(self):
        if not self.upgrade_window_open or not self.upgrade_target:
            return

        b = self.upgrade_target

        # затемнение фона
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # окно
        pygame.draw.rect(self.screen, (40, 40, 60), self.upgrade_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.upgrade_rect, 2, border_radius=10)

        x, y, w, h = self.upgrade_rect

        # заголовок
        title = self.font.render(f"Улучшение: {b.type}", True, (255, 220, 120))
        self.screen.blit(title, (x + 20, y + 20))

        # уровень
        lvl_text = self.font.render(f"Уровень: {b.level}", True, (255, 255, 255))
        self.screen.blit(lvl_text, (x + 20, y + 70))

        # стоимость
        cost = self.buildings.get_upgrade_cost(b)
        cost_str = ", ".join(f"{rid}: {int(val)}" for rid, val in cost.items())
        cost_text = self.font.render(f"Стоимость: {cost_str}", True, (200, 200, 120))
        self.screen.blit(cost_text, (x + 20, y + 110))

        # кнопка улучшения
        self.upgrade_btn = pygame.Rect(x + 100, y + 180, 200, 50)
        pygame.draw.rect(self.screen, (80, 120, 80), self.upgrade_btn, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.upgrade_btn, 2, border_radius=8)

        btn_text = self.font.render("Улучшить", True, (255, 255, 255))
        self.screen.blit(btn_text, (self.upgrade_btn.x + 40, self.upgrade_btn.y + 10))

    # ---------- сохранения ----------

    def save_game(self):
        """
        Сохранение текущего состояния игры в save.json через SaveManager.
        """
        data = {
            "resources": self.resources.values,  # все ресурсы
            "buildings": self.buildings.to_save_data(),  # все здания
            # можно добавить любое доп. состояние:
            "state": {
                "first_goal": getattr(self.state, "first_goal", True),
                "show_hint": getattr(self.state, "show_hint", True),
            }
        }
        self.save_manager.save(data)
        print("Игра сохранена")

    def load_game(self):
        """
        Загрузка состояния игры из save.json. Если файла нет — просто выходим.
        """
        data = self.save_manager.load()
        if not data:
            print("Сохранения нет, загрузка отменена")
            return

        # ресурсы
        resources_data = data.get("resources", {})
        for rid, value in resources_data.items():
            self.resources.set(rid, value)

        # здания
        buildings_data = data.get("buildings", [])
        self.buildings.load_from_save_data(buildings_data)

        # простое состояние
        state_data = data.get("state", {})
        if hasattr(self.state, "first_goal"):
            self.state.first_goal = state_data.get("first_goal", True)
        if hasattr(self.state, "show_hint"):
            self.state.show_hint = state_data.get("show_hint", True)

        print("Игра загружена")

    def reset_game(self):
        self.save_manager.reset()
        self.state.reset()

        # ✅ НЕ создаём новый ResourceManager — обновляем старый
        new_res = ResourceManager(self.balance)
        self.resources.values = new_res.values.copy()

        self.buildings.buildings = []

        self.shop._init_items()
        self.shop.layout_buttons()

        self.click_particles.clear()
        self.upgrade_window_open = False
        self.upgrade_target = None
