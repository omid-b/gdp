
import math
import warnings
import numpy as np
import os

from ..ascii import io

def gridder(args):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from ..extensions import _funcs as funcs
        except ImportError:
            print("WARNING! Could not use cythonized module: funcs")
            from ..extensions import funcs
            
        try:
            from ..extensions import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from ..extensions import geographic

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
        circ = math.radians(earth_radius)

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
            ynode.append(circ * math.sin(math.radians(delta)) * tazdiff)

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
                rygrid.append(circ * math.sin(math.radians(delta)) * tazdiff)
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
                    rygrid.append(circ * math.sin(math.radians(delta)) * tazdiff)

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
        