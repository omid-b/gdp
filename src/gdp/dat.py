# numerical data type processing module

import os
from . import io

import numpy as np
from numba import jit


def gridder(args):
    from . import geographic
    from scipy.spatial import distance
    args.nan = False
    args.skipnan = True
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
    # start main process
    # d: data, g: gridded
    for idat, xy in enumerate(data_xy):
        dlon = [row[0] for row in xy]
        dlat = [row[1] for row in xy]
        reflon = (np.min(dlon)+np.max(dlon))/2
        reflat = (np.min(dlat)+np.max(dlat))/2
        
        applat = reflat-90
        if applat < -90:
            applat = applat+180

        applon = reflon-90
        if applon < -180:
            applon = applon+180

        point_ref = geographic.Point(reflon, reflat)
        point_app = geographic.Point(applon, applat)
        line = geographic.Line(point_app, point_ref)
        deltaref = line.calc_gcarc()
        tazimref = line.calc_az()

        earth_radius = geographic.calc_earth_radius((reflat + applat) / 2)
        circ = np.radians(earth_radius)


        # grid lon & lat
        glon = []; glat = []
        for lon in np.arange(np.min(dlon), np.max(dlon)+args.spacing[0], args.spacing[0]):
            for lat in np.arange(np.min(dlat), np.max(dlat)+args.spacing[0], args.spacing[0]):
                glon.append(lon)
                glat.append(lat)

        ngp = len(glon) # number of grid points
        ndp = len(dlon) # number of data points

        # input data relative coordinates: xnode & ynode
        xnode = [];  ynode = []
        for ip in range(len(xy)):
            point = geographic.Point(xy[ip][0], xy[ip][1])
            line = geographic.Line(point_app, point)
            delta = line.calc_gcarc()
            tazim = line.calc_az()
            deltadiff = delta - deltaref
            tazdiff = tazimref - tazim
            if deltadiff > 180:
                deltadiff -= 360
            elif deltadiff < -180:
                deltadiff += 360
            if tazdiff > 180:
                tazdiff -= 360
            elif tazdiff < -180:
                tazdiff += 360
            xnode.append(circ * deltadiff)
            ynode.append(circ * np.sin(np.radians(delta)) * tazdiff)

        # gridded data relative coordinates: xgrid & ygrid
        xgrid = [];  ygrid = []
        for ip in range(ngp):
            point = geographic.Point(glon[ip], glat[ip])
            line = geographic.Line(point_app, point)
            delta = line.calc_gcarc()
            tazim = line.calc_az()
            deltadiff = delta - deltaref
            tazdiff = tazimref - tazim
            if deltadiff > 180:
                deltadiff -= 360
            elif deltadiff < -180:
                deltadiff += 360
            if tazdiff > 180:
                tazdiff -= 360
            elif tazdiff < -180:
                tazdiff += 360
            xgrid.append(circ * deltadiff)
            ygrid.append(circ * np.sin(np.radians(delta)) * tazdiff)

        # gval: [[gval_column_1],[gval_column_2],...]
        gval = [np.zeros(ndp).tolist() for x in range(nvals)]

        for igp in range(ngp):
            # lon = round(glon[igp], 1)
            # lat = round(glat[igp], 1)
            wgt = calc_wgt(xgrid[igp], ygrid[igp], xnode, ynode, args.smoothing)
            wgtsum = np.sum(wgt)
            for iv in range(nvals):
                gval[iv] += np.array(data_val[idat][iv]) * wgt
                gval[iv] = (1/wgtsum) * gval[iv]

        print('1/wgtsum', wgtsum)








def calc_wgt(xg, yg, xnode, ynode, smoothing):
    nnodes = len(xnode)
    alpha = 1 / (smoothing ** 2)
    xg = np.ones(nnodes) * xg
    yg = np.ones(nnodes) * yg
    adistsq = alpha * ( (xg - xnode)**2 + (yg - ynode)**2 )
    wgt = np.exp(-adistsq)
    mask = np.ma.masked_greater(adistsq, smoothing).mask * np.ones(nnodes)
    wgt = wgt * mask
    return wgt
    




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
    from . import geographic
    outfile_orig = args.outfile
    for points_file in args.points_file:
        polygon_file = args.polygon_file[0]
        points_data = io.read_numerical_data(points_file, args.header, args.footer,  [".10",".10"], args.x, [])
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
        nop = len(points_data[0][0]) # number of points
        if nop:
            outdata_lines = []
            for ip in range(nop):
                point = geographic.Point(points_data[0][0][ip], points_data[0][1][ip])
                if polygon.is_point_in(point,args.inverse):
                    outdata_lines.append(f"%f %f %s" %(point.lon, point.lat, points_data[2][ip]))
            args.uniq = False
            args.sort = False
            if len(args.points_file) > 1:
                if args.outfile:
                    if not os.path.isdir(outfile_orig):
                        os.mkdir(outfile_orig)
                    args.outfile = os.path.join(outfile_orig, os.path.split(points_file)[1])
                else:
                    print(f"\nFile: '{os.path.split(points_file)[1]}'")
                io.output_lines(outdata_lines, args)
            else:
                io.output_lines(outdata_lines, args)
        else:
            print(f"Error in reading points_file: {points_file}\nNaN columns will be ignored")
            continue

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
