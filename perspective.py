#! /usr/bin/python -t
# _*_ coding: iso-8859-1 _*_
# Last edited on 2009-05-02 20:09:04 by stolfi

MODULE_NAME = "perspective"
MODULE_DESC = "Computes a perspective projection matrix from camera data"
MODULE_VERS = "1.0"

MODULE_COPYRIGHT = "Copyright © 2009 State University of Campinas"

MODULE_INFO = \
  "A library module to compute a homogeneous perspective matrix.\n" \
  "\n" \
  "  Bla bla.\n"

import sys
import copy
import rn
import rmxn
import hrn

def camera_matrix(att,obs,upd,mag,ctr) :
  "Computes a perspective projection matrix from given camera parameters.\n" \
  "\n" \
  "\n" \
  "  The camera parameters are either points (P), vectors (V), or scalars.  Points" \
  " and vectors are either in World (W) or Image (I) coordinates.\n" \
  "\n" \
  "    {att} = center of attention (PW).\n" \
  "    {obs} = position of observer (PW).\n" \
  "    {upd} = approximate 'up' direction (VW).\n" \
  "    {mag} = post-projection magnification factors (VI).\n" \
  "    {ctr} = coordinates of image center (PI).\n" \
  "\n" \
  "  Point arguments can be given as 3 Cartesian coordinates or equivalent 4" \
  " homogeneous coordinates.  The latter have the weight at coordinate" \
  " number 0.  For Image points, the Cartesian Z coordinate being interpreted" \
  " as a height relative to the image plane. \n" \
  "\n" \
  "  The result is a {4×4} projective matrix that maps World points" \
  " to Image points, both as 4-vectors in homogeneous coordinates.\n" \
  "\n" \
  "  The camera is placed at {obs}, which may be finite and hither or" \
  " at infinity.  It is pointed towards the point {att}, which must be" \
  " finite, hither, and distinct from {obs}.  The {obs}--{att} line will be" \
  " the camera's optical axis.  The projection plane is perpendicular to that" \
  " line and passes through {att}.  The camera is then rotated around the optical" \
  " axis so that its vertical axis points as far as close as possible to" \
  " the {upd} vector; which must not be parallel to the camera axis.\n" \
  "\n" \
  "  The intermediate projection coordinate system has origin {att}, and X and Y axes" \
  " pointing to the camera's right and top.  Points on the projection plane (or" \
  " infinitesimally close to it) are fixed by the perspective projection.  After" \
  " the perspective projection, the point coordinates are scaled by the" \
  " magnification factors in {mag} and then translated by {ctr} to obtain" \
  " the Image coordinates.  Thus the orld {att} point gets mapped to Image {ctr}; moving" \
  " in World from {att} in the World {upd} direction moves on the Image" \
  " from {ctr} without changing the Image X coordinate.\n" \
  "\n" \
  "  Note that the image X axis points to the camera's right, the Y axis points" \
  " to camera's up, and the image Z axis points out of the image towards the" \
  " viewer.  To reverse either or both these axes, use negative {mag} weights."

  # Convert {att,obs} to homogeneous coordinates if necessary:
  if (len(att) == 3) : att = copy.copy(att); att[0:0] = [ 1 ]
  assert len(att) == 4, "{att} must be a point of R^3 or H^3";

  if (len(obs) == 3) : obs = copy.copy(obs); obs[0:0] = [ 1 ]
  assert len(obs) == 4, "{obs} must be a point of R^3 or H^3";

  # Create a matrix {mt} that translates {att} to the origin:
  assert att[0] > 0.0, "{att} must be finite and hither";
  Mt = hrn.trans_matrix(hrn.pt_scale(att, [-1,-1,-1]));

  # Make {obs} relative to {att}:
  obs = rmxn.map_row(obs, Mt);

  # Build the perspective projection matrix {mp} with attention point at {(0,0,0)}:
  Mp = proj_matrix(obs,upd);

  # Build the projection-to-image matrix {mi}:
  Mi = image_matrix(mag,ctr);

  # Now combine them all:
  return rmxn.mul(Mt,rmxn.mul(Mp,Mi));
  # ----------------------------------------------------------------------

def proj_matrix(obs,upd) :
  "Computes a perspective projection matrix given camera parameters.\n" \
  "\n" \
  "  The camera parameters have the same meaning as in {camera_matrix}, except" \
  " that the {obs} point must be a 4-vector of homogeneous coordinates.\n" \
  "\n" \
  "  The result is a {4×4} homogeneous matrix as in {camera_matrix}. It computes" \
  " the homogeneous projected coordinates without any extra scaling and" \
  " translation, assuming that the center of attention is the origin {[1 0 0 0]}.  Thus" \
  " the origin stays fixed.  Moving the point from the origin in the {upd} direction" \
  " moves the projection along the vertical image axis. Distances on the projection" \
  " plane (or infnitesimally close to it) are preserved. Note that the" \
  " projection's Y axis points as close as possible to the" \
  " {upd} vector, and the projection's Z axis points out" \
  " of the projection plane towards {obs}."

  # Get the homogeneous coordinates of the observation point
  assert len(obs) == 4, "{obs} must be a point of H^3";
  assert obs[0] >= 0.0, "{obs} must be hither or infinite";
  assert len(upd) == 3, "{upd} must be a vector of R^3";

  # Vector {t} points from proj. center towards {obs}:
  t, et = rn.dir([obs[1], obs[2], obs[3]]);
  assert et > 0, "bad {obs}";
             
  # The projection's horizontal direction {r} is perpendicular to {t} and {u}:
  r, er = rn.dir(rn.cross2(upd, t));
  assert et > 0, "bad {upd}, parallel to the camera axis";

  # The projection's vertical direction {r} is perpendicular to {t} and {r}:
  s, es = rn.dir(rn.cross2(t, r));
  assert et > 0, "program bug ({cross2(t,r) == 0})";
  
  # Build the rotation matrix that turns {r,s,t} into X,Y,Z:
  R = rmxn.ident_matrix(4,4);
  for i in range(3) :
    R[i+1][1] = r[i];
    R[i+1][2] = s[i];
    R[i+1][3] = t[i];

  wo = obs[0];
  if (wo != 0) :
    # Observer is finite; add conical projection step.
    d = rn.norm([obs[1]/wo, obs[2]/wo, obs[3]/wo]);
    # Try to avoid large numbers in perspective matrix:
    if (abs(d) > 1.0) :
      a = -1.0/d; b = 1.0;
    else :
      a = -1.0; b = d
    # Build perpective matrix {P}:
    P = rmxn.zero_matrix(4,4);
    for i in range(4) :
      P[i][i] = b;
    P[3][0] = a;
    R = rmxn.mul(R, P);
  return R;
  # ----------------------------------------------------------------------

def image_matrix(mag,ctr) :
  "Computes an affine map from projection coords to image coords.\n" \
  "\n" \
  "  The camera parameters {mag,ctr} have the same meaning as in {camera_matrix}.\n" \
  "\n" \
  "  The result is a {4×4} homogeneous matrix as in {camera_matrix}. It takes" \
  " the homogeneous projected coordinates and applies to them a scaling by {mag} followed by a" \
  " displacement by {ctr}."
  
  if (len(mag) == 3) : mag = copy.copy(mag); mag[0:0] = [ 1 ]
  assert len(mag) == 4, "{mag} must be a point of R^3 or H^3";

  if (len(ctr) == 3) : ctr = copy.copy(ctr); ctr[0:0] = [ 1 ]
  assert len(ctr) == 4, "{ctr} must be a point of R^3 or H^3";

  Ms = hrn.scale_matrix(mag);
  Mt = hrn.trans_matrix(ctr);
  return rmxn.mul(Ms,Mt);

# ----------------------------------------------------------------------

