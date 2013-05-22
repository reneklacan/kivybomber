
from player import Player
from monsters import EnemyPlayer

from components import game_objects

class Effect:
    pass

class FlameUpEffect(Effect):
    def __init__(self):
        self.image = game_objects.powerup_flame_up

    def apply(self, sprite):
        if type(sprite) is Player or type(sprite) is EnemyPlayer:
            sprite.bomb_power += 1
