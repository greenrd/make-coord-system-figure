#! /usr/bin/python -t
# _*_ coding: iso-8859-1 _*_

MODULE_NAME = "hrn"
MODULE_DESC = "Oriented projective geometry in {n} dimensions"
MODULE_VERS = "1.0"

MODULE_COPYRIGHT = "Copyright © 2009 State University of Campinas"

MODULE_INFO = \
  "A library module to perform oriented projective geometry in {n} dimensions.\n" \
  "\n" \
  "  Bla bla.\n"

import sys
import rn
import rmxn

def pt_pt_add(x,y) :
  "Adds the points {x,y} interpreted as Cartesian vectors of {R^3} embedded in {H^3}." \
  "\n" \
  "  Returns a point at infinity (or null) if {x,y} are in opposite ranges of {H^3}."
  n = len(x);
  assert len(y) == n, "incompatible {x},{y} lengths";
  wx = abs(x[0]);
  wy = abs(y[0]);
  r = [None]*n;
  for i in range(n) :
    if (i == 0) :
      r[i] = (wy*x[0] + wx*y[0])/2;
    else :
      r[i] = wy*x[i] + wx*y[i];
  return r;

def pt_scale(x,s) :
  "Applies to the point {x} the affine scaling whose Cartesian diagonal is {s}."
  assert len(x) == len(s)+1, "incompatible {x},{s} lengths";
  r = x;
  d = len(s);
  for i in range(d) :
    r[i+1] = r[i+1] * s[i]
  return r;

def trans_matrix(ref) :
  "Projective matrix of a translation that takes the origin to the point {ref}."
  
  n = len(ref);
  w = ref[0];
  M = [ref];
  for i in range(n) :
    if (i > 0) :
      M[i:i] = [[]];
      for j in range(n) :
        M[i][j:j] = [ 0 ];
        if (i == j) : M[i][j] = w;
  return M;

def scale_matrix(s) :
  "Projective matrix of an axial scaling that takes {[1,1...1]} to the point {s} of {H^n}."
  return rmxn.diag_matrix(s);

