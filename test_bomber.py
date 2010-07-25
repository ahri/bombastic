#!/usr/bin/env python
"""
Tests for bomber module
"""

from py import test
from bomber import GameState, Player
import os

class TestArena:
    def test_tile_get(self):
        state = GameState()
        state.arena_load(["arenas", "test.bmm"])
        assert state.tile_get(0, 0) == GameState.BLOCK
        assert state.tile_get(1, 1) == GameState.SPAWN
        assert state.tile_get(6, 6) == GameState.BLOCK

        with test.raises(IndexError):
            state.tile_get(-1, 0)

        with test.raises(IndexError):
            state.tile_get(0, -1)

        with test.raises(IndexError):
            state.tile_get(0, 7)

        with test.raises(IndexError):
            state.tile_get(7, 0)

        with test.raises(IndexError):
            state.tile_get(7, 7)

    def test_coord_sanity(self):
        state = GameState()
        assert state.coord_sanity(0, 0) is None

        with test.raises(IndexError):
            state.coord_sanity(-1, 0)

        with test.raises(IndexError):
            state.coord_sanity(0, -1)

        with test.raises(IndexError):
            state.coord_sanity(-1, -1)

    def test_tile_has(self):
        state = GameState()
        state.arena_load(["arenas", "test.bmm"])
        assert state.tile_get(0, 0) == GameState.BLOCK
        assert state.tile_has((0, 0), 0) # all tiles should have 0

class TestGameState:
    """
    Tests for Game class
    """

    def test_arena(self):
        """
        Default arena returned
        """
        state = GameState()
        arena = open(os.sep.join(["arenas", "default.bmm"]), 'r')
        assert str(state) == arena.read()
        arena.close()

    def test_arena_load(self):
        """
        Load a arena from a file
        """
        state = GameState()
        arena = open(os.sep.join(["arenas", "test.bmm"]), 'r')
        state.arena_load(["arenas", "test.bmm"])

        assert str(state) == arena.read()
        arena.close()

    def test_player_add(self):
        """
        Add a player to the game
        """
        state = GameState()
        player = Player()
        state.player_add(player)
        assert player in state.get_players()

    def test_player_number(self):
        """
        Check player numbers
        """
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.player_add(p1) # try and break with copies of p1
        state.spawn()
        assert p1.number == 1

    def test_player_spawn(self):
        """
        Check player numbers and spawn positions
        """
        state = GameState()
        p1 = Player()
        p2 = Player()
        p3 = Player()
        p4 = Player()
        p5 = Player()
        state.player_add(p1)
        state.player_add(p1) # just to mess with stuff
        state.player_add(p2)
        state.player_add(p3)
        state.player_add(p4)
        state.player_add(p5) # too many players
        state.spawn()
        assert p1.number == 1
        assert p2.number == 2
        assert p3.number == 3
        assert p4.number == 4
        assert p5.number == 0

        assert p1.coords == (1, 1)
        assert p2.coords == (37, 1)
        assert p3.coords == (1, 17)
        assert p4.coords == (37, 17)

        assert state.tile_get(1, 1)   == GameState.P1
        assert state.tile_get(37, 1)  == GameState.P2
        assert state.tile_get(1, 17)  == GameState.P3
        assert state.tile_get(37, 17) == GameState.P4

    def test_player_current(self):
        """
        Player current action
        """
        p1 = Player()
        p1.action_add(Player.DOWN)
        p1.action_add(Player.UP)
        assert p1.action_current() == Player.DOWN
        assert p1.action_current() == Player.UP
        assert p1.action_current() == Player.UP
        p1.action_add(Player.LEFT)
        assert p1.action_current() == Player.LEFT

    def test_tile_add(self):
        state = GameState()
        coords = (1, 2)
        assert state.tile_get(*coords) == GameState.SPACE
        state.tile_add(coords, GameState.BLOCK)
        assert state.tile_get(*coords) == GameState.BLOCK
        assert state.tile_has(coords, GameState.SPACE)
        assert state.tile_has(coords, GameState.BLOCK)

    def test_tile_remove(self):
        state = GameState()
        coords = (1, 1)
        assert state.tile_get(*coords) == GameState.SPAWN
        state.tile_remove(coords, GameState.SPAWN)
        assert state.tile_get(*coords) == GameState.SPACE

    def test_move(self):
        """
        Move players
        """
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert state.tile_get(1, 1) == GameState.P1
        assert state.tile_get(1, 2) == GameState.SPACE
        state.player_move(p1, (1, 2))
        assert state.tile_get(1, 1) == GameState.SPACE
        assert state.tile_get(1, 2) == GameState.P1

        assert state.tile_get(0, 0) == GameState.BLOCK
        state.player_move(p1, (0, 0))
        assert str(state) # asserting that state is still sane (i.e. player is not overlayed on block)
        assert state.tile_get(1, 3) == GameState.DESTRUCTABLE
        state.player_move(p1, (1, 3))
        assert str(state) # asserting that state is still sane (i.e. player is not overlayed on destructable)

    def test_tick(self):
        """
        Tick the game and check player position
        """
        state = GameState()
        assert state.tick() == None
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert state.tick() == None

        coords_start = (1, 1)
        coords_vt = (1, 2)
        coords_hz = (2, 1)

        assert state.tile_get(*coords_start) == GameState.P1
        assert state.tile_get(*coords_vt) == GameState.SPACE
        p1.action_add(Player.DOWN)
        state.tick()
        assert state.tile_get(*coords_start) == GameState.SPACE
        assert state.tile_get(*coords_vt) == GameState.P1
        p1.action_add(Player.UP)
        state.tick()
        assert state.tile_get(*coords_start) == GameState.P1
        assert state.tile_get(*coords_vt) == GameState.SPACE
        p1.action_add(Player.RIGHT)
        state.tick()
        assert state.tile_get(*coords_start) == GameState.SPACE
        assert state.tile_get(*coords_hz) == GameState.P1
        p1.action_add(Player.LEFT)
        state.tick()
        assert state.tile_get(*coords_start) == GameState.P1
        assert state.tile_get(*coords_hz) == GameState.SPACE

class TestPlayer:
    """
    Tests for Player class
    """

    def test_actions(self):
        """
        A series of actions should be entered and pulled out properly
        """
        p1 = Player()
        p1.action_add(Player.DOWN)
        p1.action_add(Player.LEFT)
        p1.action_add(Player.BOMB)
        p1.action_add(Player.RIGHT)
        p1.action_add(Player.RIGHT)
        p1.action_add(Player.RIGHT)
        assert p1.action_next() == Player.DOWN
        assert p1.action_next() == Player.LEFT
        assert p1.action_next() == Player.BOMB
        assert p1.action_next() == Player.RIGHT
        assert p1.action_next() == Player.RIGHT
        assert p1.action_next() == Player.RIGHT
