from math import cos, pi, sin
from time import altzone
from jolly.sunvec.sunpos import sunpos
from jolly.sunvec.util import rad, deg
import omni.ui as ui
import omni.kit.commands
import omni.usd

def write(field: ui.AbstractValueModel, value):
    field.model.set_value(value)

def read_int(field: ui.AbstractValueModel):
    return(field.model.as_int)

def read_float(field: ui.AbstractValueModel):
    return(field.model.as_float)