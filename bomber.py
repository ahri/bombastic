#!/usr/bin/env python
"""Bomberman Clone"""

from collections import deque
from udeque import udeque
import os

class Arena(object):
    """Represent a 2D arena whose coord spaces are stackable"""

    def __init__(self, cols, rows):
        """Create the data structure"""
        self.cols = cols
        self.rows = rows
        self.data = [[] for i in xrange(rows*cols)]

    def _get_list(self, x, y):
        """The 2D -> 1D convertermatron"""
        return self.data[x+y*self.cols]

    def coords_add(self, coords, obj):
        """Add an object by coords"""
        self._get_list(*coords).append(obj)

    def coords_get(self, x, y):
        """Get a list of objects by coords"""
        return self._get_list(x, y)

    def coords_remove(self, coords, obj):
        """Remove an object by coords"""
        for i, o in enumerate(self._get_list(*coords)):
            if o == obj:
                del self._get_list(*coords)[i]
                return o

        raise LookupError("Did not find object")

    # TODO: maybe implement the "have" functions separately so we can use them when iterating

    def coords_have_obj(self, coords, obj):
        """Test for an object by coords"""
        for o in self._get_list(*coords):
            if o == obj:
                return True

        return False

    def coords_have_class(self, coords, classref):
        """Test for a class by coords"""
        for o in self._get_list(*coords):
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
    pass

class Block(GameObject):
    def __str__(self):
        return 'B'

class Destructible(GameObject):
    def __str__(self):
        return '.'

class SpawnPoint(GameObject):
    def __str__(self):
        return 'S'

class Player(GameObject):
    """Represent a player"""

    # constants for actions
    UP    = 1
    DOWN  = 2
    LEFT  = 3
    RIGHT = 4
    BOMB  = 5

    def __init__(self):
        self.number = -1
        self.coords = (-1, -1)

    def __str__(self):
        return 'P'

# TODO: Person class with name/score etc. (Player should be created with Person in __init__())

class GameState(object):
    """Represents the game state"""

    def __init__(self):
        "Simple init of variables"
        self.player_queue = udeque()
        self.sticky_actions = {}
        self.action_queue = deque()

        self.lookup = {
            'B': Block,
            '.': Destructible,
            'S': SpawnPoint,
        }

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

                self.arena.coords_add((col, row), self.lookup[char]())

    def __str__(self):
        """Produce a string representation of the arena in the same format as the map files"""
        chars = []
        old_y = 0
        for x, y, l in self.arena:
            if y != old_y:
                chars.append('\n')
                old_y = y

            try:
                chars.append(str(l[0]))
            except (IndexError):
                chars.append(' ')

        chars.append('\n')

        return ''.join(chars)

    def player_add(self, player):
        """Add a player to the game state"""
        self.player_queue.appendleft(player)

    def get_players(self):
        """Get currently loaded players"""
        return self.player_queue

    def spawn(self):
        """Spawn the players into the arena"""
        p_no = 0
        for x, y, l in self.arena:
            if self.arena.coords_have_class((x, y), SpawnPoint):
                try:
                    player = self.player_queue.pop()
                except (IndexError):
                    break

                p_no += 1
                self.arena.coords_add((x, y), player)
                player.number = p_no
                player.coords = (x, y)
                self.sticky_actions[player] = None

    def tick(self):
        """Step to the next game state"""
        self._actions_process()
        self._bombs_process()

    def _player_move(self, player, new_coords):
        """Move a player"""
        if self.arena.coords_have_class(new_coords, Block) or self.arena.coords_have_class(new_coords, Destructible):
            return False

        self.arena.coords_remove(player.coords, player)
        self.arena.coords_add(new_coords, player)

        player.coords = new_coords

        return True

    def action_add(self, player, action):
        self.action_queue.appendleft((player, action))

    def _actions_process(self):
        unexecuted = deque()
        had_turn = []
        while self.action_queue:
            player, action = self.action_queue.pop()
            if player in had_turn:
                unexecuted.appendleft((player, action))
            else:
                self._player_action(player, action)
                self._player_sticky(player, action)
                had_turn.append(player)

        for player in self.sticky_actions:
            if player not in had_turn:
                self._player_action(player, self.sticky_actions[player])

        self.action_queue = unexecuted

    def _player_action(self, player, action):
        px, py = player.coords
        nx, ny = -1, -1

        if action == Player.BOMB:
            pass
        elif action == Player.UP:
            nx, ny = px, py-1
        elif action == Player.DOWN:
            nx, ny = px, py+1
        elif action == Player.LEFT:
            nx, ny = px-1, py
        elif action == Player.RIGHT:
            nx, ny = px+1, py

        if (nx, ny) != (-1, -1):
            self._player_move(player, (nx, ny))

    def _player_sticky(self, player, action):
        if action == Player.BOMB:
            self.sticky_actions[player] = None
        else:
            self.sticky_actions[player] = action

    def _bombs_process(self):
        pass
