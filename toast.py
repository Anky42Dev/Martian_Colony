import pygame
class ToastManager:
    def __init__(self, font):
        self.font = font
        self.toasts = []

    def show(self, text, duration=2000):
        self.toasts.append({
            "text": text,
            "time": duration
        })

    def update(self, dt):
        for t in self.toasts:
            t["time"] -= dt
        self.toasts = [t for t in self.toasts if t["time"] > 0]

    def draw(self, screen, width, height):
        y = height - 80
        for t in self.toasts:
            surf = self.font.render(t["text"], True, (255, 230, 150))
            screen.blit(surf, (width//2 - surf.get_width()//2, y))
            y -= 40
