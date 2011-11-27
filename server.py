#!/usr/bin/env python
# coding: utf-8

from bomber import GameState, Player
from twisted.internet import reactor
from twisted.web import server, resource, http, util, static
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
from simplejson.decoder import JSONDecodeError
from pprint import pprint
from functools import wraps
import simplejson as json
import uuid

FLAME_TICK_TIME  = 1
ACTION_TICK_TIME = 0.25
BOMB_TICK_TIME   = 1

GAME = GameState()
PLAYERS = {}
ADMIN_UID = uuid.uuid4().hex

def player_status(uid, player):
    """Consistent output per player"""
    info = dict(uid=uid, game=str(GAME))
    for stat in 'coords', 'number', 'flame', 'bomb',\
                'kills', 'deaths', 'suicides', 'name':
        info[stat] = getattr(player, stat)
    return info

def json_req_handler(f):
    @wraps(f)
    def convert(self, request, *args, **kwargs):
        #request.setHeader('Content-Type', 'text/json')
        return json.dumps(f(self, request, *args, **kwargs))
    return convert

class ClientError(resource.Resource, object):

    """
    Provide useful information to client
    """

    def __init__(self, received):
        super(ClientError, self).__init__()
        self.received = received

    @json_req_handler
    def provide_message(self, request, message):
        request.setResponseCode(http.BAD_REQUEST)
        return dict(message=message, received=self.received)

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
    An HTTP resource capable of easily sharing data
    """

    def __init__(self, data):
        super(BomberResource, self).__init__()
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
            return BomberAdmin(data)
        if name == 'game':
            return BomberState(data)
        if name == 'player':
            return BomberPlayer(data)
        if name == 'client':
            return static.File('client_web')
        return self

class BomberAdmin(BomberResource):

    """
    Handle /admin
    """

    @json_req_handler
    def render_GET(self, request):
        return "Supply the admin UID"

    def getChild(self, uid, request):
        if uid != ADMIN_UID:
            return Forbidden(self.data)

        return BomberAdminValid(self.data)

class BomberAdminValid(BomberResource):

    """
    Handle (valid) /admin/uid
    """

    @json_req_handler
    def render_GET(self, request):
        # list players
        return [dict(uid=uid,
                     name=player.name,
                     number=player.number,
                     coords=player.coords) for
                 uid, player in PLAYERS.items()]

    def render_PUT(self, request):
        if 'spawn' in self.data:
            GAME.spawn()

        return self.render_GET(request)

    def getChild(self, uid, request):
        return self


class BomberState(BomberResource):

    """
    Handle /game
    """

    @json_req_handler
    def render_GET(self, request):
        return str(GAME)

class BomberPlayer(BomberResource):

    """
    Handle /player
    """

    def render_POST(self, request):
        p = Player()
        uid = uuid.uuid4().hex
        while uid in PLAYERS:
            uid = uuid.uuid4().hex
        PLAYERS[uid] = p
        GAME.player_add(p)

        if self.data is not None and 'name' in self.data:
            p.name = self.data['name']

        return BomberPlayerValid(self.data, uid).render_GET(request)

    def getChild(self, uid, request):
        if uid not in PLAYERS:
            return Invalid(self.data)

        return BomberPlayerValid(self.data, uid)

class BomberPlayerValid(BomberResource):

    """
    Handle /player/UID
    """

    def __init__(self, data, uid):
        super(BomberPlayerValid, self).__init__(data)
        self.uid = uid
        self.player = PLAYERS[uid]

    @json_req_handler
    def render_GET(self, request):
        return player_status(self.uid, self.player)

    def render_PUT(self, request):
        try:
            GAME.action_add(self.player, getattr(Player, self.data['action']))
        except KeyError:
            pass
        except AttributeError:
            pass

        try:
            self.player.name = self.data['name']
        except KeyError:
            pass

        return self.render_GET(request)

    def render_DELETE(self, request):
        del PLAYERS[self.uid]
        try:
            GAME.player_remove(self.player)
        except KeyError: # the game doesn't know about the player
            pass
        except AttributeError: # the player isn't in the game
            pass

        return self.render_GET(request)

class GameProtocol(WebSocketServerProtocol, object):
    def __init__(self, *args, **kwargs):
        super(GameProtocol, self).__init__(*args, **kwargs)
        self.uid = None
        self.player = None
        self.sample_rate = min([FLAME_TICK_TIME, ACTION_TICK_TIME, BOMB_TICK_TIME]) / 2

    def onOpen(self):
        self.player_update()

    def status_update(self):
        self.sendMessage("TODO: data here!")

    def onClose(self, wasClean, code, reason):
        self.player_quit()

    def sendMessage(self, message):
        return super(GameProtocol, self).sendMessage(json.dumps(message))

    def onMessage(self, msg, binary):
        if self.player is None:
            return self.player_set(msg)

        self.player_act(msg)

    def player_set(self, uid):
        try:
            self.player = PLAYERS[uid]
            self._uid = uid
        except KeyError:
            self.sendMessage("Invalid player UID")

    def player_act(self, action):
        GAME.action_add(self.player, getattr(Player, action))

    def player_quit(self):
        #GAME.player_remove(self.player)
        pass

    def player_update(self):
        reactor.callLater(self.sample_rate, self.player_update)

        if self.player is None:
            return

        self.sendMessage(player_status(self._uid, self.player))

if __name__ == '__main__':
    listen = raw_input('hostname:port to listen on? defaults to localhost:21513 : ')
    try:
        hostname, port = listen.split(':')
        port = int(port)
    except ValueError:
        hostname, port = 'localhost', 21513

    def traceerr(f, *args, **kwargs):
        last_state = str(GAME)
        last_arena = GAME.arena.data[:]
        try:
            f(*args, **kwargs)
        except Exception as e:
            reactor.stop()
            with file('trace.err', 'a') as tracefile:
                tracefile.write("%r\n" % e)
                tracefile.write("last_state =\n%s\n" % last_state)
                tracefile.write("last_arena =\n")
                pprint(last_arena, tracefile)
                tracefile.write("\n")
                tracefile.write("state =\n%s\n" % str(GAME))
                tracefile.write("arena =\n")
                pprint(GAME.arena.data, tracefile)
                tracefile.write("\n\n\n")
            raise

    def tick_flames():
        traceerr(GAME._flames_process)
        reactor.callLater(FLAME_TICK_TIME, tick_flames)

    def tick_actions():
        traceerr(GAME._actions_process)
        reactor.callLater(ACTION_TICK_TIME, tick_actions)

    def tick_bombs():
        traceerr(GAME._bombs_process)
        reactor.callLater(BOMB_TICK_TIME, tick_bombs)

    factory = WebSocketServerFactory()
    # TODO: choose a more sensible port
    # TODO: add a REST interface to get the port
    factory.port = 9000 # ugh, why do I have to do this twice?
    factory.protocol = GameProtocol
    reactor.listenTCP(interface=hostname, port=9000, factory=factory)

    reactor.listenTCP(factory=server.Site(ServerRoot(None)),
                      interface=hostname,
                      port=port)

    reactor.callWhenRunning(tick_flames)
    reactor.callWhenRunning(tick_actions)
    reactor.callWhenRunning(tick_bombs)

    print "Listening on: http://%s:%d" % (hostname, port)
    print "Admin uid:", ADMIN_UID

    reactor.run()
