#!/usr/bin/env python

import bomber

def test_map():
    assert bomber.map() == """BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
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

def test_load_map():
    map = open("maps/test.bmm", 'r')
    bomber.map(set="maps/test.bmm")

    assert bomber.map() == map.read()
