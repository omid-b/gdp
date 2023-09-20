#!/usr/bin/env python3

import os
import shutil
import subprocess

from ..ascii_procs import io
from ..ascii_procs import dependency


def datasets_1Dto2D(args):
    if len(args.fmt) == 1:
        args.fmt = [args.fmt[0], args.fmt[0], "03.0"]
    elif len(args.fmt) == 2:
        args.fmt = [args.fmt[0], args.fmt[1], "03.0"]
    elif len(args.fmt) > 2:
        pass

    datalist = io.read_1D_datalist(args.datalist, args.fmt[0])
    args.fmt = [args.fmt[2], args.fmt[1]] # this line MUST be after datalist = ...
    outmodel_xy = {}
    outmodel_lines = {}
    for xy in datalist.keys():
        datafile = datalist[xy]
        args.nan = False
        args.noextra = True
        data = io.data_lines(datafile,args)
        for dline in data:
            fid = dline.split()[0] # fid could be period, depth etc.
            fid_vals = ' '.join(dline.split()[1:])
            if fid not in outmodel_xy.keys():
                outmodel_xy[fid] = []
                outmodel_lines[fid] = []

            outmodel_xy[fid].append(f"{xy}")
            outmodel_lines[fid].append(f"{xy} {fid_vals}")

    fids = sorted(list(outmodel_xy.keys()))

    # add nans to outmodel_lines
    if not args.skipnan:
        nans = ' '.join(["nan" for x in range(len(args.v))])
        for fid in fids:
            for xy in datalist.keys():
                if xy not in outmodel_xy[fid]:
                    outmodel_lines[fid].append(f"{xy} {nans}")

    args.sort = True
    args.uniq = False
    args.append = False
    # write files to outdir
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)
    for fid in fids:
        fout = f"{args.prefix}{fid}{args.suffix}.{args.ext}"
        args.outfile = os.path.join(args.outdir, fout)
        print(f"1Dto2D: '{args.datalist}' >> '{args.outfile}'")
        io.output_lines(outmodel_lines[fid], args)


#--------------------------#


def datasets_1Dto3D(args):
    if len(args.fmt) == 1:
        args.fmt = [args.fmt[0], args.fmt[0], "03.0"]
    elif len(args.fmt) == 2:
        args.fmt = [args.fmt[0], args.fmt[1], "03.0"]
    elif len(args.fmt) > 2:
        pass

    datalist = io.read_1D_datalist(args.datalist, args.fmt[0])
    args.fmt = [args.fmt[2], args.fmt[1]] # this line MUST be after datalist = ...
    outmodel_xy = {}
    outmodel_lines = {}
    for xy in datalist.keys():
        datafile = datalist[xy]
        args.nan = False
        args.noextra = True
        data = io.data_lines(datafile,args)
        for dline in data:
            fid = dline.split()[0] # fid could be period, depth etc.
            fid_vals = ' '.join(dline.split()[1:])
            if fid not in outmodel_xy.keys():
                outmodel_xy[fid] = []
                outmodel_lines[fid] = []

            outmodel_xy[fid].append(f"{xy}")
            outmodel_lines[fid].append(f"{xy} {fid} {fid_vals}")

    fids = sorted(list(outmodel_xy.keys()))

    # add nans to outmodel_lines
    if not args.skipnan:
        nans = ' '.join(["nan" for x in range(len(args.v))])
        for fid in fids:
            for xy in datalist.keys():
                if xy not in outmodel_xy[fid]:
                    outmodel_lines[fid].append(f"{xy} {fid} {nans}")


    model_3D = []
    for fid in fids:
        model_3D.append(outmodel_lines[fid])

    model_3D = [j for i in model_3D[:] for j in i]

    args.sort = False
    args.uniq = False
    args.append = False
    io.output_lines(model_3D, args)

#-----------------------#

def datasets_2Dto1D(args):
    if len(args.fmt) == 1:
        args.fmt = [args.fmt[0], args.fmt[0], "03.0"]
    elif len(args.fmt) == 2:
        args.fmt = [args.fmt[0], args.fmt[1], "03.0"]
    elif len(args.fmt) > 2:
        pass

    if args.x[0] == args.x[1]:
        print("Error! The two positional column numbers (flag '-x') cannot be the same!")
        exit(1)

    datalist = io.read_2D_datalist(args.datalist, args.fmt[2])
    fids = sorted(list(datalist.keys()))

    outmodel_fids = {}
    outmodel_lines = {}
    for fid in fids:
        datafile = datalist[fid]
        args.nan = False
        args.noextra = True
        data = io.data_lines(datafile,args)
        for dline in data:
            xy = ' '.join(dline.split()[0:2])
            vals = ' '.join(dline.split()[2:])
            if xy not in outmodel_fids.keys():
                outmodel_fids[xy] = []
                outmodel_lines[xy] = []

            outmodel_fids[xy].append(f"{fid}")
            outmodel_lines[xy].append(f"{fid} {vals}")

    # add nans to outmodel_lines
    if not args.skipnan:
        nans = ' '.join(["nan" for x in range(len(args.v))])
        for xy in outmodel_fids.keys():
            for fid in fids:
                if fid not in outmodel_fids[xy]:
                    outmodel_lines[xy].append(f"{fid} {nans}")

    args.sort = True
    args.uniq = False
    args.append = False
    # write files to outdir
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)
    for xy in outmodel_fids.keys():
        fout = f"X{xy.split()[0]}Y{xy.split()[1]}.{args.ext}"
        args.outfile = os.path.join(args.outdir, fout)
        print(f"2Dto1D: '{args.datalist}' >> '{args.outfile}'")
        io.output_lines(outmodel_lines[xy], args)


#-----------------------#

def datasets_2Dto3D(args):
    if len(args.fmt) == 1:
        args.fmt = [args.fmt[0], args.fmt[0], "03.0"]
    elif len(args.fmt) == 2:
        args.fmt = [args.fmt[0], args.fmt[1], "03.0"]
    elif len(args.fmt) > 2:
        pass

    if args.x[0] == args.x[1]:
        print("Error! The two positional column numbers (flag '-x') cannot be the same!")
        exit(1)

    datalist = io.read_2D_datalist(args.datalist, args.fmt[2])
    fids = sorted(list(datalist.keys()))

    output_lines = []
    for fid in fids:
        datafile = datalist[fid]
        args.nan = False
        args.noextra = True
        data = io.data_lines(datafile,args)
        for dline in data:
            xy = ' '.join(dline.split()[0:2])
            vals = ' '.join(dline.split()[2:])
            output_lines.append(f"{xy} %{args.fmt[2]}f {vals}" %(float(fid)))
            

    # add nans to outmodel_lines
    args.sort = False
    args.uniq = False
    args.append = False
    io.output_lines(output_lines, args)

