#! /usr/bin/python -t
# _*_ coding: iso-8859-1 _*_

MODULE_NAME = "argparser"
MODULE_DESC = "Tools for command line parsing"
MODULE_VERS = "1.0"

# !!! TO DO : write the module info.
# !!! TO DO : change the {pp.next} cursor to be {pp.last} (last parsed). 
# !!! TO DO : add the remaining methods from {argparser.h}

MODULE_COPYRIGHT = "Copyright © 2008 State University of Campinas"

MODULE_INFO = "!!! MODULE_INFO to be written"

import sys
import re
import string
import copy
import decimal
from decimal import Decimal

# Functions for parsing UNIX command line arguments.

class ArgParser :
  "A parser for command line options.\n" \
  "\n" \
  "  An {ArgParser} instance is a tool that parses a list of" \
  " command line arguments, given when the instance is created.  It supports" \
  " both keyword arguments in any order, and positional arguments" \
  " given in a fixed order, either relative to the keywords or absolute, as in\n" \
  "  \n" \
  "    printdoc \\\n" \
  "      -justify \\\n" \
  "      -pageRange 1 10 \\\n" \
  "      -page 17 -page 22 \\\n" \
  "      -format portrait pagenumbers '%03d' \\\n" \
  "      -title 'Foo' \\\n" \
  "      file1.txt file2.txt file3.txt\n" \
  "  \n"
  
  def __init__(pp, argv, errf, help, info) :
    "Initalizes the {ArgParser} instance and handles '-help'/'-info' options.\n" \
    "\n" \
    "  The arguments are:\n" \
    "    {argv} = the command line argument list.\n" \
    "    {errf} = a file where error messages should be printed.\n" \
    "    {help} = help text to be printed by '-help' or after errors.\n" \
    "    {info} = documentation text to be printed by '-info'.\n" \
    "  Also parses the '-help' and '-info' options, if present."
    
    # Instance setup:
    # {pp.argv} is a local copy of the {argv} list, and {pp.argc} is its length:
    pp.argv = copy.copy(argv)
    pp.argc = len(pp.argv)
    # {pp.errf} is the file for error messages:
    pp.errf = errf;
    # {pp.parsed[i]} tells whether {pp.argv[i]} has been consumed:
    pp.parsed = [ 0 ]*len(pp.argv)
    # {pp.next} is the index of the next argument for sequential parsing:
    pp.parsed[0] = 1; # Mark the command name as having been parsed already.
    pp.next = 1;      # Position the cursor just after the command name.
    # {pp.help} is the help text to be printed in case of errors:
    pp.help = help
    
    # Parse the "-help" option:
    if pp.help != None and (pp.keyword_present("-help") or pp.keyword_present("--help")) :
      pp.errf.write("usage: %s\n" % pp.help)
      sys.exit(0)
      
    # Parse the "-info" option:
    if info != None and (pp.keyword_present("-info") or pp.keyword_present("--info")) :
      print_info(pp.errf, info + "\n")
      sys.exit(0)
  # ----------------------------------------------------------------------

  def keyword_present(pp, key) :
    "Parses an optional keyword argument {key}.\n" \
    "\n" \
    "  If the string {key} occurs among the arguments, marks it parsed," \
    " positions the argument cursor just after it, and returns 1.  Otherwise" \
    " does not change anything and returns 0." \
    
    # Must add {key} at the end to prevent raising {ValueError}:
    k = (pp.argv + [key]).index(key);
    if k >= pp.argc : 
      return 0
    else :
      pp.parsed[k] = 1
      pp.next = k+1
      return 1
  # ----------------------------------------------------------------------
    
  def get_keyword(pp, key) :
    "Parses a mandatory keyword argument {key}.\n" \
    "\n" \
    "  If the string {key} occurs among the arguments, marks it parsed," \
    " and positions the argument cursor just after it.  Otherwise" \
    " raises an error." \
    
    # Must add {key} at the end to prevent raising {ValueError}:
    k = (pp.argv + [key]).index(key);
    if k >= pp.argc : 
      pp.error("keyword %s missing or already parsed" % (key))
    else :
      pp.parsed[k] = 1
      pp.next = k+1
  # ----------------------------------------------------------------------
    
  def get_next(pp, mayBeNone = 0) :
    "Returns and consumes the next argument after the cursor.\n" \
    "\n" \
    "  If the next argument after the cursor exists and is still unparsed," \
    " marks it as parsed, advances the cursor past it, and returns it.  Otherwise" \
    " raises {ValueError}.\n" \
    "\n" \
    "  If {mayBeNone} is true, the strings 'NONE', 'None', 'none' and '' are" \
    " mapped to the {None} value.  Otherwise the result is never {None}."
    
    if pp.next < pp.argc and (not pp.parsed[pp.next]) : 
      v = pp.argv[pp.next]
      pp.parsed[pp.next] = 1
      pp.next += 1;
      if mayBeNone and (v == 'None' or v == 'none' or v == 'NONE' or v == '') :
        v = None
      return v
    else :
      if pp.next < pp.argc :
        xv = " = «" + pp.argv[pp.next] + "»"
      else:
        xv = ""
      pp.error("argument %d%s missing or already parsed" % (pp.next, xv))
  # ----------------------------------------------------------------------

  def get_next_char(pp, mayBeNone = 0) :
    "Returns and consumes the next 1-character argument after the cursor.\n" \
    "\n" \
    "  Like {get_next}, but requires the argument to be a single-character" \
    " string.  Otherwise raises {ValueError}.\n" \
    "\n" \
    "  If {mayBeNone} is true, also accepts the strings 'NONE', 'None', 'none' and ''," \
    " which get converted to {None}." 
    
    mn = ["", " or 'None'"][mayBeNone]
    v = pp.get_next(mayBeNone)
    if (mayBeNone and v == None) or (v != None and len(v) == 1) :
      return v
    else :
      pp.error("argument %d = «%s» should be one char%s" % (pp.next, v, mn))
  # ----------------------------------------------------------------------

  def get_next_int(pp, vmin, vmax, mayBeNone = 0) :
    "Returns and consumes the next 1-character argument after the cursor.\n" \
    "\n" \
    "  Like {get_next}, but requires the argument to be a decimal integer" \
    " between {vmin} and {vmax}.  Otherwise raises {ValueError}.\n" \
    "\n" \
    "  If {mayBeNone} is true, also accepts the strings 'NONE', 'None', 'none' and ''," \
    " which get converted to {None}." 

    mn = ["", " or 'None'"][mayBeNone]
    v = pp.get_next(mayBeNone)
    if mayBeNone and v == None : 
      return None
    elif v == None :
      # Just in case:
      pp.error("argument %d is missing, expected an integer" % pp.next)
    else :
      vn = Decimal(v)
      if vn.same_quantum(Decimal("NaN")) or vn != vn.to_integral():
        pp.error("argument %d = «%s» should be an integer%s" % (pp.next, v, mn))
      elif vn < vmin or vn > vmax :
        pp.error("argument %d = «%s» should be in [%d .. %d]%s" % (pp.next, v, vmin, vmax, mn))
      else :
        return vn
  # ----------------------------------------------------------------------

  def error(pp, msg) :
    "Prints the error message {msg}, the help text, and stops.\n"

    pp.errf.write("%s\n" % msg)
    pp.errf.write("usage: %s\n" % pp.help)
    sys.exit(1)
  # ----------------------------------------------------------------------

def print_info(wr, info) :
  "Prints a program's manpage {info} to file {wr}.\n" \
  "\n" \
  "  Writes to file {wr} the string {info}, assumed to" \
  " contain a UNIX-like program's manpage.  It is usually" \
  " called to procss the standard '-info'/'--info' command" \
  " line argument.\n" \
  "\n" \
  "  At present, the procedure merely writes {info} to {wr}" \
  " unchanged. Eventually it should break long lines" \
  " preserving their initial indentation."

  wr.write(info)

help_info_HELP = \
  "    [ -help | --help ] [ -info | --info ]"

help_info_INFO = \
  "  -help\n" \
  "  --help\n" \
  "    Prints an options summary and exits.\n" \
  "\n" \
  "  -info\n" \
  "  --info\n" \
  "    Prints this manpage and exits."

help_info_NO_WARRANTY = \
  "This software is provided 'as is', WITHOUT ANY EXPLICIT OR" \
  " IMPLICIT WARRANTY, not even the implied warranties of merchantibility" \
  " and fitness for a particular purpose."

help_info_STANDARD_RIGHTS = \
  "See the GNU Free Documentation License, Version 1.2, 1.3, or any later version published by the Free Software Foundation"
