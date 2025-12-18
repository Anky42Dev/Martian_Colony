# quest_manager.py
import pygame

class QuestManager:
    def __init__(self, font):
        self.font = font
        self.active_quest = None
        self.completed = []
        self.queue = []

    def add_quest(self, quest_id, text, condition):

        self.queue.append({
            "id": quest_id,
            "text": text,
            "condition": condition
        })

        if self.active_quest is None:
            self.active_quest = self.queue.pop(0)

    def update(self):
        if self.active_quest and self.active_quest["condition"]():
            self.completed.append(self.active_quest["id"])
            if self.queue:
                self.active_quest = self.queue.pop(0)
            else:
                self.active_quest = None

    def draw(self, screen):
        if not self.active_quest:
            return
        txt = self.font.render(f"Задание: {self.active_quest['text']}", True, (255, 230, 120))
        screen.blit(txt, (20, 20))
