
# this is plan B if could not import _funcs.pyx

import numpy as np 
from math import dist
from math import sin
from math import cos
from math import acos
from math import atan2
from math import degrees
from math import radians
from math import exp
from math import pow


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


def calc_nodes_adaptive_smoothing(data_x, data_y, nodes_x, nodes_y, smoothfactor, maxdist):
    # calculate nodes smoothing (adaptive smoothing)
    nodes_smoothing = []
    for i, xn in enumerate(nodes_x):
        yn = nodes_y[i]
        indices = np.where((data_x >= (xn-maxdist)) &\
                           (data_x <= (xn+maxdist)) &\
                           (data_y >= (yn-maxdist)) &\
                           (data_y <= (yn+maxdist)) )
        data_x_win = data_x[indices]
        data_y_win = data_y[indices]
        # loop through data points and find distance from this node to data points
        dists = []
        for j, xd in enumerate(data_x_win):
            yd = data_y_win[j]
            dists.append(dist([xn, yn], [xd, yd]))
        dists = np.sort(dists)
        # use second closest data point distance for smoothing
        nodes_smoothing.append(dists[1] * smoothfactor) 
    return nodes_smoothing


#-------------------------#
def window_xyz(data_x, data_y, data_z, min_x, max_x, min_y, max_y):
    data_x = np.array(data_x, dtype=float)
    data_y = np.array(data_y, dtype=float)
    data_z = np.array(data_z, dtype=float)
    indices = np.where((data_x >= min_x) &\
                             (data_x <= max_x) &\
                             (data_y >= min_y) &\
                             (data_y <= max_y))
    return [data_x[indices], data_y[indices], data_z[indices]]


#-------------------------#
def gridder_node_weights(x, y, data_x, data_y, smoothing):
    wgt = []
    for i, xd in enumerate(data_x):
        yd = data_y[i]
        temp = exp(-1 * (1 / pow(smoothing, 2)) * (pow(xd - x, 2) + pow(yd - y, 2)))
        if temp < smoothing:
            wgt.append(temp)
        else:
            wgt.append(0)
    return wgt


#-------------------------#
def gridder_node_value(node_weights, data_val):
    ret = np.sum(np.multiply(node_weights, data_val)) / np.sum(node_weights)
    return ret


#-------------------------#
def get_grid_value(x, y, data_x, data_y, data_val, smoothing):
    data_x_win, data_y_win, data_val_win = window_xyz(data_x, data_y, data_val,
                                                      x - 3*smoothing,
                                                      x + 3*smoothing,
                                                      y - 3*smoothing,
                                                      y + 3*smoothing)
    node_weights = gridder_node_weights(x, y, data_x_win, data_y_win, smoothing)
    node_val = gridder_node_value(node_weights, data_val_win)
    return node_val
