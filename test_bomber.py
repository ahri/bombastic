#!/usr/bin/env python
"""
Tests for bomber module
"""

from bomber import GameState, Player
import os

class TestGameState:
    def test_arena(self):
        """
        Default arena returned
        """
        state = GameState()
        assert state.arena == """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
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

    def test_load_arena(self):
        """
        Load a arena from a file
        """
        state = GameState()
        arena = open(os.sep.join(["arenas", "test.bmm"]), 'r')
        state.load_arena(os.sep.join(["arenas", "test.bmm"]))

        assert state.arena == arena.read()
        arena.close()

    def test_add_player(self):
        """
        Add a player to the game
        """
        state = GameState()
        player = Player()
        state.add_player(player)
        assert player in state.get_players()

    def test_spawn_players(self):
        """
        Spawn (add to arena) players
        """
        state = GameState()
        p1 = Player()
        p2 = Player()
        state.add_player(p1)
        state.add_player(p2)
        state.spawn()
        assert state.arena == """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
B1 ................................. 2B
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

    def test_player_number(self):
        """
        Check player numbers
        """
        state = GameState()
        p1 = Player()
        state.add_player(p1)
        state.add_player(p1) # try and break with copies of p1
        state.spawn()
        assert p1.number == 1

    def test_player_order(self):
        """
        Check player numbers
        """
        state = GameState()
        p1 = Player()
        p2 = Player()
        p3 = Player()
        p4 = Player()
        p5 = Player()
        state.add_player(p1)
        state.add_player(p1) # just to mess with stuff
        state.add_player(p2)
        state.add_player(p3)
        state.add_player(p4)
        state.add_player(p5) # too many players
        state.spawn()
        assert p1.number == 1
        assert p2.number == 2
        assert p3.number == 3
        assert p4.number == 4
        assert p5.number == 0

    def est_move(self): # TODO
        """
        Move players
        """
        state = GameState()
        p1 = Player()
        state.add_player(p1)
        state.spawn()
        p1.act = Player.DOWN
        state.tick()
        # TODO: py.test exhibits weird behaviour if a test comparing to a triplequote fails -- investigate and patch?
        assert state.arena == """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
B  ................................. 2B
B1B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B B
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

class TestPlayer:
    def test_actions(self):
        """
        A series of actions should be entered and pulled out properly
        """
        p1 = Player()
        p1.act = Player.DOWN
        p1.act = Player.LEFT
        p1.act = Player.BOMB
        p1.act = Player.RIGHT
        p1.act = Player.RIGHT
        p1.act = Player.RIGHT
        assert p1.act == Player.DOWN
        assert p1.act == Player.LEFT
        assert p1.act == Player.BOMB
        assert p1.act == Player.RIGHT
        assert p1.act == Player.RIGHT
        assert p1.act == Player.RIGHT
