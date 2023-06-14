
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


# Bezier smoothing from:
# https://towardsdatascience.com/b%C3%A9zier-interpolation-8033e9a262c2

def get_bezier_coef(points):
    # since the formulas work given that we have n+1 points
    # then n must be this:
    n = len(points) - 1

    # build coefficents matrix
    C = 4 * np.identity(n)
    np.fill_diagonal(C[1:], 1)
    np.fill_diagonal(C[:, 1:], 1)
    C[0, 0] = 2
    C[n - 1, n - 1] = 7
    C[n - 1, n - 2] = 2

    # build points vector
    P = [2 * (2 * points[i] + points[i + 1]) for i in range(n)]
    P[0] = points[0] + 2 * points[1]
    P[n - 1] = 8 * points[n - 1] + points[n]

    # solve system, find a & b
    A = np.linalg.solve(C, P)
    B = [0] * n
    for i in range(n - 1):
        B[i] = 2 * points[i + 1] - A[i + 1]
    B[n - 1] = (A[n - 1] + points[n]) / 2

    return A, B

# returns the general Bezier cubic formula given 4 control points
def get_cubic(a, b, c, d):
    return lambda t: np.power(1 - t, 3) * a + 3 * np.power(1 - t, 2) * t * b + 3 * (1 - t) * np.power(t, 2) * c + np.power(t, 3) * d

# return one cubic curve for each consecutive points
def get_bezier_cubic(points):
    A, B = get_bezier_coef(points)
    return [
        get_cubic(points[i], A[i], B[i], points[i + 1])
        for i in range(len(points) - 1)
    ]

# evalute each cubic curve on the range [0, 1] sliced in n points
def evaluate_bezier(points, n):
    curves = get_bezier_cubic(points)
    return np.array([fun(t) for fun in curves for t in np.linspace(0, 1, n)])

#---------------#

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
