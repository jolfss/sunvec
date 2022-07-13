from math import cos, pi, sin

from pxr import Gf

def rad(x: float):
    return(x*pi/180)

def deg(x: float):
    return(x*180/pi)

def scale_vec(vec, n):
    x, y, z = vec
    return Gf.Vec3d(x * n, y * n, z * n)

def sunvector_spherical(theta, phi): 
    return Gf.Vec3d(-deg(phi),0,-deg(theta))

def sunvector_cartesian(theta, phi):
    return Gf.Vec3d(sin(theta)*sin(phi),cos(theta)*sin(phi),cos(phi))

def sunvector_xyz(theta, phi):
    return sin(theta)*sin(phi), cos(theta)*sin(phi), cos(phi)
