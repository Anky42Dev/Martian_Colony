# event_manager.py
import random
import pygame

class EventManager:
    def __init__(self):
        self.timer = 0
        self.interval = 20000  # каждые 20 секунд шанс события
        self.active_event = None
        self.event_timer = 0

    def update(self, dt, resources):
        self.timer += dt

        # если нет активного события — шанс вызвать новое
        if self.timer >= self.interval and not self.active_event:
            self.timer = 0
            if random.random() < 0.25:  # 25% шанс
                self.start_event(resources)

        # если событие активно — уменьшаем таймер
        if self.active_event:
            self.event_timer -= dt
            if self.event_timer <= 0:
                self.active_event = None

    def start_event(self, resources):
        events = [
            ("Песчаная буря! Производство снижено.", -0.5),
            ("Поломка оборудования! Потеря материалов.", -5),
            ("Солнечная вспышка! Энергия нестабильна.", -3)
        ]
        text, effect = random.choice(events)
        self.active_event = text
        self.event_timer = 6000  # 6 секунд
        resources["materials"] = max(0, resources["materials"] + effect)

    def draw(self, screen, font, width):
        if self.active_event:
            txt = font.render(self.active_event, True, (255, 120, 120))
            screen.blit(txt, (width//2 - txt.get_width()//2, 60))
