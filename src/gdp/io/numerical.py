#!/usr/bin/env python3

# numerical data type processing module

import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import warnings

from .non_numerical import read_ascii_lines
from .non_numerical import write_ascii_lines




def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    union = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = data_lines(input_files[i],args)
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

#######################################

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
        datlines[i] = data_lines(input_files[i],args)
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
        datlines[i] = data_lines(input_files[i],args)
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

#######################################


def read_lines(datfile,args):
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
        datalines = []
        nol = len(data[2])
        for i in range(nol):
            pos_str = []
            for ix in range(len(data[0])):
                pos_str.append( f"%{fmt[0]}f" %(data[0][ix][i]) )
            line_str = ' '.join(pos_str)
            for iv in range(len(data[1])):
                if data[1][iv][i] != np.nan:
                    line_str = f"%s %{fmt[1]}f" %(line_str, data[1][iv][i])
                else:
                    line_str = f"{line_str} {np.nan}"
            if len(data[2][i]) and not args.noextra:
                line_str = "%s %s" %(line_str, data[2][i])
            datalines.append(line_str)
    return datalines



def calc_min(args):
    outdata_lines = []
    for inpfile in args.input_files:
        min_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            min_column.append(f"%.{args.decimal[0]}f" %(np.nanmin(col)))
        outdata_lines.append(' '.join([inpfile] + min_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)


#######################################


def calc_max(args):
    outdata_lines = []
    for inpfile in args.input_files:
        max_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            max_column.append(f"%.{args.decimal[0]}f" %(np.nanmax(col)))
        outdata_lines.append(' '.join([inpfile] + max_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)


#######################################


def calc_sum(args):
    outdata_lines = []
    for inpfile in args.input_files:
        sum_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            sum_column.append(f"%.{args.decimal[0]}f" %(np.nansum(col)))
        outdata_lines.append(' '.join([inpfile] + sum_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)

#######################################

def calc_mean(args):

    outdata_lines = []
    for inpfile in args.input_files:
        mean_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            mean_column.append(f"%.{args.decimal[0]}f" %(float(np.nanmean(col))))
        outdata_lines.append(' '.join([inpfile] + mean_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)

#######################################


def calc_median(args):
    outdata_lines = []
    for inpfile in args.input_files:
        median_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            median_column.append(f"%.{args.decimal[0]}f" %(float(np.nanmedian(col))))
        outdata_lines.append(' '.join([inpfile] + median_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)

#######################################

def calc_std(args):
    outdata_lines = []
    for inpfile in args.input_files:
        std_column = []
        data = read_numerical_data(inpfile, args.header, args.footer,  [f".{args.decimal[0]}"], [], args.v)
        for col in data[1]:
            std_column.append(f"%.{args.decimal[0]}f" %(np.nanstd(col)))
        outdata_lines.append(' '.join([inpfile] + std_column))
    args.sort = False
    args.uniq = False
    if len(outdata_lines) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
    write_ascii_lines(outdata_lines, args)


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
        datlines[i] = read_ascii_lines(input_files[i], args)
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
    write_ascii_lines(intersect, args)


#######################################

def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = read_ascii_lines(input_files[i], args)
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
        write_ascii_lines(union_inv, args)
    else:
        if len(union) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        write_ascii_lines(union, args)

#######################################

def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = read_ascii_lines(input_files[i], args)
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
        write_ascii_lines(intersect_inv, args)
    else:
        if len(intersect) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        write_ascii_lines(intersect, args)

#######################################

def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = read_ascii_lines(input_files[i], args)
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
        write_ascii_lines(difference_inv, args)
    else:
        if len(difference) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        write_ascii_lines(difference, args)


#######################################


def anomaly_2D(args):
    # read models
    absmodel_x, [absmodel_v], _ = read_numerical_data(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
    [refmodel_x], [refmodel_v], _ = read_numerical_data(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
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
    write_ascii_lines(output_lines, args)

    # print reference model value into stdout
    if args.outfile == None:
        print(f"\nCalculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}\n")
    else:
        print(f"Calculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}")


#######################################

def anomaly_1D(args):

    outfile_orig = args.outfile
    # read models
    [absmodel_x], [absmodel_v], _ = read_numerical_data(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
    [refmodel_x], [refmodel_v], _ = read_numerical_data(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
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
        write_ascii_lines(outlines_markers, args)

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
        write_ascii_lines(outline_anomaly, args)
        # plot
        plt.show()
    else: # output anomaly data and plot to files
        # anomaly data
        args.outfile = outfile_orig
        if len(outline_anomaly) == 0:
            print("Error! Number of outputs is zero!")
            exit(1)
        write_ascii_lines(outline_anomaly, args)
        # plot
        outplot = os.path.abspath(f"{os.path.splitext(outfile_orig)[0]}.{args.ext}")
        plt.savefig(outplot, dpi=args.dpi, format=args.ext)
    plt.close()


#######################################

def read_1D_datalist(input_datalist, fmt):
    datalist = {}
    try:
        fopen = open(input_datalist, 'r')
        flines = fopen.read().splitlines()
        fopen.close()
    except Exception as e:
        print(f"{e}\nError! Could not read/find input datalist: '{input_datalist}'")
        exit(1)
    for i, line in enumerate(flines):
        if len(line.split()) == 3:
            try:
                x = float(line.split()[0])
                y = float(line.split()[1])
                data = line.split()[2]
            except Exception as e:
                print(f"{e}\nDatalist format error at line {i+1}!")
                print("All lines must have 3 columns: (1) lon/X, (2) lat/Y, (3) path to 1D data")
                exit(1)

            if not os.path.isfile(data):
                print(f"Error! Could not find data at line {i+1}: '{data}'")
                exit(1)
            else:
                key = f"%{fmt}f %{fmt}f" %(x, y)
                datalist[key] = data
        else:
            print(f"Datalist format error at line {i+1}!")
            print("All lines must have 3 columns: (1) lon/X, (2) lat/Y, (3) path to 1D data")
            exit(1)

    return datalist


#######################################

def read_2D_datalist(input_datalist, fmt):
    datalist = {}
    try:
        fopen = open(input_datalist, 'r')
        flines = fopen.read().splitlines()
        fopen.close()
    except Exception as e:
        print(f"{e}\nError! Could not read/find input datalist: '{input_datalist}'")
        exit(1)
    for i, line in enumerate(flines):
        if len(line.split()) == 2:
            try:
                fid = float(line.split()[0])
                data = line.split()[1]
            except Exception as e:
                print(f"{e}\nDatalist format error at line {i+1}!")
                print("All lines must have 2 columns: (1) data identifier e.g. period, depth etc., (2) path to 2D data")
                exit(1)
            
            if not os.path.isfile(data):
                print(f"Error! Could not find data at line {i+1}: '{data}'")
                exit(1)
            else:
                key = f"%{fmt}f" %(fid)
                datalist[key] = data

        else:
            print(f"Datalist format error at line {i+1}!")
            print("All lines must have 2 columns: (1) data identifier e.g. period, depth etc., (2) path to 2D data")
            exit(1)

    return datalist

#######################################

def read_numerical_data(datfile, header, footer,  fmt, pos_indx, val_indx, skipnan=False):
    if len(fmt) == 1:
        fmt = [fmt[0], fmt[0]]
    else:
        fmt = fmt
    if len(pos_indx):
        pos_indx = np.array(pos_indx) - 1 # index of positional columns
        pos_indx = pos_indx.tolist()
    else:
        pos_indx = []
    if len(val_indx):
        val_indx = np.array(val_indx) - 1
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
                    pos[ix].append(np.nan)
                else:
                    pos[ix].append(float(datalines[i].split()[pos_indx[ix]]))
            except:
                pos[ix].append(np.nan)
    # process lines: val & extra
    for i in range(nol):
        ncol = len(datalines[i].split())
        for iv in range(len(val_indx)):
            # value arguments
            try:
                if datalines[i].split()[val_indx[iv]] == 'nan':
                    val[iv].append(np.nan)
                else:
                    val[iv].append(float(datalines[i].split()[val_indx[iv]]))
            except:
                val[iv].append(np.nan)
        # extra
        extra_str_lst = datalines[i].split()
        for ix in range(len(pos_indx)):
            if pos_indx[ix] >= len(datalines[i].split()):
                pos_str = np.nan
            else:
                pos_str = datalines[i].split()[pos_indx[ix]]
            if pos_str in extra_str_lst:
                extra_str_lst.remove(pos_str)
        for iv in range(len(val_indx)):
            if val_indx[iv] >= len(datalines[i].split()):
                val_str = np.nan
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
            if np.nan not in temp:
                for ix in range(len(pos_indx)):
                    pos_skipnan[ix].append(pos[ix][i])
                for iv in range(len(val_indx)):
                    val_skipnan[iv].append(val[iv][i])
                extra_skipnan.append(extra[i])
        dat = [pos_skipnan, val_skipnan, extra_skipnan]
    return dat

