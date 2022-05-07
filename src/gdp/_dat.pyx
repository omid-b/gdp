
import numpy as np 
cimport numpy as _np 
from math import sin
from math import cos
from math import acos
from math import atan2
from math import degrees
from math import radians


def calc_wgt( double xg, double yg,  _np.ndarray[_np.float64_t, ndim=1] xnode,\
    _np.ndarray[_np.float64_t, ndim=1] ynode,  double smoothing):
    cdef int nnodes
    cdef double alpha
    cdef _np.ndarray[_np.float64_t, ndim=1] Xg
    cdef _np.ndarray[_np.float64_t, ndim=1] Yg
    cdef _np.ndarray[_np.float64_t, ndim=1] adistsq
    cdef _np.ndarray[_np.float64_t, ndim=1] wgt
    cdef _np.ndarray[_np.float64_t, ndim=1] mask

    nnodes = len(xnode)
    alpha = 1 / (smoothing ** 2)
    Xg = np.ones(nnodes) * xg
    Yg = np.ones(nnodes) * yg
    adistsq = alpha * ( (Xg - xnode)**2 + (Yg - ynode)**2 )
    wgt = np.exp(-adistsq)
    mask = np.ma.masked_less(adistsq, smoothing).mask * np.ones(nnodes)
    wgt = wgt * mask
    return wgt

