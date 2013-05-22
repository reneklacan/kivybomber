
import random
import time
import math
from threading import Timer
from constants import *

FIND_ROUTE_TO_PLAYER = 0
HUNT_PLAYER = 1

DESTROY_BLOCK = 0
EVADE_BOMB = 1
PLANT_BOMB = 2
TAKE_POWERUP = 3
MOVING = 4
EVADING = 5
WAITING = 6
STANDING = 7

string_states = {}
string_states[DESTROY_BLOCK] = 'DESTROY_BLOCK'
string_states[EVADE_BOMB] = 'EVADE_BOMB'
string_states[PLANT_BOMB] = 'PLANT_BOMB'
string_states[TAKE_POWERUP] = 'TAKE_POWERUP'
string_states[MOVING] = 'MOVING'
string_states[EVADING] = 'EVADING'
string_states[WAITING] = 'WAITING'
string_states[STANDING] = 'STANDING'

class AIMap:
    def __init__(self, map):
        self.grid = map
        self.layout = [[None for x in range(self.grid.grid_size[0])] for y in range(self.grid.grid_size[1])]
        self.print_time = 0
        self.score_map = None
        self.danger_map = [[False for x in range(self.grid.grid_size[0])] for y in range(self.grid.grid_size[1])]
        self.bomb_counter = 1

    def reset(self):
        self.layout = [[None for x in range(self.grid.grid_size[0])] for y in range(self.grid.grid_size[1])]
        self.score_map = None

    def evaluate(self, grid):
        if self.score_map is None:
            self.score_map = [[None for x in range(self.grid.grid_size[0])] for y in range(self.grid.grid_size[1])]

            for iy in range(self.grid.grid_size[1]):
                for ix in range(self.grid.grid_size[0]):
                    tile = grid.get_tile(ix, iy)
                    score = 0
                    if tile.is_space():
                        for neighbor in tile.tiles_around():
                            if neighbor.is_block():
                                score += 1
                    self.score_map[iy][ix] = score
        else:
            # TODO layout changes
            print 'changer', grid.changes
            while grid.changes:
                tile = grid.changes.pop()
                for pos in [tile] + tile.tiles_around():
                    score = 0
                    if pos.is_space():
                        for neighbor in pos.tiles_around():
                            if neighbor.is_block():
                                score += 1
                    self.score_map[pos.iy][pos.ix] = score
                    if pos in grid.changes:
                        grid.changes.remove(pos)

    def printmap(self, layout=None):
        #if self.print_time + 0.5 > time.time():
        #    return
        self.print_time = time.time()

        if layout is None:
            layout = self.layout
        #print(40 * '-')
        #print(self.layout)
        output = ''
        for row in layout:
            for item in row:
                if item is None:
                    item = 'N'
                elif type(item) is int:
                    if item > 60 and item < 70:
                        item = 'F'
                elif type(item) is bool:
                    if item == False:
                        item = '.'
                output += '%3s' % item
            output += '\n'
        print 43 * '-'
        print output

    def distance(self, pos1, pos2):
        return math.sqrt(math.pow(abs(pos1.ix - pos2.ix), 2) + math.pow(abs(pos1.iy - pos2.iy), 2))

    def get_bomb_id(self):
        bomb_id = self.bomb_counter
        self.bomb_counter += 1
        return bomb_id

    def clean_danger(self, bomb_id, tile, strength):
        if self.danger_map[tile.iy][tile.ix] == bomb_id:
            self.danger_map[tile.iy][tile.ix] = False

        ix = tile.ix
        iy = tile.iy

        for i in range(strength):
            ixiys = [
                (ix - (i + 1),  iy),
                (ix + (i + 1),  iy),
                (ix,            iy + (i + 1)),
                (ix,            iy - (i + 1)),
            ]

            for x, y in ixiys:
                if x > 0 and x < self.grid.grid_size[0] and y > 0 and y < self.grid.grid_size[1]:
                    if self.danger_map[y][x] == bomb_id:
                        self.danger_map[y][x] = False

    def plant_bomb(self, player, tile):
        bomb_id = self.get_bomb_id()
        self.danger_map[tile.iy][tile.ix] = bomb_id

        ix = tile.ix
        iy = tile.iy
        
        for i in range(player.bomb_power):
            ixiys = [
                (ix - (i + 1),  iy),
                (ix + (i + 1),  iy),
                (ix,            iy + (i + 1)),
                (ix,            iy - (i + 1)),
            ]

            for x, y in ixiys:
                if x > 0 and x < self.grid.grid_size[0] and y > 0 and y < self.grid.grid_size[1]:
                    self.danger_map[y][x] = bomb_id

        safe_time = player.bomb_timeout + player.flame_timeout
        Timer(safe_time, self.clean_danger, args=[bomb_id, tile, player.bomb_power]).start()

    def is_safe(self, pos):
        return not self.danger_map[pos.iy][pos.ix]

    def contain(self, pos):
        if self.layout[pos.iy][pos.ix] is None:
            return False
        return True

class AIPlayer:
    def __init__(self, player):
        self.player = player
        self.alive = True
        self.state = FIND_ROUTE_TO_PLAYER
        self.substate = STANDING
        self.next_substate = None
        self.last_plant = 0
        self.grid = player.grid
        self.aimap = player.grid.aimap
        self.substate_timeout = None

    def set_substate(self, substate, force=False):
        if self.substate_timeout is not None:
            self.substate_timeout.cancel()
            self.substate_timeout = None
        if not force and self.substate == MOVING:
            self.next_substate = substate
        else:
            #print('AIPlayer substate: %s -> %s' % (string_states[self.substate], string_states[substate]))
            self.substate = substate

    def get_move(self):
        from_tuple = self.grid.get_tile_indexes(*self.player.center_pos)
        current_pos = self.grid.get_tile(*from_tuple)
        current_pos = self.player.get_tile()
        self.aimap.reset()
        #self.aimap.print(self.aimap.danger_map)

        if self.state == FIND_ROUTE_TO_PLAYER:
            #print 'substate', string_states[self.substate]
            if self.substate == STANDING:
                if not self.aimap.is_safe(current_pos):
                    self.set_substate(EVADE_BOMB)
                else:
                    self.set_substate(DESTROY_BLOCK)
                return self.get_move()
            elif self.substate == PLANT_BOMB:
                if self.plant_bomb():
                    self.aimap.plant_bomb(self.player, current_pos)
                    self.set_substate(EVADE_BOMB)
                    safe_time = self.player.bomb_timeout + self.player.flame_timeout

                    self.substate_timeout = Timer(
                            safe_time, self.set_substate, [DESTROY_BLOCK]
                    )
                    self.substate_timeout.start()
                    return self.get_move()
                else:
                    #print('bomb plant fail')
                    self.set_substate(WAITING)
                    return self.get_move()
            elif self.substate == WAITING:
                if not self.aimap.is_safe(current_pos):
                    self.set_substate(EVADE_BOMB)
                    return self.get_move()
                else:
                    if self.substate_timeout is None:
                        self.substate_timeout = Timer(0.1, self.set_substate, [DESTROY_BLOCK])
                        self.substate_timeout.start()
                    return None
            elif self.substate == EVADE_BOMB:
                if self.aimap.is_safe(current_pos):
                    print 'safe'
                    self.set_substate(WAITING)
                    return None
                else:
                    coords = current_pos.tiles_around(space=True)
                    best_move = None

                    while coords:
                        pos = coords.pop()
                        if self.aimap.is_safe(pos):
                            best_move = pos
                            break
                        self.aimap.layout[pos.iy][pos.ix] = pos.type
                        around = pos.tiles_around(space=True)
                        for item in around:
                            if not self.aimap.contain(item):
                                coords.insert(0, item)
                            
                    #print('best move (x:%d, y:%d)' % (best_move.ix, best_move.iy))

                    if best_move is None:
                        self.set_substate(WAITING)
                        return None
                    if best_move is not None and best_move == current_pos:
                        self.set_substate(WAITING)
                        return None
                    else:
                        from_tuple = (current_pos.ix, current_pos.iy)
                        path = self.grid.find_path(from_tuple, best_move.get_index_tuple())
                        if not path:
                            return
                        first_move = path[-1]

                        self.set_substate(STANDING)
                        return (first_move.ix, first_move.iy)

                        #self.aimap.print()

            elif self.substate == DESTROY_BLOCK:
                if not self.aimap.is_safe(current_pos):
                    print('not safe')
                    self.set_substate(EVADE_BOMB)
                    return self.get_move()

                coords = [current_pos]

                closest_player = None
                closest_player_distance = 9999

                enemy = self.player.parent.player
                distance = self.aimap.distance(enemy.get_tile(), current_pos)
                if distance < closest_player_distance:
                    closest_player = enemy
                    closest_player_distance = distance

                #print('closest player (x:%d, y:%d)' % (closest_player.ix, closest_player.iy))

                self.aimap.evaluate(self.grid)

                best_move = None
                best_move_score = 0

                attack_pos = None
                attack_pos_distance = 9999

                while coords:
                    pos = coords.pop()
                    if self.aimap.contain(pos):
                        continue
                    self.aimap.layout[pos.iy][pos.ix] = pos.type
                    if pos.is_space():
                        coords += pos.tiles_around()
                        if closest_player is not None: 
                            distance = self.aimap.distance(closest_player.get_tile(), pos)
                            if distance < attack_pos_distance:
                                attack_pos = pos
                                attack_pos_distance = distance
                        score = self.aimap.score_map[pos.iy][pos.ix]
                        if score > best_move_score:
                            best_move = pos
                            best_move_score = self.aimap.score_map[pos.iy][pos.ix]

                #print 'dtsnace map'
                #self.aimap.printmap(self.aimap.distance_map)
                #print('attack pos (x:%d, y:%d)' % (attack_pos.ix, attack_pos.iy))
                #print('attack pos distance (%d)' % distance)

                if attack_pos is not None:
                    self.aimap.score_map[attack_pos.iy][attack_pos.ix] += 3.5
                    score = self.aimap.score_map[attack_pos.iy][attack_pos.ix]

                    if score > best_move_score:
                        best_move = attack_pos
                        best_move_score = score

                    attack_moves = attack_pos.tiles_around(space=True)

                    for move in attack_moves:
                        self.aimap.score_map[move.iy][move.ix] += 4.0
                        score = self.aimap.score_map[move.iy][move.ix]

                        if score > best_move_score:
                            best_move = move
                            best_move_score = score

                    #print 'score map'
                    #self.aimap.printmap(self.aimap.score_map)

                    self.aimap.score_map[attack_pos.iy][attack_pos.ix] -= 3.5
                    for move in attack_moves:
                        self.aimap.score_map[move.iy][move.ix] -= 4.0

                #print('best move (x:%d, y:%d, score:%d)' % (best_move.ix, best_move.iy, best_move_score))


                """
                for player in self.grid.players.values():
                    if player == self:
                        continue
                    self.aimap.layout[player.iy][player.ix] = 'P'
                """

                if best_move is None:
                    print('best move does not exists')
                    self.set_substate(WAITING)
                    return self.get_move()
                elif best_move == current_pos:
                    self.set_substate(PLANT_BOMB)
                    return self.get_move()
                else:
                    from_tuple = current_pos.get_index_tuple()
                    to_tuple = best_move.get_index_tuple()

                    path = self.grid.find_path(from_tuple, to_tuple)
                    if not path:
                        self.set_substate(STANDING)
                        return None
                    first_move = path.pop()

                    if not self.aimap.is_safe(first_move):
                        self.set_substate(EVADE_BOMB)
                        return self.get_move()

                    return (first_move.ix, first_move.iy)

                    #self.aimap.print()
                    #self.aimap.reset()

    def plant_bomb(self):
        if not self.alive:
            return False
        safe_time = self.player.bomb_timeout + self.player.flame_timeout
        if time.time() - self.last_plant < safe_time:
            return False
        planted = self.player.get_tile().add_bomb(self.player)
        if planted:
            self.last_plant = time.time()
        return planted

    def print_state(self):
        if self.state == STANDING:
            print('state = STANDING')
        elif self.state == MOVING:
            print('state = MOVING')
        elif self.state == HIDING:
            print('state = HIDING')
        elif self.state == WAITING:
            print('state = WAITING')
        elif self.state == PLANTING:
            print('state = PLANTING')
