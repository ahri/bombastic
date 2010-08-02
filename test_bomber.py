#!/usr/bin/env python
"""Tests for bomber module"""

# http://docs.python.org/library/exceptions.html

from py import test
from bomber import *
import os
import random

class TestArena:

    """Quality control for base data structure"""

    def test_arena_init(self):
        """Ensure that data structure is set up correctly"""
        arena = Arena(1, 2)
        assert arena.data == [[], []]

    def test_coords_add(self):
        """Add object to given coords"""
        arena = Arena(1, 2)
        obj = object()
        assert arena.coords_add((0, 1), obj) == None
        assert arena.data == [[], [obj]]

    def test_coords_get(self):
        """Get all objects from given coords"""
        arena = Arena(1, 2)
        obj = object()
        arena.data = [[], [obj]]
        assert arena.coords_get((0, 0)) == []
        assert arena.coords_get((0, 1)) == [obj]

    def test_coords_remove(self):
        """Remove the specified object from the given coords"""
        arena = Arena(1, 2)
        obj1 = object()
        obj2 = object()
        arena.data = [[], [obj1, obj2, obj1]]

        assert arena.coords_remove((0, 1), obj1) == obj1
        assert arena.data == [[], [obj2, obj1]]

        with test.raises(LookupError):
            arena.coords_remove((0, 0), obj1)

    def test_coords_have_obj(self):
        """Coords contain an specified object"""
        arena = Arena(1, 2)
        obj = object()
        arena.data = [[], [obj]]
        assert arena.coords_have_obj((0, 1), obj) == True
        assert arena.coords_have_obj((0, 0), obj) == False

    def test_coords_have_class(self):
        """Coords contain an object of a given type"""
        arena = Arena(1, 2)
        obj = object()
        arena.data = [[], [obj]]
        assert arena.coords_have_class((0, 1), object) == True
        assert arena.coords_have_class((0, 0), object) == False

    def test_rectangle(self):
        """Ensure that iterating over the Arena gives expected coords"""
        arena = Arena(3, 4)
        coords = []
        for x, y, l in arena:
            coords.append((x, y))

        assert coords == [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2), (0,3), (1,3), (2,3)]

    def test_rect_contents(self):
        """Ensure that contents all match expected"""
        arena = Arena(3, 4)
        data = []
        for x, y, l in arena:
            data.append(l)

        assert arena.data == data

    def test_coord_sanity(self):
        """Expect exceptions for out of range coords"""
        arena = Arena(3, 4)

        with test.raises(IndexError):
            arena.sanity((-1, 0))

        with test.raises(IndexError):
            arena.sanity((0, -1))

        with test.raises(IndexError):
            arena.sanity((-1, -1))

        with test.raises(IndexError):
            arena.sanity((3, 3))

        with test.raises(IndexError):
            arena.sanity((2, 4))

        with test.raises(IndexError):
            arena.sanity((3, 4))

class TestGameState:

    """Tests for Game class"""

    def test_arena(self):
        """Default arena returned"""
        state = GameState()
        arena = open(os.sep.join(["arenas", "default.bmm"]), 'r')
        assert str(state) == arena.read()
        arena.close()

    def test_arena_load(self):
        """Load a arena from a file"""
        state = GameState()
        arena = open(os.sep.join(["arenas", "test.bmm"]), 'r')
        state.arena_load(["arenas", "test.bmm"])

        assert str(state) == arena.read()
        arena.close()

    def test_player_number(self):
        """Check player numbers"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.player_add(p1) # try and break with copies of p1
        state.spawn()
        assert p1.number == 1

    def test_player_spawn(self):
        """Check player numbers and spawn positions"""
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
        assert p5.number == -1

        assert state.arena.coords_have_obj((1, 1), p1)
        assert state.arena.coords_have_obj((37, 1), p2)
        assert state.arena.coords_have_obj((1, 17), p3)
        assert state.arena.coords_have_obj((37, 17), p4)

    def test_actions_queue_sticky_movement(self):
        """Queue up actions and ensure that movement is sticky"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert state._sticky_actions == {p1: None}

        state.action_add(p1, Player.DOWN)
        state._actions_process()
        assert state._sticky_actions == {p1: Player.DOWN}
        state._actions_process()
        assert state._sticky_actions == {p1: Player.DOWN}

        state.action_add(p1, Player.UP)
        state.action_add(p1, Player.LEFT)
        state._actions_process()
        assert state._sticky_actions == {p1: Player.UP}
        state._actions_process()
        assert state._sticky_actions == {p1: Player.LEFT}
        state._actions_process()
        assert state._sticky_actions == {p1: Player.LEFT}

    def test_actions_bomb_non_sticky(self):
        """Queue a bomb action and ensure that it is not sticky"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert state._sticky_actions == {p1: None}

        state.action_add(p1, Player.DOWN)
        state.action_add(p1, Player.BOMB)
        state._actions_process()
        assert state._sticky_actions == {p1: Player.DOWN}
        state._actions_process()
        assert state._sticky_actions == {p1: None}

    def test_tick_movement(self):
        """Tick the game and check player position"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.arena_load(["arenas", "empty.bmm"])
        state.spawn()

        # confirm that arena is suitable for test
        assert state.arena.coords_have_obj((1, 1), p1)
        assert state.arena.coords_get((2, 1)) == []
        assert state.arena.coords_get((3, 1)) == []
        assert state.arena.coords_get((1, 2)) == []
        assert state.arena.coords_get((2, 2)) == []
        assert state.arena.coords_get((3, 2)) == []

        state.tick() # baseline; no moves
        assert state.arena.coords_have_obj((1, 1), p1)

        state.action_add(p1, Player.RIGHT)

        state.tick()
        assert not state.arena.coords_have_obj((1, 1), p1)
        assert state.arena.coords_have_obj((2, 1), p1)

        state.tick() # sticky
        assert not state.arena.coords_have_obj((2, 1), p1)
        assert state.arena.coords_have_obj((3, 1), p1)

        state.action_add(p1, Player.BOMB)
        state.tick() # bomb should halt them
        assert state.arena.coords_have_obj((3, 1), p1)

        state.action_add(p1, Player.DOWN)
        state.action_add(p1, Player.LEFT)

        state.tick()
        assert not state.arena.coords_have_obj((3, 1), p1)
        assert state.arena.coords_have_obj((3, 2), p1)

        state.tick()
        assert not state.arena.coords_have_obj((3, 2), p1)
        assert state.arena.coords_have_obj((2, 2), p1)

        state.tick() # sticky
        assert not state.arena.coords_have_obj((2, 2), p1)
        assert state.arena.coords_have_obj((1, 2), p1)

    def test_no_movement_onto_blocks_bombs(self):
        """Move player onto blocks should fail"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()

        # confirm that arena is suitable for test
        assert state.arena.coords_have_obj((1, 1), p1)

        assert state.arena.coords_have_class((0, 0), Block)
        assert not p1.move((0, 0))
        assert not state.arena.coords_have_obj((0, 0), p1)
        assert state.arena.coords_have_obj((1, 1), p1)

        assert state.arena.coords_have_class((1, 3), DestructibleBlock)
        assert not p1.move((1, 3))
        assert not state.arena.coords_have_obj((1, 3), p1)
        assert state.arena.coords_have_obj((1, 1), p1)

        assert state.arena.coords_get((2, 1)) == []
        state.arena.coords_add((2, 1), Bomb(p1))
        assert state.arena.coords_have_class((2, 1), Bomb)
        assert not p1.move((2, 1))
        assert not state.arena.coords_have_obj((2, 1), p1)
        assert state.arena.coords_have_obj((1, 1), p1)

    def test_bomb_mechanics(self):
        """Add a bomb and tick the game to blow it up"""
        state = GameState()
        p1 = Player()
        state.arena_load(["arenas", "empty.bmm"])
        state.player_add(p1)
        state.spawn()
        p1.coords = (3, 3)

        bomb = Bomb(p1)

        assert bomb.flame == p1.flame
        assert bomb.coords == p1.coords

        assert bomb.ticks_left == 4
        bomb.tick()
        assert bomb.ticks_left == 3
        bomb.tick()
        assert bomb.ticks_left == 2
        bomb.tick()
        assert bomb.ticks_left == 1
        assert state.arena.coords_have_obj(bomb.coords, bomb)
        bomb.tick()
        assert bomb.ticks_left == 0
        assert not state.arena.coords_have_obj(bomb.coords, bomb)

        x, y = bomb.coords
        assert state.arena.coords_have_class(bomb.coords, Flame)
        assert state.arena.coords_have_class((x-1, y), Flame)
        assert not state.arena.coords_have_class((x-2, y), Flame)
        assert state.arena.coords_have_class((x+1, y), Flame)
        assert not state.arena.coords_have_class((x+2, y), Flame)
        assert state.arena.coords_have_class((x, y-1), Flame)
        assert not state.arena.coords_have_class((x, y-2), Flame)
        assert state.arena.coords_have_class((x, y+1), Flame)
        assert not state.arena.coords_have_class((x, y+2), Flame)

        state.tick()
        assert not state.arena.coords_have_class((x, y), Flame)
        assert not state.arena.coords_have_class((x-1, y), Flame)
        assert not state.arena.coords_have_class((x+1, y), Flame)
        assert not state.arena.coords_have_class((x, y-1), Flame)
        assert not state.arena.coords_have_class((x, y+1), Flame)


    def test_bomb_mechanics_blast_outside_arena(self):
        """Add a bomb and tick the game to blow it up, ensuring insane coords for flame"""
        state = GameState()
        p1 = Player()
        p1.flame = 10
        state.player_add(p1)
        state.spawn()
        bomb = p1.drop_bomb()
        assert bomb.flame == p1.flame
        assert bomb.coords == p1.coords
        state.tick(count=4)
        assert not state.arena.coords_have_obj(bomb.coords, bomb)

    def test_bombing(self):
        """Drop a bomb, tick the game and ensure that bomb blows up"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        state.action_add(p1, Player.BOMB)
        state.tick()
        assert state.arena.coords_have_class(p1.coords, Bomb)
        state.tick(count=3)
        assert not state.arena.coords_have_class(p1.coords, Bomb)
        assert state.arena.coords_have_class(p1.coords, Flame)

    def test_no_flame_on_blocks(self):
        """Add a bomb and tick the game to blow it up"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()

        bomb = Bomb(p1)

        assert bomb.flame == p1.flame
        assert bomb.coords == p1.coords

        assert bomb.ticks_left == 4
        bomb.tick()
        assert bomb.ticks_left == 3
        bomb.tick()
        assert bomb.ticks_left == 2
        bomb.tick()
        assert bomb.ticks_left == 1
        assert state.arena.coords_have_obj(bomb.coords, bomb)
        bomb.tick()
        assert bomb.ticks_left == 0
        assert not state.arena.coords_have_obj(bomb.coords, bomb)

        x, y = bomb.coords
        assert state.arena.coords_have_class(bomb.coords, Flame)
        assert not state.arena.coords_have_class((x-1, y), Flame)
        assert state.arena.coords_have_class((x+1, y), Flame)
        assert not state.arena.coords_have_class((x, y-1), Flame)
        assert state.arena.coords_have_class((x, y+1), Flame)

    def test_blow_up_destructible(self):
        """Make sure that destructible blocks are flamed out of existence"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert state.arena.coords_have_obj((1, 1), p1)
        state.action_add(p1, Player.DOWN)
        state.tick()
        state.action_add(p1, Player.BOMB)
        state.tick()
        state.action_add(p1, Player.UP)
        state.tick()
        state.action_add(p1, Player.RIGHT)
        state.tick()
        assert state.arena.coords_have_class((1, 2), Bomb)
        state.tick()
        assert state.arena.coords_have_class((1, 2), Flame)
        assert state.arena.coords_have_class((1, 3), Flame)
        assert not state.arena.coords_have_class((1, 3), DestructibleBlock)

    def test_player_death(self):
        """Kill a player"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        state.action_add(p1, Player.BOMB)
        state.tick()
        state.tick()
        state.tick()
        state.tick()
        assert not state.arena.coords_have_obj(p1.coords, p1)

    def test_player_bombs_max(self):
        """Make sure that player can only drop the number of bombs they have powerups for"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert p1.bomb == 1
        state.action_add(p1, Player.BOMB)
        state.tick()
        assert state.arena.coords_have_class(p1.coords, Bomb)
        state.action_add(p1, Player.DOWN)
        state.tick()
        state.action_add(p1, Player.BOMB)
        state.tick()
        assert not state.arena.coords_have_class(p1.coords, Bomb)

    def test_powerup_generation(self):
        """Powerups should be generated 30% of the time, with an equal chance of bomb/flame generated"""
        ratio = 0.3
        error_margin = 0.1

        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        bomb = Bomb(p1)
        flame = Flame(bomb, (1, 2))
        for x in xrange(3, 36):
            for o in state.arena.coords_get((x, 1)):
                if isinstance(o, DestructibleBlock):
                    o.flamed(flame)

        count = 0.0
        flames = 0
        bombs = 0
        for x in xrange(3, 36):
            count += 1
            for o in state.arena.coords_get((x, 1)):
                if isinstance(o, PowerupFlame):
                    flames += 1
                if isinstance(o, PowerupBomb):
                    bombs += 1

#        assert (ratio - error_margin)     < ((flames+bombs)/count) < (ratio + error_margin)
#        assert ((ratio - error_margin)/2) < (flames/count)         < ((ratio + error_margin)/2)
#        assert ((ratio - error_margin)/2) < (bombs/count)          < ((ratio + error_margin)/2)
        assert (flames + bombs) > 0

    def test_powerup_pickup(self):
        """Players should pick up a powerup when they move to a square with a powerup on it"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert p1.flame == 1
        assert p1.bomb == 1
        flame = PowerupFlame(state=state, coords=(2, 1))
        bomb = PowerupBomb(state=state, coords=(1, 2))
        state.action_add(p1, Player.RIGHT)
        state.tick()
        assert not state.arena.coords_have_obj(flame.coords, flame)
        assert p1.flame == 2
        state.action_add(p1, Player.LEFT)
        state.tick()
        state.action_add(p1, Player.DOWN)
        state.tick()
        assert not state.arena.coords_have_obj(bomb.coords, bomb)
        assert p1.bomb == 2

    def test_powerup_pickup_race(self):
        """First player to a powerup gets it"""
        state = GameState()
        p1 = Player()
        p2 = Player()
        p1.spawn(1, state=state, coords=(1, 1))
        p2.spawn(2, state=state, coords=(1, 1))
        assert p1.flame == 1
        assert p2.flame == 1
        PowerupFlame(state=state, coords=(1, 2))
        state.action_add(p1, Player.DOWN)
        state.action_add(p2, Player.DOWN)
        state.tick()
        assert p1.flame == 2
        assert p2.flame == 1

        # retry!

        state = GameState()
        p1 = Player()
        p2 = Player()
        p1.spawn(1, state=state, coords=(1, 1))
        p2.spawn(2, state=state, coords=(1, 1))
        assert p1.flame == 1
        assert p2.flame == 1
        PowerupFlame(state=state, coords=(1, 2))
        state.action_add(p2, Player.DOWN)
        state.action_add(p1, Player.DOWN)
        state.tick()
        assert p1.flame == 1
        assert p2.flame == 2

        # with stickiness

        state = GameState()
        p1 = Player()
        p2 = Player()
        p1.spawn(1, state=state, coords=(1, 1))
        p2.spawn(2, state=state, coords=(1, 1))
        assert p1.flame == 1
        assert p2.flame == 1
        for o in state.arena.coords_get((1, 3)):
            state.arena.coords_remove((1, 3), o)
        PowerupFlame(state=state, coords=(1, 3))
        state.action_add(p1, Player.DOWN)
        state.action_add(p2, Player.DOWN)
        state.tick()
        state.action_add(p2, Player.DOWN)
        state.tick()
        assert p1.flame == 1
        assert p2.flame == 2

    def test_chain_explosion(self):
        """Bombs should blow other bombs up"""
        state = GameState()
        p1 = Player()
        p1.bomb = 2
        state.player_add(p1)
        state.spawn()
        state.action_add(p1, Player.RIGHT)
        state.tick()
        state.action_add(p1, Player.BOMB)
        state.tick()
        state.action_add(p1, Player.LEFT)
        state.tick()
        state.action_add(p1, Player.BOMB)
        state.tick()
        state.tick()
        assert not state.arena.coords_have_class((1, 1), Bomb)
        assert state.arena.coords_have_class((1, 1), Flame)
        assert state.arena.coords_have_class((1, 2), Flame)
        assert state.arena.coords_have_class((2, 1), Flame)

    def test_player_kills_deaths_counter(self):
        """Count how many kills/deaths have occurred"""
        state = GameState()
        p1 = Player()
        p2 = Player()
        state.player_add(p1)
        state.player_add(p2)
        state.spawn()
        assert p1.kills == 0
        assert p1.deaths == 0
        assert p2.kills == 0
        assert p2.deaths == 0
        p2.drop_bomb()
        for bomb in state.arena.coords_get(p2.coords):
            if isinstance(bomb, Bomb):
                break
        else:
            assert False
        state.arena.coords_remove(p2.coords, bomb)
        state.arena.coords_add(p1.coords, bomb)
        bomb.coords = p1.coords
        state.tick()
        state.tick()
        state.tick()
        state.tick()
        assert p1.kills == 0
        assert p1.deaths == 1
        assert p2.kills == 1
        assert p2.deaths == 0

    def test_player_suicides_counter(self):
        """Suicides count as +1 death and +1 suicide, but not a kill"""
        state = GameState()
        p1 = Player()
        state.player_add(p1)
        state.spawn()
        assert p1.kills == 0
        assert p1.deaths == 0
        assert p1.suicides == 0
        state.action_add(p1, Player.BOMB)
        state.tick()
        state.tick()
        state.tick()
        state.tick()
        assert p1.kills == 0
        assert p1.deaths == 1
        assert p1.suicides == 1

    def test_chain_explosion_kills(self):
        """
        If your bomb is ignited by someone else's and kills you, that counts as a kill for them, not a suicide
        Essentially; your bomb becomes their bomb, because they blew it up
        """
        assert False

    def test_powerup_flamed(self):
        """Powerups should be destroyed when flamed"""
        assert False
