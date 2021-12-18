
import os
from . import io

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
    points_file = args.points_file[0]
    polygon_file = args.polygon_file[0]
    points_data = io.read_numerical_data(points_file, args.header, args.footer,  [".10",".10"], args.x, [])
    if os.path.splitext(polygon_file)[1] == ".shp":
        # if polygon_file is *.shp
        import numpy as np
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
        io.output_lines(outdata_lines, args)
    else:
        print(f"Error in reading points_file: {points_file}\nNaN columns will be ignored")
        exit(1)


def calc_sum(args):
    from numpy import nansum
    outdata_lines = []
    for inpfile in args.input_files:
        sum_column = []
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal}"], [], args.v)
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
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal}"], [], args.v)
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
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal}"], [], args.v)
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
        data = io.read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal}"], [], args.v)
        for col in data[1]:
            std_column.append(f"%.{args.decimal[0]}f" %(nanstd(col)))
        outdata_lines.append(' '.join([inpfile] + std_column))
    args.sort = False
    args.uniq = False
    io.output_lines(outdata_lines, args)
