#!/usr/bin/env python3

# non-numerical/NaN data type processing module

import os
import numpy as np

#######################################

def read_lines(input_file, header=0, footer=0):
    try:
        fopen = open(input_file, 'r')
        if footer != 0:
            lines = fopen.read().splitlines()[header:-footer]
        else:
            lines = fopen.read().splitlines()[header:]
        fopen.close()
    except:
        print(f"Error reading input file: {input_file}\n")
        exit(1)
    for i, x in enumerate(lines):
        lines[i] = x.strip()
    return lines

#######################################

def calc_union(datasets):
    nod = len(datasets) # number of datasets
    if nod < 2:
        print("Error! Number of datasets must be larger than 2 for union operation.")
        exit(1)
    union = []
    for i in range(nod):
        for line in datasets[i]:
            if line not in union:
                union.append(line)
    return union

#######################################

def calc_intersect(datasets, inverse=False):
    nod = len(datasets) # number of datasets
    if nod < 2:
        print("Error! Number of datasets must be larger than 2 for intersect operation.")
        exit(1)
    intersect = []
    num_lines = len(datasets[0])
    for j in range(num_lines):
        if all(datasets[0][j] in l for l in datasets[1:]):
            intersect.append(datasets[0][j])

    if inverse:
        intersect_inv = []
        for i in range(nof):
            num_lines = len(datasets[i])
            for j in range(num_lines):
                if datlines[i][j] not in intersect:
                    intersect_inv.append(datlines[i][j])
        return intersect_inv
    else:
        return intersect


#######################################

def calc_difference(datasets, inverse=False):
    nod = len(datasets) # number of datasets
    if nod < 2:
        print("Error! Number of datasets must be larger than 2 for difference operation.")
        exit(1)
    difference = []
    num_lines = len(datasets[0])
    for j in range(num_lines):
        if all(datasets[0][j] not in l for l in datasets[1:]):
            difference.append(datasets[0][j])

    if inverse:
        difference_inv = []
        for i in range(nod):
            num_lines = len(datasets[i])
            for j in range(num_lines):
                if datasets[i][j] not in difference:
                    difference_inv.append(datasets[i][j])
        return difference_inv
    else:
        return difference

#######################################

def split_data_nrow(args):
    try:
        fopen = open(args.input_file[0],'r')
        if args.footer != 0:
            datalines = fopen.read().splitlines()[args.header:-args.footer]
        else:
            datalines = fopen.read().splitlines()[args.header:]
    except Exception as exc:
        print(exc)
        exit(1)
    indexes = [x for x in range(0, len(datalines), args.number)]
    if indexes[-1] < len(datalines):
        indexes.append(len(datalines))
    # split data
    ndata = len(indexes) - 1
    for i in range(ndata):
        split_data_lines = datalines[indexes[i]:indexes[i+1]]
        split_data_name = f"{'_'.join(split_data_lines[args.name-1].split())}.{args.ext}"
        if args.outdir:
            if not os.path.isdir(args.outdir):
                os.mkdir(args.outdir)
            fopen = open(f'{os.path.join(args.outdir, split_data_name)}','w')
            fopen.write('\n'.join(split_data_lines))
            fopen.write('\n')
            fopen.close()
        else:
            stdout = [f"File name: {split_data_name}"] + split_data_lines
            stdout = '\n'.join(stdout)
            print(f"{stdout}\n")

#######################################

def split_data_ncol(args):
    try:
        fopen = open(args.input_file[0],'r')
        if args.footer != 0:
            datalines = fopen.read().splitlines()[args.header:-args.footer]
        else:
            datalines = fopen.read().splitlines()[args.header:]
    except Exception as exc:
        print(exc)
        exit(1)
    indexes = []
    for i, dline in enumerate(datalines):
        if len(dline.split()) == args.number:
            indexes.append(i + args.start)
    if indexes[-1] < len(datalines):
        indexes.append(len(datalines))
    # handle errors
    if min(indexes) < 0:
        print(f"\nError! Argument 'start' is too low!\n")
        exit(1)
    # split data
    ndata = len(indexes) - 1
    for i in range(ndata):
        split_data_lines = datalines[indexes[i]:indexes[i+1]]
        split_data_name = f"{'_'.join(split_data_lines[args.name-1].split())}.{args.ext}"
        if args.outdir:
            if not os.path.isdir(args.outdir):
                os.mkdir(args.outdir)
            fopen = open(f'{os.path.join(args.outdir, split_data_name)}','w')
            fopen.write('\n'.join(split_data_lines))
            fopen.write('\n')
            fopen.close()
        else:
            stdout = [f"File name: {split_data_name}"] + split_data_lines
            stdout = '\n'.join(stdout)
            print(f"{stdout}\n")

#######################################

def write_to_stdout(lines,\
                    uniq=False, sort=False):
    len_line = []
    lines_strip = []
    for x in lines:
        len_line.append(len(x))
        lines_strip.append(x.strip())
    lines_out = []
    if args.uniq:
        for x in lines_strip:
            if x not in lines_out:
                lines_out.append(x)
    else:
        lines_out = lines_strip
    if args.sort:
        lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
        lines_out = list(lines_out)
        len_line = list(len_line)
    # undo strip
    for i,x in enumerate(lines_out):
        lines_out[i] = f"%{len_line[i]}s" %(x)
    # write to stdout
    for x in lines_out:
            print(f"{x}")

#######################################            

def write_to_file(lines, outfile,\
                  uniq=False, sort=False, append=False):
    len_line = []
    lines_strip = []
    for x in lines:
        len_line.append(len(x))
        lines_strip.append(x.strip())
    lines_out = []
    if args.uniq:
        for x in lines_strip:
            if x not in lines_out:
                lines_out.append(x)
    else:
        lines_out = lines_strip
    if args.sort:
        lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
        lines_out = list(lines_out)
        len_line = list(len_line)
    # undo strip
    for i,x in enumerate(lines_out):
        lines_out[i] = f"%{len_line[i]}s" %(x)
    # write to file
    if args.append:
        fopen = open(outfile,'a')
    else:
        fopen = open(outfile,'w')
    for x in lines_out:
        fopen.write(f"{x}\n")
    fopen.close()


# def data_lines(datfile,args):
#     if len(args.fmt) == 1:
#         fmt = [args.fmt[0], args.fmt[0]]
#     else:
#         fmt = args.fmt
#     if args.nan or len(args.x) == len(args.v) == 0:
#         try:
#             fopen = open(datfile,'r')
#             if args.footer != 0:
#                 datalines_all = fopen.read().splitlines()[args.header:-args.footer]
#             else:
#                 datalines_all = fopen.read().splitlines()[args.header:]
#             fopen.close()
#         except Exception as exc:
#             print(f"Error reading input file: {datfile}\n")
#             exit(1)
#         datalines = []
#         for x in datalines_all:
#             datalines.append(x.strip())
#     else:
#         data = read_numerical_data(datfile, args.header, args.footer,  args.fmt, args.x, args.v, args.skipnan)
#         datalines = []
#         nol = len(data[2])
#         for i in range(nol):
#             pos_str = []
#             for ix in range(len(data[0])):
#                 pos_str.append( f"%{fmt[0]}f" %(data[0][ix][i]) )
#             line_str = ' '.join(pos_str)
#             for iv in range(len(data[1])):
#                 if data[1][iv][i] != np.nan:
#                     line_str = f"%s %{fmt[1]}f" %(line_str, data[1][iv][i])
#                 else:
#                     line_str = f"{line_str} {np.nan}"
#             if len(data[2][i]) and not args.noextra:
#                 line_str = "%s %s" %(line_str, data[2][i])
#             datalines.append(line_str)
#     return datalines

