#! /usr/bin/python -t
# _*_ coding: iso-8859-1 _*_

MODULE_NAME = "rn"
MODULE_DESC = "Linear algebra operations on numeric vectors"
MODULE_VERS = "1.0"

MODULE_COPYRIGHT = "Copyright © 2009 State University of Campinas"

MODULE_INFO = \
  "A library module to perform linear algebra operations on numeric vectors.\n" \
  "\n" \
  "  Bla bla.\n"

import sys
import copy
from math import sqrt

def add(x,y) :
  "Vector sum of {x+y}."
  n = len(x);
  assert len(y) == n, "incompatible {x,y} lenghts";
  r = copy.copy(x);
  for i in range(n) :
    r[i] += y[i];
  return r;
  # ----------------------------------------------------------------------

def sub(x,y) :
  "Vector difference {x-y}."
  n = len(x);
  assert len(y) == n, "incompatible {x,y} lenghts";
  r = copy.copy(x);
  for i in range(n) :
    r[i] -= y[i];
  return r;
  # ----------------------------------------------------------------------

def scale(s,x) :
  "Scals the vector {x} by {s}."
  n = len(x);
  r = copy.copy(x);
  for i in range(n) :
    r[i] *= s;
  return r;
  # ----------------------------------------------------------------------

def dir(x) :
  "Vector {x} normalized to unit Euclidean length. Also returns the original norm."
  n = len(x);
  e = norm(x);
  r = copy.copy(x);
  for i in range(n) :
    r[i] /= e;
  return r, e;
  # ----------------------------------------------------------------------

def dot(x,y) :
  "Scalar product of {x} by {y}."
  n = len(x);
  assert len(y) == n, "incompatible {x,y} lenghts";
  s = 0;
  for i in range(n) :
    s += x[i] * y[i];
  return s;
  # ----------------------------------------------------------------------

def norm_sqr(x) :
  "Square of Euclidean norm of {x}."
  n = len(x);
  s = 0;
  for i in range(n) :
    xi=x[i]; s += xi*xi;
  return s;
  # ----------------------------------------------------------------------

def norm(x) :
  "Euclidean norm of {x}."
  return sqrt(norm_sqr(x));
  # ----------------------------------------------------------------------

def dist(x,y) :
  "Euclidean distance between {x} and {y}."
  return norm(sub(x,y));
  # ----------------------------------------------------------------------

def cross2(x,y) :
  "Cross product of two vectors in R^3."
  assert len(x) == 3, "{x} must be a point of R^3";
  assert len(y) == 3, "{y} must be a point of R^3";
  return [ x[1]*y[2]-x[2]*y[1], x[2]*y[0]-x[0]*y[2], x[0]*y[1]-x[1]*y[0]];
  # ----------------------------------------------------------------------

# ----------------------------------------------------------------------
