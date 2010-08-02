#!/usr/bin/env python
"""Bomberman Clone"""

from collections import deque
from udeque import udeque
import os
import random

class Arena(object):

    """Represent a 2D arena whose coord spaces are stackable"""

    def __init__(self, cols, rows):
        """Create the data structure"""
        self.cols = cols
        self.rows = rows
        self.data = [[] for i in xrange(rows*cols)]

    def sanity(self, coords):
        x, y = coords
        if not (0 <= x < self.cols) or not (0 <= y < self.rows):
            raise IndexError("Coords (%d, %d) are not valid: must be in range (0, 0) to (%d, %d)" % (x, y, self.cols-1, self.rows-1))

    def _get_list(self, coords):
        """The 2D -> 1D convertermatron"""
        self.sanity(coords)
        x, y = coords
        return self.data[x+y*self.cols]

    def coords_add(self, coords, obj):
        """Add an object by coords"""
        self._get_list(coords).append(obj)

    def coords_get_real(self, coords):
        """Get the list of objects at a set of coords"""
        return self._get_list(coords)

    def coords_get(self, coords):
        """Get a copy of the list of objects at a set of coords"""
        return self.coords_get_real(coords)[:]

    def coords_remove(self, coords, obj):
        """Remove an object by coords"""
        for i, o in enumerate(self._get_list(coords)):
            if o == obj:
                del self._get_list(coords)[i]
                return o

        raise LookupError("Did not find object")

    # TODO: maybe implement the "have" functions separately so we can use them when iterating

    def coords_have_obj(self, coords, obj):
        """Test for an object by coords"""
        for o in self._get_list(coords):
            if o == obj:
                return True

        return False

    def coords_have_class(self, coords, classref):
        """Test for a class by coords"""
        for o in self._get_list(coords):
            if isinstance(o, classref):
                return True

        return False

    def __iter__(self):
        """Iterate over the coords, providing x, y, list"""
        for i, l in enumerate(self.data):
            x = i % self.cols
            y = i / self.cols
            yield x, y, l

class GameObject(object):

    """
    Extendable class for items represented in the game arena
    Mostly populated with debugging helpers
    """

    DEBUG_CHR = ' '
    ZINDEX = 0

    def __init__(self, **kwargs):
        self.state = kwargs["state"]
        self.coords = kwargs["coords"]
        if self.state:
            self.state.arena.coords_add(self.coords, self)

    def __str__(self):
        """Output debug information"""
        return self.DEBUG_CHR

    def remove(self):
        self.state.arena.coords_remove(self.coords, self)

class Block(GameObject):

    """The indestructible block"""

    DEBUG_CHR = 'B'
    ZINDEX = 1

class PowerupFlame(GameObject):
    DEBUG_CHR = 'f'
    ZINDEX = 1

    def picked_up(self, player):
        player.flame += 1
        self.remove()

class PowerupBomb(GameObject):
    DEBUG_CHR = 'b'
    ZINDEX = 1

    def picked_up(self, player):
        player.bomb += 1
        self.remove()

class DestructibleBlock(GameObject):

    """The indestructible block"""

    DEBUG_CHR = '.'
    ZINDEX = 1

    def flamed(self, flame):
        """What to do when I get flamed; remove self"""
        self.remove()

        rand = random.random()
        if   0.00 <= rand < 0.15:
            PowerupFlame(state=self.state, coords=self.coords)
        elif 0.15 <= rand < 0.30:
            PowerupBomb(state=self.state, coords=self.coords)

class SpawnPoint(GameObject):
    DEBUG_CHR = 'S'
    ZINDEX = 1

    def flamed(self, flame):
        pass

    def picked_up(self, player):
        pass

class Player(GameObject):

    """Represent a player"""

    DEBUG_CHR = 'P'
    ZINDEX = 3

    # constants for actions
    UP    = 1
    DOWN  = 2
    LEFT  = 3
    RIGHT = 4
    BOMB  = 5

    def __init__(self):
        """Set up some defaults"""
        self.state = None
        self.coords = (-1, -1)

        self._bombs_live = []

        self.number = -1
        self.flame = 1
        self.bomb = 1

        self.kills = 0
        self.deaths = 0
        self.suicides = 0

    def spawn(self, number, **kwargs):
        self.number = number
        super(Player, self).__init__(state=kwargs["state"], coords=kwargs["coords"])

    def __str__(self):
        """Output debug information"""
        if -1 < self.number < 10:
            return str(self.number)
        else:
            return self.DEBUG_CHR

    def drop_bomb(self):
        """Drop a bomb on the current coords"""
        if len(self._bombs_live) < self.bomb:
            bomb = Bomb(self)
            self._bombs_live.append(bomb)
            return bomb

        return None

    def flamed(self, flame):
        self.deaths += 1
        if flame.bomb.player == self:
            self.suicides += 1
        else:
            flame.bomb.player.kills += 1
        self.remove()

    def move(self, new_coords):
        """Move a player"""
        objs = []
        for o in self.state.arena.coords_get(new_coords):
            if isinstance(o, (Block, DestructibleBlock, Bomb)):
                return False

            objs.append(o)

        self.remove()
        self.state.arena.coords_add(new_coords, self)
        for o in objs:
            o.picked_up(self)

        self.coords = new_coords

        return True

    def picked_up(self, player):
        pass

class Bomb(GameObject):

    """Boom!"""

    DEBUG_CHR = 'x'
    ZINDEX = 2

    def __init__(self, player):
        """Set up some defaults and references"""
        self.player = player
        self.flame = player.flame
        self.ticks_left = 4
        super(Bomb, self).__init__(state=player.state, coords=player.coords)

    def tick(self):
        """What to do when the game ticks; count down and explode"""
        self.ticks_left -= 1

        if self.ticks_left > 0:
            return

        self.explode()

    def explode(self):
        self.remove()
        self.state.flame_add(self, self.coords)
        self.incinerate(self.coords, (0, -1), self.flame)
        self.incinerate(self.coords, (0, +1), self.flame)
        self.incinerate(self.coords, (-1, 0), self.flame)
        self.incinerate(self.coords, (+1, 0), self.flame)

    def incinerate(self, coords, coord_mod, flame):
        """Recursive function to spread the flames"""
        coords = coords[0] + coord_mod[0], coords[1] + coord_mod[1]
        try:
            self.state.arena.sanity(coords)
        except (IndexError):
            return

        if self.state.arena.coords_have_class(coords, Block):
            return

        self.state.flame_add(self, coords)
        if self.state.arena.coords_have_class(coords, DestructibleBlock):
            return

        if flame == 1:
            return

        self.incinerate(coords,
                        coord_mod,
                        flame-1)

    def flamed(self, flame):
        """What to do when I get flamed; explode"""
        self.explode()


class Flame(GameObject):

    """Crackle"""

    DEBUG_CHR = "~"
    ZINDEX = 4

    def __init__(self, bomb, coords):
        """Set up some defaults and references"""
        self.bomb = bomb
        super(Flame, self).__init__(state=bomb.state, coords=coords)

        objs = []
        for o in self.state.arena.coords_get(coords):
            if o != self:
                o.flamed(self)

    def tick(self):
        """What to do when the game ticks; remove self"""
        self.remove()

    def flamed(self, flame):
        """Don't do anything when flamed"""
        pass

class GameState(object):

    """Represents the game state"""

    def __init__(self):
        "Simple init of variables"
        self._player_queue = udeque()
        self._sticky_actions = {}
        self._action_queue = deque()

        self._lookup = {
            'B': Block,
            '.': DestructibleBlock,
            'S': SpawnPoint,
        }

        self._flames = []

        self.arena_load(["arenas", "default.bmm"])

    def arena_load(self, filename_list):
        """Load an arena from a file"""
        lines = []

        with open(os.sep.join(filename_list), 'r') as fp:
            for line in fp:
                lines.append(line.rstrip())

        self.arena = Arena(reduce(lambda a, b: max(a, b),
                                  map(lambda line: len(line), lines)),
                           len(lines))

        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                if char == ' ':
                    continue

                self._lookup[char](state=self, coords=(col, row))

    def __str__(self):
        """Produce a string representation of the arena in the same format as the map files"""
        chars = []
        old_y = 0
        for x, y, l in self.arena:
            if y != old_y:
                chars.append('\n')
                old_y = y

            chars.append(str(reduce(
                lambda a, b: a.ZINDEX > b.ZINDEX and a or b,
                l,
                GameObject(state=None, coords=None)
            )))

        chars.append('\n')

        return ''.join(chars)

    def player_add(self, player):
        """Add a player to the game state"""
        self._player_queue.appendleft(player)

    def spawn(self):
        """Spawn the players into the arena"""
        p_no = 0
        for x, y, l in self.arena:
            if self.arena.coords_have_class((x, y), SpawnPoint):
                try:
                    player = self._player_queue.pop()
                except (IndexError):
                    break

                p_no += 1
                player.spawn(p_no, state=self, coords=(x, y))
                self._sticky_actions[player] = None

    def tick(self, count=1):
        """Step to the next game state"""
        for _ in xrange(count):
            self._flames_process()
            self._actions_process()
            self._bombs_process()

    def action_add(self, player, action):
        """Add player actions to a queue for processing"""
        self._action_queue.appendleft((player, action))

    def _actions_process(self):
        """Process queued actions or fall back to sticky actions"""
        unexecuted = deque()
        had_turn = []
        while self._action_queue:
            player, action = self._action_queue.pop()
            if player in had_turn:
                unexecuted.appendleft((player, action))
            else:
                self._player_action(player, action)
                self._player_sticky(player, action)
                had_turn.append(player)

        for player in self._sticky_actions:
            if player not in had_turn:
                self._player_action(player, self._sticky_actions[player])

        self._action_queue = unexecuted

    def _player_action(self, player, action):
        """Perform player action"""
        px, py = player.coords

        if action == Player.BOMB:
            player.drop_bomb()
        elif action == Player.UP:
            player.move((px, py-1))
        elif action == Player.DOWN:
            player.move((px, py+1))
        elif action == Player.LEFT:
            player.move((px-1, py))
        elif action == Player.RIGHT:
            player.move((px+1, py))

    def _player_sticky(self, player, action):
        """Add actions to "sticky" lookup, if applicable"""
        if action == Player.BOMB:
            self._sticky_actions[player] = None
        else:
            self._sticky_actions[player] = action

    def _bombs_process(self):
        """Tick bombs and forget about them when their timers run out"""
        for p in self._sticky_actions:
            for i, b in enumerate(p._bombs_live):
                if b.ticks_left == 0:
                    del p._bombs_live[i]
                    continue

                b.tick()

    def flame_add(self, bomb, coords):
        """Add and track some flame"""
        self._flames.append(Flame(bomb, coords))

    def _flames_process(self):
        """Tick the flames and forget about them"""
        for i, f in enumerate(self._flames):
            f.tick()

        self._flames = []

if __name__ == "bomber":
    s = GameState()
    p1 = Player()
    s.player_add(p1)
    s.spawn()
    print(s)

    def up():
        s.action_add(p1, Player.UP)
        tick()

    def down():
        s.action_add(p1, Player.DOWN)
        tick()

    def left():
        s.action_add(p1, Player.LEFT)
        tick()

    def right():
        s.action_add(p1, Player.RIGHT)
        tick()

    def bomb():
        s.action_add(p1, Player.BOMB)
        tick()

    def tick():
        s.tick()
        print(s)
