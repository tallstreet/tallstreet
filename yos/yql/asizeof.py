# Copyright (c) 2008 Yahoo! Inc. All rights reserved.
# Licensed under the Yahoo! Search BOSS Terms of Use
# (http://info.yahoo.com/legal/us/yahoo/search/bosstos/bosstos-2317.html)

"""
Calculate the size of an object in python
This code used to be very complicated, and then realized in certain cases it failed
Given the structures handled in this framework, string'ing it and computing the length works fine
Especially since the # of bytes is not important - just need the relative sizes between objects
relsize is used to rank candidate collections of objects inferred from a REST response
The largest sized one wins
"""

__author__ = "Vik Singh (viksi@yahoo-inc)"

def relsize(o):
  return len(str(o))
