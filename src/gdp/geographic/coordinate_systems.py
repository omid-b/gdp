
import math
import pyproj
import numpy as np

from . import epsg

from .. import ascii


def csproj_fix(args):
    [known_x, known_y], _, _ = ascii.io.read_numerical_data(args.known, 0, 0,  ".10", args.x, [], skipnan=True)
    [unknown_x, unknown_y], _, _ = ascii.io.read_numerical_data(args.unknown, 0, 0,  ".10", args.x, [], skipnan=True)
    if (len(known_x) != len(unknown_x) or len(known_y) != len(unknown_y)):
        print("Error: number of known and unknown points must match.")
        exit(1)
    else:
        nop = len(known_x) # number of points
    # check the known cs
    if args.cs not in list(epsg.EPSG_Proj4.keys()) and \
    epsg.get_utm(args.cs) == None and epsg.get_epsg(args.cs) == None:
            print(f"Error: could not find epsg code for the known data: '{args.cs}'")
            exit(1)
    # populate unknown cs (trylist) from args.trylist or targs.tryall
    if args.tryall:
        trylist = list(epsg.EPSG_Proj4.keys())
    else:
        fopen = open(args.trylist, 'r')
        trylist = fopen.read().splitlines()
        fopen.close()
        for cs in trylist:
            if cs not in list(epsg.EPSG_Proj4.keys()) and \
            epsg.get_utm(cs) == None and epsg.get_epsg(cs) == None:
                print(f"Error: could not find the try list epsg code for '{cs}'")
                exit(1)
    # start main process
    mean_dist_mismatch = {}
    for cs in trylist:
        # mean_dist_mismatch[f"{cs}"] = 0
        dist = []
        for i in range(nop):
            xnew, ynew = transform_point_coordinates(unknown_x[i], unknown_y[i], cs, args.cs, accept_same_cs=True)
            d = math.sqrt((xnew - known_x[i])**2 + (ynew - known_y[i])**2)
            dist.append(d)
        mean_dist_mismatch[f"{cs}"] = round(np.mean(dist), 2)

    mean_dist_mismatch = {k: v for k, v in sorted(mean_dist_mismatch.items(), key=lambda item: item[1])}
    for i,x in enumerate(mean_dist_mismatch.keys()):
        if i < args.n:
            print(args.cs, x, mean_dist_mismatch[f"{x}"])

    exit(0)


def csproj_ascii(args):
    pos, _, extra = ascii.io.read_numerical_data(args.input_file, args.header, args.footer,  ".10", args.x, [], skipnan=True)
    nop = len(pos[0]) # number of points
    output_lines = []
    for ip in range(nop):
        x, y = [pos[0][ip], pos[1][ip]]
        xnew, ynew = transform_point_coordinates(x, y, args.cs[0], args.cs[1])
        if args.skiporig:
            output_lines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f %s" %(xnew, ynew, extra[ip]))
        else:
            output_lines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[1]}f %{args.fmt[1]}f %s" %(xnew, ynew, x, y, extra[ip]))
    args.sort = False
    args.uniq = False
    if len(output_lines) == 0:
        print("Error! Number of calculated nodes is zero!")
        exit(1)
    ascii.io.output_lines(output_lines, args)


def transform_point_coordinates(x, y, cs_from, cs_to, accept_same_cs=False):
    try:
        from osgeo import ogr
        from osgeo import osr
    except Exception as e:
        print(f"{e}. Hint: install and test GDAL.")
        print("install GDAL: $ pip install GDAL")
        print("   test GDAL: $ python3 -c 'from osgeo import ogr, osr'")
        exit(1)
    epsg_from = return_epsg_code(cs_from)
    epsg_to = return_epsg_code(cs_to)
    if epsg_from == epsg_to and accept_same_cs==False:
        print('Error! The input-output coordinate systems are the same!')
        exit(1)

    if epsg.get_epsg_proj(epsg_from) == None and epsg_from != 4326:
        print(f'Error! The Proj4 transformation codes not available for: "{cs_from}"')
        exit(1)
    elif epsg.get_epsg_proj(epsg_to) == None and epsg_to != 4326:
        print(f'Error! The Proj4 transformation codes not available for: "{cs_to}"')
        exit(1)
    # calculate the transformed coordinates
    if epsg_from == 4326:
        proj = pyproj.Proj(epsg.get_epsg_proj(epsg_to))
        xnew, ynew = proj(x, y, inverse=False)
    elif epsg_to == 4326:
        proj = pyproj.Proj(epsg.get_epsg_proj(epsg_from))
        xnew, ynew = proj(x, y, inverse=True)
    else:
        # first transform to wgs84
        proj = pyproj.Proj(epsg.get_epsg_proj(epsg_from))
        xtemp, ytemp = proj(x, y, inverse=True)
        # now transform to final coordinate system
        proj = pyproj.Proj(epsg.get_epsg_proj(epsg_to))
        xnew, ynew = proj(xtemp, ytemp, inverse=False)

    return [xnew, ynew]



def return_epsg_code(cs_code):
    # return integer EPSG code or give an error and exit program
    # initialize variables
    epsg_code, utm_zone = [None, None]
    try:
        epsg_code = int(cs_code)
    except:
        utm_zone = cs_code
    # find epsg_code
    if epsg_code != None:
        if epsg.get_epsg_info(str(epsg_code)) == None:
            print(f"Error! Could not find entry for EPSG: {epsg_code}")
            exit(1)
    elif utm_zone.lower() == 'wgs84':
        epsg_code = 4326
    else:
        epsg_code = epsg.get_epsg(utm_zone.upper())
        if epsg_code == None:
            print(f"Error! Could not figure out the EPSG code for: '{cs_code}'")
            exit(1)
    return epsg_code
