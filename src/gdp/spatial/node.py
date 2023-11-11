#!/usr/bin/env python

"""
Node design and manipulation class 

"""

from scipy.spatial import Delaunay
from scipy.spatial import Voronoi


class Nodes:

    def __init__(self, xnodes=None, ynodes=None, dataset=None):
        self.nodes = []
        if dataset:
            self.append(dataset=dataset)
        if xnodes and ynodes:
            self.append(xnodes=xnodes, ynodes=ynodes)


    def append(self, xnodes=None, ynodes=None, dataset=None):
        if dataset:
            if type(dataset) == Dataset:
                numericals = dataset.get_numericals(merge=True)
                xnodes, ynodes = numericals[0], numericals[1]
            else:
                raise TypeError("Input dataset must be a type 'Dataset'")
        if xnodes and ynodes:
            if len(xnodes) != len(ynodes):
                raise ValueError("Error: number of xnodes and ynodes do not match!")
            nnodes = len(xnodes)
            for inod in range(nnodes):
                self.nodes.append((xnodes[inod], ynodes[inod]))


    def design(self, interval, polygon=None):
        if not len(self.nodes):
            return
        else:
            xnodes = np.array(self.nodes).T[0]
            ynodes = np.array(self.nodes).T[1]
        nodes = []
        for x in np.arange(np.nanmin(xnodes), np.nanmax(xnodes) + interval, interval):
            for y in np.arange(np.nanmin(ynodes), np.nanmax(ynodes) + interval, interval):
                nodes.append((x, y))
        self.nodes = nodes

        if polygon:
            self.mask()


    def get_nodes(self):
        return self.nodes





# import os
# import numpy as np
# from ..ascii import io

# def nodes(args):
#     try:
#         from ..geographic import _geographic as geographic
#     except ImportError:
#         print("WARNING! Could not use cythonized module: geographic")
#         from ..geographic import geographic
#     # check arguments
#     if args.xrange[0] >= args.xrange[1]:
#         print(f"Error! Argument 'xrange' should be entered in [min_x, max_x] format.")
#         exit(1)
#     elif args.xstep <= 0.0:
#         print(f"Error! Argument 'xstep' should have a positive value!")
#         exit(1)

#     if args.yrange[0] >= args.yrange[1]:
#         print(f"Error! Argument 'yrange' should be entered in [min_y, max_y] format.")
#         exit(1)
#     elif args.ystep <= 0.0:
#         print(f"Error! Argument 'ystep' should have a positive value!")
#         exit(1)

#     x_vals, y_vals, z_vals, output_lines = [[],[],[],[]]
#     if args.zrange != None: # 3D
#         if args.zrange[0] >= args.zrange[1]:
#             print(f"Error! Argument 'zrange' should be entered in [min_z, max_z] format.")
#             exit(1)
#         elif args.zstep == None:
#             print(f"Error! Argument 'zstep' is required.")
#             exit(1)
#         elif args.zstep <= 0.0:
#             print(f"Error! Argument 'zstep' should have a positive value!")
#             exit(1)

#         # calculate nodes (3D)
#         for z in np.arange(args.zrange[0], args.zrange[1] + args.zstep, args.zstep):
#             for x in np.arange(args.xrange[0], args.xrange[1] + args.xstep, args.xstep):
#                 for y in np.arange(args.yrange[0], args.yrange[1] + args.ystep, args.ystep):
#                     x_vals.append(round(x, 10))
#                     y_vals.append(round(y, 10))
#                     z_vals.append(round(z, 10))

#     else: # 2D
#         # calculate nodes (2D)
#         for x in np.arange(args.xrange[0], args.xrange[1] + args.xstep, args.xstep):
#             for y in np.arange(args.yrange[0], args.yrange[1] + args.ystep, args.ystep):
#                     x_vals.append(round(x, 10))
#                     y_vals.append(round(y, 10))

#     # store calculated node in output_lines
#     if args.polygon:
#         if os.path.splitext(args.polygon)[1] == ".shp":
#             # if args.polygon is *.shp
#             polygons = io.read_polygon_shp(args.polygon)
#         else:
#             # else if args.polygon is not *.shp (ascii file)
#             polygon_data = io.read_numerical_data(args.polygon, 0, 0, [".10",".10"], [1,2], [])
#             polygons = [[polygon_data[0][0], polygon_data[0][1]]]
#     else:
#         include_point = True

#     for i, x in enumerate(x_vals):
#         include_point = True
#         if args.polygon:
#             point = geographic.Point(x, y_vals[i])
#             for iply in range(len(polygons)):
#                 polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
#                 if not polygon.is_point_in(point):
#                     include_point = False

#         if include_point:
#             if args.zrange != None: # 3D
#                 output_lines.append(f"%{args.fmt[0]}f %{args.fmt[1]}f %{args.fmt[2]}f" %(x, y_vals[i], z_vals[i]))
#             else:
#                 output_lines.append(f"%{args.fmt[0]}f %{args.fmt[1]}f" %(x, y_vals[i]))
#     args.sort = False
#     args.uniq = False
#     args.append = False
#     if len(output_lines) == 0:
#         print("Error! Number of calculated nodes is zero!")
#         exit(1)
#     io.output_lines(output_lines, args)