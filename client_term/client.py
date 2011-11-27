#!/usr/bin/env python
# coding: utf-8

from pycurlbrowser.rest_client import RestClientJson
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol
import termios, tty, sys
import blessings

BASE = "http://localhost:21513"

def termios_wrapped(f):
    def m(*args, **kwargs):
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            f(*args, **kwargs)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return m

class Api(object):

    """
    """

class GameProtocol(WebSocketClientProtocol):

    """
    """

    def onOpen(self):
        print "sending UID:", self.uid
        self.sendMessage(self.uid)

    def onMessage(self, message, binary):
        print message
        # TODO: update game state

class BombasticClientFactory(WebSocketClientFactory, object):

    """
    Be able to set a UID
    """

    protocol = GameProtocol

    def __init__(self, uid, *args, **kwargs):
        super(BombasticClientFactory, self).__init__(*args, **kwargs)
        self.uid = uid

    def buildProtocol(self, *args, **kwargs):
        protocol = super(BombasticClientFactory, self).buildProtocol(*args, **kwargs)
        protocol.uid = self.uid
        return protocol

if __name__ == '__main__':
    # TODO: get base url from cmdline

    name = raw_input('Name: ')
    if len(name) == 0:
        player_data = None
    else:
        player_data = dict(name=name)

    # create a player
    uid = RestClientJson(BASE).create('player', player_data).get('uid')

    # TODO: connect to a different host
    reactor.connectTCP("localhost", 9000, BombasticClientFactory(uid, url="ws://localhost:9000"))
    reactor.run()
