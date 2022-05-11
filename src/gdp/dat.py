# numerical data type processing module

import os
import warnings
import shutil
import numpy as np
from math import radians, degrees, sin, cos, atan2, acos

from . import io

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    try:
        from . import _funcs as funcs
        from . import _geographic as geographic
    except ImportError:
        from . import funcs
        from . import geographic


def gridder(args):
    outfile_orig = args.outfile
    skipnan_orig = args.skipnan
    args.nan = False
    args.skipnan = True
    args.noextra = True
    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    data_xy = [[] for i in range(nof)]
    data_val = [[] for i in range(nof)]
    nvals = len(args.v)
    for i in range(nof):
        data_val[i] = [[] for iv in range(nvals)]
    # preprocessing: read data and omit NaNs
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i], args)
        for line in datlines[i]:
            xy = line.split()[0:len(args.x)]
            vals = line.split()[len(args.x):len(args.x)+len(args.v)]
            if 'nan' not in xy and 'nan' not in vals:
                xy = np.array(xy, dtype=float).tolist()
                data_xy[i].append(xy)
                vals = np.array(vals, dtype=float).tolist()
                for iv in range(nvals):
                    data_val[i][iv].append(vals[iv])

    # point in polygon? If so, read polygon data & instantiate polygon object
    if args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            import geopandas as gpd
            from shapely.geometry import mapping
            try:
                shp = gpd.read_file(polygon_file)
                polygon_lon = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_lat = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], [1,2], [])
            polygon_lon = polygon_data[0][0]
            polygon_lat = polygon_data[0][1]
        polygon = geographic.Polygon(polygon_lon, polygon_lat)

    # start main process
    # d: data, g: gridded
    for idat, xy in enumerate(data_xy):
        dlon = [row[0] for row in xy]
        dlat = [row[1] for row in xy]
        if len(dlon) == 0:
            print(f"\nError! No data for input value column; File: '{os.path.split(input_files[idat])[1]}'\n" +
                  f"value column number(s): {' '.join(np.array(args.v, dtype=str))}\n")
            continue

        if not outfile_orig and nof > 1:
            print(f"\nFile: '{os.path.split(input_files[idat])[1]}'")

        reflon = (np.nanmin(dlon)+np.nanmax(dlon))/2
        reflat = (np.nanmin(dlat)+np.nanmax(dlat))/2
        
        applat = reflat-90
        if applat < -90:
            applat = applat+180

        applon = reflon-90
        if applon < -180:
            applon = applon+180

        point_app = geographic.Point(applon, applat)
        point_ref = geographic.Point(reflon, reflat)
        line_ref = geographic.Line(point_app, point_ref)

        deltaref = line_ref.calc_gcarc()
        tazimref = line_ref.calc_az()

        earth_radius = geographic.calc_earth_radius(reflat)
        circ = radians(earth_radius)

        if args.lonrange[1] == 0.999: # Auto
            minLon = min(dlon)
            maxLon = max(dlon)
        else:
            minLon = args.lonrange[0]
            maxLon = args.lonrange[1]

        if args.latrange[1] == 0.999: # Auto
            minLat = min(dlat)
            maxLat = max(dlat)
        else:
            minLat = args.latrange[0]
            maxLat = args.latrange[1]

        loninc = args.spacing[0]
        latinc = args.spacing[1]

        nx = int(((maxLon-minLon)/loninc)+1)
        ny = int(((maxLat-minLat)/latinc)+1)

        ndp = len(dlon) # number of data points
        ngp = nx * ny # number of grid points

        # input data relative coordinates: xnode & ynode
        xnode = [];  ynode = []
        for ip in range(ndp):
            point = geographic.Point(dlon[ip], dlat[ip])
            line = geographic.Line(point_app, point)

            delta = line.calc_gcarc()
            tazim = line.calc_az()

            deltadiff = delta - deltaref
            if deltadiff > 180:
                deltadiff -= 360
            elif deltadiff < -180:
                deltadiff += 360
            xnode.append(circ * deltadiff)
            
            tazdiff = tazimref - tazim
            if tazdiff > 180:
                tazdiff -= 360
            elif tazdiff < -180:
                tazdiff += 360
            ynode.append(circ * sin(radians(delta)) * tazdiff)

        # grid coordinates
        gridlon = []; gridlat = []
        xgrid = [];  ygrid = []
        for ix in range(nx):
            lon = minLon + ix*loninc
            for iy in range(ny):
                lat = minLat + iy*latinc

                point = geographic.Point(lon, lat)
                line = geographic.Line(point_app, point)

                delta = line.calc_gcarc()
                tazim = line.calc_az()

                deltadiff = delta - deltaref
                if deltadiff > 180:
                    deltadiff -= 360
                elif deltadiff < -180:
                    deltadiff += 360
                
                tazdiff =tazimref-tazim
                if tazdiff > 180:
                    tazdiff -= 360
                elif tazdiff < -180:
                    tazdiff += 360
                
                gridlon.append(lon)
                gridlat.append(lat)
                xgrid.append(circ * deltadiff)
                ygrid.append(circ * sin(radians(delta)) * tazdiff)

        # gridding 
        out_lines = []
        gval = [np.zeros(ngp).tolist() for x in range(nvals)]
        for igp in range(ngp):
            line = f"%{fmt[0]}f %{fmt[0]}f" %(gridlon[igp], gridlat[igp])
            xnode = np.array(xnode)
            ynode = np.array(ynode)
            wgt = funcs.calc_wgt(xgrid[igp], ygrid[igp], xnode, ynode, args.smoothing)
            wgtsum = np.sum(wgt)

            for iv in range(nvals):

                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    gval[iv][igp] += np.sum(wgt * np.array(data_val[idat][iv])) / wgtsum

                line = f"{line} %{fmt[1]}f" %(gval[iv][igp])

            point = geographic.Point(float(line.split()[0]), float(line.split()[1]))

            if skipnan_orig:
                if 'nan' not in line.split():
                    if args.polygon:
                        if polygon.is_point_in(point):
                            out_lines.append(line)
                    else:
                        out_lines.append(line)
            else:
                if args.polygon:
                    if polygon.is_point_in(point):
                        out_lines.append(line)
                else:
                    out_lines.append(line)

        # output results
        args.append = False
        args.sort = True
        args.uniq = False

        if nof > 1 and outfile_orig:
            if not os.path.isdir(outfile_orig):
                os.mkdir(outfile_orig)
            args.outfile = os.path.join(outfile_orig, os.path.split(input_files[idat])[1])
        else:
            args.outfile = outfile_orig

        io.output_lines(out_lines, args)



def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    union = []
    union_pos = []
    for i in range(nof):
        nol = len(datlines_pos[i])
        for j in range(nol):
            if datlines_pos[i][j] not in union_pos:
                union.append(datlines[i][j])
                union_pos.append(datlines_pos[i][j])
    if args.inverse:
        union_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in union:
                    union_inv.append(datlines[i][j])
        io.output_lines(union_inv, args)
    else:
        io.output_lines(union, args)


def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    intersect = []
    intersect_pos = []
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines_pos[0][j] in l for l in datlines_pos[1:])\
        and datlines_pos[i][j] not in intersect_pos:
            intersect.append(datlines[0][j])
            intersect_pos.append(datlines_pos[0][j])
    if args.inverse:
        intersect_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                line = datlines[i][j]
                if line not in intersect:
                    intersect_inv.append(line)
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)


def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    difference = []
    difference_pos = []
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines_pos[0][j] not in l for l in datlines_pos[1:])\
        and datlines_pos[0][j] not in difference_pos:
            difference.append(datlines[0][j])
            difference_pos.append(datlines_pos[0][j])
    if args.inverse:
        difference_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                line = datlines[i][j]
                if line not in difference:
                    difference_inv.append(line)
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)


def points_in_polygon(args):
    outfile_orig = args.outfile

    # build polygon class
    polygon_lon = []
    polygon_lat = []
    if args.lonrange != [-0.999, 0.999] and args.latrange != [-0.999, 0.999]:
        if args.lonrange[0] >= args.lonrange[1]:
            print(f"Error! Argument 'lonrange' should be entered in [minlon, maxlon] format.")
            exit(1)
        elif args.latrange[0] >= args.latrange[1]:
            print(f"Error! Argument 'latrange' should be entered in [minlat, maxlat] format.")
            exit(1)
        elif args.lonrange[0] < -180:
            print(f"Error! minimum longitude is less than -180.")
            exit(1)
        elif args.lonrange[1] > 180:
            print(f"Error! maximum longitude is greater than 180.")
            exit(1)
        elif args.latrange[0] < -90:
            print(f"Error! minimum latitude is less than -90.")
            exit(1)
        elif args.latrange[1] > 90:
            print(f"Error! maximum latitude is greater than 90.")
            exit(1)
        polygon_lon = [args.lonrange[0], args.lonrange[1], args.lonrange[1], args.lonrange[0], args.lonrange[0]]
        polygon_lat = [args.latrange[0], args.latrange[0], args.latrange[1], args.latrange[1], args.latrange[0]]
    elif args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            import geopandas as gpd
            from shapely.geometry import mapping
            try:
                shp = gpd.read_file(polygon_file)
                polygon_lon = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_lat = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
            polygon_lon = polygon_data[0][0]
            polygon_lat = polygon_data[0][1]
    
    if len(polygon_lon): 
        polygon = geographic.Polygon(polygon_lon, polygon_lat)
    else:
        print(f"Error: polygon is not specified. Please use either '--lonrange & --latrange' or '--polygon'.")
        exit(1)

    # main process
    for points_file in args.points_file:
        points_data = io.read_numerical_data(points_file, args.header, args.footer,  [".10",".10"], args.x, [])
        nop = len(points_data[0][0]) # number of points
        if nop:
            outdata_lines = []
            for ip in range(nop):
                point = geographic.Point(points_data[0][0][ip], points_data[0][1][ip])
                if polygon.is_point_in(point,args.inverse):
                    outdata_lines.append(f"%f %f %s" %(point.lon, point.lat, points_data[2][ip]))
            if len(args.points_file) > 1:
                if args.outfile:
                    if not os.path.isdir(outfile_orig):
                        os.mkdir(outfile_orig)
                    args.outfile = os.path.join(outfile_orig, os.path.split(points_file)[1])
            elif outfile_orig:
                args.outfile = os.path.join(outfile_orig)

            args.uniq = False
            args.sort = False
            if len(outdata_lines):
                if not outfile_orig and len(args.points_file) > 1:
                    print(f"\nFile: '{os.path.split(points_file)[1]}'")
                io.output_lines(outdata_lines, args)
            elif not outfile_orig:
                print(f"Warning! Zero output lines for data: '{os.path.split(points_file)[1]}'")
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


def calc_min(args):
    from numpy import nanmin
    outdata_lines = []
    for inpfile in args.input_files:
        min_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            min_column.append(f"%.{args.decimal[0]}f" %(nanmin(col)))
        outdata_lines.append(' '.join([inpfile] + min_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)


def calc_max(args):
    from numpy import nanmax
    outdata_lines = []
    for inpfile in args.input_files:
        max_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            max_column.append(f"%.{args.decimal[0]}f" %(nanmax(col)))
        outdata_lines.append(' '.join([inpfile] + max_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)


def calc_sum(args):
    from numpy import nansum
    outdata_lines = []
    for inpfile in args.input_files:
        sum_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            sum_column.append(f"%.{args.decimal[0]}f" %(nansum(col)))
        outdata_lines.append(' '.join([inpfile] + sum_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)


def calc_mean(args):
    from numpy import nanmean
    outdata_lines = []
    for inpfile in args.input_files:
        mean_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            mean_column.append(f"%.{args.decimal[0]}f" %(float(nanmean(col))))
        outdata_lines.append(' '.join([inpfile] + mean_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)


def calc_median(args):
    from numpy import nanmedian
    outdata_lines = []
    for inpfile in args.input_files:
        median_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            median_column.append(f"%.{args.decimal[0]}f" %(float(nanmedian(col))))
        outdata_lines.append(' '.join([inpfile] + median_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)


def calc_std(args):
    from numpy import nanstd
    outdata_lines = []
    for inpfile in args.input_files:
        std_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            std_column.append(f"%.{args.decimal[0]}f" %(nanstd(col)))
        outdata_lines.append(' '.join([inpfile] + std_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)
