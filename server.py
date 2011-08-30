#!/usr/bin/env python
# coding: utf-8

from twisted.internet import reactor
from twisted.web import server, resource, http
import simplejson as json
import uuid
from bomber import GameState, Player

FLAME_TICK_TIME  = 1
ACTION_TICK_TIME = 1
BOMB_TICK_TIME   = 1

uid = lambda: uuid.uuid4().hex

class Forbidden(resource.Resource):

    """
    Forbidden page
    """

    def render(self, request):
        request.setResponseCode(http.BAD_REQUEST)
        return 'Forbidden'

class Forbidden(resource.Resource):

    """
    Forbidden page
    """

    def render(self, request):
        request.setResponseCode(http.BAD_REQUEST)
        return 'Forbidden'

class BomberResource(resource.Resource):

    """
    An HTTP resource that is game-state and player aware
    """

    def __init__(self, state):
        resource.Resource.__init__(self)

        for req_key in 'game', 'admin_uid':
            if req_key not in state:
                raise TypeError('Webserver state needs "%s" key' % req_key)

        if 'players' not in state:
            state['players'] = {}

        self.state = state

class ServerRoot(BomberResource):

    """
    Root of our webserver
    """

    def render(self, request):
        return 'This is a bomberman server'

    def getChild(self, name, request):
        if name == 'admin':
            return BomberAdmin(self.state)
        if name == 'state':
            return BomberState(self.state)
        if name == 'player':
            return BomberPlayer(self.state)
        return self

class BomberAdmin(BomberResource):

    """
    Handle /admin
    """

    def render_GET(self, request):
        return "Supply the admin UID"

    def getChild(self, uid, request):
        if uid != self.state['admin_uid']:
            return Forbidden()

        return BomberAdminValid(self.state)

class BomberAdminValid(BomberResource):

    """
    Handle (valid) /admin/uid
    """

    def render_GET(self, request):
        return json.dumps("admin!")

    def render_PUT(self, request):
        pass

    def getChild(self, uid, request):
        return self


class BomberState(BomberResource):

    """
    Handle /state
    """

    def render_GET(self, request):
        return json.dumps(str(self.state['game']))

class BomberPlayer(BomberResource):

    """
    Handle /player
    """

    def render_POST(self, request):
        p = Player()
        uid = uid()
        self.state['players'][uid] = p
        self.state['game'].player_add(p)
        request.redirect('/player/' + uid)
        request.finish()
        return twisted.web.server.NOT_DONE_YET # http://stackoverflow.com/questions/3254965/why-does-twisted-think-im-calling-request-finish-twice-when-i-am-not -- doesn't seem to help though......

    def getChild(self, uid, request):
        return BomberPlayerUid(self.state, uid)

class BomberPlayerUid(BomberResource):

    """
    Handle /player/uid
    """

    def __init__(self, state, uid, *args, **kwargs):
        BomberResource.__init__(self, state, *args, **kwargs)
        self.uid = uid

    def render_GET(self, request):
        if self.uid not in self.players:
            # TODO: 404
            return 'meh'

        return json.dumps({'uid': self.uid})

    def render_PUT(self, request):
        return 'PUT'

    def render_DELETE(self, request):
        return 'DELETE'

# TODO:
#
# server
#   generate unique identifiers for players
#   game state (GET)
#   admin (GET/PUT/DELETE)
#       generate a uid for the admin
#   player spawning needs to occur somehow(?)
#   player create (POST)
#   player action (PUT)
#   redirect POST to player ID
#   send Content-Type: text/json
#   generate docs when calling without children (instead of just returning "This is a bomberman server")
#
# client 1 (python)
#   use termio thingy
#   clear screen between frames?
#   display game state
#   player create
#   player action
#
# client 2 (jquery)
#   grab input
#   output game state to table
#
# client 3 (jquery)
#   output game state, with img lookup (simple dict)



if __name__ == '__main__':
    admin_uid = uid()
    print "Admin uid:", admin_uid

    state = GameState()

    def tick_flames():
        state._flames_process()
        reactor.callLater(FLAME_TICK_TIME, tick_flames)

    def tick_actions():
        state._actions_process()
        reactor.callLater(ACTION_TICK_TIME, tick_actions)

    def tick_bombs():
        state._bombs_process()
        reactor.callLater(BOMB_TICK_TIME, tick_bombs)

    reactor.listenTCP(21513, server.Site(ServerRoot(dict(game=state, admin_uid=admin_uid))))

    reactor.callWhenRunning(tick_flames)
    reactor.callWhenRunning(tick_actions)
    reactor.callWhenRunning(tick_bombs)

    reactor.run()
