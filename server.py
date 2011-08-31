#!/usr/bin/env python
# coding: utf-8

from twisted.internet import reactor
from twisted.web import server, resource, http, util
import simplejson as json
import uuid
from bomber import GameState, Player

FLAME_TICK_TIME  = 1
ACTION_TICK_TIME = 1
BOMB_TICK_TIME   = 1

class Forbidden(resource.Resource):

    """
    Forbidden page
    """

    def render(self, request):
        request.setResponseCode(http.BAD_REQUEST)
        return json.loads('Forbidden')

class Invalid(resource.Resource):

    """
    Invalid page
    """

    def render(self, request):
        request.setResponseCode(http.BAD_REQUEST)
        return json.loads('Invalid')

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
        uid = uuid.uuid4().hex
        while uid in self.state['players']:
            uid = uuid.uuid4().hex
        self.state['players'][uid] = p
        self.state['game'].player_add(p)
        return util.redirectTo('/player/' + uid, request)

    def getChild(self, uid, request):
        if uid not in self.state['players']:
            return Invalid()

        return BomberPlayerValid(self.state, uid)

class BomberPlayerValid(BomberResource):

    """
    Handle /player/UID
    """

    def __init__(self, state, uid, *args, **kwargs):
        BomberResource.__init__(self, state, *args, **kwargs)
        self.uid = uid
        self.player = self.state['players'][uid]

    def render_GET(self, request):
        info = dict(uid=self.uid)
        for stat in 'state', 'coords', 'number', 'flame',\
                    'bomb', 'kills', 'deaths', 'suicides':
            info[stat] = getattr(self.player, stat)

        return json.dumps(info)

    def render_PUT(self, request):
        data = json.loads(request.content.read())
        if 'action' in data:
            action = getattr(Player, data['action'])
            self.player.action_add(action)

        return util.redirectTo('/player/' + self.uid, request)

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
    admin_uid = uuid.uuid4().hex
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
