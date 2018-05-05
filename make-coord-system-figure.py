#! /usr/bin/python -t 
# _*_ coding: iso-8859-1 _*_

PROG_NAME = "make-coord-system-figure"
PROG_DESC = "Generates an SVG illustration for the Wikipedia articles on coord systems"
PROG_VERS = "1.0"

import sys
import re
import os
import copy
import math
from math import sqrt,sin,cos
sys.path[1:0] = [ sys.path[0] + '/../lib', os.path.expandvars('${STOLFIHOME}/lib'), '.' ] 
import argparser; from argparser import ArgParser
import rn
import rmxn
import hrn
import perspective

from decimal import *
from datetime import date

PROG_COPYRIGHT = "Copyright © 2009-05-02 by the State University of Campinas (UNICAMP)"

PROG_HELP = \
  PROG_NAME+ " \\\n" \
  "    -back {BOOL} \\\n" \
  "    -frame {BOOL} \\\n" \
  "    -rho {BOOL} \\\n" \
  "    -system { \"SE\" | \"SZ\" | \"CY\" | \"CA\" } \\\n" \
  +argparser.help_info_HELP+ " \\\n" \
  "    > {FIGURE}.svg"
  
PROG_INFO = \
  "NAME\n" \
  "  " +PROG_NAME+ " - " +PROG_DESC+  ".\n" \
  "\n" \
  "SYNOPSIS\n" \
  "  " +PROG_HELP+ "\n" \
  "\n" \
  "DESCRIPTION\n" \
  "  Writes an SVG illustration for the Wikipedia articles on coord systems.\n" \
  "\n" \
  "OPTIONS\n" \
  "  -back {BOOL} \n" \
  "    If {BOOL} is 1, paints the background with a nonwhite color. If {BOOL} is 0," \
  " leaves it transparent. This option is meant to debug the image size.\n" \
  "\n" \
  "  -frame {BOOL} \n" \
  "    If {BOOL} is 1, draws some framing lines. This option is meant" \
  " to debug the plot dimensions.\n" \
  "\n" \
  "  -rho {BOOL} \n" \
  "    If {BOOL} is 1, uses \"rho\" for radius, else uses \"r\".\n" \
  "\n" \
  "  -system { \"SE\" | \"SZ\" | \"CY\" | \"CA\" } \n" \
  "    Coordinate system to illustrate.\n" \
  "      \"SE\" = Spherical (elevation angle).\n" \
  "      \"SZ\" = Spherical (zenith angle).\n" \
  "      \"CY\" = Cylindrical.\n" \
  "      \"CA\" = Cartesian.\n" \
  "\n" \
  "DOCUMENTATION OPTIONS\n" \
  +argparser.help_info_INFO+ "\n" \
  "\n" \
  "SEE ALSO\n" \
  "  cat(1).\n" \
  "\n" \
  "AUTHOR\n" \
  "  Created 2009-04-04 by Jorge Stolfi, IC-UNICAMP.\n" \
  "\n" \
  "MODIFICATION HISTORY\n" \
  "  2009-04-04 by J. Stolfi, IC-UNICAMP: created.\n" \
  "\n" \
  "WARRANTY\n" \
  "  " +argparser.help_info_NO_WARRANTY+ "\n" \
  "\n" \
  "RIGHTS\n" \
  "  " +PROG_COPYRIGHT+ ".\n" \
  "\n" \
  "  " +argparser.help_info_STANDARD_RIGHTS

# COMMAND ARGUMENT PARSING
pp = ArgParser(sys.argv, sys.stderr, PROG_HELP, PROG_INFO)

class Options :
  back = None;
  system = None;
  err = None;
 
def arg_error(msg):
  "Prints the error message {msg} about the command line arguments, and aborts."
  sys.stderr.write("%s\n" % msg);
  sys.stderr.write("usage: %s\n" % PROG_HELP);
  sys.exit(1)

def parse_args(pp) :
  "Parses command line arguments.\n" \
  "\n" \
  "  Expects an {ArgParser} instance {pp} containing the arguments," \
  " still unparsed.  Returns an {Options} instance {op}, where" \
  " {op.err} is an error message, if any (a string) or {None}."
  
  op = Options();
 
  # Being optimistic:
  op.err = None

  pp.get_keyword("-back")
  op.back = pp.get_next_int(0, 1)
  
  pp.get_keyword("-frame")
  op.frame = pp.get_next_int(0, 1)
  
  pp.get_keyword("-rho")
  op.rho = pp.get_next_int(0, 1)
  
  pp.get_keyword("-system")
  op.system = pp.get_next()

  return op
  #----------------------------------------------------------------------

class Dimensions :
  "Plot dimensions and perspective matrix." 
  
  def __init__(dim, op) :

    dim.map = None;     # World to Image perspective map.

    # Coordinates of point:
    dim.xc_val = None; # X coordinate (for all systems).
    dim.yc_val = None; # Y coordinate (for all systems).
    dim.zc_val = None; # Z coordinate (for all systems).
    dim.rc_val = None; # Radial coordinate (for SE, SZ, CY).
    dim.ac_val = None; # Azimuth angle (for SE, SZ, CY).
    dim.ec_val = None; # Elevation angle (for SE, SZ).

    dim.hd_len = 0.08; # Length of arrow heads (W).
    dim.ax_len = 1.20; # Length of coord axes (W).

    dim.font_wy = 30;  # Font size in pixels.

    dim.pt_rad = 0.02; # Point size in World units.

    dim.ax_unit = 0.2; # Unit for axis ticks.

    dim.fig_wx = 620;  # Total figure width.
    dim.fig_wy = 600;  # Total figure height.

    dim.ct_color = '200,0,100';  # Color for significant coord traces.

    dim.map = None;    # World to Image perspective map.
    dim.scale = 1.0;   # Final scale factor (can be chaged without changing any other dim).

    # Coordinates of point:
    if (op.system == 'CA') :
      dim.xc_val = 0.4;
      dim.yc_val = 0.6;
      dim.zc_val = 0.8;
    elif (op.system == 'CY') :
      dim.rc_val = 0.8;
      dim.ac_val = math.radians(130);
      dim.zc_val = 0.8;
      # Compute X,Y from azimuth and radius:
      dim.xc_val = dim.rc_val*cos(dim.ac_val);
      dim.yc_val = dim.rc_val*sin(dim.ac_val);
    elif (op.system == 'SE'):
      dim.rc_val = 0.8;
      dim.ac_val = math.radians(130);
      dim.ec_val = math.radians(50);
      # Compute X,Y,Z from azimuth, elevation, and radius:
      dim.xc_val = dim.rc_val*cos(dim.ec_val)*cos(dim.ac_val);
      dim.yc_val = dim.rc_val*cos(dim.ec_val)*sin(dim.ac_val);
      dim.zc_val = dim.rc_val*sin(dim.ec_val);
    elif (op.system == 'SZ'):
      dim.rc_val = 0.8;
      dim.ac_val = math.radians(130);
      dim.ec_val = math.radians(70);
      # Compute X,Y,Z from azimuth, elevation, and radius:
      dim.xc_val = dim.rc_val*sin(dim.ec_val)*cos(dim.ac_val);
      dim.yc_val = dim.rc_val*sin(dim.ec_val)*sin(dim.ac_val);
      dim.zc_val = dim.rc_val*cos(dim.ec_val);
    else :
      assert False, "invalid coord system";

    # Perspective map:
    att = [0,0,0];
    obs = [5,3,3];
    upd = [0,0,1];

    mag = [+220,-220,+220];
    ctr = [+320,+300,0000];

    dim.map = perspective.camera_matrix(att,obs,upd,mag,ctr);
    sys.stderr.write("dim.map = %s\n" % dim.map);
    #----------------------------------------------------------------------

  #----------------------------------------------------------------------
  
def output_figure(op) :
  "Writes the figure to {stdout}."
  "\n" \
  "  Expects an {Options} instance {op}."

  # Computes the sizes of things and the perspective map:
  dim = Dimensions(op)

  output_figure_preamble(op,dim)
  sys.stdout.write('\n')
  output_figure_obj_defs(op,dim)
  sys.stdout.write('\n')
  output_figure_body(op,dim)
  sys.stdout.write('\n')
  output_figure_postamble(op,dim)
  sys.stderr.write("done.\n")
  #----------------------------------------------------------------------
  
def output_figure_preamble(op,dim) :
  "Writes the SVG preamble to {stdout}."
  
  sys.stdout.write( \
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' \
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n' \
    '<!-- Created on '+ date.isoformat(date.today()) +' by Robin Green with the script make-coord-system-figure -->\n' \
    '<!-- This file is declared PUBLIC DOMAIN by its creator -->\n' \
    '\n' \
    '<svg\n' \
    '  id="fig"\n' \
    '  xmlns="http://www.w3.org/2000/svg"\n' \
    '  xmlns:xlink="http://www.w3.org/1999/xlink"\n' \
    '\n' \
    '  fill="none"\n' \
    '  fill-opacity="1"\n' \
    '  fill-rule="evenodd"\n' \
    '\n' \
    '  stroke-linecap="round"\n' \
    '  stroke-linejoin="round"\n' \
    '  stroke-dasharray="none"\n' \
    '  stroke-opacity="1"\n' \
    '  stroke-width="1.5px"\n' \
    '\n' \
    '  font-style="normal"\n' \
    '  font-weight="normal"\n' \
    '  font-size="'+ dts(dim.font_wy) +'px"\n' \
    '  font-family="Bitstream Vera"\n' \
    '\n' \
    '  width="'+ dts(dim.scale*dim.fig_wx) +'"\n' \
    '  height="'+ dts(dim.scale*dim.fig_wy) +'"\n' \
    '>\n' \
  )
  sys.stdout.write('\n')
  if (op.back) :
    sys.stdout.write( \
      '    <!-- Rectangle to test the figure size -->\n' \
      '    <rect x="000" y="000" width="'+ dts(dim.scale*dim.fig_wx) +'" height="'+ dts(dim.scale*dim.fig_wy) +'"' \
             ' stroke="#000000" stroke-width="2px" fill="#ffcc55"' \
             ' />\n' \
    )
  sys.stdout.write('\n')

  # Scale everything and position the diagram:
  sys.stdout.write( \
    '  <g\n' \
    '    transform="scale('+ dts(dim.scale)+ ')"\n' \
    '  >\n' \
  )
  #----------------------------------------------------------------------

def output_figure_obj_defs(op,dim) :
  "Writes the main object definitions to {stdout}."

  sys.stdout.write( \
    '  <defs>\n' \
    '  </defs>\n' \
  )
  #----------------------------------------------------------------------

def output_figure_body(op,dim) :
  "Writes the body of the figure to {stdout}."

  # Plot the reference plane(s):
  if (op.system == 'CA') :
    output_system_planes_CA(op,dim);
  else:
    output_system_planes_CY_SE_SZ(op,dim);

  pos_W = [dim.xc_val,dim.yc_val,dim.zc_val];
  
  if (op.system == 'SE') :
    output_system_SE(op,dim,pos_W);
  elif (op.system == 'CA') :  
    output_system_CA(op,dim,pos_W);
  elif (op.system == 'CY') :  
    output_system_CY(op,dim,pos_W);
  elif (op.system == 'SZ') :  
    output_system_SZ(op,dim,pos_W);
  else :
    assert False, "invalid {op.system}";

def output_system_planes_CA(op,dim):

  # Key World points:
  ooo_W = [00,00,00]; # Origin.

  poo_W = [+1,00,00]; # +X axis dir.
  moo_W = [-1,00,00]; # -X axis dir.
  
  opo_W = [00,+1,00]; # +Y axis dir.
  omo_W = [00,-1,00]; # -Y axis dir.
  
  oop_W = [00,00,+1]; # +Z axis dir.
  oom_W = [00,00,-1]; # -Z axis dir.

  # Key Image points:
  ooo = img_point(ooo_W,dim.map); # Origin.

  moo = img_point(moo_W,dim.map); # Point -1 on X axis
  poo = img_point(poo_W,dim.map); # Point +1 on X axis

  omo = img_point(omo_W,dim.map); # Point -1 on U axis
  opo = img_point(opo_W,dim.map); # Point +1 on U axis

  oom = img_point(oom_W,dim.map); # Point -1 on Z axis
  oop = img_point(oop_W,dim.map); # Point +1 on Z axis

  pmo = img_point(rn.add(poo_W,omo_W),dim.map); # Corner A of XY square.
  ppo = img_point(rn.add(poo_W,opo_W),dim.map); # Corner B of XY square.
  mpo = img_point(rn.add(moo_W,opo_W),dim.map); # Corner C of XY square.
  mmo = img_point(rn.add(moo_W,omo_W),dim.map); # Corner D of XY square.

  opm = img_point(rn.add(opo_W,oom_W),dim.map); # Corner A of UZ square.
  opp = img_point(rn.add(opo_W,oop_W),dim.map); # Corner B of UZ square.
  omp = img_point(rn.add(omo_W,oop_W),dim.map); # Corner C of UZ square.
  omm = img_point(rn.add(omo_W,oom_W),dim.map); # Corner D of UZ square.

  mop = img_point(rn.add(moo_W,oop_W),dim.map); # Corner A of ZX square.
  pop = img_point(rn.add(poo_W,oop_W),dim.map); # Corner B of ZX square.
  pom = img_point(rn.add(poo_W,oom_W),dim.map); # Corner C of ZX square.
  mom = img_point(rn.add(moo_W,oom_W),dim.map); # Corner D of ZX square.

  sys.stdout.write( \
    '    <!-- The reference planes: -->\n' \
    '    <g stroke="rgb(185, 205, 170)" fill="rgb(215, 235, 200)" fill-opacity="0.5">\n' \
    '      <polygon points="'+ pfm(moo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(mom) +'"/>\n' \
    '      <polygon points="'+ pfm(omo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(omm) +'"/>\n' \
    '      <polygon points="'+ pfm(poo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(pom) +'"/>\n' \
    '      <polygon points="'+ pfm(opo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(opm) +'"/>\n' \
    '      \n' \
    '      <polygon points="'+ pfm(pmo) +' '+ pfm(ppo) +' '+ pfm(mpo) +' '+ pfm(mmo) +'"/>\n' \
    '      \n' \
    '      <polygon points="'+ pfm(moo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(mop) +'"/>\n' \
    '      <polygon points="'+ pfm(omo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(omp) +'"/>\n' \
    '      <polygon points="'+ pfm(poo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(pop) +'"/>\n' \
    '      <polygon points="'+ pfm(opo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(opp) +'"/>\n' \
    '    </g>\n' \
  );
  if (op.frame) :
    # Auxiliary lines for debugging:
    sys.stdout.write( \
      '    <polygon points="'+ pfm(pmo) +' '+ pfm(ppo) +' '+ pfm(mpo) +' '+ pfm(mmo) +'" stroke="rgb(177,0,0)" fill="none" />\n' \
      '    <path d="M '+ pfm(pmo) +' L '+ pfm(mpo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(ppo) +' L '+ pfm(mmo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(moo) +' L '+ pfm(poo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(omo) +' L '+ pfm(opo) +'" stroke="rgb(137, 137, 137)"/>\n' \
    );
    sys.stdout.write('\n');
  #----------------------------------------------------------------------
  
def output_system_planes_CY_SE_SZ(op,dim):

  # Key World points:
  ooo_W = [00,00,00]; # Origin.

  poo_W = [+1,00,00]; # +X axis dir.
  moo_W = [-1,00,00]; # -X axis dir.
  
  opo_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,1.0); # +U axis dir.
  omo_W = vec_from_ang_rad([-1,00,00],[00,-1,00],dim.ac_val,1.0); # -U axis dir.
  
  oop_W = [00,00,+1]; # +Z axis dir.
  oom_W = [00,00,-1]; # -Z axis dir.

  # Key Image points:
  ooo = img_point(ooo_W,dim.map); # Origin.

  moo = img_point(moo_W,dim.map); # Point -1 on X axis
  poo = img_point(poo_W,dim.map); # Point +1 on X axis

  omo = img_point(omo_W,dim.map); # Point -1 on U axis
  opo = img_point(opo_W,dim.map); # Point +1 on U axis

  oom = img_point(oom_W,dim.map); # Point -1 on Z axis
  oop = img_point(oop_W,dim.map); # Point +1 on Z axis

  opm = img_point(rn.add(opo_W,oom_W),dim.map); # Corner A of UZ square.
  opp = img_point(rn.add(opo_W,oop_W),dim.map); # Corner B of UZ square.
  omp = img_point(rn.add(omo_W,oop_W),dim.map); # Corner C of UZ square.
  omm = img_point(rn.add(omo_W,oom_W),dim.map); # Corner D of UZ square.

  mop = img_point(rn.add(moo_W,oop_W),dim.map); # Corner A of ZX square.
  pop = img_point(rn.add(poo_W,oop_W),dim.map); # Corner B of ZX square.
  pom = img_point(rn.add(poo_W,oom_W),dim.map); # Corner C of ZX square.
  mom = img_point(rn.add(moo_W,oom_W),dim.map); # Corner D of ZX square.

  # !!! BUG !!! should compute the ellipse from the map !!!
  sys.stdout.write( \
    '    <!-- The reference planes: -->\n' \
    '    <g stroke="rgb(185, 205, 170)" fill="rgb(215, 235, 200)" fill-opacity="0.5">\n' \
    '      <polygon points="'+ pfm(moo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(mom) +'"/>\n' \
    '      <polygon points="'+ pfm(omo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(omm) +'"/>\n' \
    '      <polygon points="'+ pfm(poo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(pom) +'"/>\n' \
    '      <polygon points="'+ pfm(opo) +' '+ pfm(ooo) +' '+ pfm(oom) +' '+ pfm(opm) +'"/>\n' \
    '      \n' \
    '      <ellipse cx="0" cy="14" rx="222" ry="102" transform="translate('+ pfm(ooo) +')rotate(0)"/>\n' \
    '      \n' \
    '      <polygon points="'+ pfm(moo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(mop) +'"/>\n' \
    '      <polygon points="'+ pfm(omo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(omp) +'"/>\n' \
    '      <polygon points="'+ pfm(poo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(pop) +'"/>\n' \
    '      <polygon points="'+ pfm(opo) +' '+ pfm(ooo) +' '+ pfm(oop) +' '+ pfm(opp) +'"/>\n' \
    '    </g>\n' \
  );

  sys.stdout.write('\n');
  if (op.frame) :
    # Auxiliary lines for debugging:
    pmo = img_point([+1,-1,00],dim.map); # Corner A of XY square.
    ppo = img_point([+1,+1,00],dim.map); # Corner B of XY square.
    mpo = img_point([-1,+1,00],dim.map); # Corner C of XY square.
    mmo = img_point([-1,-1,00],dim.map); # Corner D of XY square.
    sys.stdout.write( \
      '    <polygon points="'+ pfm(pmo) +' '+ pfm(ppo) +' '+ pfm(mpo) +' '+ pfm(mmo) +'" stroke="rgb(177,0,0)" fill="none" />\n' \
      '    <path d="M '+ pfm(pmo) +' L '+ pfm(mpo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(ppo) +' L '+ pfm(mmo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(moo) +' L '+ pfm(poo) +'" stroke="rgb(137, 137, 137)"/>\n' \
      '    <path d="M '+ pfm(omo) +' L '+ pfm(opo) +'" stroke="rgb(137, 137, 137)"/>\n' \
    );
    sys.stdout.write('\n');
  #----------------------------------------------------------------------

def output_system_CA(op,dim,pos_W) :

  # Relevant points:
  ooo_W = [00,00,00];
  px_W = [dim.xc_val,00,00];
  py_W = [00,dim.yc_val,00];
  pz_W = [00,00,dim.zc_val];
  pxy_W = [dim.xc_val,dim.yc_val,00];
  pyz_W = [00,dim.yc_val,dim.zc_val];
  pxz_W = [dim.xc_val,00,dim.zc_val];

  output_coord_axis(op,dim,[+1,00,00],[-10,+5],'X');
  output_coord_axis(op,dim,[00,+1,00],[+5,-5],'Y');
  output_coord_axis(op,dim,[00,00,+1],[-7,+5],'Z');
  sys.stdout.write('\n');

  ooo = img_point(ooo_W,dim.map)
  output_label(op,dim,ooo,[-5,-5],make_italic_style('O'));

  # Coordinate traces:
  output_straight_trace(op,dim,ooo_W,px_W,True,'x');
  # output_straight_trace(op,dim,ooo_W,py_W,False,'');
  # output_straight_trace(op,dim,ooo_W,pz_W,False,'');

  output_straight_trace(op,dim,px_W,pxy_W,True,'y');
  output_straight_trace(op,dim,px_W,pxz_W,True,'');
  output_straight_trace(op,dim,py_W,pxy_W,True,'');
  output_straight_trace(op,dim,py_W,pyz_W,True,'');
  output_straight_trace(op,dim,pz_W,pxz_W,True,'');
  output_straight_trace(op,dim,pz_W,pyz_W,True,'');

  output_straight_trace(op,dim,pyz_W,pos_W,True,'');
  output_straight_trace(op,dim,pxz_W,pos_W,True,'');
  output_straight_trace(op,dim,pxy_W,pos_W,True,'z');

  # The point:
  output_point(op,dim,pos_W,dim.pt_rad,'x','y','z');
  #----------------------------------------------------------------------  

def output_system_CY(op,dim,pos_W) :
  output_coord_axis(op,dim,[+1,00,00],[-5,+5],'A');
  output_coord_axis(op,dim,[00,00,+1],[-5,-5],'L');
  sys.stdout.write('\n');

  if (op.rho) : 
    r_str = '&#961;'; 
  else : 
    r_str = 'r';  

  # Relevant points:
  ooo_W = [00,00,00];
  Pr_W = [dim.rc_val,00,00];
  Pz_W = [00,00,dim.zc_val];
  Pra_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,dim.rc_val);
  Prz_W = [dim.rc_val,00,dim.zc_val];

  ooo = img_point(ooo_W,dim.map)
  output_label(op,dim,ooo,[-5,-5],make_italic_style('O'));

  # Radial traces:
  output_straight_trace(op,dim,ooo_W,Pr_W,True,r_str);
  output_straight_trace(op,dim,ooo_W,Pra_W,True,'');
  output_straight_trace(op,dim,Pz_W,Prz_W,True,'');
  output_straight_trace(op,dim,Pz_W,pos_W,True,'');

  # Azimuth traces:
  output_circular_trace(op,dim,ooo_W,[+1,00,00],[00,+1,00],0,dim.ac_val,dim.rc_val,'&#966;');
  output_circular_trace(op,dim,Pz_W,[+1,00,00],[00,+1,00],0,dim.ac_val,dim.rc_val,'');

  # Longitudinal traces:
  # output_straight_trace(op,dim,ooo_W,Pz_W,False,'');
  output_straight_trace(op,dim,Pr_W,Prz_W,True,'');
  output_straight_trace(op,dim,Pra_W,pos_W,True,'z');

  # The point:
  output_point(op,dim,pos_W,dim.pt_rad,r_str,'&#966;','z');
  #----------------------------------------------------------------------

def output_system_SE(op,dim,pos_W) :
  output_coord_axis(op,dim,[+1,00,00],[-5,+5],'A');
  sys.stdout.write('\n');

  if (op.rho) : 
    r_str = '&#961;'; 
  else : 
    r_str = 'r';  

  # Relevant points:
  ooo_W = [00,00,00];
  Pr_W = [dim.rc_val,00,00];
  Pz_W = [00,00,dim.zc_val];
  Pra_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,dim.rc_val);
  Pre_W = vec_from_ang_rad([+1,00,00],[00,00,+1],dim.ec_val,dim.rc_val);

  # Radial traces:
  output_straight_trace(op,dim,ooo_W,Pr_W,True,r_str);
  output_straight_trace(op,dim,ooo_W,Pra_W,True,'');
  output_straight_trace(op,dim,ooo_W,Pre_W,True,'');
  output_straight_trace(op,dim,ooo_W,pos_W,True,'');
  output_straight_trace(op,dim,Pz_W,Pre_W,True,'');
  output_straight_trace(op,dim,Pz_W,pos_W,True,'');
  output_straight_trace(op,dim,ooo_W,Pz_W,True,'');
  
  # Elevation traces:
  xy_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,1.0);
  output_circular_trace(op,dim,ooo_W,[+1,00,00],[00,00,+1],0,dim.ec_val,dim.rc_val,'&#952;');
  output_circular_trace(op,dim,ooo_W,xy_W,[00,00,+1],0,dim.ec_val,dim.rc_val,'');

  # Azimuth traces:
  tp_rad = dim.rc_val*cos(dim.ec_val);
  output_circular_trace(op,dim,ooo_W,[+1,00,00],[00,+1,00],0,dim.ac_val,dim.rc_val,'');
  output_circular_trace(op,dim,Pz_W,[+1,00,00],[00,+1,00],0,dim.ac_val,tp_rad,'&#966;');

  # The point:
  output_point(op,dim,pos_W,dim.pt_rad,r_str,'&#952;','&#966;');
  #----------------------------------------------------------------------
    
def output_system_SZ(op,dim,pos_W) :
  output_coord_axis(op,dim,[+1,00,00],[-5,+5],'A');
  output_coord_axis(op,dim,[00,00,+1],[-5,-5],'Z');

  if (op.rho) : 
    r_str = '&#961;'; 
  else : 
    r_str = 'r';  

  # Relevant points:
  ooo_W = [00,00,00];
  Pr_W = [00,00,dim.rc_val];
  Pz_W = [00,00,dim.zc_val];
  Pre_W = vec_from_ang_rad([00,00,+1],[+1,00,00],dim.ec_val,dim.rc_val);

  Qr_W = [dim.rc_val*sin(dim.ec_val),00,00];
  Qra_W = [pos_W[0],pos_W[1],00];

  Sr_W = [dim.rc_val,00,00];
  Sra_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,dim.rc_val);

  # Radial traces:
  output_straight_trace(op,dim,ooo_W,Pr_W,True,r_str);
  output_straight_trace(op,dim,ooo_W,Pre_W,True,'');
  output_straight_trace(op,dim,ooo_W,pos_W,True,'');
  output_straight_trace(op,dim,Pz_W,Pre_W,True,'');
  output_straight_trace(op,dim,Pz_W,pos_W,True,'');
  # output_straight_trace(op,dim,ooo_W,Qr_W,True,'');
  # output_straight_trace(op,dim,ooo_W,Qra_W,True,'');
  output_straight_trace(op,dim,ooo_W,Sr_W,True,'');
  output_straight_trace(op,dim,ooo_W,Sra_W,True,'');

  # Vertical traces:
  # output_straight_trace(op,dim,Qr_W,Pre_W,True,'');
  # output_straight_trace(op,dim,Qra_W,pos_W,True,'');
   
  # Elevation traces:
  xy_W = vec_from_ang_rad([+1,00,00],[00,+1,00],dim.ac_val,1.0);
  output_circular_trace(op,dim,ooo_W,[00,00,+1],[+1,00,00],0,dim.ec_val,dim.rc_val,'&#952;');
  output_circular_trace(op,dim,ooo_W,[00,00,+1],[+1,00,00],dim.ec_val,math.pi/2,dim.rc_val,'');
  output_circular_trace(op,dim,ooo_W,[00,00,+1],xy_W,0,dim.ec_val,dim.rc_val,'');
  output_circular_trace(op,dim,ooo_W,[00,00,+1],xy_W,dim.ec_val,math.pi/2,dim.rc_val,'');
 
  # Azimuth traces:
  tp_rad = dim.rc_val*sin(dim.ec_val);
  output_circular_trace(op,dim,Pz_W,[+1,00,00],[00,+1,00],0,dim.ac_val,tp_rad,'&#966;');
  # output_circular_trace(op,dim,ooo_W,[+1,00,00],[00,+1,00],0,dim.ac_val,tp_rad,'');
  output_circular_trace(op,dim,ooo_W,[+1,00,00],[00,+1,00],0,dim.ac_val,dim.rc_val,'');

  # The point:
  output_point(op,dim,pos_W,dim.pt_rad,r_str,'&#952;','&#966;');
  #----------------------------------------------------------------------

def output_coord_axis(op,dim,ax_dir,lab_dp,lab_str) :
  "Draws a coordinate axis." \
  "\n" \
  "  The axis goes from the origin to {dim.ax_len*ax_dir}.  The arrow tip has" \
  " size {dim.hd_len}.  The label is {lab_str} offset by {lab_dp} from the tip."
  
  # World points:
  ooo_W = [00,00,00]; # Origin.
  tip_W = rn.add(ooo_W,rn.scale(dim.ax_len,ax_dir)); # Tip of axis.
 
  # Image points:
  ooo = img_point(ooo_W,dim.map); # Origin.
  tip = img_point(tip_W,dim.map); # Axis tip.
  
  # Axis line:
  sys.stdout.write( \
    '    <!-- The '+ lab_str +' axis: -->\n' \
    '    <path d="M '+ pfm(ooo) +' L '+ pfm(tip) +'" stroke="rgb(0,0,0)"/>\n' \
  );

  # Tics:
  # Axis line:
  sys.stdout.write( \
    '    <g stroke="rgb(0,0,0)" fill="rgb(0,0,0)">\n' \
  );
  ct = dim.ax_unit;
  while (ct < dim.ax_len - dim.hd_len) :
    tic_W = rn.add(ooo_W,rn.scale(ct,ax_dir)); # Axis tic (World).
    tic = img_point(tic_W,dim.map); # Axis tic (Image).
    sys.stdout.write( \
      '      <circle '+ xyfm(tic,'c') +' r="1px"/>\n' \
    );
    ct += dim.ax_unit;
  sys.stdout.write( \
    '    </g>\n' \
  );

  # Auxiliary directions perpendicular to the axis:
  bx_dir = [ax_dir[2], ax_dir[0], ax_dir[1]]; # Sideways direction B for arrow tip. 
  cx_dir = [ax_dir[1], ax_dir[2], ax_dir[0]]; # Sideways direction C for arrow tip. 
  output_arrow_head(op,dim,tip_W,ax_dir,bx_dir,cx_dir);

  lab_pos = rn.add(lab_dp, tip);
  output_label(op,dim,tip,lab_dp,make_italic_style(lab_str));
  sys.stdout.write('\n');
  #----------------------------------------------------------------------

def output_arrow_head(op,dim,tip_W,ax_dir,bx_dir,cx_dir) :
  "Draws an arrow head with tip at point {tip}, direction {ax_dir}, length {hd_len}." \
  "\n" \
  "  The directions {bx,dir,cx_dir} must be orthogonal to {ax_dir} and to each other."

  # World points:
  eip_W = rn.add(tip_W,rn.scale(-dim.hd_len,ax_dir));      # Base of arrow head.
  tbm_W = rn.add(eip_W,rn.scale(-0.25*dim.hd_len,bx_dir)); # Corner B+ of arrow head. 
  tbp_W = rn.add(eip_W,rn.scale(+0.25*dim.hd_len,bx_dir)); # Corner B- of arrow head. 
  tcm_W = rn.add(eip_W,rn.scale(-0.25*dim.hd_len,cx_dir)); # Corner C+ of arrow head. 
  tcp_W = rn.add(eip_W,rn.scale(+0.25*dim.hd_len,cx_dir)); # Corner C- of arrow head. 

  # Image points:
  tip = img_point(tip_W,dim.map); # Arrow tip.
  tbm = img_point(tbm_W,dim.map); # Corner B+ of arrow head. 
  tbp = img_point(tbp_W,dim.map); # Corner B- of arrow head. 
  tcm = img_point(tcm_W,dim.map); # Corner C+ of arrow head. 
  tcp = img_point(tcp_W,dim.map); # Corner C- of arrow head. 
  
  sys.stdout.write( \
    '    <path d="M '+ pfm(tcm) +' L '+ pfm(tbm) +' L '+ pfm(tcp) +' L '+ pfm(tbp) +'" stroke="rgb(0,0,0)" fill="rgb(0,0,0)" />\n' \
    '    <path d="M '+ pfm(tip) +' L '+ pfm(tbm) +' L '+ pfm(tbp) +'" stroke="rgb(0,0,0)" fill="rgb(0,0,0)" />\n' \
    '    <path d="M '+ pfm(tip) +' L '+ pfm(tcm) +' L '+ pfm(tcp) +'" stroke="rgb(0,0,0)" fill="rgb(0,0,0)" />\n' \
  );
  #----------------------------------------------------------------------

def output_label(op,dim,pos,dp,str) :
  "Ouputs a label {str} at image position {pos} displaced by {dp}."

  if (str != '') :
    dpx = dp[0];
    dpy = dp[1];
    # Compute anchor {anch}:
    if (dpx < 0) :
      anch = 'end'
    elif (dpx > 0) :
      anch = 'start'
    else :
      anch = 'middle';
    if (dpy > 0) :
      # Adjust {dpy} for font height:
      dpy += 0.6*dim.font_wy; 
    elif (dpy == 0) :
      dpy += 0.3*dim.font_wy; 
    pos = rn.add(pos, [dpx,dpy]);
    sys.stdout.write( \
      '    <text '+ xyfm(pos,'') +' stroke="rgb(255,255,255)"' \
             ' stroke-width="3px" fill="none" text-anchor="'+ anch +'">'+ str +'</text>\n' \
      '    <text '+ xyfm(pos,'') +' stroke="none"' \
             ' fill="rgb(0,0,0)" text-anchor="'+ anch +'">'+ str +'</text>\n' \
    );
  #----------------------------------------------------------------------

def output_circular_trace(op,dim,ctr_W,u_W,v_W,ang_ini,ang_fin,rad,lab_str) :
  "Draws an angular coordinate trace.\n" \
  "\n" \
  "  The arc goes from {d_ini} to {d_fin} given the center {ctr_W}, the plane's ortho" \
  " axes {u_W,v_W}, the angle interval {ang_ini,ang_fin}, and the radius {rad}." \
  "\n" \
  "  If the label is not empty, uses solid colored line, else a dashed "

  # Parameters:
  dashed = (lab_str == '');
  ang = ang_ini; # Current angle.
  step = math.pi/100; # Initial guess for step.
  if (dashed) :
    down = False; # Is the pen down?
    dlen = 2;     # Length of current dash/gap (px).
    color = '0,0,0';
  else :
    down = True;  # Is the pen down?
    dlen = 4;     # Length of current dash/gap (px).
    color = dim.ct_color;

  # Compute the dash start and stop points {dini[k],dfin[k]}:
  dini = [];
  dfin = [];
  nd = 0;

  # Initial point:
  pos_W = rn.add(ctr_W, vec_from_ang_rad(u_W,v_W,ang_ini,rad)); # Current World point.
  pos = img_point(pos_W,dim.map); # Current Image point.
  ctr = img_point(ctr_W,dim.map); # Image arc center.

  # Loop on steps:
  while (ang < ang_fin) :
    pos_old = pos; # Save previous position.
    ang_old = ang; # Save previous angle.
    
    # Find {ang > ang_old} such that the step takes us about {dlen} avawy from {pre}
    while (True) :
      ang = ang_old + step;
      pos_W = rn.add(ctr_W, vec_from_ang_rad(u_W,v_W,ang,rad)); # Current World point.
      pos = img_point(pos_W,dim.map); # Current Image point.
      dst = rn.dist(pos_old,pos);
      rel = dst/dlen;
      # sys.stderr.write("ang = %6.2f  dst = %6.2f  dlen = %6.2f  rel = %8.4f\n" % (ang,dst,dlen,rel));
      if ((rel >= 0.9) and (rel <= 1.1)) :
        break;
      elif (rel < 0.5) :
        step *= 2;
      elif (rel > 2.0) :
        step /= 2;
      else :
        step /= rel;

    # Trim the angle to {ang_fin}:
    if (ang > ang_fin) :
      ang = ang_fin;
      pos_W = rn.add(ctr_W, vec_from_ang_rad(u_W,v_W,ang,rad)); # Current World point.
      pos = img_point(pos_W,dim.map); # Current Image point.

    # Process a gap/dash from {pre} to {pos}:
    if (down) :
      # Dash:
      dini[nd:nd] = [pos_old];
      dfin[nd:nd] = [pos];
      nd += 1;
      if (dashed) :
        down = False;
        dlen = 3;
    else :
      # Gap:
      down = True;
      dlen = 4;

  nd = len(dini);

  if (not dashed) :
    # Paint the sectors:
    sys.stdout.write( \
      '    <g stroke="none" fill="rgb(100,0,200)" fill-opacity="0.25">\n' \
    );
    for k in range(nd) :
      sys.stdout.write( \
        '      <path d="M '+ pfm(dini[k]) +' L '+ pfm(dfin[k]) +' L '+ pfm(ctr) +'"/>\n' \
      );
    sys.stdout.write( \
      '    </g>\n' \
    );

  # Draw the arc:
  sys.stdout.write( \
    '    <g stroke="rgb(' + color + ')" fill="none">\n' \
  );
  for k in range(nd) :
    sys.stdout.write( \
      '      <path d="M '+ pfm(dini[k]) +' L '+ pfm(dfin[k]) +'" />\n' \
    );
  sys.stdout.write( \
    '    </g>\n' \
  );

  # Compute the label position and displacement:
  ang_mid = (ang_ini + ang_fin)/2;
  mid_W = rn.add(ctr_W, vec_from_ang_rad(u_W,v_W,ang_mid,rad)); # Arc midpoint.
  mid = img_point(mid_W,dim.map); # Midpoint of arc.
  dmd,emd = rn.dir(rn.sub(mid,ctr)); # Direction from center to midpoint of arc.
  dpx = 5*dmd[0];
  dpy = 5*dmd[1];
  output_label(op,dim,mid,[dpx,dpy],make_italic_style(lab_str));
  #----------------------------------------------------------------------

def output_straight_trace(op,dim,ini_W,fin_W,draw,lab_str) :
  "Draws and/or labels a dashed straight line.\n" \
  "\n" \
  "  The line goes from {ini_W} to {fin_W} and is labeled {lab-str}.  If {draw}" \
  " is FALSE, does not plot it, just writes the label." \
  "\n" \
  "  "

  # Parameters:
  dashed = (lab_str == '');
  if (dashed) :
    style = 'stroke="rgb(0,0,0)" stroke-dasharray="3,4" stroke-dashoffset="9"';
  else :
    style = 'stroke="rgb(' + dim.ct_color + ')"';

  ini = img_point(ini_W,dim.map); # Start point.
  fin = img_point(fin_W,dim.map); # End point.
  if (draw) :
    sys.stdout.write( \
      '    <path d="M '+ pfm(ini) +' L '+ pfm(fin) +'" ' + style + '/>\n' \
    );
  # Compute the label position and displacement:
  mid = rn.scale(0.5,rn.add(ini,fin)); # Midpoint of trace.
  dtr,ntr = rn.dir(rn.sub(ini,fin)); # Direction and length of trace.
  dpx = +5*dtr[1];
  dpy = -5*dtr[0];
  ooo = img_point([00,00,00],dim.map); # Origin.
  if (abs(dpx) > abs(dpy)) :
    if ((mid[0] < ooo[0]) != (dpx < 0))  :
      dpx = -dpx; dpy = -dpy;
  else :
    if ((mid[1] < ooo[1]) != (dpy < 0))  :
      dpx = -dpx; dpy = -dpy;
  output_label(op,dim,mid,[dpx,dpy],make_italic_style(lab_str));
  #----------------------------------------------------------------------

def output_point(op,dim,pos_W,rad_W,x_str,y_str,z_str) :
  "Draws a dot with the given World position and radius, and its coordinate labels."

  # Image point and radius:
  pos = img_point(pos_W,dim.map);       # Image point.
  rad = img_scale(pos_W,dim.map)*rad_W; # Image radius. 
  if (rad > 0) :
    sys.stdout.write( \
      '    <circle '+ xyfm(pos,'c') +' r="'+ dts(rad) +'"' \
             ' stroke="rgb(0,0,0)" fill="rgb(0,0,0)"/>\n' \
    );
  
  # Compute the label position and displacement:
  ooo = img_point([00,00,00],dim.map); # Origin.
  if (pos[0] > ooo[0]) :
    dpx = +20
  else :
    dpx = -20;
  dmd,emd = rn.dir(rn.sub(pos,ooo)); # Direction from center to midpoint of arc.
  dpy = 0;
  lab_fmt = make_roman_style('(') \
    + make_italic_style(x_str) \
    + make_roman_style(',') \
    + make_italic_style(y_str) \
    + make_roman_style(',') \
    + make_italic_style(z_str) \
    + make_roman_style(')');
  output_label(op,dim,pos,[dpx,dpy],lab_fmt);
  #----------------------------------------------------------------------

def output_figure_postamble(op,dim) :
  "Writes the SVG postamble to {stdout}."

  sys.stdout.write( \
      '  </g>\n' \
      '</svg>\n' \
  )

def vec_from_ang_rad(u,v,ang,rad) :
  "Converts polar coords {ang,rad} to Cartesia, given two axis directions {u,v} in {R^3}."
  c = rad*cos(ang);
  s = rad*sin(ang);
  return rn.add(rn.scale(c,u),rn.scale(s,v))
  #----------------------------------------------------------------------

def dts(x) :
  "Converts the decimal number {x} to string."
  return ("%r" % x)
  #----------------------------------------------------------------------

def img_point(p,map):  
  "Computes a two-dimensional Cartesian Image point {p} from a World point."
  if (len(p) == 3) : p = copy.copy(p); p[0:0] = [1];
  assert (len(p) == 4), "invalid point";
  q = rmxn.map_row(p,map);
  return [q[1]/q[0], q[2]/q[0]];
  
def img_scale(p,map):  
  "Computes the World to Image magnificatin factor at the World point {p}."
  if (len(p) == 3) : p = copy.copy(p); p[0:0] = [1];
  assert (len(p) == 4), "invalid point";
  q = rmxn.map_row(p,map);
  s = sqrt(map[1][1]*map[1][1] + map[2][1]*map[2][1] + map[3][1]*map[3][1])
  return s*p[0]/q[0];
  
def make_italic_style(str) :
  "Packages a string with italic style markup."
  if (str != '') :
    return '<tspan font-style="italic">' + str + '</tspan>'
  else :
    return ''

def make_roman_style(str) :
  "Packages a string with normal style (non-italic) markup."
  if (str != '') :
    return '<tspan>' + str + '</tspan>'
  else :
    return ''

def pfm(p) :
  "Formats a two-dimensional Image point {p} as two numbers separated by a comma."
  return "%+06.1f,%+06.1f" % (p[0],p[1]);

def xyfm(p,tag) :
  "Formats a  two-dimensional Image point {p} as '{tag}x=\"{p[0]}\" {tag}y=\"{p[1]}\"'."
  return "%sx=\"%+06.1f\" %sy=\"%+06.1f\"" % (tag,p[0],tag,p[1]);
  
#----------------------------------------------------------------------

# Main program:
op = parse_args(pp);
output_figure(op);
