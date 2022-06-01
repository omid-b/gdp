
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
