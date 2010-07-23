"""
A unique (set-like) version of deque
"""

from collections import deque

class udeque(deque):
    """
    Modified deque with guards on the appends
    NB. completely unoptimized; use only on small queues
    """
    def append(self, item):
        """
        Wrapper for collections.deque.append()
        """
        if not item in list(self):
            super(udeque, self).append(item)

    def appendleft(self, item):
        """
        Wrapper for collections.deque.appendleft()
        """
        if not item in list(self):
            super(udeque, self).appendleft(item)
