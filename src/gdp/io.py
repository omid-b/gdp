#!/usr/bin/env python3

def read_numerical_data(datfile, header, footer,  decimal, pos_indx, val_indx, novalue=False):
    from numpy import array
    from numpy import nan as npnan
    if len(decimal) == 1:
        dec = [decimal[0], decimal[0]]
    else:
        dec = decimal
    pos_indx = array(pos_indx) - 1 # index of positional columns
    pos_indx = pos_indx.tolist()
    if novalue:
        val_indx = []
    else:
        val_indx = array(val_indx) - 1
        val_indx = val_indx.tolist()
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
                pos[ix].append(float(datalines[i].split()[pos_indx[ix]]))
            except:
                pos[ix].append(npnan)
    # process lines: val & extra
    for i in range(nol):
        ncol = len(datalines[i].split())
        for iv in range(len(val_indx)):
            # value arguments
            try:
                val[iv].append(float(datalines[i].split()[val_indx[iv]]))
            except:
                val[iv].append(npnan)
        # extra
        extra_str_lst = datalines[i].split()
        for ix in range(len(pos_indx)):
            if pos_indx[ix] >= len(datalines[i].split()):
                pos_str = 'nan'
            else:
                pos_str = datalines[i].split()[pos_indx[ix]]
            if pos_str in extra_str_lst:
                extra_str_lst.remove(pos_str)
        for iv in range(len(val_indx)):
            if val_indx[iv] >= len(datalines[i].split()):
                val_str = 'nan'
            else:
                val_str = datalines[i].split()[val_indx[iv]]
            if val_str in extra_str_lst:
                extra_str_lst.remove(val_str)
        extra_str = ' '.join(extra_str_lst).strip()
        extra.append(extra_str)
    dat = [pos, val, extra]
    return dat


def data_lines(datfile,args):
    if len(args.decimal) == 1:
        dec = [args.decimal[0], args.decimal[0]]
    else:
        dec = args.decimal
    if args.nan:
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
        data = read_numerical_data(datfile, args.header, args.footer,  args.decimal, args.x, args.v, args.novalue)
        from numpy import nan as npnan
        datalines = []
        nol = len(data[2])
        for i in range(nol):
            pos_str = []
            for ix in range(len(data[0])):
                pos_str.append( f"%.{dec[0]}f" %(data[0][ix][i]) )
            line_str = ' '.join(pos_str)
            for iv in range(len(data[1])):
                if data[1][iv][i] != npnan:
                    line_str = f"%s %.{dec[1]}f" %(line_str, data[1][iv][i])
                else:
                    line_str = f"{line_str} NaN"
            if len(data[2][i]) and not args.noextra:
                line_str = "%s %s" %(line_str, data[2][i])
            datalines.append(line_str)
    return datalines


def output_lines(lines, args):
    if args.skipnan:
        nonan = []
        for line in lines:
            if 'nan' not in line.lower().split():
                nonan.append(line)
        lines = nonan
    lines_out = []
    if args.nouniq == False:
        for x in lines:
            if x not in lines_out:
                lines_out.append(x)
    else:
        lines_out = lines
    if args.nosort == False:
        lines_out = sorted(lines_out)
    # print to stdout or write to outfile
    if args.outfile:
        if args.append:
            fopen = open(args.outfile,'a')
        else:
            fopen = open(args.outfile,'w')
        for x in lines_out:
            fopen.write(f"{x.lower()}\n")
        fopen.close()
    else:
        for x in lines_out:
            print(f"{x.lower()}")


