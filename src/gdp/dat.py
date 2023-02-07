# numerical data type processing module

import os
import warnings
import shutil
import numpy as np
from math import radians, degrees, sin, cos, atan2, acos
from . import io

#####################################################################


def csproj_ascii(args):
    pos, _, extra = io.read_numerical_data(args.input_file, args.header, args.footer,  ".10", args.x, [], skipnan=True)
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
    io.output_lines(output_lines, args)


def transform_point_coordinates(x, y, cs_from, cs_to):
    from . import epsg
    import pyproj
    try:
        from osgeo import ogr, osr
    except Exception as e:
        print(f"{e}. Hint: install and test GDAL.")
        print("install GDAL: $ pip install GDAL")
        print("   test GDAL: $ python3 -c 'from osgeo import ogr, osr'")
        exit(1)
    epsg_from = return_epsg_code(cs_from)
    epsg_to = return_epsg_code(cs_to)
    if epsg_from == epsg_to:
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
    from . import epsg
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



def add_intersect_values(args):
    args.nan = False
    args.noextra = True
    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    datlines_vals = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
            datlines_vals[i].append(' '.join(line.split()[len(args.x):]))
    intersect = []
    intersect_pos = []
    intersect_add_vals = []
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines_pos[0][j] in l for l in datlines_pos[1:])\
        and datlines_pos[i][j] not in intersect_pos:
            added_vals = [0 for ivc in range(len(args.v))]
            for ivc in range(len(args.v)):
                for idc in range(nof):
                    added_vals[ivc] += float(datlines_vals[idc][j].split()[ivc])
                added_vals[ivc] = f"%{fmt[1]}f" %(added_vals[ivc])
            intersect_pos.append(datlines_pos[0][j])
            intersect_add_vals.append(' '.join(added_vals))
            intersect.append(f"{intersect_pos[-1]} {intersect_add_vals[-1]}")

    args.uniq = False # it's already uniq!
    if len(intersect) == 0:
        print("Error! Number of calculated nodes is zero!")
        exit(1)
    io.output_lines(intersect, args)


def nodes(args):
    try:
        from . import _geographic as geographic
    except ImportError:
        print("WARNING! Could not use cythonized module: geographic")
        from . import geographic
    # check arguments
    if args.xrange[0] >= args.xrange[1]:
        print(f"Error! Argument 'xrange' should be entered in [min_x, max_x] format.")
        exit(1)
    elif args.xstep <= 0.0:
        print(f"Error! Argument 'xstep' should have a positive value!")
        exit(1)

    if args.yrange[0] >= args.yrange[1]:
        print(f"Error! Argument 'yrange' should be entered in [min_y, max_y] format.")
        exit(1)
    elif args.ystep <= 0.0:
        print(f"Error! Argument 'ystep' should have a positive value!")
        exit(1)

    x_vals, y_vals, z_vals, output_lines = [[],[],[],[]]
    if args.zrange != None: # 3D
        if args.zrange[0] >= args.zrange[1]:
            print(f"Error! Argument 'zrange' should be entered in [min_z, max_z] format.")
            exit(1)
        elif args.zstep == None:
            print(f"Error! Argument 'zstep' is required.")
            exit(1)
        elif args.zstep <= 0.0:
            print(f"Error! Argument 'zstep' should have a positive value!")
            exit(1)

        # calculate nodes (3D)
        for z in np.arange(args.zrange[0], args.zrange[1] + args.zstep, args.zstep):
            for x in np.arange(args.xrange[0], args.xrange[1] + args.xstep, args.xstep):
                for y in np.arange(args.yrange[0], args.yrange[1] + args.ystep, args.ystep):
                    x_vals.append(round(x, 10))
                    y_vals.append(round(y, 10))
                    z_vals.append(round(z, 10))

    else: # 2D
        # calculate nodes (2D)
        for x in np.arange(args.xrange[0], args.xrange[1] + args.xstep, args.xstep):
            for y in np.arange(args.yrange[0], args.yrange[1] + args.ystep, args.ystep):
                    x_vals.append(round(x, 10))
                    y_vals.append(round(y, 10))

    # store calculated node in output_lines
    if args.polygon:
        if os.path.splitext(args.polygon)[1] == ".shp":
            # if args.polygon is *.shp
            polygons = io.read_polygon_shp(args.polygon)
        else:
            # else if args.polygon is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(args.polygon, 0, 0, [".10",".10"], [1,2], [])
            polygons = [[polygon_data[0][0], polygon_data[0][1]]]
    else:
        include_point = True

    for i, x in enumerate(x_vals):
        include_point = True
        if args.polygon:
            point = geographic.Point(x, y_vals[i])
            for iply in range(len(polygons)):
                polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
                if not polygon.is_point_in(point):
                    include_point = False

        if include_point:
            if args.zrange != None: # 3D
                output_lines.append(f"%{args.fmt[0]}f %{args.fmt[1]}f %{args.fmt[2]}f" %(x, y_vals[i], z_vals[i]))
            else:
                output_lines.append(f"%{args.fmt[0]}f %{args.fmt[1]}f" %(x, y_vals[i]))
    args.sort = False
    args.uniq = False
    args.append = False
    if len(output_lines) == 0:
        print("Error! Number of calculated nodes is zero!")
        exit(1)
    io.output_lines(output_lines, args)




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


    if not args.nodes:
        if len(args.spacing) == 1:
            args.spacing = [args.spacing[0], args.spacing[0]]
        if args.spacing[0] <= 0 or args.spacing[1] <= 0:
            print(f"Error! 'spacing' should be positive.")
            exit(1)
    else:
        nodes_xy, _, _ = io.read_numerical_data(args.nodes, 0, 0, [".10",".10"], [1,2], [], skipnan=True)
        nodes_x = nodes_xy[0]
        nodes_y = nodes_xy[1]

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
            polygons = io.read_polygon_shp(polygon_file)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], [1,2], [])
            polygons = [[polygon_data[0][0], polygon_data[0][1]]]

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

        ndp = len(dataX) # number of data points

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
        if args.nodes:
            ngp = len(nodes_x) # number of grid points
            for ix, x in enumerate(nodes_x):
                y = nodes_y[ix]
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
        else:
            xinc = args.spacing[0]
            yinc = args.spacing[1]
            nx = int(((maxX-minX)/xinc)+1)
            ny = int(((maxY-minY)/yinc)+1)
            ngp = nx * ny # number of grid points
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
                        for iply in range(len(polygons)):
                            polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
                            if polygon.is_point_in(point):
                                out_lines.append(line)
                    else:
                        out_lines.append(line)
            else:
                if args.polygon:
                    for iply in range(len(polygons)):
                        polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
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

        if len(out_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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

    if  args.nodes:
        nodes_xy, _, _ = io.read_numerical_data(args.nodes, 0, 0, [".10",".10"], [1,2], [], skipnan=True)
        nodes_x = nodes_xy[0]
        nodes_y = nodes_xy[1]
    else:
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

        

        ndp = len(dataX) # number of data points

        # input data relative coordinates: xnode & ynode
        xnode = [];  ynode = []
        for ip in range(ndp):
            xnode.append(dataX[ip] - refX)
            ynode.append(dataY[ip] - refY)

        # grid coordinates
        gridx = []; gridy = []
        rxgrid = [];  rygrid = []
        if args.nodes:
            ngp = len(nodes_x)
            for ix, x in enumerate(nodes_x):
                y = nodes_y[ix]
                gridx.append(x)
                gridy.append(y)
                rxgrid.append(x - refX)
                rygrid.append(y - refY)
        else:
            xinc = args.spacing[0]
            yinc = args.spacing[1]
            nx = int(((maxX-minX)/xinc)+1)
            ny = int(((maxY-minY)/yinc)+1)
            ngp = nx * ny # number of grid points
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

        if len(out_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
        if len(union_inv) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(union_inv, args)
    else:
        if len(union) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
        if len(intersect_inv) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(intersect_inv, args)
    else:
        if len(intersect) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
        if len(difference_inv) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(difference_inv, args)
    else:
        if len(difference) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
        line = f"%{args.fmt[0]}f %{args.fmt[0]}f" %(ip[0], ip[1])
        if line not in outlines:
            outlines.append(line)
    outlines.append(outlines[0])
    args.append = False
    if len(outlines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
            polygons = io.read_polygon_shp(polygon_file)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
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
            points_data = io.read_numerical_data(points_file, args.header, args.footer,  [".10",".10"], args.x, [])
            nop = len(points_data[0][0]) # number of points
        if nop:
            outdata_lines = []
            for ip in range(nop):
                point = geographic.Point(points_data[0][0][ip], points_data[0][1][ip])
                for iply in range(len(polygons)):
                    polygon = geographic.Polygon(polygons[iply][0], polygons[iply][1])
                    if polygon.is_point_in(point, args.inverse):
                        outdata_lines.append(f"%f %f %s" %(point.lon, point.lat, points_data[2][ip]))
            if len(args.point) > 1:
                if args.outfile:
                    if not os.path.isdir(outfile_orig):
                        os.mkdir(outfile_orig)
                    args.outfile = os.path.join(outfile_orig, os.path.split(points_file)[1])
            elif outfile_orig:
                args.outfile = os.path.join(outfile_orig)

            args.uniq = True
            args.sort = True

            if len(outdata_lines):
                if not outfile_orig and len(args.point) > 1:
                    print(f"\nFile: '{os.path.split(points_file)[1]}'")
                io.output_lines(outdata_lines, args)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
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
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    io.output_lines(outdata_lines, args)


#####################################################################

def anomaly_2D(args):
    # read models
    absmodel_x, [absmodel_v], _ = io.read_numerical_data(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
    [refmodel_x], [refmodel_v], _ = io.read_numerical_data(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
    nop = len(absmodel_v)
    if nop == 0:
        print(f"Error! Number of points read from the absmodel is zero! Check absmodel: '{args.absmodel}'")
        exit(1)
    # check if reference model covers the abs model positional data range
    if args.depth < min(refmodel_x) or args.depth > max(refmodel_x):
        print(f"Error: reference model does not cover the absolute model depth={args.depth}\n")
        exit(1)
    # linear interpolation and find rederence model value at the given depth
    refmodel_depth_interp = np.array([args.depth], dtype=float)
    refmodel_value_interp = np.interp(refmodel_depth_interp, refmodel_x, refmodel_v)
    # calculate anomaly model
    if args.outfile == None:
        output_lines = ["X/Lon  Y/Lat  Anomaly_value"]
    else:
        output_lines = []
    for i in range(nop):
        xy = f"%{args.fmt[0]}f %{args.fmt[0]}f" %(absmodel_x[0][i], absmodel_x[1][i])
        if args.type == 'difference':
            anom_val = f"%{args.fmt[1]}f" %(absmodel_v[i] - refmodel_value_interp[0])
        elif args.type == 'percentage':
            anom_val = f"%{args.fmt[1]}f" %((absmodel_v[i] - refmodel_value_interp[0]) * 100 / refmodel_value_interp[0])
        output_lines.append(f"{xy} {anom_val}")
    # output lines to std or file
    args.append = False
    args.sort = False
    args.uniq = False
    io.output_lines(output_lines, args)

    # print reference model value into stdout
    if args.outfile == None:
        print(f"\nCalculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}\n")
    else:
        print(f"Calculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}")

def anomaly_1D(args):
    import matplotlib.pyplot as plt
    outfile_orig = args.outfile
    # read models
    [absmodel_x], [absmodel_v], _ = io.read_numerical_data(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
    [refmodel_x], [refmodel_v], _ = io.read_numerical_data(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
    # check if reference model covers the abs model positional data range
    if min(absmodel_x) < min(refmodel_x) or max(absmodel_x) > max(refmodel_x):
        print("Error: reference model does not fully cover the absolute model positional range:\n")
        print(f"  absmodel range (positional column): {min(absmodel_x)} to {max(absmodel_x)}")
        print(f"  refmodel range (positional column): {min(refmodel_x)} to {max(refmodel_x)}\n")
        exit(1)
    # linear interpolation and convert python lists to numpy arrays for easier processing
    refmodel_x_interp = np.array(absmodel_x, dtype=float)
    refmodel_v_interp = np.interp(refmodel_x_interp, refmodel_x, refmodel_v)
    absmodel_x = np.array(absmodel_x, dtype=float)
    absmodel_v = np.array(absmodel_v, dtype=float)
    refmodel_x = np.array(refmodel_x, dtype=float)
    refmodel_v = np.array(refmodel_v, dtype=float)

    anomaly_model_x = absmodel_x
    anomaly_model_v = absmodel_v - refmodel_v_interp # args.type == 'difference'
    if args.type == 'percentage':
        anomaly_model_v = (anomaly_model_v / refmodel_v_interp) * 100

    # Calculate markers
    markers = {}
    if args.markers_depths == None:
        args.markers_depths = [min(absmodel_x), max(absmodel_x)]
    elif args.markers_depths[0] > args.markers_depths[1]:
        args.markers_depths = args.markers_depths[::-1]

    for mv in args.markers: # mv: marker value
        markers[f"{mv}"] = []
        for idep, dep in enumerate(anomaly_model_x[1:len(anomaly_model_x)+1], start=1):
            if dep < args.markers_depths[0] or dep > args.markers_depths[1]:
                continue
            
            if args.markers_case == 'both':
                if (anomaly_model_v[idep] <= mv and anomaly_model_v[idep-1] >= mv) \
                or (anomaly_model_v[idep] >= mv and anomaly_model_v[idep-1] <= mv):
                    markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)
            else:
                if args.markers_case == 'increase' \
                and anomaly_model_v[idep] >= mv and anomaly_model_v[idep-1] <= mv:
                    markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)
                elif args.markers_case == 'decrease' \
                and anomaly_model_v[idep] <= mv and anomaly_model_v[idep-1] >= mv:
                    markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)

    # Generate Plot
    fig = plt.figure(figsize=(6,7))

    # subplot 1: absolute model and reference model profiles
    ax1 = fig.add_subplot(121)
    if args.invert_yaxis == 'True':
        ax1.invert_yaxis()
    ax1.plot(refmodel_v, refmodel_x, color='#D2691E', label="ref model")
    ax1.scatter(refmodel_v, refmodel_x, c='#D2691E', s=5)
    ax1.plot(absmodel_v, absmodel_x, color='#4169E1', label="abs model")
    ax1.scatter(absmodel_v, absmodel_x, c='#4169E1', s=5)
    ax1.legend(loc=f"{args.legend_loc}")
    ax1.set_xlabel(' '.join(args.vlabel))
    ax1.set_ylabel(' '.join(args.depthlabel))

    # subplot 2: anomaly model profile and markers
    ax2 = fig.add_subplot(122)
    if args.invert_yaxis == 'True':
        ax2.invert_yaxis()
    if args.type == 'percentage':
        anomaly_vlabel = f"{args.vlabel[0]} anomaly (%)"
    else:
        anomaly_vlabel = f"{args.vlabel[0]} anomaly (abs diff)"
    ax2.plot(anomaly_model_v, anomaly_model_x, color='#4169E1')
    ax2.scatter(anomaly_model_v, anomaly_model_x, c='#4169E1', s=5)
    ax2.set_xlabel(anomaly_vlabel)
    ax2.plot([0,0], ax1.get_ylim(), color='#555', linewidth=0.5, linestyle='--')
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_yticks([])

    # subplot 2: add markers
    any_marker_found = False
    for mv in markers.keys(): # marker value
        for md in  markers[f"{mv}"]: # marker depth
            any_marker_found = True
            if args.type == 'percentage':
                marker_label = f"{mv}%"
            else:
                marker_label = f"{mv} (abs diff)"
            ax2.plot([min(anomaly_model_v), max(anomaly_model_v)], 2*[md], linestyle='--', label=marker_label)

    if any_marker_found:
        ax2.legend(loc=f"{args.legend_loc}")

    plt.suptitle(f"{os.path.split(args.absmodel)[1]}")
    plt.tight_layout()

    # output to stdout/screen or to files

    args.append = False
    args.sort = False
    args.uniq = False
    if any_marker_found:
        outlines_markers = ["value depth"]
        for mv in markers.keys(): # marker value
            for md in  markers[f"{mv}"]: # marker depth
                outlines_markers.append(f"{mv} {md}")
        if outfile_orig == None:
            args.outfile = None
            outlines_markers.insert(0,f"Markers found for '{os.path.split(args.absmodel)[1]}'")
            outlines_markers.append("")
        else:
            args.outfile = f"{os.path.splitext(outfile_orig)[0]}_markers{os.path.splitext(outfile_orig)[1]}"
        if len(outlines_markers) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(outlines_markers, args)

    outline_anomaly = [f"depth abs_model ref_model anomaly_model"]
    for idep, dep in enumerate(anomaly_model_x):
        outline_anomaly.append(\
        f"%{args.fmt[0]}f %{args.fmt[1]}f %{args.fmt[1]}f %{args.fmt[1]}f" %(dep, absmodel_v[idep], refmodel_v_interp[idep], anomaly_model_v[idep]))
    if outfile_orig == None: # output anomaly data and plot to stdout and screen
        # anomaly data
        args.outfile = None
        outline_anomaly.insert(0,f"Anomaly data for '{os.path.split(args.absmodel)[1]}'")
        if len(outline_anomaly) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(outline_anomaly, args)
        # plot
        plt.show()
    else: # output anomaly data and plot to files
        # anomaly data
        args.outfile = outfile_orig
        if len(outline_anomaly) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        io.output_lines(outline_anomaly, args)
        # plot
        outplot = os.path.abspath(f"{os.path.splitext(outfile_orig)[0]}.{args.ext}")
        plt.savefig(outplot, dpi=args.dpi, format=args.ext)
    plt.close()



