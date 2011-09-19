#!/usr/bin/env python
"""Bomberman Clone"""

from collections import deque
from udeque import udeque
from arena import Arena
import os
import random
import codecs

class GameObject(object):

    """
    Extendable class for items represented in the game arena
    Mostly populated with debugging helpers
    """

    DEBUG_CHR = ' '
    ZINDEX = 0

    def __init__(self, state, coords):
        self.state = state
        self.coords = coords
        if self.state:
            self.state.arena.coords_add(self.coords, self)

    def __str__(self):
        """Output debug information"""
        return self.DEBUG_CHR

    def remove(self):
        """Lots of game objects need to remove themselves, so it's centralised here"""
        self.state.arena.coords_remove(self.coords, self)

    def __repr__(self):
        return '<%s %s 0x%x>' % (self.__class__.__name__, str(self.coords), id(self))

class Block(GameObject):

    """The indestructible block"""

    DEBUG_CHR = 'B'
    ZINDEX = 1

class Powerup(GameObject):

    """Base class for powerups"""

    ZINDEX = 1

    def flamed(self, _):
        """When flamed, remove"""
        self.remove()

class PowerupFlame(Powerup):

    """Longer flames!"""

    DEBUG_CHR = 'f'
    ZINDEX = 1

    def picked_up(self, player):
        """When picked up by a player, increased that player's powerup stats"""
        player.flame += 1
        self.remove()

class PowerupBomb(Powerup):

    """More bombs!"""

    DEBUG_CHR = 'b'
    ZINDEX = 1

    def picked_up(self, player):
        """When picked up by a player, increased that player's powerup stats"""
        player.bomb += 1
        self.remove()

class DestructibleBlock(GameObject):

    """The destructible block"""

    DEBUG_CHR = '.'
    ZINDEX = 1

    def flamed(self, _):
        """What to do when I get flamed; remove self, spawn a powerup (maybe)"""
        self.remove()

        rand = random.random()
        if   0.00 <= rand < 0.15:
            PowerupFlame(state=self.state, coords=self.coords)
        elif 0.15 <= rand < 0.30:
            PowerupBomb(state=self.state, coords=self.coords)

class SpawnPoint(GameObject):

    """Starting point for spawned players"""

    DEBUG_CHR = 'S'
    ZINDEX = 1

    def flamed(self, flame):
        """SpawnPoints are indestructible"""
        pass

    def picked_up(self, player):
        """SpawnPoints cannot be picked up"""
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
        self.coords = None

        self._bombs_live = []

        self.number = None
        self.flame = 1
        self.bomb = 1

        self.kills = 0
        self.deaths = 0
        self.suicides = 0

        self.name = 'Nameless'

    def spawn(self, number, state, coords):
        """Do our (delayed) init"""
        self.number = number
        super(Player, self).__init__(state=state, coords=coords)

    def __str__(self):
        """Output debug information"""
        if -1 < self.number < 10:
            return str(self.number)
        else:
            return self.DEBUG_CHR

    def drop_bomb(self):
        """Drop a bomb on the current coords"""
        if self.state.arena.coords_have_class(self.coords, Bomb):
            return None

        if len(self._bombs_live) >= self.bomb:
            return None

        bomb = Bomb(self)
        return bomb


    def flamed(self, flame):
        """What happens when a player catches fire? Depends whose fault it is..."""
        self.deaths += 1
        if flame.bomb.player == self:
            self.suicides += 1
        else:
            flame.bomb.player.kills += 1
        self.remove()
        self.coords = None

    def move(self, new_coords):
        """Move a player"""
        objs = []
        for o in self.state.arena.coords_get(new_coords):
            if isinstance(o, (Block, DestructibleBlock, Bomb)):
                return False

            objs.append(o)

        self.remove()
        self.state.arena.coords_add(new_coords, self)
        self.coords = new_coords
        for o in objs:
            o.picked_up(self)

        return True

    def picked_up(self, player):
        """Picked up by another player? Nah"""
        pass

class Bomb(GameObject):

    """Boom!"""

    DEBUG_CHR = 'x'
    ZINDEX = 2

    def __init__(self, player):
        """Set up some defaults and references"""
        player._bombs_live.append(self)
        self.player = player
        self.original_owner = player # exists for cases where the bomb changes owner, e.g. when flamed by another player
        self.flame = player.flame
        self.ticks_left = 4
        super(Bomb, self).__init__(player.state, player.coords)

    def tick(self):
        """What to do when the game ticks; count down and explode"""
        self.ticks_left -= 1

        if self.ticks_left > 0:
            return

        self.explode()

    def explode(self):
        """Probably the most important method in the game"""
        self.remove()
        FlameCross(self, self.coords)
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

        # keep note if we have a DestructibleBlock, as it'll removed itself before we check on it
        destructible = self.state.arena.coords_have_class(coords, DestructibleBlock)

        if flame > 1 and not destructible:
            if coord_mod == (0, -1) or coord_mod == (0, +1):
                FlameVt(self, coords)
            if coord_mod == (-1, 0) or coord_mod == (+1, 0):
                FlameHz(self, coords)
        else:
            if coord_mod == (0, -1):
                FlameEndUp(self, coords)
            if coord_mod == (0, +1):
                FlameEndDown(self, coords)
            if coord_mod == (-1, 0):
                FlameEndLeft(self, coords)
            if coord_mod == (+1, 0):
                FlameEndRight(self, coords)

        if destructible:
            return

        if flame == 1:
            return

        self.incinerate(coords,
                        coord_mod,
                        flame-1)

    def flamed(self, flame):
        """What to do when I get flamed; become property of flamer and explode"""
        self.player = flame.bomb.player
        self.explode()

    def remove(self):
        self.original_owner._bombs_live.remove(self)
        super(Bomb, self).remove()

class Flame(GameObject):

    """Crackle"""

    DEBUG_CHR = "~"
    ZINDEX = 4

    def __init__(self, bomb, coords):
        """Set up some defaults and references"""
        self.bomb = bomb
        super(Flame, self).__init__(bomb.state, coords)

        self.state._flames.append(self)

        for o in self.state.arena.coords_get(coords):
            if o != self:
                o.flamed(self)

    def tick(self):
        """What to do when the game ticks; remove self"""
        self.remove()

    def flamed(self, flame):
        """Turn into a FlameCross"""
        flame.remove()
        if (self.__class__ == FlameHz and flame.__class__ == FlameVt) or \
           (self.__class__ == FlameVt and flame.__class__ == FlameHz):
            FlameCross(self.bomb, self.coords)
            self.remove()

    def picked_up(self, player):
        """What to do when a player picks us up?; flame 'em"""
        player.flamed(self)

    def remove(self):
        self.state._flames.remove(self)
        super(Flame, self).remove()

class FlameCross(Flame):

    """Horizonal/Vertical flame"""

    DEBUG_CHR = "+"

class FlameHz(Flame):

    """Horizonal flame"""

    DEBUG_CHR = "-"

class FlameVt(Flame):

    """Vertical flame"""

    DEBUG_CHR = "|"

class FlameEndUp(Flame):

    """Flame endpoint"""

    DEBUG_CHR = "^"

class FlameEndDown(Flame):

    """Flame endpoint"""

    DEBUG_CHR = "v"

class FlameEndLeft(Flame):

    """Flame endpoint"""

    DEBUG_CHR = "<"

class FlameEndRight(Flame):

    """Flame endpoint"""

    DEBUG_CHR = ">"

class GameState(object):

    """Represents the game state"""

    def __init__(self):
        "Simple init of variables"
        self._debug = False
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

    def track_debug(self):
        if self._debug == False:
            return

        if type(self._debug) is not deque:
            self._debug = deque()

        self._debug.append(dict(state=str(self),
                                player_queue=self._player_queue,
                                sticky_actions=self._sticky_actions,
                                action_queue=self._action_queue,
                                flames=self._flames))

        while len(self._debug) > 10:
            self._debug.popleft()

    def arena_load(self, filename_list):
        """Load an arena from a file"""
        lines = []

        with codecs.open(os.sep.join(filename_list), 'r', 'UTF-8') as fp:
            for line in fp:
                lines.append(line.rstrip())

        self.arena = Arena(max((len(line) for line in lines)), len(lines))

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

            chars.append(str(max(l + [GameObject(state=None, coords=None)],
                                 key=lambda o: o.ZINDEX)))

        chars.append('\n')

        return ''.join(chars)

    def __repr__(self):
        return str(self)

    def player_add(self, player):
        """Add a player to the game state"""
        self._player_queue.appendleft(player)

    def player_remove(self, player):
        """Remove a player from the game state"""
        player.remove()

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
        """Step to the next game state: this is an example and is used for testing"""
        for _ in xrange(count):
            self._flames_process()
            self._actions_process()
            self._bombs_process()

    def action_add(self, player, action):
        """Add player actions to a queue for processing"""
        self._action_queue.appendleft((player, action))

    def _actions_process(self):
        """Process queued actions or fall back to sticky actions"""
        self.track_debug()
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
        self.track_debug()

    def _player_action(self, player, action):
        """Perform player action"""
        try:
            px, py = player.coords
        except TypeError:
            # coords are invalid, player is not in the arena: noop
            return

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
        self.track_debug()
        for p in self._sticky_actions:
            for b in p._bombs_live[:]:
                b.tick()
        self.track_debug()

    def _flames_process(self):
        """Tick the flames and forget about them"""
        self.track_debug()
        # copy the list so we don't get confused
        for f in self._flames[:]:
            f.tick()
        self.track_debug()
