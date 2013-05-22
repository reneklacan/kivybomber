
from threading import Timer
from kivy.animation import Animation
from kivy.graphics import Rectangle

from components import game_objects, textures
from constants import *
from bases.sprite import Sprite

class Player(Sprite):
    def after_init(self):
        self.bomb_timeout = 3
        self.bomb_power = 1
        self.flame_timeout = 0.3
        self.flame_penetration = 1
        self.move_duration = 0.25

        self.face('right')

    def setup(self):
        self.images = game_objects.player
        self.textures = textures.player

    def face(self, direction):
        self.canvas.clear()

        if direction not in self.images:
            texture = self.textures[direction]
            self.rectangle = Rectangle(
                    texture=texture,
                    pos=(0,0),
                    size=self.size,
            )
            self.images[direction] = self.rectangle
        else:
            self.rectangle = self.images[direction]

        self.canvas.add(self.rectangle)

    def is_bot(self):
        return False

    def move_direction(self, direction):
        if not self.alive:
            return

        self.face(direction)
        if direction == 'top':
            delta = self.parent.tile_size[1]
            destination = (self.pos[0], self.pos[1] + 10*delta)
        elif direction == 'bottom':
            delta = self.parent.tile_size[1]
            destination = (self.pos[0], self.pos[1] - 10*delta)
        elif direction == 'left':
            delta = self.parent.tile_size[0]
            destination = (self.pos[0] - 10*delta, self.pos[1])
        elif direction == 'right':
            delta = self.parent.tile_size[0]
            destination = (self.pos[0] + 10*delta, self.pos[1])

        self.stop_move()

        self.animation = Animation(
                pos=(destination[0], destination[1]),
                #pos=(destination.pos[0] + 5, destination.pos[1] + 5),
                duration=10*self.move_duration,
        )
        #self.animation.on_complete = lambda x: self.move_direction(direction)
        self.animation.on_progress = self.on_every_pos
        self.animation.start(self)

    def on_every_pos(self, _, __):
        self.take_effect()
        for tile in self.get_tile().eight_tiles_around():
            if tile.type == SPACE:
                continue
            if self.collide_widget(tile):
                print 'collide with ', tile.get_index_tuple()
                self.stop_move()
                self.load_pos()
                break
        else:
            # without collision
            self.save_pos()

    def plant_bomb(self):
        self.get_tile().add_bomb(self)
