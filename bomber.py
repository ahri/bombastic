#!/usr/bin/env python

map_content = """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
BS ................................. SB
B B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B
B.....................................B
B B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B.B B
BS ................................. SB
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"""

def map(set=None):
    global map_content

    if set:
        map = open(set, 'r')
        map_content = map.read()

    return map_content
