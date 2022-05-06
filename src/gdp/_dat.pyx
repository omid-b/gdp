
import numpy as np 
cimport numpy as cnp 

# def calc_wgt( double xg, double yg, list xnode, list ynode,  double smoothing):
def calc_wgt( double xg, double yg,  cnp.ndarray[cnp.float64_t, ndim=1] xnode, cnp.ndarray[cnp.float64_t, ndim=1] ynode,  double smoothing):
	# cdef int nnodes
	# cpdef double alpha
	# cdef double [:] Xg
	# cdef double [:] Yg
	# cpdef list adistsq
	# cpdef list wgt
	# cpdef list mask

	# assert xnode.dtype == DTYPE

    nnodes = len(xnode)
    alpha = 1 / (smoothing ** 2)
    Xg = np.ones(nnodes) * xg
    Yg = np.ones(nnodes) * yg
    adistsq = alpha * ( (Xg - xnode)**2 + (Yg - ynode)**2 )
    wgt = np.exp(-adistsq)
    mask = np.ma.masked_less(adistsq, smoothing).mask * np.ones(nnodes)
    wgt = wgt * mask
    return wgt


