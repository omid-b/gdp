#!/usr/bin/env python3

def read_xyz(xyzfile, args):
    from numpy import nan as npnan
    x = args.x - 1
    y = args.y - 1
    if args.noz:
        z = x
    else:
        z = args.z - 1
    lon = []
    lat = []
    zval = []
    extra = []
    # read lines
    try:
        fopen = open(xyzfile, 'r')
        if args.footers:
            xyzlines = fopen.read().splitlines()[args.headers:-args.footers]
        else:
            xyzlines = fopen.read().splitlines()[args.headers:]
        fopen.close()
    except Exception as exc:
        print(exc)
        exit(0)
    nol = len(xyzlines)
    # process lines: lon & lat
    try:
        for i in range(nol):
            lon.append(float(xyzlines[i].split()[x]))
            lat.append(float(xyzlines[i].split()[y]))
    except Exception as exc:
        print(f"Error reading/converting-to-float xyz at line {i+1}. {exc}")
        exit(0)
    # process lines: zval & extra
    for i in range(nol):
        ncol = len(xyzlines[i].split())
        # zval
        if z < ncol and not args.noz:
            try:
                zval.append(float(xyzlines[i].split()[z]))
            except:
                print(f"Error converting Z value to float at line {i+1} in file: {xyzfile}")
                exit()
        else:
            zval.append(npnan)
        # extra
        if ncol > (max([x,y,z]) + 1):
            lon_str = xyzlines[i].split()[x]
            lat_str = xyzlines[i].split()[y]
            zval_str = xyzlines[i].split()[z]
            extra_str_lst = xyzlines[i].split()
            if lon_str in extra_str_lst:
                extra_str_lst.remove(lon_str)
            if lat_str in extra_str_lst:
                extra_str_lst.remove(lat_str)
            if zval_str in extra_str_lst:
                extra_str_lst.remove(zval_str)
            extra_str = ' '.join(extra_str_lst).strip()
        else:
            extra_str = ''
        extra.append(extra_str)
    xyz = [lon, lat, zval, extra]
    return xyz


def xyz_lines(xyzfile, args):
    xyz_data = read_xyz(xyzfile,args)
    from numpy import nan as npnan
    xyzlines = []
    nol = len(xyz_data[0])
    for i in range(nol):
        line_str = f"%.{args.decimals}f %.{args.decimals}f" %(xyz_data[0][i],xyz_data[1][i])
        if xyz_data[2][i] != npnan and not args.noz:
            line_str = f"%s %.{args.decimals}f" %(line_str, xyz_data[2][i])
        if len(xyz_data[3][i]) and not args.noextra:
            line_str = "%s %s" %(line_str, xyz_data[3][i])
        xyzlines.append(line_str)
    return xyzlines


def dat_lines(datfile,args):
    try:
        fopen = open(datfile,'r')
        if args.footers:
            datlines = fopen.read().splitlines()[args.headers:-args.footers]
        else:
            datlines = fopen.read().splitlines()[args.headers:]
        fopen.close()
    except Exception as exc:
        print(f"Error reading input file: {datfile}\n")
        exit(1)
    return datlines


def output_lines(lines, args):
    # output to stout or a file
    lines_uniq = []
    for x in lines:
        if x not in lines_uniq:
            lines_uniq.append(x)
    lines_uniq = sorted(lines_uniq)
    if args.output:
        if args.append:
            fopen = open(args.output,'a')
        else:
            fopen = open(args.output,'w')
        for x in lines_uniq:
            fopen.write(f"{x}\n")
        fopen.close()
    else:
        for x in lines_uniq:
            print(f"{x}")


def read_pollygon_dat(datfile, args):
    x = args.x - 1
    y = args.y - 1
    lon = []
    lat = []
    # read lines
    try:
        fopen = open(datfile, 'r')
        datlines = fopen.read().splitlines()[args.headers:]
        fopen.close()
    except Exception as exc:
        print(exc)
        exit(0)
    # process lines
    try:
        for line in datlines:
            lon.append(float(line.split()[x]))
            lat.append(float(line.split()[y]))
    except Exception as exc:
        print(exc)
        exit(0)
    ret = [lon, lat]
    return ret

