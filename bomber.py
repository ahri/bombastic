#!/usr/bin/env python

"""
Bomberman Clone
"""

from collections import deque
from udeque import udeque
import os

class Arena(object):
    def __init__(self):
        self.arena = []

    def traverse(self):
        """
        an iterable for traversing the game arena
        """
        for y, row in enumerate(self.arena):
            for x, tile in enumerate(row):
                yield x, y, tile

    def coord_sanity(self, x, y):
        if x < 0 or y < 0:
            raise IndexError("Negative indices don't make sense")

    def tile_get(self, x, y):
        """
        access the values of tiles in the game arena
        """
        self.coord_sanity(x, y)
        return self.arena[y][x]

    def tile_set(self, coords, value):
        """
        set the values of tiles in the game arena
        """
        self.coord_sanity(*coords)
        x, y = coords
        self.arena[y][x] = value

    def tile_has(self, coords, item):
        """
        detect whether a tile has a certain game item in it
        everything has a 0 in it, unfortunately this evaluates to false
        """
        if item == 0:
            self.coord_sanity(*coords)
            return True

        return self.tile_get(*coords) & item

    def tile_add(self, coords, item):
        """
        add an item to a tile
        """
        return self.tile_set(coords, self.tile_get(*coords) | item)

    def tile_remove(self, coords, item):
        """
        remove an item from a tile
        """
        self.tile_set(coords, self.tile_get(*coords) ^ item)

class GameState(Arena):
    """
    Represents the game state
    """

    SPACE = 0
    DESTRUCTABLE = 1
    BLOCK = 2
    SPAWN = 4
    P1 = 8
    P2 = 16
    P3 = 32
    P4 = 64
    P5 = 128
    P6 = 256
    P7 = 512
    P8 = 1024

    def __init__(self):
        """
        simple init of variables
        """
        self.players = udeque()
        self.players_ingame = []

        self.lookup = {
            ' ': self.SPACE,
            '.': self.DESTRUCTABLE,
            'B': self.BLOCK,
            'S': self.SPAWN,
            '1': self.P1,
            '2': self.P2,
            '3': self.P3,
            '4': self.P4,
            '5': self.P5,
            '6': self.P6,
            '7': self.P7,
            '8': self.P8,
        }

        self.player_list = [
            self.P1,
            self.P2,
            self.P3,
            self.P4,
            self.P5,
            self.P6,
            self.P7,
            self.P8,
        ]

        self.rlookup = {}
        for k, v in self.lookup.iteritems():
            self.rlookup[v] = k

        self.arena_load(["arenas", "default.bmm"])

    def arena_load(self, filename_list):
        """
        load an arena from a file
        """
        fp = open(os.sep.join(filename_list), 'r')

        line_length = 0
        lines = []
        for line_number, line in enumerate(fp):
            if len(line) > line_length:
                line_length = len(line)

            lines.append(line)

        fp.close()

        self.arena = [[self.SPACE for x in range(line_length - 1)]
                                  for y in range(line_number + 1)]

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == "\n":
                    break

                self.tile_set((x, y), self.lookup[char])

    def __str__(self):
        """
        produce a string representation of the arena
        in the same format as the map files
        """
        chars = []
        old_y = 0
        for x, y, tile in self.traverse():
            if y != old_y:
                chars.append('\n')
                old_y = y

            chars.append(self.rlookup[tile])

        chars.append('\n')

        return ''.join(chars)

    def player_add(self, player):
        """
        add a player to the game state
        """
        self.players.appendleft(player)

    def get_players(self):
        """
        get currently loaded players
        """
        return self.players

    def spawn(self):
        """
        spawn the players into the arena
        """
        p_no = 0
        for x, y, tile in self.traverse():
            if tile == self.SPAWN and len(self.players):
                self.tile_set((x, y), self.player_list[p_no])
                player = self.players.pop()
                player.number = p_no + 1
                player.item = self.player_list[p_no]
                player.coords = (x, y)
                self.players_ingame.append(player)
                p_no += 1

    def tick(self):
        """
        step to the next game state
        """
        for player in self.players_ingame:
            px, py = player.coords
            nx, ny = -1, -1

            if player.action_current() == None:
                continue
            elif player.action_current() == Player.UP:
                nx, ny = px, py-1
            elif player.action_current() == Player.DOWN:
                nx, ny = px, py+1
            elif player.action_current() == Player.LEFT:
                nx, ny = px-1, py
            elif player.action_current() == Player.RIGHT:
                nx, ny = px+1, py

            if (nx, ny) != (-1, -1):
                self.player_move(player, (nx, ny))


    def player_move(self, player, new_coords):
        """
        move a player
        """
        if self.tile_has(new_coords, self.BLOCK) or self.tile_has(new_coords, self.DESTRUCTABLE):
            return

        self.tile_remove(player.coords, player.item)
        self.tile_add(new_coords, player.item)
        player.coords = new_coords


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
        self.actions = deque()
        self.current = None
        self.coords = ()
        self.item =  -1

    def action_next(self):
        return self.actions.pop()

    def action_add(self, action):
        self.actions.appendleft(action)

    def action_current(self):
        try:
            self.current = self.action_next()
        except IndexError:
            pass

        return self.current
