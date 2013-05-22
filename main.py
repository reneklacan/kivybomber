
import os
import sys
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from editor import Wizard
from game import Game
from level import LevelBase

class Simplibomber(App):
    def build(self):
        self.root = MainWidget()

    def on_stop(self):
        self.root.game.restart()

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, orientation='horizontal')

    def on_size(self, mw, size):
        self.menu()
        #self.levels()
        #self.game()

    def menu(self):
        """
        1. New game
        2. Levels
        3. Multiplayer (Coming soon)
        4. Settings
        5. Exit
        """
        self.clear_widgets()
        layout = BoxLayout(
                size_hint=(1, 1),
                orientation='vertical',
                spacing=20,
                padding=150,
        )
        layout.add_widget(Label(text='[b]Simplibomber[/b]', markup=True))
        layout.add_widget(
                Button(
                    text='New game',
                    on_release=lambda btn: self.play(),
                )
        )
        layout.add_widget(
                Button(
                    text='Levels',
                    on_release=lambda btn: self.levels(),
                )
        )
        layout.add_widget(
                Button(
                    text='Level editor',
                    on_release=lambda btn: self.editor(),
                )
        )
        layout.add_widget(
                Button(
                    text='Exit',
                    on_release=lambda btn: self.exit(),
                )
        )
        self.add_widget(layout)

    def play(self, level=None):
        self.clear_widgets()
        level_cls = None
        if level is not None:
            level_cls = LevelBase
            LevelBase.name = level['name']
            LevelBase.layout = level['layout']
            LevelBase.monster_dict = level['monster_dict']
            LevelBase.effects_propability = level['effects_propability']
            LevelBase.grid_size = level['grid_size']

        self.game = Game(level=level_cls, android=False)
        self.add_widget(self.game)

    def levels(self):
        self.clear_widgets()
        layout = BoxLayout(
                size_hint=(1, 1),
                orientation='vertical',
                spacing=20,
                padding=150,
        )
        topmenu = BoxLayout(
                orientation='horizontal',
        )
        topmenu.add_widget(
                Button(
                    text='Back',
                    on_release=lambda btn: self.menu()
                )
        )
        topmenu.add_widget(Label())
        topmenu.add_widget(Label())
        layout.add_widget(topmenu)
        layout.add_widget(Label(text='[b]Levels:[/b]', markup=True))

        for level_filename in os.listdir('levels'):
            if not level_filename.endswith('.json'):
                continue
            
            with open('levels/' + level_filename) as f:
                lvl = json.loads(f.read())

            button = Button(text=lvl['name'])
            button.level = lvl
            button.bind(on_release=lambda btn: self.play(btn.level))
            layout.add_widget(button)

        self.add_widget(layout)

    def editor(self):
        self.clear_widgets()

        self.add_widget(Wizard())

    def exit(self):
        sys.exit(0)

    def settings(self):
        pass

if __name__ in ('__main__', '__android__'):
    try:
        app = Simplibomber()
        app.use_kivy_settings = True
        app.run()
    except KeyboardInterrupt:
        pass
