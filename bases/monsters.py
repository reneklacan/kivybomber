
import random
from threading import Timer
from kivy.graphics import Rectangle
from bases.sprite import Sprite

class Monster(Sprite):
    def setup_from_texture(self, texture):
        #self.size = self.image_size
        #size = map(lambda x: x*self.size_ratio, self.size)
        #player_pos = [
        #        0,0
        #        #(a - b)/2 for a, b in zip(self.size, player_size)
        #]
        self.rectangle = Rectangle(
                texture=texture,
                #pos=player_pos,
                pos=(0,0),
                #size=player_size,
                size=self.size,
        )
        self.canvas.add(self.rectangle)

class DummyMonster(Monster):
    def start(self):
        self.on_every_move()

    def on_every_move(self):
        if not self.alive:
            return

        current_tile = self.get_tile()
        if self.collide(self.parent.player):
            self.parent.player.die()

        next_tile = current_tile.next_tile(self.last_direction)
        if next_tile is not None and next_tile.is_crossable() and self.traveled < 3:
            self.traveled += 1
            self.move(next_tile.get_index_tuple())
            return

        self.traveled = 0

        tiles_dict = current_tile.tiles_around(space=True, dictionary=True)
        if not tiles_dict:
            self.move_timer = Timer(0.2, self.on_every_move)
            self.move_timer.start()
            return
        direction = random.choice(tiles_dict.keys())
        self.last_direction = direction
        self.move(tiles_dict[direction].get_index_tuple())

class FertileMonster(DummyMonster):
    def after_stop(self):
        if self.infertility_timer is not None:
            self.infertility_timer.cancel()

    def start(self):
        self.infertility = False
        self.infertility_timer = None
        self.infertile()
        self.on_every_move()

    def after_stop(self):
        if self.infertility_timer is not None:
            self.infertility_timer.cancel()

    def bear(self):
        tile_indexes = self.get_tile().get_index_tuple()
        monster = self.parent.add_monster(self.__class__, *tile_indexes)
        monster.infertility = True
        monster.start()

    def fertile(self):
        self.infertility = False

    def infertile(self):
        self.infertility = True
        self.infertility_timer = Timer(20, self.fertile)
        self.infertility_timer.start()

    def on_every_move(self):
        if not self.alive:
            return

        if not self.infertility and len(self.parent.monsters) < 20:
            for monster in self.parent.monsters:
                if monster == self or not monster.alive or monster.infertility:
                    continue
                if self.collide(monster):
                    self.infertile()
                    monster.infertile()
                    self.bear()
                    break

