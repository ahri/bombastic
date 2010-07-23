#!/usr/bin/env python

"""
Bomberman Clone
"""

from collections import deque
from udeque import udeque

class GameState(object):
    """
    Represents the game state
    """
    def __init__(self):
        """
        simple init of variables
        """
        self._arena = """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BS ................................. SB
B B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B B
BS ................................. SB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"""
        self._players = udeque()

    def load_arena(self, arena_file):
        """
        load an arena from a file
        """
        arena = open(arena_file, 'r')
        self._arena = arena.read()
        arena.close()

    def get_arena(self):
        return self._arena

    arena = property(get_arena, load_arena)

    def add_player(self, player):
        """
        add a player to the game state
        """
        self._players.appendleft(player)

    def get_players(self):
        """
        get currently loaded players
        """
        return self._players

    def spawn(self):
        """
        spawn the players into the arena
        TODO: move this to Arena class
        """
        p_no = 1
        arena = ''
        for tile in self.arena:
            if tile == 'S' and len(self._players):
                arena += p_no.__str__()
                player = self._players.pop()
                player.number = p_no
                p_no += 1
            else:
                arena += tile

        self._arena = arena

    def tick(self):
        pass

class Player(object):
    """
    represent a player
    """

    # constants for actions
    UP    = 1
    DOWN  = 2
    LEFT  = 3
    RIGHT = 4
    BOMB  = 5

    def __init__(self):
        self.number = 0
        self._actions = deque()

    def action_next(self):
        return self._actions.pop()

    def action_add(self, action):
        self._actions.appendleft(action)

    act = property(action_next, action_add)

class Arena(object):
    pass
