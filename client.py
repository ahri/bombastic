#!/usr/bin/env python
# coding: utf-8
from pycurlbrowser.rest_client import RestClient


def state_command(base='http://localhost:21513'):
    """Print the current state of the server"""
    rc = RestClient(base)
    print rc.get('state')

def admin_command(uid, base='http://localhost:21513'):
    """Get/set admin variables"""
    rc = RestClient(base)
    try:
        print rc.get('admin', uid)
    except AssertionError:
        print 'Incorrect UID'

if __name__ == '__main__':
    import scriptine
    scriptine.run()
