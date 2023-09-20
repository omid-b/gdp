
# a set of cythonized functions

cimport numpy as _np
from cython.view cimport array


import numpy as np 
from math import dist
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


##############################
# ADAPTIVE GRIDDING FUNCTIONS (JUST FOR TEST AT THIS STAGE!)

def calc_nodes_smoothing(\
    _np.ndarray[_np.float64_t, ndim=1] data_x,
    _np.ndarray[_np.float64_t, ndim=1] data_y,\
    _np.ndarray[_np.float64_t, ndim=1] nodes_x,\
    _np.ndarray[_np.float64_t, ndim=1] nodes_y,\
    double smoothfactor,
    double maxdist):
    cdef int i
    cdef int j
    cdef double xn
    cdef double yn
    cdef double xd
    cdef double yd
    cdef int data_len
    cdef int nodes_len
    cdef _np.ndarray[_np.float64_t, ndim=1] dists
    cdef _np.ndarray[_np.float64_t, ndim=1] nodes_smoothing
    # calculate nodes smoothing (adaptive smoothing)
    data_len = len(data_x)
    nodes_len = len(nodes_x)

    dists = np.zeros(data_len, dtype=np.double)

    nodes_smoothing = np.zeros(nodes_len, dtype=np.double)

    for i, xn in enumerate(nodes_x):
        yn = nodes_y[i]
        for j, xd in enumerate(data_x):
            yd = data_y[j]
            dists[j] = dist([xn, yn], [xd, yd])
        dists = np.sort(dists)
        # use second closest data point distance for smoothing
        nodes_smoothing[i] = dists[1] * smoothfactor
    return nodes_smoothing




