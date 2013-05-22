
import os
import json
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle
from components import file_paths, textures
from constants import *
import monsters
from monsters import *

class Wizard(FloatLayout):
    def __init__(self, **kwargs):
        FloatLayout.__init__(self, **kwargs)

        self.level_select()
        #self.info_input()

    def level_select(self):
        self.clear_widgets()

        levels_layout = BoxLayout(orientation='vertical', spacing=50, padding=50)

        topmenu = BoxLayout(
                orientation='horizontal',
        )
        topmenu.add_widget(
                Button(
                    text='Back',
                    on_release=lambda btn: self.parent.menu()
                )
        )
        topmenu.add_widget(Label())
        topmenu.add_widget(Label())

        levels_layout.add_widget(topmenu)

        def delete_level(btn):
            os.remove('levels/' + btn.filename)
            self.level_select()

        for level_filename in os.listdir('levels'):
            if not level_filename.endswith('.json'):
                continue
            
            with open('levels/' + level_filename) as f:
                level = json.loads(f.read())

            level_layout = BoxLayout(orientation='horizontal', spacing=50)
            level_layout.add_widget(Label(text=level['name']))

            edit_button = Button(
                    text='Edit',
                    on_release=lambda btn: self.load_level(btn.level)
            )
            edit_button.level = level
            level_layout.add_widget(edit_button)

            delete_button = Button(
                    text='Delete',
                    on_release = delete_level,
            )
            delete_button.filename = level_filename
            level_layout.add_widget(delete_button)

            levels_layout.add_widget(level_layout)

        levels_layout.add_widget(
                Button(
                    text='New level',
                    on_release=lambda btn: self.info_input()
                )
        )
        self.add_widget(levels_layout)

    def load_level(self, level):
        self.name = level['name']
        self.grid_width = level['grid_size'][0]
        self.grid_height = level['grid_size'][1]

        self.grid_setup(level)

    def info_input(self):
        self.clear_widgets()
        self.info = InfoInput(
                size_hint=(None,None),
                size=(400, 200),
        )
        self.add_widget(self.info)
        self.info.init()

    def grid_setup(self, level=None):
        self.clear_widgets()

        self.grid = GridSetup(
                size_hint=(1,1),
                level=level,
        )
        self.add_widget(self.grid)
        #self.grid_setup.init()

    def export(self):
        level = {}
        level['name'] = self.name

        level['layout'] = []
        for tile in self.grid.tiles:
            item = None
            if tile.category == 'map':
                item = tile.item
                if tile.item == SPAWNPOINT:
                    item = 'S'
            elif tile.category == 'monsters':
                item = tile.item.shortcut
            level['layout'].append(item)

        level['monster_dict'] = {}
        for monster in monsters.registered:
            level['monster_dict'][monster.shortcut] = monster.__name__

        level['effects_propability'] = {
                "FlameUpEffect": 0.4
        }
        level['grid_size'] = [
                self.grid_width,
                self.grid_height
        ]

        level_name = level['name'].lower().replace(' ', '_')
        with open('levels/' + level_name + '.json', 'w') as f:
            f.write(json.dumps(level, indent=4))

class Tile(RelativeLayout):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.item = SPACE
        self.category = 'map'

    def to_space(self):
        texture = textures.space

        self.rectangle = Rectangle(
                texture=texture,
                pos=(0,0),
                size=self.size,
        )
        self.canvas.add(self.rectangle)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return

        item = self.parent.parent.parent.current_item
        category = self.parent.parent.parent.current_category

        if item is None or category is None:
            return

        self.item = item
        self.category = category

        self.update()

    def update(self):
        self.to_space()

        if self.category == 'map':
            if self.item == SPAWNPOINT:
                texture = textures.player_up
            if self.item == SPACE:
                return
            elif self.item == BLOCK:
                texture = textures.block
            elif self.item == MAZE:
                texture = textures.maze
            elif self.item == VOID:
                self.canvas.clear()
                return
        elif self.category == 'monsters':
            texture = self.item.cls_texture

        self.rectangle = Rectangle(
                texture=texture,
                pos=(0,0),
                size=self.size,
        )
        self.canvas.add(self.rectangle)

    def on_touch_move(self, movement):
        self.on_touch_down(movement)

    def load(self, level, index):
        item = level['layout'][index]
        if item == 'S':
            item = SPAWNPOINT
        if type(item) is int:
            self.category = 'map'
            self.item = item
        elif type(item) is str or type(item) is unicode:
            self.category = 'monsters'
            self.item = eval('monsters.' + level['monster_dict'][item])
        self.update()

class GridSetup(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, orientation='horizontal', **kwargs)
        self.level = kwargs['level']
        self.current_item = None
        self.current_category = None

    def on_size(self, grid, size):
        self.clear_widgets()
        self.init()

    def init(self):
        self.grid = GridLayout(
                cols=self.parent.grid_width,
                size_hint=(1, None),
        )

        width = self.parent.grid_width
        height = self.parent.grid_height

        tile_size = self.size[0] * 0.8 / width
        self.grid.size = (tile_size * width, tile_size * height)
        
        # TODO is self.level is not None
        self.tiles = []
        for i in range(width * height):
            tile = Tile(
                size=(tile_size, tile_size),
                size_hint=(None, None)
            )
            tile.ix = i % width
            tile.iy = i // width
            tile.to_space()
            if self.level is not None:
                tile.load(self.level, i)
            self.tiles.append(tile)
            self.grid.add_widget(tile)

        self.sidebar = BoxLayout(
                orientation='vertical',
                size_hint=(0.2, 1),
        )
        self.sidebar.add_widget(Label(text='Tiles:'))
        self.sidebar.add_widget(
                Button(
                    text='Spawnpoint',
                    on_release=lambda btn: self.change_tool('map', SPAWNPOINT),
                )
        )
        self.sidebar.add_widget(
                Button(
                    text='Void',
                    on_release=lambda btn: self.change_tool('map', VOID),
                )
        )
        self.sidebar.add_widget(
                Button(
                    text='Space',
                    on_release=lambda btn: self.change_tool('map', SPACE),
                )
        )
        self.sidebar.add_widget(
                Button(
                    text='Block',
                    on_release=lambda btn: self.change_tool('map', BLOCK),
                )
        )
        self.sidebar.add_widget(
                Button(
                    text='Maze',
                    on_release=lambda btn: self.change_tool('map', MAZE),
                )
        )
        self.sidebar.add_widget(Label(text='Monsters:'))

        for monster_cls in monsters.registered:
            button = Button(
                text=monster_cls.name,
                on_release=lambda btn: self.change_tool(btn.category, btn.monster_cls),
            )
            button.category = 'monsters'
            button.monster_cls = monster_cls
            self.sidebar.add_widget(button)

        self.main = BoxLayout(
                orientation='vertical',
                size_hint=(0.8, 1),
        )
        self.topbar = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                size=(0, 40),
        )
        self.topbar.add_widget(
                Button(
                    text='Main menu',
                    on_release=lambda btn: self.parent.parent.menu(),
                )
        )
        self.topbar.add_widget(
                Button(
                    text='Edit another level',
                    on_release=lambda btn: self.parent.level_select(),
                )
        )
        self.topbar.add_widget(Label(text=''))
        self.topbar.add_widget(
                Button(
                    text='Save level',
                    on_release=lambda btn: self.parent.export(),
                )
        )
        self.main.add_widget(self.topbar)
        self.main.add_widget(FloatLayout())
        self.main.add_widget(self.grid)

        self.add_widget(self.main)
        self.add_widget(self.sidebar)

    def change_tool(self, category, item):
        self.current_category = category
        self.current_item = item

class InfoInput(GridLayout):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=2, **kwargs)

    def init(self):
        self.width_input = TextInput(text='21')
        self.height_input = TextInput(text='11')
        self.name_input = TextInput(text='level_name')

        self.add_widget(Label(text='Level name:', markup=True))
        self.add_widget(self.name_input)

        self.add_widget(Label(text='Width:', markup=True))
        self.add_widget(self.width_input)

        self.add_widget(Label(text='Height:', markup=True))
        self.add_widget(self.height_input)

        self.add_widget(FloatLayout())
        button = Button(text='Continue')
        button.bind(on_release=lambda btn: self.finish())
        self.add_widget(button)

    def finish(self):
        self.parent.name = self.name_input.text
        self.parent.grid_width = int(self.width_input.text)
        self.parent.grid_height = int(self.height_input.text)
        self.parent.grid_setup()

class LevelEditor(App):
    def build(self):
        self.root = Wizard()

if __name__ in ('__main__', '__android__'):
    try:
        app = LevelEditor()
        app.run()
    except KeyboardInterrupt:
        pass
