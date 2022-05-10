
# this is plan B if could not import _funcs.pyx

import numpy as np 
from math import sin
from math import cos
from math import acos
from math import atan2
from math import degrees
from math import radians


def calc_wgt(xg, yg, xnode, ynode, smoothing):
    nnodes = len(xnode)
    alpha = 1 / (smoothing ** 2)
    Xg = np.ones(nnodes) * xg
    Yg = np.ones(nnodes) * yg
    adistsq = alpha * ( (Xg - xnode)**2 + (Yg - ynode)**2 )
    wgt = np.exp(-adistsq)
    mask = np.ma.masked_less(adistsq, smoothing).mask * np.ones(nnodes)
    wgt = wgt * mask
    return wgt

