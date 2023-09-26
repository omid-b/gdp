#!/usr/bin/env python3

"""
 Numerical & Non-numerical ascii Dataset class

 List of possible processes:
    - merge
    - union
    - intersect
    - difference
    - add intersect values
    - split by row
    - split by column
    - return numerical dataset
    - return truncated lines
    - ...

"""

import os
import numpy as np
from argparse import Namespace

class Dataset:

    def __init__(self, files=[]):
        self.nds = 0 # number of datasets
        self.files = [] # list of files
        self.lines = [] # list of file lines
        self.titles = [] # list of processed datset titles
        self.processed = [] # list of processed datsets
        self.last_process = None
        self.default_args = Namespace(
            header = 0,
            footer = 0,
            x = [], # positional columns e.g. x, y, z
            v = [], # value columns e.g. velocity, density
            noextra = False, # no extra columns
            skipnan = False, # skip nan data
            fmt = [".4", ".4"], # format for positional and value columns
            sort = False, # sort when output 
            uniq = False, # uniq when output
        )
        self.options(**vars(self.default_args))
        self.append(files) # must be after self.options()


    def options(self, **kwargs):
        self.input_args = Namespace(**kwargs)
        for option in kwargs.keys():
            if option == 'header':
                self.header = kwargs['header']
            elif option == 'footer':
                self.footer = kwargs['footer']
            elif option == 'x':
                self.x = kwargs['x']
            elif option == 'v':
                self.v = kwargs['v']
            elif option == 'noextra':
                self.noextra = kwargs['noextra']
            elif option == 'skipnan':
                self.skipnan = kwargs['skipnan']
            elif option == 'fmt':
                self.fmt = kwargs['fmt']
                if len(kwargs['fmt']) == 1:
                    self.fmt = [kwargs['fmt'][0], kwargs['fmt'][0]]
            elif option == 'sort':
                self.sort = kwargs['sort']
            elif option == 'uniq':
                self.uniq = kwargs['uniq']
        self.update()


    def append(self, new_files):
        try:
            assert isinstance(new_files, list)
        except AssertionError:
            new_files = [new_files]
        nof = len(new_files)
        for i in range(nof):
            if new_files[i] in self.files:
                continue
            try:
                fopen = open(new_files[i], 'r')
                lines = fopen.read().splitlines()
                fopen.close()
            except Exception as e:
                print(f"{e}")
                exit(1)
            self.files.append(new_files[i])
            self.lines.append(lines)
        self.nds = len(self.files)
        self.update()


    def merge(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            merge = [[], [], []]
            for ids in range(self.nds):
                for line in self.processed[ids][2]:
                    merge[2].append(line)
        else:
            merge = [ [[] for ix in range(self.nx)], [[] for ival in range(self.nv)], [] ]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2])
                for iline in range(nol):
                    for ix in range(self.nx):
                        merge[0][ix].append(self.processed[ids][0][ix][iline])
                    for iv in range(self.nv):
                        merge[1][iv].append(self.processed[ids][1][iv][iline])
                    merge[2].append(self.processed[ids][2][iline])
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, merge)]
            self.titles = ['merge_inv']
        else:
            self.processed = [merge]
            self.titles = ['merge']
        self.last_process = 'merge'
        self.nds = 1


    def union(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            union = [[], [], []]
            for ids in range(self.nds):
                for line in self.processed[ids][2]:
                    if line not in union[2]:
                        union[2].append(line)
        else:
            union = [ [[] for ix in range(self.nx)], [[] for iv in range(self.nv)], [] ]
            pos_data_uniq = []
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][k][iline] for k in range(self.nx)]
                    val_data = [self.processed[ids][1][k][iline] for k in range(self.nv)]
                    ext_data = self.processed[ids][2][iline]
                    if pos_data not in pos_data_uniq:
                        pos_data_uniq.append(pos_data)
                        for ix in range(self.nx):
                            union[0][ix].append(pos_data[ix])
                        for iv in range(self.nv):
                            union[1][iv].append(val_data[iv])
                        union[2].append(ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, union)]
            self.titles = ['union_inv']
        else:
            self.processed = [union]
            self.titles = ['union']
        self.last_process = 'union'
        self.nds = 1


    def intersect(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:

            intersect = [[], [], []]
            nol = len(self.processed[0][2])
            comparing_extras = []
            for ids in range(1, self.nds):
                comparing_extras.append(self.processed[ids][2])

            for iline in range(nol):
                line = self.processed[0][2][iline]
                if all(line in l for l in comparing_extras):
                    intersect[2].append(line)
        else:
            intersect = [ [[] for ix in range(self.nx)], [[] for iv in range(self.nv)], [] ]
            pos_data_datasets = [[] for ids in range(self.nds)]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][ix][iline] for ix in range(self.nx)]
                    pos_data_datasets[ids].append(pos_data)

            first_ds_nol = len(self.processed[0][2]) # first dataset number of lines
            for iline in range(first_ds_nol):
                first_ds_pos_data = [self.processed[0][0][ix][iline] for ix in range(self.nx)]
                first_ds_val_data = [self.processed[0][1][iv][iline] for iv in range(self.nv)]
                first_ds_ext_data = self.processed[0][2][iline]
                if all(first_ds_pos_data in l for l in pos_data_datasets[1:]):
                    for ipos in range(self.nx):
                        intersect[0][ipos].append(first_ds_pos_data[ipos])
                    for ival in range(self.nv):
                        intersect[1][ival].append(first_ds_val_data[ival])
                    intersect[2].append(first_ds_ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, intersect)]
            self.titles = ['intersect_inv']
        else:
            self.processed = [intersect]
            self.titles = ['intersect']
        self.last_process = 'intersect'
        self.nds = 1



    def difference(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            difference = [[], [], []]
            comparing_extras = []
            for ids in range(1, self.nds):
                comparing_extras.append(self.processed[ids][2])
            nol = len(self.processed[0][2])
            for iline in range(nol):
                line = self.processed[0][2][iline]
                if all(line not in l for l in comparing_extras):
                    difference[2].append(line)
        else:
            difference = [[[] for ix in range(self.nx)],[[] for iv in range(self.nv)],[]]
            pos_data_datasets = [[] for ids in range(self.nds)]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][ix][iline] for ix in range(self.nx)]
                    pos_data_datasets[ids].append(pos_data)

            first_ds_nol = len(self.processed[0][2]) # first dataset number of lines
            for iline in range(first_ds_nol):
                first_ds_pos_data = [self.processed[0][0][ix][iline] for ix in range(self.nx)]
                first_ds_val_data = [self.processed[0][1][iv][iline] for iv in range(self.nv)]
                first_ds_ext_data = self.processed[0][2][iline]
                if all(first_ds_pos_data not in l for l in pos_data_datasets[1:]):
                    for ix in range(self.nx):
                        difference[0][ix].append(first_ds_pos_data[ix])
                    for iv in range(self.nv):
                        difference[1][iv].append(first_ds_val_data[iv])
                    difference[2].append(first_ds_ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, difference)]
            self.titles = ['difference_inv']
        else:
            self.processed = [difference]
            self.titles = ['difference']
        self.last_process = 'difference'
        self.nds = 1


    def add_intersect(self):
        self.reset()
        if self.nan:
            print("Error: add_intersect operation is only allowed for numerical datasets.")
            exit(1)
        if self.nds < 2:
            return
        # store intersect dataset first
        self.intersect()
        intersect_ds = self.processed[0]
        num_intersects = len(intersect_ds[2])
        if not num_intersects:
            print("Error: found no intersect dataset to calculate 'add_intersect'.")
            exit(0)
        self.reset()
        # lines for intersect_ds positional data
        intersect_pos_data = [[] for ii in range(num_intersects)]
        for ii in range(num_intersects):
            for ix in range(self.nx):
                intersect_pos_data[ii].append(intersect_ds[0][ix][ii])
        # initialize with zeros
        added_values = [[] for iv in range(self.nv)]
        for iv in range(self.nv):
            for ii in range(num_intersects):
                added_values[iv].append(0)
        # calculate add_intersect values
        for ii in range(num_intersects):
            candidate_intersect_pos_data = intersect_pos_data[ii]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = []
                    for ix in range(self.nx):
                        pos_data.append(self.processed[ids][0][ix][iline])
                    if pos_data == candidate_intersect_pos_data:
                        for iv in range(self.nv):
                            added_values[iv][ii] += self.processed[ids][1][iv][iline]
        # finalize self.processed
        self.processed = [intersect_ds]
        self.processed[0][1] = added_values
        self.titles = ['add_intersect']
        self.last_process = 'add_intersect'
        self.nds = 1


    def split_by_row(self, number, name_index_offset=0):
        self.reset()
        if self.nds != 1:
            print("Error: split dataset operation is only allowed for single file input.")
            exit(1)
        combined_dataset = self.get_truncated()[0][2]
        split_dataset = {}
        split_indices = [x for x in range(0, len(combined_dataset), number)]
        if split_indices[-1] < len(combined_dataset):
            split_indices.append(len(combined_dataset))
        num_split_datasets = len(split_indices) - 1 # number of split datasets
        # start split_by_row
        self.titles = []
        self.processed = [[[], [], []] for ids in range(num_split_datasets)]
        for ids in range(num_split_datasets):
            split_data_lines = combined_dataset[split_indices[ids]:split_indices[ids + 1]]
            split_data_name = f"{'_'.join(split_data_lines[name_index_offset].split())}"
            self.processed[ids][2] = split_data_lines
            self.titles.append(split_data_name)
        # finalize self.processed
        self.sort = self.uniq = self.skipnan =  False
        self.nds = num_split_datasets
        self.last_process = 'split_by_row'


    def split_by_column(self, number, start_index_offset=0, name_index_offset=0):
        self.reset()
        if self.nds != 1:
            print("Error: split dataset operation is only allowed for single file input.")
            exit(1)

        combined_dataset = self.get_truncated()[0][2]
        split_dataset = {}
        split_indices = []
        for i, line in enumerate(combined_dataset):
            if len(line.split()) == number:
                split_indices.append(i + start_index_offset)
                if split_indices[-1] < 0:
                    print("Error: split_by_column(): 'split_index' cannot be negative!")
                    print("       (check argument 'start_index_offset')")
                    exit(1)

        if split_indices[-1] < len(combined_dataset):
            split_indices.append(len(combined_dataset))
        num_split_datasets = len(split_indices) - 1 # number of split datasets

        # start split_by_column
        self.titles = []
        self.processed = [[[], [], []] for ids in range(num_split_datasets)]
        for ids in range(num_split_datasets):
            split_data_lines = combined_dataset[split_indices[ids]:split_indices[ids+1]]
            split_data_name = f"{'_'.join(split_data_lines[name_index_offset].split())}"
            # self.processed[ids][2] = split_data_lines
            self.processed[ids][2] = ["", "", f"'{split_data_name}'"] + split_data_lines
            self.titles.append(split_data_name)
        # finalize self.processed
        self.sort = self.uniq = self.skipnan =  False
        self.nds = num_split_datasets
        self.last_process = 'split_by_column'


    def return_lines(self, merge=False):
        output_lines = [[] for ids in range(self.nds)]
        for ids in range(self.nds):
            nol = len(self.processed[ids][2])
            for iline in range(nol):
                pos_str = []
                for ix in range(len(self.processed[ids][0])):
                    pos_str.append( f"%{self.fmt[0]}f" %(self.processed[ids][0][ix][iline]) )
                str_line = ' '.join(pos_str)
                for iv in range(len(self.processed[ids][1])):
                    if self.processed[ids][1][iv][iline] != np.nan:
                        str_line = f"%s %{self.fmt[1]}f" %(str_line, self.processed[ids][1][iv][iline])
                    else:
                        str_line = f"{str_line} {np.nan}"
                if len(self.processed[ids][2][iline]) and not self.noextra:
                    str_line = "%s %s" %(str_line, self.processed[ids][2][iline])
                if self.nan:
                    str_line = str_line.strip()
                output_lines[ids].append(str_line)

        if merge:
            output_lines_merged = []
            for ids in range(len(output_lines)):
                output_lines_merged += output_lines[ids]
            output_lines = output_lines_merged
        
        for ids in range(len(output_lines)):
            if self.sort:
                output_lines[ids] = sorted(output_lines[ids])
            if self.uniq:
                uniq_lines = []
                for line in output_lines[ids]:
                    if line not in uniq_lines:
                        uniq_lines.append(line)
                output_lines[ids] = uniq_lines
        
        return output_lines


    def return_numerical(self, merge=False):
        if self.nan:
            print("Error: return_numerical operation is only allowed for numerical datasets")
            exit(1)
        num_numericals = self.nx + self.nv
        numericals = []
        if self.nds == 1:
            for ix in range(self.nx):
                numericals.append(self.processed[0][0][ix])
            for iv in range(self.nv):
                numericals.append(self.processed[0][1][iv])
        else:
            for ids in range(self.nds):
                numericals.append([])
                for ix in range(self.nx):
                    numericals[ids].append(self.processed[ids][0][ix])
                for iv in range(self.nv):
                    numericals[ids].append(self.processed[ids][1][iv])
            if merge:
                numericals_merged = numericals[0]
                for ids in range(1, self.nds):
                    for inum in range(num_numericals):
                        numericals_merged[inum] += numericals[ids][inum]
                numericals = numericals_merged

        return numericals


    def return_dataset(self):
        return self.processed


    def write(self, path=None):
        if path:
            pass
        else:
            output_lines = self.return_lines(merge=True)
            for line in output_lines:
                print(line)


    def get_truncated(self):
        # outputs a nan dataset object with header and footer lines removed
        truncated = []
        for ids in range(self.nds):
            if self.footer != 0:
                extra = self.lines[ids][self.header:-self.footer]
            else:
                extra = self.lines[ids][self.header:]
            truncated.append(
                [[ ], [ ], extra]
            #   [pos, val, extra]
            )
        return truncated


    def update(self):
        # check types
        try:
            assert isinstance(self.files, list)
        except AssertionError:
            print("Error: argument 'files' must be a list")
            exit(1)
        try:
            assert isinstance(self.header, int)
        except AssertionError:
            print("Error: argument 'header' must be an integer")
            exit(1)
        try:
            assert isinstance(self.footer, int)
        except AssertionError:
            print("Error: argument 'footer' must be an integer")
            exit(1)
        try:
            assert isinstance(self.x, list)
        except AssertionError:
            print("Error: argument 'x' must be a list")
            exit(1)
        try:
            assert isinstance(self.v, list)
        except AssertionError:
            print("Error: argument 'v' must be a list")
            exit(1)
        try:
            assert isinstance(self.skipnan, bool)
        except AssertionError:
            print("Error: argument 'skipnan' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.noextra, bool)
        except AssertionError:
            print("Error: argument 'noextra' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.fmt, list)
        except AssertionError:
            print("Error: argument 'fmt' must be a list")
            exit(1)
        try:
            assert isinstance(self.sort, bool)
        except AssertionError:
            print("Error: argument 'sort' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.uniq, bool)
        except AssertionError:
            print("Error: argument 'uniq' must be a boolean")
            exit(1)

        # truncate (remove header and footer lines): a nan dataset object
        self.processed = self.get_truncated()

        # update self.titles ?
        if len(self.titles) != len(self.processed):
            self.titles = []
            for i in range(self.nds):
                self.titles.append(os.path.split(self.files[i])[1])

        # is it a nan dataset?
        if len(self.x) == 0 and len(self.v) == 0:
            self.nan = True
            self.noextra = False
            self.skipnan = False
        else:
            self.nan = False

        # update/finalize dataset
        self.nx = len(self.x)
        self.nv = len(self.v)


        # initial processing of numerical datasets:
        if not self.nan:
            for ids in range(self.nds):
                pos = [[] for ix in range(self.nx)] # list of positional values
                val = [[] for iv in range(self.nv)] # list of values/data
                extra = self.processed[ids][2]
                nol = len(extra)
                for iline in range(nol):
                    extra_line_split = extra[iline].split()
                    remove_from_extra = []
                    ncol = len(extra_line_split)

                    # positional columns
                    for ix in range(self.nx):
                        pos_col = self.x[ix] - 1
                        if pos_col < 0 or pos_col >= ncol:
                            pos[ix].append(np.nan)
                            continue
                        pos_data_str = extra_line_split[pos_col]
                        try:
                            pos[ix].append(float(pos_data_str))
                        except ValueError:
                            pos[ix].append(np.nan)
                        # update remove_from_extra
                        if pos_data_str in extra_line_split:
                            remove_from_extra.append(pos_data_str)

                    # value columns
                    for iv in range(self.nv):
                        val_col = self.v[iv] - 1
                        if val_col < 0 or val_col >= ncol:
                            val[iv].append(np.nan)
                            continue
                        val_data_str = extra_line_split[val_col]
                        try:
                            val[iv].append(float(val_data_str))
                        except ValueError:
                            val[iv].append(np.nan)
                        # update remove_from_extra
                        if val_data_str in extra_line_split:
                            remove_from_extra.append(val_data_str)

                    # finalize extra for this line
                    for x in remove_from_extra:
                        if x in extra_line_split:
                            extra_line_split.remove(x)

                    extra_line = ' '.join(extra_line_split).strip()
                    self.processed[ids][2][iline] = extra_line
                self.processed[ids][0] = pos
                self.processed[ids][1] = val

            # skipnan process
            if self.skipnan:
                for ids in range(self.nds):
                    pos_skipnan = [[] for ix in range(self.nx)]
                    val_skipnan = [[] for iv in range(self.nx)]
                    extra_skipnan = []
                    nol = len(self.processed[ids][2])
                    for iline in range(nol):
                        temp = []
                        for ix in range(self.nx):
                            temp.append(self.processed[ids][0][ix][iline])
                        for iv in range(self.nv):
                            temp.append(self.processed[ids][1][iv][iline])
                        
                        if np.nan not in temp:
                            for ix in range(self.nx):
                                pos_skipnan[ix].append(self.processed[ids][0][ix][iline])
                            for iv in range(self.nv):
                                val_skipnan[iv].append(self.processed[ids][1][iv][iline])
                            extra_skipnan.append(self.processed[ids][2][iline])
                    self.processed[ids] = [pos_skipnan, val_skipnan, extra_skipnan]


    def reset(self):
        self.titles = []
        self.processed = []
        self.options(**vars(self.input_args))
        self.append(self.files)
        self.update()



#------------FUNCTIONS------------#

def calc_complementary_dataset(datasets, sub_dataset):
    # both datasets and sub_dataset must have the same number of
    # positional and value columns
    nds = len(datasets) # number of datasets
    nx = len(datasets[0][0]) # number of positional columns
    nv = len(datasets[0][1]) # number of velue columns
    complementary_dataset = [[[] for ix in range(nx)],\
                            [[] for iv in range(nv)],\
                             []]
    fmt = [".10",".10"]
    # collect sub_dataset lines
    sub_dataset_lines = []
    nol = len(sub_dataset[2]) # number of lines
    for iline in range(nol):
        line = ''
        for ix in range(nx):
            line = f"%s %{fmt[0]}f" %(line, sub_dataset[0][ix][iline])
        for iv in range(nv):
            line = f"%s %{fmt[1]}f" %(line, sub_dataset[1][iv][iline])
        line = f"%s %s" %(line, sub_dataset[2][iline])
        sub_dataset_lines.append(line.strip())

    # compare sub_dataset lines with all lines in datasets
    # and store the complementary ones
    found_complementary_lines = []
    for ids in range(nds):
        nol = len(datasets[ids][2]) # number of lines
        for iline in range(nol):
            line = ''
            for ix in range(nx):
                line = f"%s %{fmt[0]}f" %(line, datasets[ids][0][ix][iline])
            for iv in range(nv):
                line = f"%s %{fmt[1]}f" %(line, datasets[ids][1][iv][iline])
            line = f"%s %s" %(line, datasets[ids][2][iline])
            line = line.strip()
            if (line not in sub_dataset_lines) and (line not in found_complementary_lines):
                found_complementary_lines.append(line)
                for ix in range(nx):
                    complementary_dataset[0][ix].append(datasets[ids][0][ix][iline])
                for iv in range(nv):
                    complementary_dataset[1][iv].append(datasets[ids][1][iv][iline])
                complementary_dataset[2].append(datasets[ids][2][iline])

    return complementary_dataset

