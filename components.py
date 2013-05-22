
import time
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics import Rectangle

res_dir = './'

class FilePathsMap:
    def __init__(self):
        self.space = res_dir + 'resources/images/map/space.gif'
        self.block = res_dir + 'resources/images/map/block.jpg'
        self.maze = res_dir + 'resources/images/map/maze.jpg'
        self.bomb = res_dir + 'resources/images/map/bomb.gif'

        self.flame_center = res_dir + 'resources/images/map/flame_center.gif'
        self.flame_v = res_dir + 'resources/images/map/flame_v.gif'
        self.flame_h = res_dir + 'resources/images/map/flame_h.gif'
        self.flame_end_top = res_dir + 'resources/images/map/flame_end_top.gif'
        self.flame_end_bottom = res_dir + 'resources/images/map/flame_end_bottom.gif'
        self.flame_end_left = res_dir + 'resources/images/map/flame_end_left.gif'
        self.flame_end_right = res_dir + 'resources/images/map/flame_end_right.gif'

class FilePathsPlayers:
    def __init__(self):
        self.player_up = res_dir + 'resources/images/player/player_up.gif'
        self.player_down = res_dir + 'resources/images/player/player_down.gif'
        self.player_left = res_dir + 'resources/images/player/player_left.gif'
        self.player_right = res_dir + 'resources/images/player/player_right.gif'

        self.player2_up = res_dir + 'resources/images/player/player2_up.gif'
        self.player2_down = res_dir + 'resources/images/player/player2_down.gif'
        self.player2_left = res_dir + 'resources/images/player/player2_left.gif'
        self.player2_right = res_dir + 'resources/images/player/player2_right.gif'

class FilePathsEffects:
    def __init__(self):
        self.flame_up = res_dir + 'resources/images/effects/flame_up.png'

class FilePathsMonsters:
    def __init__(self):
        self.ghost = res_dir + 'resources/images/monsters/ghost.png'
        self.purple_fluffy = res_dir + 'resources/images/monsters/purple_fluffy.gif'
        self.red_fluffy = res_dir + 'resources/images/monsters/red_fluffy.gif'
        self.black_fluffy = res_dir + 'resources/images/monsters/black_fluffy.gif'
        self.blue_fluffy = res_dir + 'resources/images/monsters/blue_fluffy.gif'

class FilePaths:
    def __init__(self):
        self.map = FilePathsMap()
        self.monsters = FilePathsMonsters()
        self.players = FilePathsPlayers()
        self.effects = FilePathsEffects()

file_paths = FilePaths()

class Textures:
    def __init__(self):
        self.space = Image(file_paths.map.space).texture
        self.block = Image(file_paths.map.block).texture
        self.maze = Image(file_paths.map.maze).texture
        self.bomb = Image(file_paths.map.bomb).texture

        self.flame_center = Image(file_paths.map.flame_center).texture
        self.flame_v = Image(file_paths.map.flame_v).texture
        self.flame_h = Image(file_paths.map.flame_h).texture
        self.flame_end_top = Image(file_paths.map.flame_end_top).texture
        self.flame_end_bottom = Image(file_paths.map.flame_end_bottom).texture
        self.flame_end_left = Image(file_paths.map.flame_end_left).texture
        self.flame_end_right = Image(file_paths.map.flame_end_right).texture

        self.player_up = Image(file_paths.players.player_up).texture
        self.player_down = Image(file_paths.players.player_down).texture
        self.player_left = Image(file_paths.players.player_left).texture
        self.player_right = Image(file_paths.players.player_right).texture

        self.player2_up = Image(file_paths.players.player2_up).texture
        self.player2_down = Image(file_paths.players.player2_down).texture
        self.player2_left = Image(file_paths.players.player2_left).texture
        self.player2_right = Image(file_paths.players.player2_right).texture

        self.player = {}
        self.player['top'] = self.player_up
        self.player['bottom'] = self.player_down
        self.player['left'] = self.player_left
        self.player['right'] = self.player_right

        self.player2 = {}
        self.player2['top'] = self.player2_up
        self.player2['bottom'] = self.player2_down
        self.player2['left'] = self.player2_left
        self.player2['right'] = self.player2_right

        self.powerup_flame_up = Image(file_paths.effects.flame_up).texture

        self.ghost = Image(file_paths.monsters.ghost).texture
        self.purple_fluffy = Image(file_paths.monsters.purple_fluffy).texture
        self.red_fluffy = Image(file_paths.monsters.red_fluffy).texture
        self.black_fluffy = Image(file_paths.monsters.black_fluffy).texture
        self.blue_fluffy = Image(file_paths.monsters.blue_fluffy).texture

textures = Textures()

class GameObjects:
    def __init__(self):
        self.last_tile_size = None

        self.player = {}
        self.player2 = {}

    def on_resize(self):
        pass

    def resize(self, tile_size):
        if tile_size[0] < 10 or tile_size[1] < 10:
            return False

        if tile_size[0] == 100 or tile_size[1] == 100:
            return False

        tile_size = map(lambda x: int(x), tile_size)

        if self.last_tile_size != tile_size:
            self.last_tile_size = tile_size
        else:
            return True

        base_pos = (0,0)

        t = time.time()
        self.space = Rectangle(
                texture=textures.space,
                pos=base_pos,
                size=tile_size,
        )
        self.block = Rectangle(
                texture=textures.block,
                pos=base_pos,
                size=tile_size,
        )
        self.maze = Rectangle(
                texture=textures.maze,
                pos=base_pos,
                size=tile_size,
        )
        # flame objects
        self.flame_center = Rectangle(
                texture=textures.flame_center,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_v = Rectangle(
                texture=textures.flame_v,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_h = Rectangle(
                texture=textures.flame_h,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_end_top = Rectangle(
                texture=textures.flame_end_top,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_end_bottom = Rectangle(
                texture=textures.flame_end_bottom,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_end_left = Rectangle(
                texture=textures.flame_end_left,
                pos=base_pos,
                size=tile_size,
        )
        self.flame_end_right = Rectangle(
                texture=textures.flame_end_right,
                pos=base_pos,
                size=tile_size,
        )

        self.flame_arm = {}
        self.flame_arm['top'] = self.flame_v
        self.flame_arm['bottom'] = self.flame_v
        self.flame_arm['left'] = self.flame_h
        self.flame_arm['right'] = self.flame_h

        self.flame_end = {}
        self.flame_end['top'] = self.flame_end_top
        self.flame_end['bottom'] = self.flame_end_bottom
        self.flame_end['left'] = self.flame_end_left
        self.flame_end['right'] = self.flame_end_right

        bomb_size = map(lambda x: x*0.7, tile_size)
        bomb_pos = [
                (a - b)/2 for a, b in zip(tile_size, bomb_size)
        ]
        self.bomb = Rectangle(
                texture=textures.bomb,
                pos=bomb_pos,
                size=bomb_size,
        )

        self.powerup_flame_up = Rectangle(
                texture=textures.powerup_flame_up,
                pos=base_pos,
                size=tile_size,
        )

        self.ghost = Rectangle(
                texture=textures.ghost,
                pos=base_pos,
                size=tile_size,
        )

        self.on_resize()
        return True

game_objects = GameObjects()
