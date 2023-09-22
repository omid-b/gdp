
from scipy.spatial import ConvexHull
import pyclipper
import matplotlib.pyplot as plt
from alphashape import alphashape
import numpy as np
import warnings
import os

from .. import io

#----------------------#
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

def convex_hull_polygon(args):
    args.sort = False
    args.uniq = False
    args.offset = 0 # CHANGE LATER! XXX

    data = ascii.io.read_numerical_data(args.points_file, args.header, args.footer, [".10",".10"], args.x, [])
    data_points = np.vstack((data[0][0], data[0][1])).T

    chull = ConvexHull(data_points)
    chull_points = np.vstack((data_points[chull.vertices,0], data_points[chull.vertices,1])).T.tolist()
    chull_points.append(chull_points[0])
    # reformat chull_points for offset >> to be developed in later versions
    chull_points_orig = chull_points
    chull_points = ()
    for p in chull_points_orig:
        chull_points += ((p[0], p[1]),)

    if args.offset != 0:
        try:
            pco = pyclipper.PyclipperOffset()
            test = ((180, 200), (260, 200), (260, 150), (180, 150))
            pco.AddPath(chull_points, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
            pco_solution = pco.Execute(args.offset)
            chull_points = pco_solution[0]
        except Exception as e:
            print("WARNING! Could not apply offset to convex hull!")

    if args.smooth > 2:
        chull_points = evaluate_bezier(np.array(chull_points_orig, dtype=float), args.smooth)

    if args.smooth in [1, 2]:
        print("WARNING! Smooth is not performed.\nNumber of Bezier points must be larger than 2!")

    outlines = []
    for ip in chull_points:
        line = f"%{args.fmt[0]}f %{args.fmt[0]}f" %(ip[0], ip[1])
        if line not in outlines:
            outlines.append(line)
    outlines.append(outlines[0])
    args.append = False
    if len(outlines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    ascii.io.output_lines(outlines, args)

#####################################################################

def alpha_shape_polygon(args):
    args.sort = False
    args.uniq = False
    args.offset = 0 # CHANGE LATER! XXX

    data = ascii.io.read_numerical_data(args.points_file, args.header, args.footer, [".10",".10"], args.x, [])
    points = np.vstack((data[0][0], data[0][1])).T

    hull = alphashape(points, args.alpha)
    if hull.is_empty:
        print("Error: empty concave polygon; decrease alpha value")
        exit(1)
    
    hull_x, hull_y = hull.exterior.xy

    outlines = []
    for i, x in enumerate(hull_x):
        y = hull_y[i]
        line = f"%{args.fmt[0]}f %{args.fmt[0]}f" %(x, y)
        if line not in outlines:
            outlines.append(line)
    outlines.append(outlines[0])
    args.append = False
    if len(outlines) == 0:
            print("Error: Number of outputs is zero!")
            exit(1)
    ascii.io.output_lines(outlines, args)


#####################################################################


def points_in_polygon(args):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from . import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from . import geographic

    outfile_orig = args.outfile

    # build polygon class
    polygons = []
    if args.xrange != [-0.999, 0.999] and args.yrange != [-0.999, 0.999]:
        if args.xrange[0] >= args.xrange[1]:
            print(f"Error! Argument 'xrange' should be entered in [minX/minLon, maxX/maxLon] format.")
            exit(1)
        elif args.yrange[0] >= args.yrange[1]:
            print(f"Error! Argument 'yrange' should be entered in [minY/minLat, maxY/maxLat] format.")
            exit(1)

        polygon_x = [args.xrange[0], args.xrange[1], args.xrange[1], args.xrange[0], args.xrange[0]]
        polygon_y = [args.yrange[0], args.yrange[0], args.yrange[1], args.yrange[1], args.yrange[0]]
        polygons = [[polygon_x, polygon_y]]
    elif args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            polygons = ascii.io.read_polygon_shp(polygon_file)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = ascii.io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
            polygon_x = polygon_data[0][0]
            polygon_y = polygon_data[0][1]
            polygons = [[polygon_x, polygon_y]]
    
    if not len(polygons):
        print(f"Error: polygon is not specified. Please use either '--xrange & --yrange' or '--polygon'.")
        exit(1)

    # main process
    if len(polygons) > 1 and args.inverse:
        print("Error! 'inverse' cannot be enabled if two or more polygons are given!")
        exit(1)

    for points_file in args.points:
        if os.path.splitext(points_file)[1] == ".shp":
            print("In this version of gdp and this tool, shape files are not accepted for points. Use ascii instead!")
            exit()
        else:
            points_data = ascii.io.read_numerical_data(points_file, args.header, args.footer,  [".10",".10"], args.x, [])
            nop = len(points_data[0][0]) # number of points
        if nop:
            outdata_lines = []
            for ip in range(nop):
                point = geographic.Point(points_data[0][0][ip], points_data[0][1][ip])
                for iply in range(len(polygons)):
                    polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
                    if polygon.is_point_in(point, args.inverse):
                        outdata_lines.append(f"%f %f %s" %(point.lon, point.lat, points_data[2][ip]))
            if len(args.points) > 1:
                if args.outfile:
                    if not os.path.isdir(outfile_orig):
                        os.mkdir(outfile_orig)
                    args.outfile = os.path.join(outfile_orig, os.path.split(points_file)[1])
            elif outfile_orig:
                args.outfile = os.path.join(outfile_orig)

            args.uniq = True
            args.sort = True

            if len(outdata_lines):
                if not outfile_orig and len(args.points) > 1:
                    print(f"\nFile: '{os.path.split(points_file)[1]}'")
                ascii.io.output_lines(outdata_lines, args)
            elif not outfile_orig:
                print(f"Warning! No output lines for data: '{os.path.split(points_file)[1]}'")
        else:
            print(f"Error in reading points_file: {points_file}\nNote that 'nan' columns will be ignored")
            continue

    if outfile_orig and os.path.isdir(outfile_orig):
        if len(os.listdir(outfile_orig)) == 0:
            if args.inverse:
                print("Warning! No points outside polygon.")
            else:
                print("Warning! No points in polygon.")
            shutil.rmtree(outfile_orig)
    elif outfile_orig and not os.path.isfile(outfile_orig):
        if args.inverse:
            print("Warning! No points outside polygon.")
        else:
            print("Warning! No points in polygon.")
