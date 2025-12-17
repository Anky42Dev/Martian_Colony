import pygame
import os


class ImageButton:
    def __init__(self, image_path, hover_path, x, y):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.hover_image = pygame.image.load(hover_path).convert_alpha()

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hover = False

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        if self.hover:
            screen.blit(self.hover_image, self.rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class MainMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        # фон
        bg_path = "assets/backgrounds/menu_bg.png"
        self.background = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else None

        # звук клика
        click_path = "assets/sounds/btn_sound.mp3"
        self.click_sound = pygame.mixer.Sound(click_path) if os.path.exists(click_path) else None

        # кнопки
        self.start_btn = ImageButton(
            "assets/ui/btn_start.png",
            "assets/ui/btn_start.png",
            width // 2 - 150, 350
        )

        self.continue_btn = ImageButton(
            "assets/ui/btn_continue.png",
            "assets/ui/btn_continue.png",
            width // 2 - 150, 350
        )

        self.restart_btn = ImageButton(
            "assets/ui/btn_new_game.png",
            "assets/ui/btn_new_game.png",
            width // 2 - 150, 430
        )

        self.fade_alpha = 255

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.start_btn.update(mouse_pos)
        self.continue_btn.update(mouse_pos)
        self.restart_btn.update(mouse_pos)

    def draw(self, has_save: bool):
        # фон
        if self.background:
            bg = pygame.transform.scale(self.background, (self.width, self.height))
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((20, 20, 30))

        # кнопки
        if has_save:
            self.continue_btn.draw(self.screen)
            self.restart_btn.draw(self.screen)
        else:
            self.start_btn.draw(self.screen)

        # плавное появление
        if self.fade_alpha > 0:
            fade = pygame.Surface((self.width, self.height))
            fade.fill((0, 0, 0))
            fade.set_alpha(self.fade_alpha)
            self.screen.blit(fade, (0, 0))
            self.fade_alpha -= 5

    def handle_event(self, event):
        has_save = os.path.exists("save.json")

        if has_save:
            if self.continue_btn.is_clicked(event):
                if self.click_sound:
                    self.click_sound.play()
                return "continue"

            if self.restart_btn.is_clicked(event):
                if self.click_sound:
                    self.click_sound.play()
                return "restart"
        else:
            if self.start_btn.is_clicked(event):
                if self.click_sound:
                    self.click_sound.play()
                return "start"

        return None
