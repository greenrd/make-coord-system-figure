#! /usr/bin/python -t
# _*_ coding: iso-8859-1 _*_
# Last edited on 2009-05-02 19:56:43 by stolfi

MODULE_NAME = "rmxn"
MODULE_DESC = "Linear algebra operations on rectangular numeric matrices"
MODULE_VERS = "1.0"

MODULE_COPYRIGHT = "Copyright © 2009 State University of Campinas"

MODULE_INFO = \
  "A library module to perform linear algebra operations on rectangular numeric matrices.\n" \
  "\n" \
  "  Bla bla.\n"

import sys
import rn

def zero_matrix(m,n) :
  "Zero matrix with {m} rows and {n} cols."
  R = [None]*m;
  for i in range(m) :
    R[i] = [0.0]*n;
  return R;
  # ----------------------------------------------------------------------

def ident_matrix(m,n) :
  "Identity matrix with {m} rows and {n} cols."
  R = [None]*m;
  for i in range(m) :
    R[i] = [0.0]*n;
    if (i < n) : R[i][i] = 1.0;
  return R;
  # ----------------------------------------------------------------------

def diag_matrix(x) :
  "Square diagonal matrix with {x} as the diagonal."
  n = len(x);
  R = zero_matrix(n,n);
  for i in range(n) :
    R[i][i] = x[i];
  return R;
  # ----------------------------------------------------------------------

def mul(M,N) :
  "Multiplies the matrices {M} and {N}."
  m = len(M);
  n = len(N[0]);
  R = [None]*m;
  for i in range(m) :
    R[i]= map_row(M[i],N)
  return R;
  # ----------------------------------------------------------------------

def map_row(x,M) :
  "Multiplies the vector {x} by the matrix {M}."
  m = len(x);
  assert len(M) == m, "incompatible {x} lenght and {M} rows";
  n = len(M[0]);
  r = [None] * n;
  for j in range(n) :
    s = 0;
    for i in range(m) :
      s = s + x[i] * M[i][j];
    r[j] = s
  return r;
  # ----------------------------------------------------------------------

def map_col(M,x) :
  "Multiplies the matrix {M} by the vector {x}"
  n = len(x);
  m = len(M);
  r = [None] * m;
  for i in range(m) :
    r[i] = rn.dot(M[i], x);
  return r;
  # ----------------------------------------------------------------------


# ----------------------------------------------------------------------
