
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from constants import *
#from level import Level0, Level1, Level2, LevelAI

class Game(FloatLayout):
    def __init__(self, **kwargs):
        FloatLayout.__init__(self, **kwargs)

        self.android = kwargs['android']
        if 'levels' in kwargs and kwargs['levels'] is not None:
            self.levels = kwargs['levels']
            print self.levels
        else:
            self.levels = []
            #self.levels = [Level1, Level2, LevelAI]
        self.current_level = -1
        self.level = None

        if not self.android:
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_key_down)
            self.keyboard.bind(on_key_up=self.on_key_up)

    def on_resize(self):
        self.init()

    def on_size(self, game, size):
        if 1 not in size:
            self.on_resize()

    def init(self):
        self.next_level()

    def next_level(self):
        self.current_level += 1
        self.clear_widgets()
        try:
            self.level = self.levels[self.current_level](size=(1280, self.size[1]-40), size_hint=(None,None))
        except IndexError:
            self.parent.levels()

        print 'Level %s' % self.level.name
        self.add_widget(self.level)
        self.add_widget(
                Label(
                    text='Level - ' + self.level.name,
                    size=(1280, 40),
                    size_hint=(None, None),
                    pos=(0, self.size[1]-40)
                )
        )

    def restart(self):
        self.level.restart()

    def on_key_down(self, keyboard, keycode, text, modifiers):
        self.level.on_key_down(keyboard, keycode, text, modifiers)

    def on_key_up(self, keyboard, keycode):
        self.level.on_key_up(keyboard, keycode)

    def keyboard_closed(self):
        print 'My keyboard have been closed!'
        self.keyboard.unbind(on_key_down=self.level.on_key_down)
        self.keyboard = None
