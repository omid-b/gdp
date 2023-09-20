#!/usr/bin/env python3

import netCDF4 as nc
import numpy as np
import os
import random
import shutil
import subprocess
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    try:
        from . import _geographic as geographic
    except ImportError:
        print("WARNING! Could not use cythonized module: geographic")
        from . import geographic

from .. import programs
from ..ascii_procs import io

def ascii_to_netcdf(args):

    if len(args.fmt) == 1:
        args.fmt.append(args.fmt[0])

    read_input_data = io.read_numerical_data(args.input_file, 0, 0, [".10",".10"], args.x, args.data)
    read_data_points = np.vstack((read_input_data[0][0], read_input_data[0][1])).T.tolist()
    read_data_values = read_input_data[1][0]
    if args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            polygons = io.read_polygon_shp(polygon_file)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
            polygons = [[polygon_data[0][0], polygon_data[0][1]]]

        if not len(polygons):
            print(f"Error: polygon is not specified. Please check polygon file.")
            exit(1)

    data = {}
    x_uniq = []
    y_uniq = []
    for ip, point in enumerate(read_data_points):
        point = np.around(point, decimals=int(args.fmt[0][-1]))
        point = geographic.Point(point[0], point[1])
        if point.lon not in x_uniq:
            x_uniq.append(point.lon)
        if point.lat not in y_uniq:
            y_uniq.append(point.lat)
        key = f"%{args.fmt[0]}f_%{args.fmt[0]}f" %(point.lon, point.lat)
        val = f"%{args.fmt[1]}f" %(read_data_values[ip])
        if args.polygon:
            for iply in range(len(polygons)):
                polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
                if polygon.is_point_in(point):
                    data[f"{key}"] = val
        else:
            data[f"{key}"] = val

    xSpacing = np.unique( np.around(np.diff(sorted(x_uniq)), decimals=int(args.fmt[0][-1])) )
    ySpacing = np.unique( np.around(np.diff(sorted(y_uniq)), decimals=int(args.fmt[0][-1])) )
    if len(xSpacing) > 1 or len(ySpacing) > 1:
        print("Error! Input data should be in uniformly gridded format. Use 'gridder' first!")
        print(f"\n  x_spacing = {xSpacing}")
        print(f"  y_spacing = {ySpacing}\n")
        exit(1)
    else:
        xSpacing = xSpacing[0]
        ySpacing = ySpacing[0]

    minX = np.nanmin(x_uniq)
    maxX = np.nanmax(x_uniq)
    minY = np.nanmin(y_uniq)
    maxY = np.nanmax(y_uniq)

    nc_x = np.arange(minX, maxX+xSpacing, xSpacing)
    nc_y = np.arange(minY, maxY+ySpacing, ySpacing)

    # silly fix of a bug!
    if np.around(nc_x[-1], decimals=int(args.fmt[0][-1])) \
    != np.around(maxX, decimals=int(args.fmt[0][-1]) ):
        nc_x = nc_x[:-1]
    if np.around(nc_y[-1], decimals=int(args.fmt[0][-1])) \
    != np.around(maxY, decimals=int(args.fmt[0][-1]) ):
        nc_y = nc_y[:-1]

    nc_z = np.ndarray((len(nc_x), len(nc_y)), dtype=float)
    for ix, x in enumerate(nc_x):
        for iy, y in enumerate(nc_y):
            key = f"%{args.fmt[0]}f_%{args.fmt[0]}f" %(x, y)
            if key in data.keys():
                nc_z[ix][iy] = data[key]
            else:
                nc_z[ix][iy] = np.nan

    ncfile = nc.Dataset(args.output_file, mode='w', format='NETCDF4_CLASSIC')
    ncfile.createDimension('x', len(nc_x))
    ncfile.createDimension('y', len(nc_y))
    ncfile.createDimension('z', None)

    x = ncfile.createVariable('x', np.float64, ('x',))
    y = ncfile.createVariable('y', np.float64, ('y',))
    z = ncfile.createVariable('z', np.float64, ('x','y',))

    x.actual_range = (minX, maxX)
    x.long_name = 'x'
    y.actual_range = (minY, maxY)
    y.long_name = 'y'
    z.actual_range = (np.nanmin(np.nanmin(nc_z)), np.nanmax(np.nanmax(nc_z)))
    z.long_name = 'z'

    x[:] = nc_x
    y[:] = nc_y
    z[:,:] = nc_z

    ncfile.close()



#################

def netcdf_to_ascii(args):

    try:
        ncfile = args.input_file[0]
        ds = nc.Dataset(ncfile)
    except Exception as e:
        print(f"Error reading '{os.path.split(ncfile)[1]}': {e}")
        exit(1)

    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt
    
    out_lines = []
    if args.metadata:
        for key in ds.__dict__.keys():
            out_lines.append(f"{key}: {ds.__dict__[key]}")
        out_lines.append(f"\nVariables:")
        for key in ds.variables.keys():
            out_lines.append(f"\nData field: '{key}'\n {ds.variables[key]}")
    else:
        all_fields = list(ds.variables.keys())
        selected_fields = args.data
        if not selected_fields:
            print(f"Error! At least one data field name must be given using flag '--data'.\nCheck metadata for more information.")
            exit(1)

        ndf = len(selected_fields) # number of data fields
        data_val = []
        for df in selected_fields:
            if df not in all_fields:
                print(f"Error! Could not find data field: '{df}'")
                exit(1)
            else:
                data_val.append(ds[df][:].data)
                data_val_shape = np.shape(ds[df][:].data)


        data_pos = []
        for key in all_fields:
            if len(np.shape(ds[key][:])) == 1 and\
            np.shape(ds[key][:])[0] in data_val_shape:
                data_pos.append([])
                for x in ds[key][:]:
                    data_pos[-1].append(x)
        
        # match shapes for data_pos and data_val
        for iv in range(ndf):
            ntry = 0
            while True:
                ntry += 1
                pos_shape = []
                for pos in data_pos:
                    pos_shape.append(len(pos))
                if list(np.shape(data_val[iv])) == pos_shape:
                    break
                else:
                    random.shuffle(data_pos)
                if ntry == 100:
                    break
            if ntry == 100:
                print(f"Error! Could not figure out data format for '{os.path.split(ncfile)[1]}'\n")
                exit(1)

        out_lines = gen_nc_dataset_outlines(data_pos, data_val, fmt)
    
        # find and add header line info to beginning of out_lines
        header_line = list()
        for flen in (pos_shape):
            for key in all_fields:
                if (1, flen) == (len(np.shape(ds[key][:])), np.shape(ds[key][:])[0]):
                    header_line.append(key)
        for sf in selected_fields:
            header_line.append(sf)
        header_line = ' '.join(header_line)
        out_lines.insert(0, header_line)

    args.uniq = False
    args.sort = False
    io.output_lines(out_lines, args)
        

#############################################

def gen_nc_dataset_outlines(positional_matrix, values_matrix, fmt = ['.4', '.4']):
    outlines = []
    ndim = len(positional_matrix) # number of dimension
    ndf = len(values_matrix) # number of data fields
    shape = list(np.shape(values_matrix[0])) # dimension shape

    if ndim == 2:
        indices = [(i, j) for i in range(shape[0]) for j in range(shape[1])]
        for index in indices:
            outlines.append(f"%{fmt[0]}f %{fmt[0]}f" \
            %(positional_matrix[0][index[0]], positional_matrix[1][index[1]]))
            for idf in range(ndf):
                outlines[-1] += f" %{fmt[1]}f" %(values_matrix[idf][index[0]][index[1]])
    elif ndim == 3:
        indices = [(i, j, k) for i in range(shape[0]) for j in range(shape[1]) for k in range(shape[2])]
        for index in indices:
            outlines.append(f"%{fmt[0]}f %{fmt[0]}f %{fmt[0]}f" \
            %(positional_matrix[0][index[0]], positional_matrix[1][index[1]], positional_matrix[2][index[2]]))
            for idf in range(ndf):
                outlines[-1] += f" %{fmt[1]}f" %(values_matrix[idf][index[0]][index[1]][index[2]])
    else:
        print(f"Error! This is not a 2D or 3D dataset.\nCurrrent version of the program only works for 2D and 3D datasets.")
        exit(1)

    return outlines

