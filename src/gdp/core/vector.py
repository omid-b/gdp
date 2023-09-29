#!/usr/bin/env python3

import numpy as np
import geopandas as gpd
from shapely.geometry import mapping

try:
    from .._extensions import _geographic as geographic
except:
    from .._extensions import geographic

def return_polygon_objects(polygon_files):

    polygons = []
    for pf in polygon_files:
        if not os.path.isfile(pf):
            print(f"Error! Could not file polygon file: '{pf}'")
            exit(0)
        ext = os.path.splitext(pf)[1]
        if ext == '.shp':
            ply_shp_xy = read_polygon_shp(pf)
            for ply_xy in ply_shp_xy:
                polygons.append(geographic.Polygon(ply_xy[0], ply_xy[1]))
        else:
            ply_ascii_xy = read_polygon_ascii(pf)
            for iply in range(len(ply_ascii_xy)):
                polygons.append(geographic.Polygon(ply_ascii_xy[iply][0], ply_ascii_xy[iply][1]))
    return polygons


def read_polygon_ascii(polygon_file):
    fopen = open(polygon_file, 'r')
    flines = fopen.read().splitlines()
    fopen.close()
    is_geosoft_format = False
    geosoft_poly_index = []
    for iline, line in enumerate(flines):
        line = line.strip()
        flines[iline] = line
        if line.split()[0].lower() == 'poly':
            is_geosoft_format = True
            geosoft_poly_index.append(iline)
    polygons = []
    if is_geosoft_format:
        for ipoly, poly in enumerate(geosoft_poly_index):
            polygons.append([])
            start_index = poly + 1
            if (ipoly+1) == len(geosoft_poly_index):
                poly_data_lines = flines[start_index:]
            else:
                poly_data_lines = flines[start_index:geosoft_poly_index[ipoly+1]]
            poly_data_lines.append(poly_data_lines[0])
            poly_x = []
            poly_y = []
            for line in poly_data_lines:
                poly_x.append(float(line.split()[0]))
                poly_y.append(float(line.split()[1]))
            polygons[ipoly].append(poly_x)
            polygons[ipoly].append(poly_y)
    else:
        poly_x = []
        poly_y = []
        for line in flines:
            poly_x.append(float(line.split()[0]))
            poly_y.append(float(line.split()[1]))
        polygons = [[poly_x, poly_y]]
    return polygons




def read_polygon_shp(polygon_file):

    polygons = []
    try:
        shp = gpd.read_file(polygon_file)
        nply = len(mapping(shp)['features'])
    except Exception as e:
        print(f"Error! Could not read shape file: '{polygon_file}'\n{e}\n")
        exit(1)
    for i in range(nply):
        polygons.append([])
        try:
            polygon_x = np.array(mapping(shp)['features'][i]['geometry']['coordinates'][0]).flatten()[0::2].tolist()
            polygon_y = np.array(mapping(shp)['features'][i]['geometry']['coordinates'][0]).flatten()[1::2].tolist()
            if len(polygon_x) != len(polygon_y):
                print(f"Error! Cannot read polygon file: '{polygon_file}'")
                exit(1)
        except Exception as e:
            print(f"Error! Could not read shape file item '{i+1}': '{polygon_file}'\n{e}\n")
            exit(1)
        polygons[i] = [polygon_x, polygon_y]    
    return polygons



def read_point_shp(point_file):

    points = [[],[]]
    try:
        shp = gpd.read_file(point_file)
        npts = len(mapping(shp)['features'])
    except Exception as e:
        print(f"Error! Could not read shape file: '{point_file}'\n{e}\n")
        exit(1)
    for i in range(npts):
        try:
            point_x = np.array(mapping(shp)['features'][i]['geometry']['coordinates'][0]).tolist()
            point_y = np.array(mapping(shp)['features'][i]['geometry']['coordinates'][1]).tolist()
        except Exception as e:
            print(f"Error! Could not read shape file item '{i+1}': '{point_file}'\n{e}\n")
            exit(1)
        points[0].append(point_x)
        points[1].append(point_y)

    return points
