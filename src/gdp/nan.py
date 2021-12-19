# non-numerical/NaN data type processing module

import os
from . import io


def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    union = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
        nol = len(datlines[i])
        for j in range(nol):
            if datlines[i][j] not in union:
                union.append(datlines[i][j])
    if args.inverse:
        union_inv = []
        for i in range(nof):
            nol = len(args.input_files)
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
    intersect = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    ###
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines[0][j] in l for l in datlines[1:]):
            intersect.append(datlines[0][j])
    ###
    if args.inverse:
        intersect_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in intersect:
                    intersect_inv.append(datlines[i][j])
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)





def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    difference = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    ###
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines[0][j] not in l for l in datlines[1:]):
            difference.append(datlines[0][j])
    ###
    if args.inverse:
        difference_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in difference:
                    difference_inv.append(datlines[i][j])
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)


def unmerge_nrow(args):
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
        split_data_name = f"{'_'.join(split_data_lines[args.name-1].split())}.{args.outext}"
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


def unmerge_ncol(args):
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
        split_data_name = f"{'_'.join(split_data_lines[args.name-1].split())}.{args.outext}"
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




