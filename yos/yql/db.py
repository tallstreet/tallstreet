# Copyright (c) 2008 Yahoo! Inc. All rights reserved.
# Licensed under the Yahoo! Search BOSS Terms of Use
# (http://info.yahoo.com/legal/us/yahoo/search/bosstos/bosstos-2317.html)

"""
Make python more SQL like over REST responses
main entry functions are create and select

The goal here is to let the developer specify a data structure via a REST URI
or a list of dictionaries (lod) using select or create
These functions infer the structure automatically and converts the input into a unified data format (lod)
One can call on the result table the describe() method to see in stdout what the schema is to double check
If one has the data in lod format already, then pass it to the data parameter of create or select

This library provides functional libraries for doing
select, group, sort, inner_join, outer_join, cross, union, describe
on these resulting tables

See below for the join functions - more documentation there

A Quick Example (see examples directory for more involved ones)

from yos.yql import db
from yos.yql import udfs

dl = db.create(name="dl", url="http://del.icio.us/rss/popular/iphone")
dl.describe()

dl = db.select(udf=udfs.unnest_value, table=dl)
"""

__author__ = "Vik Singh (viksi@yahoo-inc.com)"

import copy
from operator import itemgetter
import random

from asizeof import relsize

import simplejson

from util.typechecks import is_dict, is_list, is_ordered
from yos.crawl import dict2xml
from yos.crawl import rest

NAMESPACE_CHAR = "$"

def infer_collection_ordered_helper(l, cands):
  for vo in l:
    tv = type(vo)
    if is_ordered(tv):
      if is_list(vo) and is_dict(type(v[0])):
        cands.append(vo)
      else:
        infer_collection_ordered_helper(vo, cands)
    elif is_dict(tv):
      infer_collection_dict_helper(vo, cands)

def infer_collection_dict_helper(d, cands):
  for k, vd in d.iteritems():
    tv = type(vd)
    if is_ordered(tv):
      if is_list(tv) and is_dict(type(vd[0])):
        cands.append(vd)
      else:
        infer_collection_ordered_helper(vd, cands)
    elif is_dict(tv):
      infer_collection_dict_helper(vd, cands)

def infer_collection(d):
  if is_list(type(d)):
    return d

  cands = []
  for k, v in d.iteritems():
    tv = type(v)
    if is_ordered(tv):
      if is_list(tv) and len(v) > 0 and is_dict(type(v[0])):
        cands.append(v)
    elif is_dict(tv):
      infer_collection_dict_helper(v, cands)

  if len(cands) > 0:
    return sorted(map(lambda c: (c, relsize(c)), cands), key=itemgetter(1), reverse=True)[0][0]
  else:
    return []

def prep_name(name, c):
  nc = []
  for d in c:
    results = {}
    for k, v in d.iteritems():
      if k.find(NAMESPACE_CHAR) >= 0:
        results[k] = v
      else:
        results[name + NAMESPACE_CHAR + k] = v
    nc.append(results)
  return nc

def strip_prep(name):
  ni = name.find(NAMESPACE_CHAR)
  if ni > 0:
    return name[ni+1:]
  else:
    return name

def strip_row(row):
  rows = [{}]
  for k, v in row.iteritems():
    nn = strip_prep(k)
    i = 0
    while i < len(rows):
      ri = rows[i]
      if nn not in ri:
        ri[nn] = v
        break
      elif i == len(rows):
        rows.append({})
      i += 1
        
  return rows


STANDARDS_PREFIX = "{http://"
STANDARDS_SUFFIX = "}"

def remove_standards_prefix(k):
  kp = k.find(STANDARDS_PREFIX)
  if kp >= 0:
    ks = k.find(STANDARDS_SUFFIX, kp + 1)
    if ks >= 0 and ks < len(k) - 1:
      return k[0:kp] + k[ks+1:]
  return k

def standardize_tags_helper(d):
  nd = {}
  for k, v in d.iteritems():
    if is_dict(type(v)):
      cd = standardize_tags_helper(v)
    else:
      cd = v
    nd[remove_standards_prefix(k)] = cd
  return nd
      
def standardize_tags(collection):
  nc = []
  for d in collection:
    nc.append(standardize_tags_helper(d))
  return nc
    
class WebTable:
  def __init__(self, name, d, keep_standards_prefix):
    self.name = name.strip()
    ic = infer_collection(d)
    if not keep_standards_prefix:
      ic = standardize_tags(ic)
    if len(self.name) > 0:
      ic = prep_name(name, ic)
    self.rows = ic

  def rename(self, before, after):
    bn = self.name + NAMESPACE_CHAR + before
    an = self.name + NAMESPACE_CHAR + after
    for d in self.rows:
      if bn in d:
        value = copy.copy(d[bn])
        del d[bn]
        d[an] = value

  def describe(self):
    print "\n"
    print "TABLENAME: %s, # RECORDS: %d" % (self.name, self.__len__())
    if len(self.rows) == 0:
      return
    c = self.rows[0]
    for k, v in c.iteritems():
      print "\tOUTER KEY:", k
      if is_dict(type(v)):
        print "\t  INNER KEYS:"
        print "\t  ", v.keys(), "\n"

  def dumps(self, format="json"):
    if format == "json":
      return simplejson.dumps(self.rows)
    elif format == "xml":
      return dict2xml.dict2Xml({self.name: self.rows})
    elif format == "opensearch":
      raise Error, "opensearch dumps needs to be implemented!"

  def dump(self, f, format="json"):
    open(f, "w").write(self.dumps(format))

  def __len__(self):
    return len(self.rows)


def create(name="", data=None, url=None, keep_standards_prefix=False):
  if data is not None:
    return WebTable(name, d=data, keep_standards_prefix=keep_standards_prefix)
  elif url is not None:
    return WebTable(name, d=rest.load(url), keep_standards_prefix=keep_standards_prefix)

def postcreate(data):
  return WebTable(name="", d=data, keep_standards_prefix=True)


def select(udf, name="", url=None, table=None, data=None, keep_standards_prefix=False):
  if table is not None:
    tb = table
    keep_standards_prefix = True
    if len(name) == 0:
      name = tb.name
  else:
    tb = create(name, data=data, url=url, keep_standards_prefix=keep_standards_prefix)

  results = []
  for d in tb.rows:
    try:
      value = udf(d)
    except KeyError:
      try:
        value = udf(strip_row(d)[0])
      except KeyError:
        continue
    if is_dict(type(value)):
      results.append(value)
  return create(name=name, data=results, keep_standards_prefix=keep_standards_prefix)


def union(name, tables):
  data = []
  for t in tables:
    rows = t.rows
    for d in rows:
      nd = {}
      for k, v in d.iteritems():
        nd[strip_prep(k)] = v
      data.append(nd)
  return create(name=name, data=data)
    

def sort(key, table, order="desc", count=None):
  nc = []
  for c in table.rows:
    if key in c:
      nc.append( (c, c[key]) )
    else:
      nc.append( (c, None) )
  rv = True
  if order == "asc":
    rv = False

  if count is None:
    return postcreate(data=[c for c, s in sorted(nc, key=itemgetter(1), reverse=rv)])
  else:
    return postcreate(data=[c for c, s in sorted(nc, key=itemgetter(1), reverse=rv)[:count]])


def identity(x):
  return x


def group(by, key, reducer, as, table, norm=identity, unique=True):
  if not is_ordered(type(by)):
    by = [by]
  r = {}
  for row in table.rows:
    thk = []
    for b in by:
      if b in row:
        thk.append(norm(row[b]))
      else:
        thk.append(None)
    thk = tuple(thk)
    if thk in r:
      r[thk].append(row)
    else:
      r[thk] = [row]

  answer = []
  for thk, rows in r.iteritems():
    try:
      nr = []
      for r in rows:
        if key in r:
          nr.append(r[key])
      asv = reduce(reducer, nr)
    except:
      asv = None

    if unique:
      r = rows[0]
      r[as] = asv
      answer.append(r)
    else:
      for r in rows:
        r[as] = asv
        answer.append(r)

  return postcreate(data=answer)    

"""
When using yos.yql.db, keep in mind that for join calls
like join (inner_join), outer_join (left_outer_join)
that the first parameter (predicate function) should operate on row keys assuming no namespacing
like row['yn$title'] => should be row['title'] within the predicate function code
This is because the predicate function is being applied like a map function,
so the order of the tables input (second parameter) does not matter
It also doesn't make sense when the number of tables exceeds 2
as a predicate function only operates on records from two tables at a time
A commutative, functional, map like join seems to make joining lots of tables more concise and easier
"""

def join_check(f, r1, r2):
  try:
    stripped_r1 = strip_row(r1)
    stripped_r2 = strip_row(r2)
    for sr1 in stripped_r1:
      for sr2 in stripped_r2:
        if f(sr1, sr2):
          return True
    return False
  except KeyError:
    return False

def inner_match(f, c1, c2):
  answer = []
  for r1 in c1:
    nr1 = copy.copy(r1)
    for r2 in c2:
      if join_check(f, r1, r2):
        nr1.update(r2)
    if r1 != nr1: 
      answer.append(nr1)
  return answer

def outer_match(f, c1, c2):
  answer = []
  for r1 in c1:
    m = False
    for r2 in c2:
      if join_check(f, r1, r2):
        nr1 = copy.copy(r1)
        nr1.update(r2)
        answer.append(nr1)
        m = True
    if not m:
      answer.append(r1)
  return answer

def inner_join(f, tbs):
  results = tbs[0].rows
  ld = len(tbs)
  if ld > 1:
    for i in xrange(1, ld):
      next = tbs[i].rows
      results = inner_match(f, results, next)
  return postcreate(results)

join = inner_join
 
def left_outer_join(f, tbs):
  results = tbs[0].rows
  ld = len(tbs)
  if ld > 1:
    for i in xrange(1, ld):
      next = tbs[i].rows
      results = outer_match(f, results, next)
  return postcreate(results)

outer_join = left_outer_join

def cross_match(rows1, rows2):
  r = []
  for r1 in rows1:
    for r2 in rows2:
      nr = copy.copy(r1)
      nr.update(r2)
      r.append(nr)
  return r

def cross(tbs):
  results = tbs[0].rows
  ld = len(tbs)
  if ld > 1:
    for i in xrange(1, ld):
      results = cross_match(results, tbs[i].rows)
  return postcreate(results)
