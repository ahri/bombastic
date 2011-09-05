#!/usr/bin/env python
# coding: utf-8
import cmd
from pycurlbrowser.rest_client import RestClientJson, StatusClientError

BASE = 'http://localhost:21513'

def game_command(base=BASE):
    """Print the current game-state of the server"""
    rc = RestClientJson(base)
    print rc.get('game')

class ExitCmd(cmd.Cmd, object):
    def can_exit(self):
        return True

    def onecmd(self, line):
        r = super (ExitCmd, self).onecmd(line)
        if r and (self.can_exit() or
            raw_input('exit anyway ? (yes/no):')=='yes'):
                 return True
        return False

    def do_exit(self, s):
        return True

    def help_exit(self):
        print "Exit the interpreter."
        print "You can also use the Ctrl-D shortcut."

    do_EOF = do_exit
    help_EOF = help_exit

class DebugCmd(cmd.Cmd, object):
    def do_debug(self, s):
        if s == 'on':
            self.rc.set_debug(True)
        else:
            self.rc.set_debug(False)

    def help_debug(self):
        print "Set debug 'on' or 'off'"

class StateCmd(cmd.Cmd, object):
    def __init__(self, rc):
        super(StateCmd, self).__init__()
        self.rc = rc

    def do_game(self, s):
        print self.rc.get('game')

    def help_game(self):
        print "Display game state"

class AdminCmd(ExitCmd, StateCmd, DebugCmd):
    def __init__(self, rc, uid):
        super(AdminCmd, self).__init__(rc)
        self.uid = uid

    def do_status(self, s):
        print self.rc.get('admin', self.uid)

    def help_status(self):
        print "Display game status"

    def do_spawn(self, s):
        print self.rc.put('admin', self.uid, dict(spawn=True))

    def help_spawn(self):
        print "Spawn players"

    def do_kick(self, s):
        try:
            print self.rc.delete('player', s)
        except StatusClientError:
            pass

    def help_kick(self):
        print "Kick a player"

class PlayerCmd(ExitCmd, StateCmd, DebugCmd):
    def __init__(self):
        super(PlayerCmd, self).__init__()
        self.uid = None

    def do_create(self, s):
        if len(s) > 0:
            data = dict(name=s)
        else:
            data = None

        res = self.rc.post('player', data)
        self.uid = res.get('uid')

    def help_create(self):
        print "Create a player, optionally pass a name"

    def do_detail(self, s):
        print self.rc.get('player', self.uid)

    def help_detail(self):
        print "Display player details"

    def do_name(self, s):
        self.rc.put('player', self.uid, dict(name=s))

    def help_name(self):
        print "Set player name"

    def do_action(self, s):
        self.rc.put('player', self.uid, dict(action=s))

    def help_action(self):
        print "Execute an action"

    def do_exit(self, s):
        if self.uid is not None:
            try:
                self.rc.delete('player', self.uid)
            except StatusClientError:
                pass
        return super(PlayerCmd, self).do_exit(s)

    do_EOF = do_exit

def admin_command(base=BASE):
    uid = raw_input("UID: ")
    rc = RestClientJson(base)
    try:
        rc.get('admin', uid)
    except StatusClientError:
        print "Invalid UID specified"
        return

    interpreter = AdminCmd(rc, uid)
    interpreter.cmdloop()

def player_command(base=BASE):
    interpreter = PlayerCmd(RestClientJson(base))
    interpreter.cmdloop()

if __name__ == '__main__':
    import scriptine
    scriptine.run()
