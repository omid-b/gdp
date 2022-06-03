# numerical data type processing module

import os
import warnings
import shutil
import numpy as np
from math import radians, degrees, sin, cos, atan2, acos
from . import io

#####################################################################

def gridder(args):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from . import _funcs as funcs
        except ImportError:
            print("WARNING! Could not use cythonized module: funcs")
            from . import funcs
        try:
            from . import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from . import geographic
    outfile_orig = args.outfile
    skipnan_orig = args.skipnan
    args.nan = False
    args.skipnan = True
    args.noextra = True
    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt

    if len(args.spacing) == 1:
        args.spacing = [args.spacing[0], args.spacing[0]]

    if args.spacing[0] <= 0 or args.spacing[1] <= 0:
        print(f"Error! 'spacing' should be positive.")
        exit(1)

    if args.smoothing <= 0:
        print(f"Error! 'smoothing' should be positive.")
        exit(1)

    if args.xrange[0] >= args.xrange[1]:
        print(f"Error! Argument 'xrange' should be entered in [min_x, max_x] format.")
        exit(1)

    if args.yrange[0] >= args.yrange[1]:
        print(f"Error! Argument 'yrange' should be entered in [min_y, max_y] format.")
        exit(1)

    if args.xrange[0] < -180:
        print(f"Error! minimum longitude is less than -180.")
        exit(1)

    if args.xrange[1] > 180:
        print(f"Error! maximum longitude is greater than 180.")
        exit(1)

    if args.yrange[0] < -90:
        print(f"Error! minimum latitude is less than -90.")
        exit(1)

    if args.yrange[1] > 90:
        print(f"Error! maximum latitude is greater than 90.")
        exit(1)

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
                polygon_x = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_y = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], [1,2], [])
            polygon_x = polygon_data[0][0]
            polygon_y = polygon_data[0][1]
        polygon = geographic.Polygon(polygon_x, polygon_y)

    # start main process
    # d: data, g: gridded
    for idat, xy in enumerate(data_xy):
        dataX = [row[0] for row in xy]
        dataY = [row[1] for row in xy]
        if len(dataX) == 0:
            print(f"\nError! No data for input value column; File: '{os.path.split(input_files[idat])[1]}'\n" +
                  f"value column number(s): {' '.join(np.array(args.v, dtype=str))}\n")
            continue

        if not outfile_orig and nof > 1:
            print(f"\nFile: '{os.path.split(input_files[idat])[1]}'")

        reflon = (np.nanmin(dataX)+np.nanmax(dataX))/2
        reflat = (np.nanmin(dataY)+np.nanmax(dataY))/2
        
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

        if args.xrange[1] == 0.999: # Auto
            minX = np.nanmin(dataX)
            maxX = np.nanmax(dataX)
        else:
            minX = args.xrange[0]
            maxX = args.xrange[1]

        if args.yrange[1] == 0.999: # Auto
            minY = np.nanmin(dataY)
            maxY = np.nanmax(dataY)
        else:
            minY = args.yrange[0]
            maxY = args.yrange[1]

        xinc = args.spacing[0]
        yinc = args.spacing[1]

        nx = int(((maxX-minX)/xinc)+1)
        ny = int(((maxY-minY)/yinc)+1)

        ndp = len(dataX) # number of data points
        ngp = nx * ny # number of grid points

        # input data relative coordinates: xnode & ynode
        xnode = [];  ynode = []
        for ip in range(ndp):
            point = geographic.Point(dataX[ip], dataY[ip])
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
        gridx = []; gridy = []
        rxgrid = [];  rygrid = []
        for ix in range(nx):
            x = minX + ix*xinc
            for iy in range(ny):
                y = minY + iy*yinc

                point = geographic.Point(x, y)
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
                
                gridx.append(x)
                gridy.append(y)
                rxgrid.append(circ * deltadiff)
                rygrid.append(circ * sin(radians(delta)) * tazdiff)

        # gridding 
        out_lines = []
        gval = [np.zeros(ngp).tolist() for x in range(nvals)]
        for igp in range(ngp):
            line = f"%{fmt[0]}f %{fmt[0]}f" %(gridx[igp], gridy[igp])
            xnode = np.array(xnode)
            ynode = np.array(ynode)
            wgt = funcs.calc_wgt(rxgrid[igp], rygrid[igp], xnode, ynode, args.smoothing)
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

#####################################################################

def gridder_utm(args):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from . import _funcs as funcs
        except ImportError:
            print("WARNING! Could not use cythonized module: funcs")
            from . import funcs
        try:
            from . import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from . import geographic

    outfile_orig = args.outfile
    skipnan_orig = args.skipnan
    args.nan = False
    args.skipnan = True
    args.noextra = True
    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt

    if len(args.spacing) == 1:
        args.spacing = [args.spacing[0], args.spacing[0]]

    if args.spacing[0] <= 0 or args.spacing[1] <= 0:
        print(f"Error! 'spacing' should be positive.")
        exit(1)

    if args.smoothing <= 0:
        print(f"Error! 'smoothing' should be positive.")
        exit(1)

    if args.xrange[0] >= args.xrange[1]:
        print(f"Error! Argument 'xrange' should be entered in [min_x, max_x] format.")
        exit(1)

    if args.yrange[0] >= args.yrange[1]:
        print(f"Error! Argument 'yrange' should be entered in [min_y, max_y] format.")
        exit(1)

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
                polygon_x = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_y = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], [1,2], [])
            polygon_x = polygon_data[0][0]
            polygon_y = polygon_data[0][1]
        polygon = geographic.Polygon(polygon_x, polygon_y)

    # start main process
    # d: data, g: gridded
    for idat, xy in enumerate(data_xy):
        dataX = [row[0] for row in xy]
        dataY = [row[1] for row in xy]
        if len(dataX) == 0:
            print(f"\nError! No data for input value column; File: '{os.path.split(input_files[idat])[1]}'\n" +
                  f"value column number(s): {' '.join(np.array(args.v, dtype=str))}\n")
            continue

        if not outfile_orig and nof > 1:
            print(f"\nFile: '{os.path.split(input_files[idat])[1]}'")

        refX = (np.nanmin(dataX)+np.nanmax(dataX))/2
        refY = (np.nanmin(dataY)+np.nanmax(dataY))/2

        if args.xrange[1] == 0.999: # Auto
            minX = np.nanmin(dataX)
            maxX = np.nanmax(dataX)
        else:
            minX = args.xrange[0]
            maxX = args.xrange[1]

        if args.yrange[1] == 0.999: # Auto
            minY = np.nanmin(dataY)
            maxY = np.nanmax(dataY)
        else:
            minY = args.yrange[0]
            maxY = args.yrange[1]

        xinc = args.spacing[0]
        yinc = args.spacing[1]

        nx = int(((maxX-minX)/xinc)+1)
        ny = int(((maxY-minY)/yinc)+1)

        ndp = len(dataX) # number of data points
        ngp = nx * ny # number of grid points

        # input data relative coordinates: xnode & ynode
        xnode = [];  ynode = []
        for ip in range(ndp):
            xnode.append(dataX[ip] - refX)
            ynode.append(dataY[ip] - refY)

        # grid coordinates
        gridx = []; gridy = []
        rxgrid = [];  rygrid = []
        for ix in range(nx):
            x = minX + ix*xinc
            for iy in range(ny):
                y = minY + iy*yinc
                gridx.append(x)
                gridy.append(y)
                rxgrid.append(x - refX)
                rygrid.append(y - refY)

        # gridding 
        out_lines = []
        gval = [np.zeros(ngp).tolist() for x in range(nvals)]
        for igp in range(ngp):
            line = f"%{fmt[0]}f %{fmt[0]}f" %(gridx[igp], gridy[igp])
            xnode = np.array(xnode)
            ynode = np.array(ynode)
            wgt = funcs.calc_wgt(rxgrid[igp], rygrid[igp], xnode, ynode, args.smoothing)
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

#####################################################################

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

#####################################################################

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

#####################################################################

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

#####################################################################

def convex_hull(args):
    from scipy.spatial import ConvexHull
    args.sort = False
    args.uniq = False
    args.offset = 0 # CHANGE LATER!

    data = io.read_numerical_data(args.points_file, args.header, args.footer, [".10",".10"], args.x, [])
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
        import pyclipper
        try:
            pco = pyclipper.PyclipperOffset()
            test = ((180, 200), (260, 200), (260, 150), (180, 150))
            pco.AddPath(chull_points, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
            pco_solution = pco.Execute(args.offset)
            chull_points = pco_solution[0]
        except Exception as e:
            print("WARNING! Could not apply offset to convex hull!")

    if args.smooth > 2:
        from . import funcs
        chull_points = funcs.evaluate_bezier(np.array(chull_points_orig, dtype=float), args.smooth)

    if args.smooth in [1, 2]:
        print("WARNING! Smooth is not performed.\nNumber of Bezier points must be larger than 2!")

    outlines = []
    for ip in chull_points:
        line = f"%{args.fmt}f %{args.fmt}f" %(ip[0], ip[1])
        if line not in outlines:
            outlines.append(line)
    outlines.append(outlines[0])
    io.output_lines(outlines, args)


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
    polygon_x = []
    polygon_y = []
    if args.xrange != [-0.999, 0.999] and args.yrange != [-0.999, 0.999]:
        if args.xrange[0] >= args.xrange[1]:
            print(f"Error! Argument 'xrange' should be entered in [minX/minLon, maxX/maxLon] format.")
            exit(1)
        elif args.yrange[0] >= args.yrange[1]:
            print(f"Error! Argument 'yrange' should be entered in [minY/minLat, maxY/maxLat] format.")
            exit(1)

        polygon_x = [args.xrange[0], args.xrange[1], args.xrange[1], args.xrange[0], args.xrange[0]]
        polygon_y = [args.yrange[0], args.yrange[0], args.yrange[1], args.yrange[1], args.yrange[0]]
    elif args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            import geopandas as gpd
            from shapely.geometry import mapping
            try:
                shp = gpd.read_file(polygon_file)
                polygon_x = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_y = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
            polygon_x = polygon_data[0][0]
            polygon_y = polygon_data[0][1]
    
    if len(polygon_x): 
        polygon = geographic.Polygon(polygon_x, polygon_y)
    else:
        print(f"Error: polygon is not specified. Please use either '--xrange & --yrange' or '--polygon'.")
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


#####################################################################


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


#####################################################################


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


#####################################################################


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

#####################################################################

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

#####################################################################


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

#####################################################################

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
