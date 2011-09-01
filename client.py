#!/usr/bin/env python
# coding: utf-8
from pycurlbrowser.rest_client import RestClientJson

BASE = 'http://localhost:21513'

def admin_spawn_command(uid, base=BASE):
    """Spawn players"""
    rc = RestClientJson(base)
    print rc.put('admin', uid, dict(spawn=True))

def state_command(base=BASE):
    """Print the current state of the server"""
    rc = RestClientJson(base)
    print rc.get('state')

def player_create_command(base=BASE):
    """Create a player"""
    rc = RestClientJson(base)
    print rc.post('player')

def player_detail_command(uid, base=BASE):
    rc = RestClientJson(base)
    print rc.get('player', uid)

def player_action_command(uid, action, base=BASE):
    """Transmit an action for an existing player"""
    rc = RestClientJson(base)
    print rc.put('player', uid, dict(action=action))

def player_name_command(uid, name, base=BASE):
    """Name an existing player"""
    rc = RestClientJson(base)
    print rc.put('player', uid, dict(name=name))

def player_remove_command(uid, base=BASE):
    """Remove a player from the game"""
    rc = RestClientJson(base)
    print rc.delete('player', uid)

if __name__ == '__main__':
    import scriptine
    scriptine.run()
