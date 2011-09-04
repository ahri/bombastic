#!/usr/bin/env python
# coding: utf-8

from twisted.internet import reactor
from twisted.web import server, resource, http, util, static
import simplejson as json
from simplejson.decoder import JSONDecodeError
import uuid
from bomber import GameState, Player

FLAME_TICK_TIME  = 1
ACTION_TICK_TIME = 0.25
BOMB_TICK_TIME   = 1

class ClientError(resource.Resource, object):

    """
    Provide useful information to client
    """

    def __init__(self, received):
        super(ClientError, self).__init__()
        self.received = received

    def provide_message(self, request, message):
        request.setResponseCode(http.BAD_REQUEST)
        return json.dumps(dict(message=message, received=self.received))

class Forbidden(ClientError):

    """
    Forbidden page
    """

    def render(self, request):
        return self.provide_message(request, 'Forbidden')

class Invalid(ClientError):

    """
    Invalid page
    """

    def render(self, request):
        return self.provide_message(request, "Invalid")

class ExpectedJson(ClientError):

    """
    We expected JSON and didn't get any
    """

    def render(self, request):
        return self.provide_message(request, "Expected JSON")

class BomberResource(resource.Resource, object):

    """
    An HTTP resource that is game-state and player aware
    """

    def __init__(self, state, data):
        super(BomberResource, self).__init__()

        for req_key in 'game', 'admin_uid':
            if req_key not in state:
                raise TypeError('Webserver state needs "%s" key' % req_key)

        if 'players' not in state:
            state['players'] = {}

        self.state = state
        self.data = data

class ServerRoot(BomberResource):

    """
    Root of our webserver
    """

    def render(self, request):
        return 'This is a bomberman server'

    def getChild(self, name, request):
        data = request.content.read()
        if len(data) == 0:
            data = None
        else:
            try:
                data = json.loads(data)
            except JSONDecodeError:
                return ExpectedJson(data)

        if name == 'admin':
            return BomberAdmin(self.state, data)
        if name == 'state':
            return BomberState(self.state, data)
        if name == 'player':
            return BomberPlayer(self.state, data)
        if name == 'client2':
            return server.Site(static.File('client2'))
        return self

class BomberAdmin(BomberResource):

    """
    Handle /admin
    """

    def render_GET(self, request):
        return json.dumps("Supply the admin UID")

    def getChild(self, uid, request):
        if uid != self.state['admin_uid']:
            return Forbidden(self.data)

        return BomberAdminValid(self.state, self.data)

class BomberAdminValid(BomberResource):

    """
    Handle (valid) /admin/uid
    """

    def render_GET(self, request):
        # list players
        return json.dumps([dict(uid=uid,
                                name=player.name,
                                number=player.number,
                                coords=player.coords) for
                            uid, player in self.state['players'].items()])

    def render_PUT(self, request):
        if 'spawn' in self.data:
            self.state['game'].spawn()

        return self.render_GET(request)

    def getChild(self, uid, request):
        return self


class BomberState(BomberResource):

    """
    Handle /state
    """

    def render_GET(self, request):
        #request.setHeader('Content-Type', 'text/json')
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

        if self.data is not None and 'name' in self.data:
            p.name = self.data['name']

        return BomberPlayerValid(self.state, self.data, uid).render_GET(request)

    def getChild(self, uid, request):
        if uid not in self.state['players']:
            return Invalid(self.data)

        return BomberPlayerValid(self.state, self.data, uid)

class BomberPlayerValid(BomberResource):

    """
    Handle /player/UID
    """

    def __init__(self, state, data, uid):
        super(BomberPlayerValid, self).__init__(state, data)
        self.uid = uid
        self.player = self.state['players'][uid]

    def render_GET(self, request):
        info = dict(uid=self.uid, state=str(self.state['game']))
        for stat in 'coords', 'number', 'flame', 'bomb',\
                    'kills', 'deaths', 'suicides', 'name':
            info[stat] = getattr(self.player, stat)

        return json.dumps(info)

    def render_PUT(self, request):
        if 'action' in self.data:
            try:
                action = getattr(Player, self.data['action'])
                self.state['game'].action_add(self.player, action)
            except AttributeError:
                pass

        if 'name' in self.data:
            self.player.name = self.data['name']

        return self.render_GET(request)

    def render_DELETE(self, request):
        del self.state['players'][self.uid]
        try:
            self.state['game'].player_remove(self.player)
        except KeyError: # the game doesn't know about the player
            pass
        except AttributeError: # the player isn't in the game
            pass

        return self.render_GET(request)

if __name__ == '__main__':
    listen = raw_input('hostname:port to listen on? defaults to localhost:21513 : ')
    try:
        hostname, port = listen.split(':')
    except ValueError:
        hostname, port = 'localhost', 21513

    admin_uid = uuid.uuid4().hex

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

    reactor.listenTCP(factory=server.Site(ServerRoot(dict(game=state, admin_uid=admin_uid), None)),
                      interface=hostname,
                      port=port)

    reactor.callWhenRunning(tick_flames)
    reactor.callWhenRunning(tick_actions)
    reactor.callWhenRunning(tick_bombs)

    print "Listening on: http://%s:%d" % (hostname, port)
    print "Admin uid:", admin_uid

    reactor.run()
