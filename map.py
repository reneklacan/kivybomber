
import random
from threading import Lock, Timer
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

from ai import AIMap
from components import game_objects
from constants import *
from effects import *

flame_lock = Lock()

class GameGrid(GridLayout):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=kwargs['grid_size'][0], **kwargs)
        self.layout = kwargs['layout']
        self.grid_size = kwargs['grid_size']
        self.effects_propability = kwargs['effects_propability']
        self.tiles = []
        self.changes = []
        self.frozen = False
        self.tile_resized = 0
        self.tiles_amount = self.grid_size[0] * self.grid_size[1]

        for i, tile_type in enumerate(self.layout):
            ix = i % self.grid_size[0]
            iy = i // self.grid_size[0]
            tile = GameTile(type=tile_type, ix=ix, iy=iy)
            self.add_widget(tile)
            self.tiles.append(tile)

        self.aimap = AIMap(self)

    def restart(self):
        self.aimap.reset()
        self.frozen = False
        for i, tile_type in enumerate(self.layout):
            self.tiles[i].type = tile_type
            self.tiles[i].restart()

    def on_tile_size(self):
        self.tile_resized += 1
        if self.tile_resized == self.tiles_amount:
            self.on_load()
            
    def on_load(self):
        pass

    def freeze(self):
        self.frozen = True

    def add_change(self, tile):
        self.changes.append(tile)

    def get_tile(self, ix, iy):
        index = (self.grid_size[0]*iy + ix)
        if index >= len(self.tiles) or index < 0:
            Logger.debug(
                    'GameGrid: get_tile(%d,%d) index is %d (min: 0, max: %d)'
                    % (ix, iy, index, len(self.tiles) - 1)
            )
            return None
        return self.tiles[index]

    def get_tile_indexes(self, x, y):
        width, height = self.parent.tile_size
        return (int(x/width), int(self.grid_size[1] - (y/height)))

    def find_path(self, from_tuple, to_tuple):
        #print 'from:', from_tuple
        #print 'to:  ', to_tuple

        start = self.get_tile(*from_tuple)
        destination = self.get_tile(*to_tuple)

        if destination is None or destination.is_obstacle():
            return []

        open_set = [start]
        path_map = [[None for x in range(self.grid_size[0])] for y in range(self.grid_size[1])]
        path_map[start.iy][start.ix] = 0

        end = False

        while open_set and not end:
            tile = open_set.pop()
            steps = path_map[tile.iy][tile.ix]

            for neighbor in tile.tiles_around():
                if neighbor is None:
                    continue
                if not neighbor.is_obstacle():
                    current_steps = path_map[neighbor.iy][neighbor.ix]
                    if current_steps is None or current_steps > steps + 1:
                        path_map[neighbor.iy][neighbor.ix] = steps + 1
                        if neighbor == destination:
                            end = True
                            break
                        open_set.insert(0, neighbor)

        if not end:
            return []

        path = [destination]
        tile = destination

        if tile is None:
            return []

        steps = path_map[tile.iy][tile.ix]

        while steps and steps != 1:
            for item in tile.tiles_around():
                if path_map[item.iy][item.ix] == steps - 1:
                    path.append(item)
                    tile = item
                    steps = steps - 1 
                    break
    
        return path

class Bomb:
    def __init__(self, tile, player):
        self.tile = tile
        self.tile.canvas.add(game_objects.bomb)
        self.player = player
        self.timer = Timer(self.player.bomb_timeout, self.explode)
        self.timer.start()

    def explode(self):
        self.timer.cancel()
        self.tile.bomb = None
        Flame(self.tile, self.player)

    def stop(self):
        self.timer.cancel()

class Flame:
    def __init__(self, epicentrum, player):
        self.player = player
        self.tiles = [epicentrum]
        epicentrum.destroy()
        epicentrum.canvas.add(game_objects.flame_center)
        epicentrum.flame.append(FLAME_CENTER)

        flame_type = {}
        flame_type['top'] = FLAME_VERTICAL
        flame_type['bottom'] = FLAME_VERTICAL
        flame_type['left'] = FLAME_HOTIZONTAL
        flame_type['right'] = FLAME_HOTIZONTAL

        bombs = []
        self.changes = []

        for direction in ('top', 'bottom', 'left', 'right'):
            tile = epicentrum
            penetration = self.player.flame_penetration

            end = False

            for i in range(player.bomb_power):
                tile = tile.next_tile(direction)
                if not tile.is_destroyable():
                    break
                if tile.is_block():
                    if penetration == 0:
                        break
                    penetration -= 1
                    self.changes.append(tile)

                if tile.bomb is not None:
                    bombs.append(tile.bomb)

                tile.destroy()
                if not tile.flame:
                    if not penetration or i == player.bomb_power - 1:
                        # end of flame
                        tile.canvas.add(game_objects.flame_end[direction])
                    else:
                        # arm of flame
                        tile.canvas.add(game_objects.flame_arm[direction])
                    tile.flame = [flame_type[direction]]
                else:
                    if tile.flame[0] == flame_type[direction]:
                        # flames have same direction
                        tile.flame.append(flame_type[direction])
                        tile.canvas.add(game_objects.flame_arm[direction])
                    else:
                        # flames are crossing
                        tile.flame.append(flame_type[direction])
                        tile.canvas.add(game_objects.flame_center)

                self.tiles.append(tile)

                if not penetration:
                    break

        characters = []
        characters += epicentrum.parent.parent.players
        characters += epicentrum.parent.parent.monsters

        for each in characters:
            if each.get_tile() in self.tiles:
                each.die()

        for bomb in bombs:
            bomb.explode()

        self.timer = Timer(self.player.flame_timeout, self.expire)
        self.timer.start()

    def expire(self):
        for tile in self.tiles:
            flame_lock.acquire()
            if tile.flame == []:
                continue # probably after restart
            tile.flame.pop(0)
            tile.destroy()
            if not tile.flame:
                pass
            else:
                if tile.flame[0] == FLAME_VERTICAL:
                    tile.canvas.add(game_objects.flame_v)
                elif tile.flame[0] == FLAME_HOTIZONTAL:
                    tile.canvas.add(game_objects.flame_h)
            flame_lock.release()
        self.player.grid.changes += self.changes

class GameTile(RelativeLayout):
    def __init__(self, **kwargs):
        self.ix = None
        self.iy = None
        RelativeLayout.__init__(self, **kwargs)
        self.type = kwargs['type']
        self.ix = kwargs['ix']
        self.iy = kwargs['iy']

        self.rectangle = None
        self.bomb = None
        self.effect = None

    def __repr__(self):
        if self.ix is None:
            return 'GameTile'
        return 'GameTile(ix: %d, iy: %d)' % (self.ix, self.iy)

    def on_size(self, tile, size):
        if not game_objects.resize(size):
            return

        if self.rectangle is not None:
            self.rectangle.size = size

        self.init()
        self.parent.on_tile_size()

    def init(self):
        self.rectangle = None
        self.bomb = None
        self.flame = []
        self.item = None
        self.effect = None

        self.canvas.clear()

        if self.type == BLOCK:
            self.canvas.add(game_objects.block)
        elif self.type == MAZE:
            self.canvas.add(game_objects.maze)
        elif self.type == EMPTY:
            pass
        else:
            self.type = SPACE
            self.canvas.add(game_objects.space)

    def restart(self):
        if self.bomb is not None:
            self.bomb.stop()

        self.init()

    def get_index_tuple(self):
        return (self.ix, self.iy)

    def is_crossable(self):
        if self.type == SPACE and self.bomb is None:
            return True
        return False

    def is_space(self):
        return self.type == SPACE
    
    def is_obstacle(self):
        if self.type != SPACE:
            return True
        if self.bomb:
            return True
        return False

    def is_destroyable(self):
        if self.type == MAZE:
            return False
        return True

    def is_block(self):
        if self.type == BLOCK:
            return True
        return False

    def destroy(self):
        self.effect = None
        self.canvas.clear()
        self.canvas.add(game_objects.space)

        if self.item is not None:
            self.canvas.add(self.item.image)
            self.effect = self.item
            self.item = None

        if self.is_block():
            random_num = random.random()
            propabilities = self.parent.effects_propability
            # sort effects by their propability
            effects = sorted(propabilities, key=propabilities.get)

            for effect in effects:
                propability = propabilities[effect]
                if propability <= random_num:
                    cls = eval(effect)
                    self.item = cls()
                    break

        self.type = SPACE

    def get_effect(self):
        effect = self.effect
        if effect is not None:
            self.destroy()
        return effect

    def add_bomb(self, player):
        # if game is restarting
        if self.parent.frozen:
            return False
        if self.bomb:
            return False
        print 'bomb has been planted'
        self.parent.aimap.plant_bomb(player, self)
        self.bomb = Bomb(self, player)
        return True

    def next_tile(self, direction):
        if direction == 'top':
            return self.top_tile()
        elif direction == 'bottom':
            return self.bottom_tile()
        elif direction == 'left':
            return self.left_tile()
        elif direction == 'right':
            return self.right_tile()
        else:
            raise Exception('next_tile - direction %s' % direction)

    def top_tile(self):
        return self.parent.get_tile(self.ix, self.iy - 1)

    def bottom_tile(self):
        return self.parent.get_tile(self.ix, self.iy + 1)

    def left_tile(self):
        return self.parent.get_tile(self.ix - 1, self.iy)

    def right_tile(self):
        return self.parent.get_tile(self.ix + 1, self.iy)

    def tiles_around(self, space=False, dictionary=False):
        tiles = {
                'top': self.top_tile(),
                'bottom': self.bottom_tile(),
                'left': self.left_tile(),
                'right': self.right_tile()
        }

        if space:
            for direction, tile in tiles.items():
                if tile is None or not tile.is_crossable():
                    del tiles[direction]

        if dictionary:
            return tiles
        return tiles.values()

    def eight_tiles_around(self):
        """
        X X X
        X O X
        X X X
        """
        tiles = []
        left_tile = self.left_tile()
        right_tile = self.right_tile()

        tiles.append(left_tile)
        tiles.append(left_tile.top_tile())
        tiles.append(left_tile.bottom_tile())

        tiles.append(right_tile)
        tiles.append(right_tile.top_tile())
        tiles.append(right_tile.bottom_tile())

        tiles.append(self.top_tile())
        tiles.append(self.bottom_tile())

        return tiles
