
from threading import Timer
from kivy.logger import Logger
from kivy.uix.floatlayout import FloatLayout

from constants import *
from monsters import *
from map import GameGrid
from player import Player
from bases.sprite import SpriteGroup

class LevelBase(FloatLayout):
    name = 'Did you forget to override name? :P'
    key_bindings = {
            'a': 'left',
            's': 'bottom',
            'd': 'right',
            'w': 'top',
    }
    easy_mode = False

    def __init__(self, **kwargs):
        FloatLayout.__init__(self, **kwargs)

        self.arrows = []
        self.setup()

    def on_size(self, game, size):
        if 1 not in size:
            self.on_resize()

    def on_resize(self):
        pass

    def setup(self):
        self.before_setup()

        Logger.debug('Level: setup() self.size = %s' % str(self.size))

        tile_size_y = self.size[1]/self.grid_size[1]
        grid_width = self.grid_size[0]
        correct_grid_width = int(round(self.size[0] / tile_size_y))

        if correct_grid_width > grid_width:
            layout = []

            start = 0
            end = self.grid_size[0]
            while True:
                if not self.layout[start:end]:
                    break
                line = self.layout[start:end]
                for i in range(correct_grid_width - grid_width):
                    if i % 2:
                        line.insert(0, FILL)
                    else:
                        line.append(FILL)

                layout += line
                start = end
                end += self.grid_size[0]
               
            self.layout = layout
            self.grid_size = (correct_grid_width, self.grid_size[1])

        self.grid = GameGrid(
                #size_hint=(1, None),
                #size=(self.size[)
                grid_size=self.grid_size,
                layout=self.layout,
                effects_propability=self.effects_propability,
        )

        self.grid.on_load = self.on_first_start
        self.frozen = False
        self.tile_size_y = self.size[1]/self.grid_size[1]
        self.tile_size = (self.size[0]/self.grid_size[0], self.size[1]/self.grid_size[1])
        Logger.debug('Level: setup() tile_size = %s' % str(self.tile_size))
        self.player_size = map(lambda x: x * 0.5, self.tile_size)
        player_offset = (self.tile_size[0] - self.player_size[0])/2

        ix = self.layout.index('S') % self.grid_size[0] # spawnpoint in layout is required
        iy = self.layout.index('S') // self.grid_size[0]
        x = ix * self.tile_size[0] + player_offset
        y = (self.grid_size[1] - iy - 1) * self.tile_size[1] + player_offset + self.tile_size[1]/10

        self.add_widget(self.grid)
        self.player = Player(
                #size_hint=(None,None),
                size=self.player_size,
                pos=(x, y),
                grid=self.grid,
        )
        self.player.on_death = lambda: self.timed_restart(3)
        self.add_widget(self.player)
        self.players = [self.player]
        self.monsters = []
        self.init_monsters()

        self.after_setup()

    def init_monsters(self):
        for monster in self.monsters:
            monster.stop()
            self.remove_widget(monster)

        self.monsters = SpriteGroup()
        for index, item in enumerate(self.layout):
            if item in self.monster_dict:
                cls = eval(self.monster_dict[item])
                iy = index // self.grid_size[0]
                ix = index % self.grid_size[0]
                self.add_monster(cls, ix, iy)

                if self.easy_mode:
                    break

    def stop_monsters(self):
        self.monsters.stop()

    def add_monster(self, cls, ix, iy):
        self.monster_size = map(lambda x: x * cls.size_ratio, self.tile_size)
        monster_offset = (self.tile_size[0] - self.monster_size[0])/2

        monster = cls(
                size=self.monster_size,
                pos=(
                    ix * self.tile_size[0] + monster_offset,
                    (self.grid_size[1] - iy - 1) * self.tile_size[1] + monster_offset + self.tile_size[1]/10,
                ),
                grid=self.grid,
        )

        monster.on_death = self.check_status
        self.add_widget(monster)
        self.monsters.append(monster)
        return monster

    def before_setup(self):
        pass

    def after_setup(self):
        pass

    def on_first_start(self):
        """ first start after load """
        self.monsters.start()

    def freeze(self):
        self.before_freeze()

        self.grid.freeze()
        self.player.freeze()
        self.frozen = True
        self.monsters.freeze()

        self.after_freeze()

    def before_freeze(self):
        pass

    def after_freeze(self):
        pass

    def timed_restart(self, seconds):
        self.freeze()
        Timer(3, self.restart).start()
        print 'Restarting in 3 seconds...'

    def restart(self):
        self.before_restart()

        self.grid.restart()
        self.player.restart()
        self.init_monsters()
        self.monsters.start()
        self.frozen = False
        print 'Game restarted...'
        self.on_touch_down = self.on_first_touch_down

        self.after_restart()

    def before_restart(self):
        pass

    def after_restart(self):
        pass

    def on_first_touch_down(self, touch):
        self.on_first_move()
        to_tuple = self.grid.get_tile_indexes(*touch.pos)
        self.player.move(to_tuple)

    def on_other_touch_down(self, touch):
        to_tuple = self.grid.get_tile_indexes(*touch.pos)
        self.player.move(to_tuple)

    def on_touch_down(self, touch):
        self.on_first_touch_down(touch)
        self.on_touch_down = self.on_other_touch_down

    def on_first_move(self):
        pass

    def check_status(self):
        if self.is_goal_comlete():
            print 'Level complete'
            self.freeze()
            Timer(2, self.parent.next_level).start()

    def is_goal_comlete(self):
        # default goal is kill all enemies
        for enemy in self.monsters:
            if enemy.alive:
                return False
        if not self.player.alive:
            return False
        return True

    def on_key_down(self, keyboard, keycode, text, modifiers):
        #print 'The key', keycode, 'have been pressed'

        key = keycode[1]
        if key in ('a', 's', 'd', 'w'):
            if key not in self.arrows:
                self.arrows.append(key)
                self.player.move_direction(self.key_bindings[key])
            return True
        elif key == 'spacebar':
            self.player.plant_bomb()

        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def on_key_up(self, keyboard, keycode):
        #print 'The key', keycode, 'have been released'

        key = keycode[1]
        if key in ('a', 's', 'd', 'w'):
            if key in self.arrows:
                self.arrows.remove(key)
            if self.arrows == []:
                self.player.stop_move()
            else:
                self.player.move_direction(self.key_bindings[self.arrows[-1]])

        # If we hit escape, release the keyboard
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def move_character(self, key):
        if key == 'w':
            self.player.y += 5
        elif key == 's':
            self.player.y -= 5
        elif key == 'a':
            self.player.x -= 5
        elif key == 'd':
            self.player.x += 5

        return True

