#!/usr/bin/env python3

def read_numerical_data(datfile, header, footer,  fmt, pos_indx, val_indx, skipnan=False):
    from numpy import array
    from numpy import nan as npnan
    if len(fmt) == 1:
        fmt = [fmt[0], fmt[0]]
    else:
        fmt = fmt
    if len(pos_indx):
        pos_indx = array(pos_indx) - 1 # index of positional columns
        pos_indx = pos_indx.tolist()
    else:
        pos_indx = []
    if len(val_indx):
        val_indx = array(val_indx) - 1
        val_indx = val_indx.tolist()
    else:
        val_indx = []
    pos = [[] for ix in range(len(pos_indx))] # list of positional values
    val = [[] for iv in range(len(val_indx))] # list of values/data
    extra = []
    # read lines
    try:
        fopen = open(datfile, 'r')
        if footer != 0:
            datalines = fopen.read().splitlines()[header:-footer]
        else:
            datalines = fopen.read().splitlines()[header:]
        fopen.close()
    except Exception as exc:
        print(exc)
        exit(0)
    nol = len(datalines)
    # process lines: positional columns
    for i in range(nol):
        ncol = len(datalines[i].split())
        for ix in range(len(pos_indx)):
            # positional arguments
            try:
                if datalines[i].split()[pos_indx[ix]] == 'nan':
                    pos[ix].append(npnan)
                else:
                    pos[ix].append(float(datalines[i].split()[pos_indx[ix]]))
            except:
                pos[ix].append(npnan)
    # process lines: val & extra
    for i in range(nol):
        ncol = len(datalines[i].split())
        for iv in range(len(val_indx)):
            # value arguments
            try:
                if datalines[i].split()[val_indx[iv]] == 'nan':
                    val[iv].append(npnan)
                else:
                    val[iv].append(float(datalines[i].split()[val_indx[iv]]))
            except:
                val[iv].append(npnan)
        # extra
        extra_str_lst = datalines[i].split()
        for ix in range(len(pos_indx)):
            if pos_indx[ix] >= len(datalines[i].split()):
                pos_str = npnan
            else:
                pos_str = datalines[i].split()[pos_indx[ix]]
            if pos_str in extra_str_lst:
                extra_str_lst.remove(pos_str)
        for iv in range(len(val_indx)):
            if val_indx[iv] >= len(datalines[i].split()):
                val_str = npnan
            else:
                val_str = datalines[i].split()[val_indx[iv]]
            if val_str in extra_str_lst:
                extra_str_lst.remove(val_str)
        extra_str = ' '.join(extra_str_lst).strip()
        extra.append(extra_str)
    dat = [pos, val, extra]
    # skipnan = True ?
    if skipnan:
        pos_skipnan = [[] for ix in range(len(pos_indx))]
        val_skipnan = [[] for iv in range(len(val_indx))]
        extra_skipnan = []
        for i in range(nol):
            temp = []
            for ix in range(len(pos_indx)):
                temp.append(pos[ix][i])
            for iv in range(len(val_indx)):
                temp.append(val[iv][i])
            if npnan not in temp:
                for ix in range(len(pos_indx)):
                    pos_skipnan[ix].append(pos[ix][i])
                for iv in range(len(val_indx)):
                    val_skipnan[iv].append(val[iv][i])
                extra_skipnan.append(extra[i])
        dat = [pos_skipnan, val_skipnan, extra_skipnan]
    return dat


def data_lines(datfile,args):
    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt
    if args.nan or len(args.x) == len(args.v) == 0:
        try:
            fopen = open(datfile,'r')
            if args.footer != 0:
                datalines_all = fopen.read().splitlines()[args.header:-args.footer]
            else:
                datalines_all = fopen.read().splitlines()[args.header:]
            fopen.close()
        except Exception as exc:
            print(f"Error reading input file: {datfile}\n")
            exit(1)
        datalines = []
        for x in datalines_all:
            datalines.append(x.strip())
    else:
        data = read_numerical_data(datfile, args.header, args.footer,  args.fmt, args.x, args.v, args.skipnan)
        from numpy import nan as npnan
        datalines = []
        nol = len(data[2])
        for i in range(nol):
            pos_str = []
            for ix in range(len(data[0])):
                pos_str.append( f"%{fmt[0]}f" %(data[0][ix][i]) )
            line_str = ' '.join(pos_str)
            for iv in range(len(data[1])):
                if data[1][iv][i] != npnan:
                    line_str = f"%s %{fmt[1]}f" %(line_str, data[1][iv][i])
                else:
                    line_str = f"{line_str} {npnan}"
            if len(data[2][i]) and not args.noextra:
                line_str = "%s %s" %(line_str, data[2][i])
            datalines.append(line_str)
    return datalines


def output_lines(lines, args):
    lines_out = []
    if args.uniq:
        for x in lines:
            if x not in lines_out:
                lines_out.append(x)
    else:
        lines_out = lines
    if args.sort:
        lines_out = sorted(lines_out)
    # print to stdout or write to outfile
    if args.outfile:
        if args.append:
            fopen = open(args.outfile,'a')
        else:
            fopen = open(args.outfile,'w')
        for x in lines_out:
            fopen.write(f"{x}\n")
        fopen.close()
    else:
        for x in lines_out:
            print(f"{x}")



def read_polygon_shp(polygon_file):
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import mapping
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
        except Exception as e:
            print(f"Error! Could not read shape file item '{i+1}': '{polygon_file}'\n{e}\n")
            exit(1)
        polygons[i] = [polygon_x, polygon_y]
    
    return polygons



def read_point_shp(point_file):
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import mapping
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


