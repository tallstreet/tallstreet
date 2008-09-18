# Copyright (c) 2008 Yahoo! Inc. All rights reserved.
# Licensed under the Yahoo! Search BOSS Terms of Use
# (http://info.yahoo.com/legal/us/yahoo/search/bosstos/bosstos-2317.html)

""" Some handy user defined functions to plug in db.select """

__author__ = "Vik Singh (viksi@yahoo-inc.com)"

from util.typechecks import is_dict

def unnest_value(row):
  """
  For data collections which have nested value parameters (like RSS)
  this function will unnest the value to the higher level.
  For example, say the row is {"title":{"value":"yahoo wins search"}}
  This function will take that row and return the following row {"title": "yahoo wins search"}
  """
  nr = {}
  for k, v in row.iteritems():
    if is_dict(type(v)) and "value" in v:
      nr[k] = v["value"]
    else:
      nr[k] = v
  return nr
