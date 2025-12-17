# worlds/building.py

class Building:
    """
    Один универсальный класс здания.
    Вся логика — через balance.json.
    """
    def __init__(self, btype: str, grid_x: int, grid_y: int, level: int = 1):
        self.type = btype
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.level = level
        self.build_anim = 300  # ms на анимацию спавна

    def to_dict(self):
        return {
            "type": self.type,
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "level": self.level
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            btype=data.get("type", "factory"),
            grid_x=data.get("grid_x", 0),
            grid_y=data.get("grid_y", 0),
            level=data.get("level", 1)
        )
