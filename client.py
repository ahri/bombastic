#!/usr/bin/env python
# coding: utf-8
from pycurlbrowser.rest_client import RestClientJson

BASE = 'http://localhost:21513'

def admin_command(uid, base=BASE):
    """Get/set admin variables"""
    rc = RestClientJson(base)
    try:
        print rc.get('admin', uid)
    except AssertionError:
        print 'Incorrect UID'

def state_command(base=BASE):
    """Print the current state of the server"""
    rc = RestClientJson(base)
    print rc.get('state')

def player_command(base=BASE, uid=None, action=None):
    """Create a player"""
    rc = RestClientJson(base)
    if uid is None:
        print rc.post('player')
    elif action is None:
        print rc.get('player', uid)
    else:
        print rc.put('player', uid, dict(action=action))

if __name__ == '__main__':
    import scriptine
    scriptine.run()
