#!/usr/bin/env python
# coding: utf-8
import termios
import sys
import tty
import select
import readline
from pycurlbrowser.rest_client import RestClientJson

FPS=2
BASE = 'http://localhost:21513'

def is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def game_loop(rc, uid):
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        while 1:
            detail = rc.get('player', uid)
            print rc.get('state')
            print 'Player: %d | Bombs: %d | Flames: %d' % (detail['number'] or 0, detail['bomb'], detail['flame'])

            if is_data():
                c = sys.stdin.read(1)
                if c == '\x1b':         # x1b is ESC
                    c += sys.stdin.read(2)

                if c == 'q':
                    rc.delete('player', uid)
                    break
                elif c == ' ':
                    rc.put('player', uid, dict(action='BOMB'))
                elif c == '\x1b[A': # up
                    rc.put('player', uid, dict(action='UP'))
                elif c == '\x1b[B': # down
                    rc.put('player', uid, dict(action='DOWN'))
                elif c == '\x1b[C': #right
                    rc.put('player', uid, dict(action='RIGHT'))
                elif c == '\x1b[D': # left
                    rc.put('player', uid, dict(action='LEFT'))

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    server = raw_input("Server (none for local): ")
    if server == '':
        server = BASE

    name = raw_input("Name: ")
    rc = RestClientJson(server)
    detail = rc.post('player', name)
    game_loop(rc, detail['uid'])
