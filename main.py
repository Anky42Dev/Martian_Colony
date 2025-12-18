import pygame
import os

from ui.menu import MainMenu
from game import Game
import os, sys

pygame.init()
pygame.mixer.init()

# --- окно ---
WIDTH, HEIGHT = 1536, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Martian Colony")

clock = pygame.time.Clock()

# --- меню и игра ---
menu = MainMenu(screen, WIDTH, HEIGHT)
game = Game(screen, WIDTH, HEIGHT)

# --- музыка меню ---
if os.path.exists("assets/sounds/game_music.mp3.mp3"):
    pygame.mixer.music.load("assets/sounds/game_music.mp3.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

state = "menu"
running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # при выходе можно сохранить игру, если мы в игре
            if state == "game":
                game.save_game()
            running = False

        # -------------------------------
        # МЕНЮ
        # -------------------------------
        if state == "menu":
            result = menu.handle_event(event)

            if result == "start":
                # музыка игры
                if os.path.exists("assets/sounds/game_music.mp3"):
                    pygame.mixer.music.load("assets/sounds/game_music.mp3")
                    pygame.mixer.music.play(-1)

                game.reset_game()
                state = "game"

            elif result == "restart":
                if os.path.exists("assets/sounds/game_music.mp3"):
                    pygame.mixer.music.load("assets/sounds/game_music.mp3")
                    pygame.mixer.music.play(-1)

                game.reset_game()
                state = "game"

            elif result == "continue":
                if os.path.exists("assets/sounds/game_music.mp3"):
                    pygame.mixer.music.load("assets/sounds/game_music.mp3")
                    pygame.mixer.music.play(-1)

                game.load_game()
                state = "game"

        # -------------------------------
        # ИГРА
        # -------------------------------
        elif state == "game":
            result = game.handle_event(event)

            if result == "exit_to_menu":
                # сохраняем игру перед выходом
                game.save_game()

                # музыка меню
                if os.path.exists("assets/sounds/menu_music.mp3"):
                    pygame.mixer.music.load("assets/sounds/menu_music.mp3")
                    pygame.mixer.music.play(-1)

                state = "menu"

    # -------------------------------
    # ОТРИСОВКА
    # -------------------------------
    if state == "menu":
        menu.update(dt)
        menu.draw(has_save=os.path.exists("save.json"))

    elif state == "game":
        game.update(dt)
        game.draw()

    pygame.display.flip()

pygame.quit()
