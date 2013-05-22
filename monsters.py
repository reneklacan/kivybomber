
import random

from threading import Timer
from player import Player
from components import file_paths, game_objects, textures
from ai import AIPlayer
from bases.monsters import DummyMonster, FertileMonster

class EnemyPlayer(Player):
    name = "Enemy Player"
    shortcut = "EP"
    register = True
    size_ratio = 0.5
    cls_texture = textures.player2_up

    def setup(self):
        self.textures = textures.player2
        self.images = game_objects.player2

    def start(self):
        self.move_duration = 0.35
        self.ai = AIPlayer(self)
        self.on_every_move()

    def on_move_finish(self):
        pass

    def on_every_move(self):
        destination = self.ai.get_move()
        if destination is None:
            self.aitimer = Timer(0.1, self.on_every_move)
            self.aitimer.start()
            return
        self.move(destination)

    def freeze(self):
        self.frozen = True
        self.aitimer.cancel()

class PurpleFluffy(DummyMonster):
    name = "Purple Fluffy"
    shortcut = "PF"
    register = True
    size_ratio = 0.8
    cls_texture = textures.purple_fluffy

    def setup(self):
        self.setup_from_texture(textures.purple_fluffy)
        self.last_direction = random.choice(('top', 'bottom', 'left', 'right'))
        self.move_duration = 0.7
        self.traveled = 0

class DummyGhost(DummyMonster):
    name = "Dummy Ghost"
    shortcut = "DG"
    register = True
    size_ratio = 0.8
    cls_texture = textures.ghost

    def setup(self):
        self.setup_from_texture(textures.ghost)
        self.last_direction = random.choice(('top', 'bottom', 'left', 'right'))
        self.move_duration = 0.5
        self.traveled = 0

class FertileGhost(FertileMonster):
    name = "Fertile Dummy Ghost"
    shortcut = "FDG"
    register = True
    size_ratio = 0.8
    cls_texture = textures.ghost

    def setup(self):
        self.setup_from_texture(textures.ghost)
        self.last_direction = random.choice(('top', 'bottom', 'left', 'right'))
        self.move_duration = 0.5
        self.infertility = False
        self.traveled = 0

    def on_every_move(self):
        FertileMonster.on_every_move(self)
        DummyMonster.on_every_move(self)

registered = (
        EnemyPlayer,
        PurpleFluffy,
        DummyGhost,
        FertileGhost,
)
