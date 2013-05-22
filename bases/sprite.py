
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout

class SpriteGroup:
    def __init__(self):
        self.sprites = []
        self.len = 0

    def __len__(self):
        return self.len

    def __iter__(self):
        return iter(self.sprites)

    def append(self, sprite):
        self.sprites.append(sprite)
        self.len += 1
   
    def start(self):
        for each in self.sprites:
            each.start()
   
    def stop(self):
        for each in self.sprites:
            each.start()

    def restart(self):
        for each in self.sprites:
            each.restart()

    def freeze(self):
        for each in self.sprites:
            each.freeze()

class Sprite(RelativeLayout):
    register = False
    size_ratio = 1.0

    def __init__(self, **kwargs):
        self.image_size = kwargs['size']
        RelativeLayout.__init__(self, size_hint=(None,None), **kwargs)

        self.grid = kwargs['grid']
        self.start_position = self.pos

        self.frozen = False
        self.alive = True
        self.animation = None
        self.safe_pos = self.pos
        self.path = []
        self.moving = False
        self.last_to_tuple = None
        self.move_duration = 0.25

        self.setup()
        self.init()

    def init(self):
        """ This method is called in initiliazation and on restart """
        self.before_init()

        self.frozen = False
        self.alive = True
        self.animation = None
        self.safe_pos = self.pos
        self.path = []
        self.moving = False
        self.last_to_tuple = None

        self.after_init()

    def before_init(self):
        pass

    def after_init(self):
        pass

    def setup(self):
        """ This method is called only in initiliazation """
        raise Exception('This method should be overridden')

    def save_pos(self):
        self.safe_pos = self.pos

    def load_pos(self):
        self.pos = self.safe_pos

    def hide(self):
        self.canvas.clear()

    def die(self):
        if not self.alive or self.parent.frozen:
            return
        print '%s died' % self.__class__.__name__
        self.alive = False
        self.stop() # hm?
        self.hide()
        self.on_death()
        return

    def on_death(self):
        pass

    def on_move_finish(self):
        pass

    def on_every_move(self):
        pass

    def freeze(self):
        self.frozen = True

    def face(self, direction):
        pass

    def continue_move(self):
        if not self.alive:
            return

        self.take_effect()

        if not self.path:
            self.moving = False
            if self.on_move_finish is not None:
                self.on_move_finish()
            self.on_move_finish = None
            self.on_every_move()
            return

        self.moving = True
        destination = self.path.pop()

        if destination.bomb is not None:
            # TODO maybe recalculate path?
            self.path = []
            self.moving = False
            return

        delta_x = abs(destination.pos[0] + self.parent.tile_size[0]/10 - self.pos[0])
        delta_y = abs(destination.pos[1] + self.parent.tile_size[1]/10 - self.pos[1])

        move_duration = self.move_duration

        if delta_x > delta_y:
            move_duration *= delta_x / self.parent.tile_size[0]
            if destination.pos[0] > self.pos[0]:
                self.face('right')
            elif destination.pos[0] < self.pos[0]:
                self.face('left')
        else:
            move_duration *= delta_y / self.parent.tile_size[1]
            if destination.pos[1] > self.pos[1]:
                self.face('top')
            elif destination.pos[1] < self.pos[1]:
                self.face('bottom')

        self.stop_move()

        offset = (self.parent.tile_size[0] - self.size[0])/4

        self.animation = Animation(
                pos=(
                    destination.pos[0] + self.parent.tile_size[0]/10 + offset, 
                    destination.pos[1] + self.parent.tile_size[1]/10 + offset
                ),
                duration=move_duration
        )
        self.animation.on_complete = lambda x: self.continue_move()
        self.animation.start(self)

    def move(self, to_tuple):
        if not self.alive:
            return

        from_tuple = self.grid.get_tile_indexes(*self.center_pos)

        if from_tuple == to_tuple:
            if not self.moving:
                self.grid.get_tile(*from_tuple).add_bomb(self)
                return
        if to_tuple == self.last_to_tuple:
            if self.is_bot():
                raise Exception('kokotina?')
            tile = self.grid.get_tile(*to_tuple)
            self.on_move_finish = lambda : tile.add_bomb(self)
            return

        path = self.grid.find_path(from_tuple, to_tuple)

        if not path:
            return

        self.on_move_finish = None
        self.last_to_tuple = to_tuple

        self.stop_move()
        self.path = path
        self.continue_move()

    def take_effect(self):
        tile = self.get_tile()
        effect = tile.get_effect()
        if effect is not None:
            effect.apply(self)

    def stop_move(self):
        if self.animation is not None:
            self.animation.on_complete = lambda x: self.nothing()
            self.animation.stop(self)

    def restart(self):
        self.before_restart()

        print 'restarting... hmm'
        self.stop()
        self.init()
        self.pos = self.start_position

        self.after_restart()

    def before_restart(self):
        pass

    def after_restart(self):
        pass

    def stop(self):
        self.before_stop()

        self.stop_move()

        self.after_stop()

    def before_stop(self):
        pass

    def after_stop(self):
        pass

    @property
    def center_pos(self):
        return self.center

    def get_tile(self):
        #print 'cp', self.center_pos
        pos_tuple = self.parent.grid.get_tile_indexes(*self.center_pos)
        #print 'pt', pos_tuple
        return self.parent.grid.get_tile(*pos_tuple)

    @property
    def name(self):
        return self.__class__.__name__

    def is_bot(self):
        return True

    def nothing(self):
        pass

    def collide(self, sprite):
        distance_x = abs(self.center_pos[0] - sprite.center_pos[0])
        if distance_x > self.parent.tile_size[0]*0.7:
            return False
        distance_y = abs(self.center_pos[1] - sprite.center_pos[1])
        if distance_y > self.parent.tile_size[1]*0.7:
            return False
        return True
