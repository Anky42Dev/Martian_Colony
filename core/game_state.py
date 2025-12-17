# core/game_state.py

class GameState:
    def __init__(self):
        self.state = "playing"  # playing, dead, paused и т.п.
        self.selected_building_type = None

        self.first_goal = True
        self.show_hint = True

        # таймеры
        self.consumption_timer = 0
        self.consumption_interval = 5000  # мс

    def is_playing(self):
        return self.state == "playing"

    def set_dead(self):
        self.state = "dead"

    def reset(self):
        self.state = "playing"
        self.selected_building_type = None
        self.first_goal = True
        self.show_hint = True
        self.consumption_timer = 0
