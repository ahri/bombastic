#!/usr/bin/env python
# coding: utf-8
import cmd
import sys
from pycurlbrowser.rest_client import RestClientJson, StatusClientError

BASE = 'http://localhost:21513'

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
        print self.rc.read('game')

    def help_game(self):
        print "Display game state"

class AdminCmd(ExitCmd, StateCmd, DebugCmd):
    def __init__(self, rc, uid):
        super(AdminCmd, self).__init__(rc)
        self.uid = uid

    def do_status(self, s):
        print self.rc.read('admin', self.uid)

    def help_status(self):
        print "Display game status"

    def do_spawn(self, s):
        print self.rc.update('admin', self.uid, dict(spawn=True))

    def help_spawn(self):
        print "Spawn players"

    def do_kick(self, s):
        try:
            print self.rc.destroy('player', s)
        except StatusClientError:
            pass

    def help_kick(self):
        print "Kick a player"

if __name__ == '__main__':
    uid = raw_input("UID: ")
    rc = RestClientJson(BASE)
    try:
        rc.read('admin', uid)
    except StatusClientError:
        print "Invalid UID specified"
        sys.exit(1)

    interpreter = AdminCmd(rc, uid)
    interpreter.cmdloop()
