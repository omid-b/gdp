#!/usr/bin/env python3

"""
 Non-numerical/NaN ascii data type processing module

"""

import os
import numpy as np

#######################################

def read_dataset(non_numerical_file, header=0, footer=0):
    try:
        fopen = open(non_numerical_file, 'r')
        if footer != 0:
            lines = fopen.read().splitlines()[header:-footer]
        else:
            lines = fopen.read().splitlines()[header:]
        fopen.close()
    except Exception as e:
        print(f"{e}")
        exit(1)
    for i, x in enumerate(lines):
        lines[i] = x.strip()
    return lines

#######################################

def write_to_stdout(lines,\
                    uniq=False, sort=False):
    len_line = []
    lines_strip = []
    for x in lines:
        len_line.append(len(x))
        lines_strip.append(x.strip())
    lines_out = lines_strip
    if sort:
        lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
        lines_out = list(lines_out)
        len_line = list(len_line)

    # undo strip
    for i, x in enumerate(lines_out):
        lines_out[i] = f"%{len_line[i]}s" %(x)

    if uniq:
        lines_out = uniq_lines(lines_out)
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
    if uniq:
        for x in lines_strip:
            if x not in lines_out:
                lines_out.append(x)
    else:
        lines_out = lines_strip
    if sort:
        lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
        lines_out = list(lines_out)
        len_line = list(len_line)
    # undo strip
    for i,x in enumerate(lines_out):
        lines_out[i] = f"%{len_line[i]}s" %(x)
    # write to file
    if append:
        fopen = open(outfile,'a')
    else:
        fopen = open(outfile,'w')
    for x in lines_out:
        fopen.write(f"{x}\n")
    fopen.close()


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
        for i in range(nod):
            num_lines = len(datasets[i])
            for j in range(num_lines):
                if datasets[i][j] not in intersect:
                    intersect_inv.append(datasets[i][j])
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

def split_by_nrows(combined_dataset, number, name_index_offset=0):
    split_dataset = {}
    split_indices = [x for x in range(0, len(combined_dataset), number)]
    if split_indices[-1] < len(combined_dataset):
        split_indices.append(len(combined_dataset))
    num_split_datasets = len(split_indices) - 1 # number of split datasets
    for i in range(num_split_datasets):
        split_data_lines = combined_dataset[split_indices[i]:split_indices[i+1]]
        split_data_name = f"{'_'.join(split_data_lines[name_index_offset-1].split())}"
        split_dataset[f"{split_data_name}"] = split_data_lines
    return split_dataset

#######################################

def split_by_ncols(combined_dataset, number, \
                   name_index_offset=0,\
                   start_index_offset=0):
    split_dataset = {}
    split_indices = []
    for i, line in enumerate(combined_dataset):
        if len(line.split()) == number:
            split_indices.append(i + start_index_offset)
            if split_indices[-1] < 0:
                print("Error: split_by_num_cols(): 'split_index' cannot be negative!")
                print("       (check argument 'start_index_offset')")
                exit(1)
    if split_indices[-1] < len(combined_dataset):
        split_indices.append(len(combined_dataset))
    num_split_datasets = len(split_indices) - 1 # number of split datasets
    for i in range(num_split_datasets):
        split_data_lines = combined_dataset[split_indices[i]:split_indices[i+1]]
        split_data_name = f"{'_'.join(split_data_lines[name_index_offset-1].split())}"
        split_dataset[f"{split_data_name}"] = split_data_lines
    return split_dataset
